#!/usr/bin/env python3
"""Run-time retrieval engine for the manual + retrieval demo.

Given a task, this script:
  1. SELECTS the relevant sections of manual/operation-manual.md
     (deterministic routing table below — the selection is visible in the
     run output, not hidden),
  2. QUERIES data/prices.db at run time for exactly the rows the task needs
     (parameterized SQL only),
  3. ASSEMBLES the full generation prompt — selected manual sections +
     retrieved rows + the task — and prints it as a delimited readout
     (the "what the model would receive" proof),
  4. PRODUCES a grounded answer computed deterministically from the
     retrieved rows only. If no rows are retrieved for a card, the answer
     is the manual's no-data guardrail sentence — nothing is invented.

Python 3 standard library only. No network, no external APIs.

Usage:
    python3 retrieve.py --type trend   --card "Ember Drake"
    python3 retrieve.py --type compare --card-a "Ember Drake" --card-b "Tidal Serpent"
    python3 retrieve.py --type lookup  --card "Solar Griffin"
    python3 retrieve.py "price trend for Crystal Phoenix"
"""

import argparse
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANUAL_PATH = ROOT / "manual" / "operation-manual.md"
DB_PATH = ROOT / "data" / "prices.db"

# --------------------------------------------------------------------------
# SECTION ROUTING TABLE (deterministic, visible by design)
#
# The manual is the "how"; not every task needs all of it. Routing:
#   trend   -> Role & Scope + Data Rules + Analysis Steps + Output Format
#              (compute a trend from the retrieved sales)
#   compare -> trend's sections + Guardrails
#              (comparisons are where unsupported claims sneak in, so the
#              guardrails ride along whenever two cards are compared)
#   lookup  -> Role & Scope + Data Rules + Output Format
#              (a single latest-sale report: no trend arithmetic, so no
#              Analysis Steps; no second card, so no Guardrails)
# --------------------------------------------------------------------------
ROUTING_TABLE = {
    "trend": ["Role & Scope", "Data Rules", "Analysis Steps", "Output Format"],
    "compare": ["Role & Scope", "Data Rules", "Analysis Steps", "Output Format", "Guardrails"],
    "lookup": ["Role & Scope", "Data Rules", "Output Format"],
}

COLUMNS = "card_name, set_name, condition, sale_date, price_usd, marketplace"


def parse_manual_sections(path):
    """Split the manual into {section_name: markdown_text} on '## ' headings."""
    sections = {}
    current = None
    buffer = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(buffer).strip()
            current = line[3:].strip()
            buffer = [line]
        elif current is not None:
            buffer.append(line)
    if current is not None:
        sections[current] = "\n".join(buffer).strip()
    return sections


def resolve_card_name(conn, name):
    """Return the canonical DB spelling for a card name (case-insensitive),
    or the name as given if the card is not in the database (no-data case)."""
    row = conn.execute(
        "SELECT card_name FROM price_history WHERE lower(card_name) = lower(?) LIMIT 1",
        (name.strip(),),
    ).fetchone()
    return row[0] if row else name.strip()


def fetch_rows(conn, task_type, card_name):
    """Query the DB at run time for exactly the rows the task needs.

    trend / compare: the card's full retrieved sale history, date-ordered.
    lookup:          only the single latest sale.
    """
    if task_type == "lookup":
        cur = conn.execute(
            f"SELECT {COLUMNS} FROM price_history WHERE card_name = ? "
            "ORDER BY sale_date DESC LIMIT 1",
            (card_name,),
        )
    else:
        cur = conn.execute(
            f"SELECT {COLUMNS} FROM price_history WHERE card_name = ? "
            "ORDER BY sale_date ASC",
            (card_name,),
        )
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def money(value):
    return f"${value:,.2f}"


def describe_sale(row):
    return (
        f"{money(row['price_usd'])} on {row['sale_date']} "
        f"({row['set_name']}, {row['condition']}, {row['marketplace']})"
    )


