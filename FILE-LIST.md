# FILE LIST — GitHub public export staging (prepared 2026-11-24)

**Status: PREP ONLY.** Nothing has been pushed, no repo created, no sign-in
attempted. This folder is the exact set proposed for Aaryn's line-by-line
review. 30 files (incl. this list), ~775 KB total.

---

## ✅ REVIEW FLAG — RESOLVED 2026-11-24 (redaction path, Aaryn-approved)

`demos/vector-rag-demo/chunks.json` and `demos/vector-rag-demo/vector-data.js`
contain **verbatim text excerpts from six private operations manuals** — that
is what the vector demo's corpus is. The excerpts include business-internal
material: unreleased RBM product pricing (e.g. Missed-Call Rescue, Review
Engine), prospecting quotas and tracker schema, series-bible product
strategy, and internal procedure detail.

**Resolution:** Aaryn approved Muse's redaction recommendation (2026-11-24).
Every commercially sensitive span in the staged copies — unreleased-offer
pricing, prospecting quotas/targets, the bible product-strategy rule,
internal SLA/refund terms — was replaced with a neutral
`[redacted — …]` placeholder (see "Sensitive-span redaction pass" under
Redactions). Chunk IDs, counts, vectors, and question/gold mappings are
untouched, and the full pipeline was re-run from scratch on the redacted
corpus: **hit@5 re-measured at vector 7/8 vs structured 4/8 — unchanged**
(same per-question hit/miss pattern), so the scores in this export are earned
by the redacted corpus as shipped.

Still true, and noted for the record: **the identical unredacted text is
served publicly today** — `vector-data.js` is the live file behind
revolutionarybusinessmarketing.com/tools/vector/demo, readable by anyone who
views the page source. Redacting the live site's copy is a separate decision
for Aaryn (assessment delivered with the redaction report).

---

## Files

| File | Size | Why it's here |
|------|------:|---------------|
| `README.md` | 5,677 B | The claim → live demo → code path → verified result map, with honest scope notes |
| `FILE-LIST.md` | (this file) | Review manifest: every file, its size, its justification |
| `.github/workflows/verify.yml` | 1,917 B | CI: re-runs the retrieval evals + both cross-checks + a Python compile pass on every push |
| `requirements.txt` | 266 B | numpy + sentence-transformers — only needed to re-run the embedding pipelines from scratch |
| `.gitignore` | 26 B | .venv / __pycache__ hygiene |
| `agents/chewybits-scriptwriter/prompt.md` | 11,392 B | The Aaryn-approved sanitized scriptwriter contract artifact, verbatim, at its planned repo path |
| `finetune-project3/DATA-CARD.md` | 13,421 B | Dataset design + base-vs-tuned eval protocol + the (blank, by design) results-table template. Dataset itself NOT included |
| `demos/manual-retrieval-demo/README.md` | 4,063 B | Demo doc: architecture, run instructions, honest scope note (synthetic data, no embeddings) |
| `demos/manual-retrieval-demo/retrieve.py` | 12,784 B | The run-time retrieval engine (section routing + parameterized SQL + prompt assembly + grounded answer) |
| `demos/manual-retrieval-demo/manual/operation-manual.md` | 3,500 B | The "how": standing instructions in headed sections; contains no prices |
| `demos/manual-retrieval-demo/data/build_db.py` | 3,486 B | Builds the synthetic sample price DB |
| `demos/manual-retrieval-demo/data/prices.db` | 8,192 B | The built sample DB (18 synthetic rows; fictional cards/prices, labeled synthetic) |
| `demos/manual-retrieval-demo/evals/cases.json` | 1,915 B | The 4 eval cases |
| `demos/manual-retrieval-demo/evals/run_evals.py` | 3,048 B | The eval battery — exits non-zero on any failure |
| `demos/manual-retrieval-demo/output/example-run.txt` | 4,855 B | Captured full run + eval summary, so the demo can be read without running it |
| `demos/vector-rag-demo/README.md` | 2,730 B | Demo doc + public-export note on the corpus (see Review Flag) |
| `demos/vector-rag-demo/chunk.py` | 5,628 B | The chunking method, inspectable and reusable on any Markdown corpus (sources adapted — see Adaptations) |
| `demos/vector-rag-demo/chunks.json` | 110,566 B | The frozen corpus, 92 chunks (identifiers + commercially sensitive spans redacted — see Redactions) |
| `demos/vector-rag-demo/pipeline.py` | 10,123 B | Embed + score pipeline for both retrievers (output path adapted — see Adaptations) |
| `demos/vector-rag-demo/results.json` | 7,253 B | Full-precision scored run: vector 7/8 vs structured 4/8 hit@5, per-question top-5s and routes |
| `demos/vector-rag-demo/vector-data.js` | 326,082 B | The shipped rounded-vector file the live site serves (identifiers + commercially sensitive spans redacted in the staged copy — see Redactions); makes `crosscheck.js` runnable standalone |
| `demos/vector-rag-demo/crosscheck.js` | 2,273 B | Proves the browser ranking from shipped rounded vectors reproduces the Python top-5 exactly (paths adapted) |
| `demos/findit-demo/README.md` | 2,185 B | Demo doc: fictional catalog, method, 8/8 result |
| `demos/findit-demo/dataset.py` | 25,140 B | The fictional Blue Ridge Outfitters catalog + hand-labeled gold answers with rationales |
| `demos/findit-demo/chunks.json` | 21,754 B | The 40 catalog chunks (36 products + 4 guides, all invented) |
| `demos/findit-demo/questions.json` | 2,435 B | The 8 shopper-intent questions |
| `demos/findit-demo/pipeline.py` | 7,081 B | Embed + score pipeline (output path adapted) |
| `demos/findit-demo/results.json` | 5,847 B | Full-precision scored run: hit@5 8/8 |
| `demos/findit-demo/findit-data.js` | 128,416 B | The shipped rounded-vector file the live site serves; makes `crosscheck.js` runnable standalone |
| `demos/findit-demo/crosscheck.js` | 2,181 B | Browser-ranking reproduction check (paths adapted) |

