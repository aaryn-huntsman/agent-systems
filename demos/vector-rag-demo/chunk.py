#!/usr/bin/env python3
"""Chunk the vector-RAG demo corpus: Aaryn's own operations manuals only.

Sources (all his own operations text — no lore DB, no book text):
  - demos/manual-retrieval-demo/manual/operation-manual.md
  - agents/chewybits-series-expert/manual.md   (largest vault manual)
  - agents/rbm-service-delivery/manual.md      (second largest)
  - agents/chewybits-scriptwriter/manual.md    (third largest)
  - agents/prospect-researcher/manual.md       (added: see note)
  - agents/vault-keeper/manual.md              (added: see note)
  - agents/rbm-funnel-operator/manual.md       (added: see note)

Note: the first four sources total only ~9K tokens, which at spec chunk
sizes yields ~52 chunks — well under the 120-250 target. Three more of
Aaryn's own agent manuals were added to reach a corpus size where the
target is attainable without shredding sections into fragments. The
own-text-only constraint is unchanged.

Chunking: split on ## / ### headings (chunk keeps its heading line and
records source + heading path). Sections over MAX_TOKENS are split at
paragraph boundaries; fragments under MIN_TOKENS merge into the previous
chunk of the same document. Token counts are estimates: words * 1.3.
"""
import json
import re
from pathlib import Path

# Public-export adaptation: the original run chunked seven of the author's
# own operations manuals. Six are private working documents and are not
# shipped; chunks.json is the frozen corpus. To re-chunk from source, list
# your own Markdown manuals here — the one public source is wired up below.
SOURCES = [
    ("operation-manual", Path(__file__).parent / "../manual-retrieval-demo/manual/operation-manual.md"),
]
MAX_TOKENS = 380
MIN_TOKENS = 50


def est_tokens(text):
    return round(len(text.split()) * 1.3)


def split_sections(text):
    """Return [(heading_path, heading_line, body_text)] split on ## and ###."""
    sections = []
    path = []
    heading_line = ""
    buf = []
    title = ""

    def flush():
        if buf or heading_line:
            sections.append((" > ".join(path), heading_line, "\n".join(buf).strip()))

    for line in text.splitlines():
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m and len(m.group(1)) == 1 and not title:
            title = m.group(2).strip()
            path = [title]
            heading_line = line
            continue
        if m and len(m.group(1)) in (2, 3):
            flush()
            level = len(m.group(1))
            name = m.group(2).strip()
            path = [title, name] if level == 2 else [title, path[1] if len(path) > 1 else "", name]
            path = [p for p in path if p]
            heading_line = line
            buf = []
            continue
        buf.append(line)
    flush()
    return sections


def split_long(heading_path, heading_line, body):
    """Split an over-long section at paragraph boundaries."""
    full = (heading_line + "\n\n" + body).strip()
    if est_tokens(full) <= MAX_TOKENS:
        return [(heading_path, full)]
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    pieces, cur = [], heading_line
    for p in paras:
        candidate = cur + "\n\n" + p
        if est_tokens(candidate) > MAX_TOKENS and cur != heading_line:
            pieces.append(cur)
            cur = heading_line + "\n\n" + p
        else:
            cur = candidate
    pieces.append(cur)
    # A single paragraph can still exceed the cap; hard-split on sentences.
    out = []
    for piece in pieces:
        if est_tokens(piece) <= MAX_TOKENS:
            out.append(piece)
            continue
        sentences = re.split(r"(?<=[.!?])\s+", piece)
        cur = ""
        for s in sentences:
            if est_tokens(cur + " " + s) > MAX_TOKENS and cur:
                out.append(cur.strip())
                cur = s
            else:
                cur = (cur + " " + s).strip()
        if cur:
            out.append(cur)
    return [(heading_path, t.strip()) for t in out if t.strip()]


def chunk_document(source_key, path):
    raw = []
    for heading_path, heading_line, body in split_sections(path.read_text(encoding="utf-8")):
        raw.extend(split_long(heading_path, heading_line, body))
    # Merge tiny fragments into the previous chunk of the same document.
    merged = []
    for heading_path, text in raw:
        if merged and est_tokens(text) < MIN_TOKENS:
            prev_heading, prev_text = merged[-1]
            merged[-1] = (prev_heading, prev_text + "\n\n" + text)
        else:
            merged.append((heading_path, text))
    chunks = []
    for i, (heading_path, text) in enumerate(merged):
        leaf = heading_path.split(" > ")[-1]
        chunks.append({
            "id": f"{source_key}-{i:03d}",
            "source": source_key,
            "heading": leaf,
            "heading_path": heading_path,
            "text": text,
            "est_tokens": est_tokens(text),
        })
    return chunks


def main():
    all_chunks = []
    for key, path in SOURCES:
        chunks = chunk_document(key, path)
        all_chunks.extend(chunks)
        toks = [c["est_tokens"] for c in chunks]
        print(f"{key}: {len(chunks)} chunks, tokens min {min(toks)} / med {sorted(toks)[len(toks)//2]} / max {max(toks)}")
    out = Path(__file__).parent / "chunks.json"
    out.write_text(json.dumps(all_chunks, indent=1), encoding="utf-8")
    toks = sorted(c["est_tokens"] for c in all_chunks)
    print(f"TOTAL: {len(all_chunks)} chunks | tokens min {toks[0]} med {toks[len(toks)//2]} max {toks[-1]}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
