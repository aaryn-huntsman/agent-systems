# Evidence Locker — Aaryn Huntsman's Agent Systems

This repository is the public evidence locker for a working fleet of AI agent
systems: the runnable demos, one real subagent contract, and the fine-tuning
data card behind the claims on
[revolutionarybusinessmarketing.com/tools](https://revolutionarybusinessmarketing.com/tools).

It is deliberately an *evidence* repo, not the operating system itself. The
production fleet — 28 agent vaults (prompts, manuals, learnings), the lore
database, the script library, and the deploy tooling — stays private. The
architecture is visible here; the corpus and the accumulated learnings are
the business, and they are not in this repo.

## Claim → demo → code → result

| # | Claim | Live demo | Code in this repo | Verified result |
|---|-------|-----------|-------------------|-----------------|
| 1 | Structured RAG works without embeddings: an operation manual (the "how") + a database (the "what") + run-time retrieval that selects the right slice of each per task, before generation | [revolutionarybusinessmarketing.com/tools/retrieval/demo](https://revolutionarybusinessmarketing.com/tools/retrieval/demo) | [`demos/manual-retrieval-demo/`](demos/manual-retrieval-demo/) | Evals **4/4 PASS** — `evals/run_evals.py` exits non-zero on any failure; stdlib only, runs fully offline |
| 2 | On the same questions over the same corpus, vector retrieval beats keyword/section routing | [revolutionarybusinessmarketing.com/tools/vector/demo](https://revolutionarybusinessmarketing.com/tools/vector/demo) | [`demos/vector-rag-demo/`](demos/vector-rag-demo/) | hit@5: **vector 7/8 vs structured 4/8** (EmbeddingGemma 2, 768 dims Matryoshka-truncated to 256). Gold #1 on 6 of 8. `crosscheck.js` proves the browser ranking from the shipped rounded vectors reproduces the Python top-5 exactly |
| 3 | Semantic (vector) product search over a small catalog answers shopper-intent questions keywords miss | [revolutionarybusinessmarketing.com/tools/find-it/demo](https://revolutionarybusinessmarketing.com/tools/find-it/demo) | [`demos/findit-demo/`](demos/findit-demo/) | hit@5: **8/8** over a 40-chunk fictional catalog (Blue Ridge Outfitters — every product invented and labeled fictional) |
| 4 | Subagents run on explicit primary↔subagent contracts: role, minimal context, hard boundaries, a machine-checkable output contract, named failure classes, a learnings loop | — (contract document) | [`agents/chewybits-scriptwriter/prompt.md`](agents/chewybits-scriptwriter/prompt.md) | The actual production prompt for the Chewy Bits scriptwriter agent, sanitized for publication (paths generalized; one pacing figure corrected at the operator's direction) and approved for release 2026-11-24 |
| 5 | Fine-tuning is for *behavior*, retrieval is for *facts*: a dataset built from real production edit pairs (draft → accepted), with a frozen held-out set and a pre-registered base-vs-tuned protocol | [revolutionarybusinessmarketing.com/tools/evals](https://revolutionarybusinessmarketing.com/tools/evals) | [`finetune-project3/DATA-CARD.md`](finetune-project3/DATA-CARD.md) | Dataset built and verified: 28 training pairs + 10 held-out, extracted mechanically from production files and asserted as exact substrings; zero leakage between train and held-out (checked programmatically). **The run has not happened yet** — the results table in the data card is the blank template, and it stays blank until the run fills it |

## Run it

```bash
# 1 — structured retrieval (Python 3 stdlib only, fully offline)
cd demos/manual-retrieval-demo
python3 data/build_db.py
python3 retrieve.py --type trend --card "Ember Drake"
python3 evals/run_evals.py            # 4/4 PASS

# 2 + 3 — cross-checks (Node; verify shipped data reproduces the scored rankings)
cd demos/vector-rag-demo && node crosscheck.js    # CROSS-CHECK PASS, hit@5 7/8
cd demos/findit-demo && node crosscheck.js        # CROSS-CHECK PASS, hit@5 8/8

# Re-running the embedding pipelines from scratch needs the model:
pip install -r requirements.txt       # numpy + sentence-transformers
cd demos/vector-rag-demo && python3 pipeline.py   # downloads google/embeddinggemma-2
```

CI (`.github/workflows/verify.yml`) re-runs all three verification batteries
on every push: the retrieval evals, and both cross-checks against the shipped
data files.

## Honest scope notes

- Every demo here is a **small-corpus demonstration of method, not a
  benchmark**. Corpora are 18 synthetic price rows, 92 manual chunks, and 40
  fictional products — sized to be inspectable end to end.
- The vector demo's corpus was chunked from seven of the author's own
  operations manuals. Six are private working documents and are **not**
  shipped; `chunks.json` is the frozen corpus from that run, with personal
  identifiers and commercially sensitive spans (unreleased-offer pricing,
  prospecting quotas, internal strategy terms) redacted for publication,
  and the headline scores re-measured on the redacted corpus — vector 7/8
  vs structured 4/8, unchanged (see FILE-LIST.md).
- The fine-tune dataset is **not** in this repo — only its data card and
  protocol. The pairs are built from unpublished production scripts, and a
  held-out eval set only works if it stays held out.
- Sample data is synthetic and labeled as such everywhere it appears.

## Layout

```
demos/manual-retrieval-demo/   structured RAG: manual + SQLite + run-time retrieval
demos/vector-rag-demo/         vector vs structured retrieval, same questions, scored
demos/findit-demo/             semantic product search over a fictional catalog
agents/chewybits-scriptwriter/ one real subagent contract (sanitized, approved)
finetune-project3/             DATA-CARD.md — dataset design + eval protocol (dataset private)
FILE-LIST.md                   every file in this export, its size, and why it's here
```
