#!/usr/bin/env python3
"""Build the demo price database (data/prices.db).

SAMPLE DATA ONLY: every row in this database is synthetic, invented for this
demonstration. Card names, set names, dates, and prices are fictional and are
NOT real market prices. Do not cite them as market fact.

Reproducible: running this script deletes any existing prices.db and rebuilds
it from the SAMPLE_ROWS below. Python 3 standard library only.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "prices.db"

# (card_name, set_name, condition, sale_date, price_usd, marketplace)
# All values are synthetic sample data.
SAMPLE_ROWS = [
    # Ember Drake — clean upward trend: 40.00 -> 48.00 (+20.00%)
    ("Ember Drake", "Ashes of Avaris", "Near Mint", "2026-01-05", 40.00, "Auction"),
    ("Ember Drake", "Ashes of Avaris", "Lightly Played", "2026-02-11", 44.00, "Marketplace"),
    ("Ember Drake", "Ashes of Avaris", "Near Mint", "2026-03-19", 46.00, "Auction"),
    ("Ember Drake", "Ashes of Avaris", "Near Mint", "2026-04-22", 48.00, "Marketplace"),
    # Tidal Serpent — 30.00 -> 33.00 (+10.00%); latest price below Ember Drake
    ("Tidal Serpent", "Mists of Lir", "Near Mint", "2026-01-08", 30.00, "Marketplace"),
    ("Tidal Serpent", "Mists of Lir", "Moderately Played", "2026-02-14", 28.50, "Auction"),
    ("Tidal Serpent", "Mists of Lir", "Lightly Played", "2026-03-10", 31.00, "Marketplace"),
    ("Tidal Serpent", "Mists of Lir", "Near Mint", "2026-04-18", 33.00, "Auction"),
    # Gloomwood Knight — slight decline: 12.00 -> 11.40 (-5.00%)
    ("Gloomwood Knight", "Thornfall Court", "Lightly Played", "2026-01-21", 12.00, "Auction"),
    ("Gloomwood Knight", "Thornfall Court", "Near Mint", "2026-02-27", 13.20, "Marketplace"),
    ("Gloomwood Knight", "Thornfall Court", "Moderately Played", "2026-04-02", 11.40, "Auction"),
    # Solar Griffin — 55.00 -> 60.50 (+10.00%); latest sale 2026-04-25
    ("Solar Griffin", "Dawnspire", "Near Mint", "2026-01-15", 55.00, "Marketplace"),
    ("Solar Griffin", "Dawnspire", "Lightly Played", "2026-02-20", 52.25, "Auction"),
    ("Solar Griffin", "Dawnspire", "Near Mint", "2026-03-28", 57.75, "Marketplace"),
    ("Solar Griffin", "Dawnspire", "Near Mint", "2026-04-25", 60.50, "Auction"),
    # Obsidian Golem — 8.00 -> 9.60 (+20.00%)
    ("Obsidian Golem", "Deepvault", "Moderately Played", "2026-01-30", 8.00, "Auction"),
    ("Obsidian Golem", "Deepvault", "Lightly Played", "2026-03-05", 8.80, "Marketplace"),
    ("Obsidian Golem", "Deepvault", "Near Mint", "2026-04-12", 9.60, "Marketplace"),
]


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE price_history (
                card_name   TEXT NOT NULL,
                set_name    TEXT NOT NULL,
                condition   TEXT NOT NULL,
                sale_date   TEXT NOT NULL,
                price_usd   REAL NOT NULL,
                marketplace TEXT NOT NULL
            )
            """
        )
        conn.executemany(
            "INSERT INTO price_history "
            "(card_name, set_name, condition, sale_date, price_usd, marketplace) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            SAMPLE_ROWS,
        )
        conn.commit()
    finally:
        conn.close()
    print(f"Built {DB_PATH} with {len(SAMPLE_ROWS)} synthetic sample rows.")


if __name__ == "__main__":
    main()