def format_rows_for_prompt(card_name, rows):
    lines = [f"Card: {card_name} — {len(rows)} row(s) retrieved"]
    if not rows:
        lines.append("  (no rows retrieved)")
    for r in rows:
        lines.append(
            f"  - {r['sale_date']} | {r['card_name']} | {r['set_name']} | "
            f"{r['condition']} | {money(r['price_usd'])} | {r['marketplace']}"
        )
    return "\n".join(lines)


def trend_stats(rows):
    first, last = rows[0], rows[-1]
    pct = (last["price_usd"] - first["price_usd"]) / first["price_usd"] * 100.0
    avg = sum(r["price_usd"] for r in rows) / len(rows)
    return {"first": first, "last": last, "pct": pct, "avg": avg}


def card_block(card_name, rows, include_change):
    """One card's grounded answer block, in the manual's Output Format."""
    if not rows:
        return (
            f"{card_name}\n"
            f"No data was retrieved for {card_name}.\n"
            "Basis: computed only from the retrieved rows above (none)."
        )
    stats = trend_stats(rows)
    lines = [
        card_name,
        f"Retrieved sales: {len(rows)}",
        f"Date range: {rows[0]['sale_date']} to {rows[-1]['sale_date']}",
        f"First retrieved sale: {describe_sale(stats['first'])}",
        f"Latest retrieved sale: {describe_sale(stats['last'])}",
    ]
    if include_change:
        lines.append(
            f"Change: {stats['pct']:+.2f}% "
            f"({money(stats['first']['price_usd'])} -> {money(stats['last']['price_usd'])})"
        )
        lines.append(f"Average retrieved price: {money(stats['avg'])}")
    lines.append(f"Basis: computed only from the {len(rows)} retrieved row(s) above.")
    return "\n".join(lines)


def build_answer(task_type, cards, rows_by_card):
    if task_type == "trend":
        return card_block(cards[0], rows_by_card[cards[0]], include_change=True)
    if task_type == "lookup":
        card = cards[0]
        rows = rows_by_card[card]
        if not rows:
            return (
                f"{card}\n"
                f"No data was retrieved for {card}.\n"
                "Basis: computed only from the retrieved rows above (none)."
            )
        return (
            f"{card}\n"
            f"Latest retrieved sale: {describe_sale(rows[0])}\n"
            "Basis: computed only from the 1 retrieved row above."
        )
    if task_type == "compare":
        a, b = cards
        blocks = [
            card_block(a, rows_by_card[a], include_change=True),
            card_block(b, rows_by_card[b], include_change=True),
        ]
        rows_a, rows_b = rows_by_card[a], rows_by_card[b]
        if rows_a and rows_b:
            latest_a = rows_a[-1]["price_usd"]
            latest_b = rows_b[-1]["price_usd"]
            diff = latest_a - latest_b
            diff_pct = diff / latest_b * 100.0
            if diff > 0:
                verdict = f"{a} ({money(latest_a)}) is {money(abs(diff))} higher than {b} ({money(latest_b)})"
            elif diff < 0:
                verdict = f"{a} ({money(latest_a)}) is {money(abs(diff))} lower than {b} ({money(latest_b)})"
            else:
                verdict = f"{a} and {b} have equal latest retrieved prices ({money(latest_a)})"
            blocks.append(
                "Latest-price comparison: "
                f"{verdict}, a difference of {diff_pct:+.2f}% relative to "
                f"{b}'s latest retrieved price."
            )
        else:
            missing = a if not rows_a else b
            blocks.append(
                f"Comparison not computed: no data was retrieved for {missing}."
            )
        return "\n\n".join(blocks)
    raise ValueError(f"unknown task type: {task_type}")


def assemble_prompt(task_text, section_names, sections, cards, rows_by_card):
    parts = [
        "=" * 72,
        "ASSEMBLED PROMPT — WHAT THE MODEL WOULD RECEIVE",
        "=" * 72,
        "",
        "[OPERATION MANUAL — SELECTED SECTIONS]",
        "",
    ]
    for name in section_names:
        parts.append(sections[name])
        parts.append("")
    parts.append("[RETRIEVED DATA — QUERIED FROM prices.db AT RUN TIME]")
    parts.append("")
    for card in cards:
        parts.append(format_rows_for_prompt(card, rows_by_card[card]))
        parts.append("")
    parts.append("[TASK]")
    parts.append(task_text)
    parts.append("")
    parts.append("=" * 72)
    parts.append("END ASSEMBLED PROMPT")
    parts.append("=" * 72)
    return "\n".join(parts)


