# Find-It Demo (semantic product search — public exhibit)

AI search for a fictional demo shop, **Blue Ridge Outfitters**: 36
invented outdoor-gear products and 4 buying guides, each one chunk,
searched by meaning instead of keywords.

- **Vector retrieval only** (no structured baseline here — that
  comparison lives in `../vector-rag-demo/`). Chunks and preset
  questions are embedded with the exact settings of the vector demo:
  `google/embeddinggemma-2` via sentence-transformers, built-in
  document/query task prompts, 768 dims Matryoshka-truncated to 256,
  L2-renormalized, with the same `all-MiniLM-L6-v2` fallback recorded
  in META. The model actually used is named in `results.json` and in
  the shipped file's META.
- Embedded chunk text is `Name. Description` — what a real store's
  search index would see. Question text is embedded as the shopper
  typed it.
- **Dataset** (`dataset.py`): every product, price, and guide is
  invented for this demo and labeled fictional on the page.
  Descriptions are written the way good product pages read — use
  cases, who it suits, conditions.

## Pipeline

```bash
python3 dataset.py                                # -> chunks.json, questions.json
python pipeline.py                                # embed + score -> results.json
                                                  # + findit-data.js (needs requirements.txt)
node crosscheck.js                                # browser-ranking reproduction test
```

## Eval

8 preset shopper-intent questions ("a gift for my dad who just got
into winter hiking", "our toddler's first camping trip", …). Gold
chunks were hand-labeled as the answer a knowledgeable shop assistant
would give, each with a written rationale (in `dataset.py` and shipped
in `findit-data.js`). Metric: hit@5 (any gold chunk in the top 5).

**Result: 8/8 hit@5.** Full-precision scores live in `results.json`;
the shipped `findit-data.js` carries vectors rounded to 4 decimals,
and `crosscheck.js` proves the browser's ranking from those rounded
vectors reproduces the Python top-5 exactly for all 8 questions.

This is a small-catalog demonstration of method (40 chunks), not a
benchmark.