## Adaptations applied to staged copies (originals untouched)

The demos were written against the live workspace; four small edits make the
staged copies self-contained. Nothing else was reworded.

1. `vector-rag-demo/pipeline.py`, `findit-demo/pipeline.py` — output path
   changed from the site's showcase-build folder to a local `./<demo>-data.js`.
2. `vector-rag-demo/crosscheck.js`, `findit-demo/crosscheck.js` — input paths
   changed from absolute home paths to files alongside the script.
3. `vector-rag-demo/chunk.py` — the SOURCES list pointed at six private
   manuals by absolute path; it now wires the one public source (the
   manual-retrieval demo's operation manual) and documents the rest.
   `chunks.json` is the frozen corpus from the original run.
4. Both demo READMEs — virtualenv invocation lines replaced with a plain
   `python pipeline.py` + requirements note; the vector README gained the
   public-export note about the corpus.
5. `finetune-project3/DATA-CARD.md` — an export note added at the top; two
   absolute workspace paths generalized to descriptions; the `cases.md`
   reference annotated as a private companion file.

## Redactions (secrets scan remediation — staged copies only)

Applied to the `text` fields of `chunks.json` and `vector-data.js` (chunk
IDs, gold labels, and vectors untouched; crosscheck re-verified after):

- 1× personal mailbox address (a non-business Gmail) →
  `[redacted-personal-mailbox]`
- 42× `~/workspace/` path prefixes → `~/`, plus 1× absolute
  home-directory path → `~/`
- 1× internal goal-folder slug → `goals/<income-goal>/`

### Sensitive-span redaction pass (2026-11-24, Aaryn-approved)

Applied to the `text`, `heading`, and `heading_path` fields of `chunks.json`
and `vector-data.js` (15 chunks per file; chunk IDs, counts, vectors, and
question/gold mappings byte-identical after — asserted programmatically):

- **Unreleased-offer pricing (12 span types):** Missed-Call Rescue,
  Review Engine, Launch Intel, and Shorts Foundry price figures →
  `[redacted — unreleased offer pricing]`; the Shorts Foundry SLA →
  `[redacted — unreleased offer terms]`
- **Prospecting quotas/targets (3 spans):** the per-lane quota figures, the
  weekly lane split, and the LANE-FULL quota tuple →
  `[redacted — internal prospecting quotas]`
- **Internal strategy/financial terms (4 spans):** the series-bible
  product-strategy rule → `[redacted — internal product strategy]`; the SLA
  refund percentage (×2) → `[redacted — internal SLA term]`; the Review
  Engine response-time targets → `[redacted — internal service targets]`

Deliberately NOT redacted: the already-public live prices (the $199/$299/$497
teardown tiers and $99/$275/$699 docket tiers named in the vault-keeper
fact-class table, and the live $199 Stripe link) — redacting published prices
would buy nothing. After the pass, the only remaining match for any redacted
figure anywhere in the tree is those public tiers.

## Secrets scan — final result (2026-11-24)

Grepped the full staged tree for: API-key/token patterns (`sk-`, `rk_`,
`ghp_`, `AKIA`, bearer headers, PEM blocks), the Cloudflare account ID,
all email addresses, the user's phone number, iCloud/personal Gmail
addresses, and absolute home paths. **Clean.** The only email addresses
remaining anywhere are the two public business addresses —
`contact@chewybits.com` and `contact@revolutionarybusinessmarketing.com`.
No credentials, no account IDs, no model weights, no `.venv`.

## Excluded by default (never staged)

- All 28 agent vaults (prompts, manuals, knowledge, learnings) — except the
  single Aaryn-approved sanitized scriptwriter contract above
- `lore.db` and the series vaults/bibles
- The Chewy Bits script library (DRAFT/STORY files)
- `finetune-project3/train.jsonl` and `eval.jsonl` — the dataset stays
  private; a held-out set only works if it stays held out
- `finetune-project3/cases.md` — per-case criteria for the held-out set;
  held with the dataset as a judgment call (the DATA-CARD's protocol and
  blank results template are included). Aaryn can reverse this at review
- `finetune-project3/work/` — dataset extraction/build scripts that read
  the private deliverables
- Prospect data, deploy tooling (incl. the Cloudflare helpers), the site
  Worker sources, and anything carrying credentials or account identifiers
- The vector demo's `.venv` (~1.4 GB of third-party packages) and all
  `__pycache__`

## Verification performed in staging (2026-11-24)

All batteries run from the staged copies themselves, after patching and
redaction:

- `demos/manual-retrieval-demo`: `build_db.py` + `run_evals.py` → **4/4 PASS**
- `demos/vector-rag-demo`: `node crosscheck.js` → **CROSS-CHECK PASS**
  (JS-derived hit@5 7/8 = META 7/8; 92 chunks, 256 dims)
- `demos/findit-demo`: `node crosscheck.js` → **CROSS-CHECK PASS**
  (hit@5 8/8 = META 8/8; 40 chunks)
- All staged Python compiles clean (`py_compile`, mirroring the CI job)
- Numbers in the root README were recomputed from the staged
  `results.json` files, not copied from prose: vector 7/8, structured 4/8,
  Find-It 8/8, retrieval evals 4/4

**Re-verification after the sensitive-span redaction pass (2026-11-24):**

- All four staged batteries re-run from the redacted staged copies:
  manual evals **4/4 PASS**; vector `crosscheck.js` **CROSS-CHECK PASS**
  (7/8 = META); Find-It `crosscheck.js` **CROSS-CHECK PASS** (8/8 = META);
  `py_compile` clean
- **Full re-measurement:** `pipeline.py` re-run from scratch (EmbeddingGemma
  2, local) on the *redacted* `chunks.json` in a scratch copy — the redacted
  text was re-embedded and both retrievers re-scored: **vector hit@5 7/8,
  structured hit@5 4/8 — identical to the original run**, including the same
  per-question hit/miss pattern. The shipped `results.json` and
  `vector-data.js` therefore stand as measured on the corpus as published
  here; no number in this export is carried over from the unredacted corpus
  on faith.
- Secrets scan re-run over the full tree after the pass: **clean** (the two
  literals the scan initially caught were inside this manifest's own
  redaction notes; they are now described, not printed)