def parse_task_string(task):
    """Parse the simple natural task forms used in the examples.

    Returns (task_type, [card, ...], canonical_task_text).
    """
    text = task.strip().rstrip(".")
    lower = text.lower()
    if lower.startswith("compare ") and " vs " in lower:
        # split on the original text to preserve card-name spelling/case
        idx = lower.index(" vs ")
        left = text[len("compare "):idx].strip()
        right = text[idx + len(" vs "):].strip()
        return "compare", [left, right], f"Compare {left} vs {right}"
    if lower.startswith("price trend for "):
        card = text[len("price trend for "):].strip()
        return "trend", [card], f"Price trend for {card}"
    if lower.startswith("trend for "):
        card = text[len("trend for "):].strip()
        return "trend", [card], f"Price trend for {card}"
    if lower.startswith("latest sale for "):
        card = text[len("latest sale for "):].strip()
        return "lookup", [card], f"Latest sale for {card}"
    if lower.startswith("lookup "):
        card = text[len("lookup "):].strip()
        return "lookup", [card], f"Latest sale for {card}"
    raise SystemExit(
        "Could not parse task. Use --type/--card flags, or one of: "
        "'price trend for <card>', 'compare <A> vs <B>', 'latest sale for <card>'."
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Manual + run-time retrieval demo engine.")
    parser.add_argument("task", nargs="?", help="Natural task string (see usage in the docstring).")
    parser.add_argument("--type", choices=sorted(ROUTING_TABLE), help="Task type.")
    parser.add_argument("--card", help="Card name (trend / lookup).")
    parser.add_argument("--card-a", help="First card (compare).")
    parser.add_argument("--card-b", help="Second card (compare).")
    args = parser.parse_args(argv)

    if args.type:
        task_type = args.type
        if task_type == "compare":
            if not (args.card_a and args.card_b):
                parser.error("compare requires --card-a and --card-b")
            raw_cards = [args.card_a, args.card_b]
            task_text = f"Compare {args.card_a} vs {args.card_b}"
        else:
            if not args.card:
                parser.error(f"{task_type} requires --card")
            raw_cards = [args.card]
            task_text = (
                f"Price trend for {args.card}"
                if task_type == "trend"
                else f"Latest sale for {args.card}"
            )
    elif args.task:
        task_type, raw_cards, task_text = parse_task_string(args.task)
    else:
        parser.error("provide a task string or --type with card flags")

    if not DB_PATH.exists():
        raise SystemExit(f"Database not found: {DB_PATH}\nRun: python3 data/build_db.py")

    sections = parse_manual_sections(MANUAL_PATH)
    section_names = ROUTING_TABLE[task_type]
    missing = [s for s in section_names if s not in sections]
    if missing:
        raise SystemExit(f"Manual is missing routed section(s): {missing}")

    conn = sqlite3.connect(DB_PATH)
    try:
        cards = [resolve_card_name(conn, c) for c in raw_cards]
        rows_by_card = {card: fetch_rows(conn, task_type, card) for card in cards}
    finally:
        conn.close()

    total_rows = sum(len(r) for r in rows_by_card.values())

    print("RUN-TIME SELECTION")
    print(f"Task type: {task_type}")
    print(f"Sections selected: {' | '.join(section_names)}")
    print(f"Rows retrieved: {total_rows}")
    print()
    print(assemble_prompt(task_text, section_names, sections, cards, rows_by_card))
    print()
    print("=" * 72)
    print("GROUNDED ANSWER — GENERATED FROM THE RETRIEVED ROWS ONLY")
    print("=" * 72)
    print(build_answer(task_type, cards, rows_by_card))
    return 0


if __name__ == "__main__":
    sys.exit(main())
