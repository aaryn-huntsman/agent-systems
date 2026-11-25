# Vector RAG Demo (Project 2 — public exhibit)

Same questions, two retrievers, scored side by side:

- **Vector retrieval** — chunks and preset questions embedded with a local
  embedding model, ranked by cosine similarity.
- **Structured routing** — deterministic keyword routing in the spirit of
  `../manual-retrieval-demo/retrieve.py`: score each manual section by
  question-word overlap (heading matches weigh 3×), route to the best
  section, rank its chunks by the same overlap. No embeddings.

## Corpus

Aaryn's own operations text only — never the lore DB, never book text.
Seven manuals (see `chunk.py` header for the list and for why the corpus
grew from the planned four manuals to seven: the first four total only
~9K tokens, too small for the target chunk count at honest chunk sizes).

Chunking (`chunk.py`): split on `##`/`###` headings, sections over ~380
estimated tokens split at paragraph boundaries, fragments under ~50
tokens merged into the previous chunk. Token counts are estimates
(words × 1.3).

## Pipeline

```bash
python3 chunk.py                      # -> chunks.json
python pipeline.py                    # embed + score -> results.json
                                      # + vector-data.js (needs requirements.txt)
node crosscheck.js                    # browser-ranking reproduction test
```

`pipeline.py` tries `google/embeddinggemma-2` first (768 dims,
Matryoshka-truncated to 256, L2-renormalized; built-in document/query
task prompts when the model config exposes them) and falls back to
`all-MiniLM-L6-v2` if the Gemma model cannot load on this VM. The model
actually used is recorded in `results.json` and in the shipped file's
META — the page names it, whichever one ran.

## Eval

8 preset questions, gold chunks hand-labeled and verified by reading
each chunk. Metric: hit@5 (any gold chunk in the top 5). Full-precision
scores live in `results.json`; the shipped `vector-data.js` carries
vectors rounded to 4 decimals, and `crosscheck.js` proves the browser's
ranking from those rounded vectors reproduces the Python top-5 exactly.

This is a small-corpus demonstration of method, not a benchmark.

## Public export note

The corpus was chunked from seven of the author's own operations manuals.
Six are private working documents and are not shipped; `chunks.json` is the
frozen corpus from that run, redacted for publication in two passes —
personal identifiers (a mailbox address and home-directory paths) and
commercially sensitive spans (unreleased-offer pricing, prospecting quotas,
internal strategy/SLA terms) replaced with `[redacted — …]` placeholders;
chunk IDs, counts, and vectors untouched — `results.json` is the
full-precision audit of that run, and `vector-data.js` is the rounded file
the live site serves. The pipeline was re-run from scratch on the redacted
corpus and re-measured the same scores (vector hit@5 7/8, structured 4/8),
so the published numbers are earned by the corpus as shipped here.
`chunk.py` is included so the chunking method is inspectable and
reusable on any Markdown corpus.
