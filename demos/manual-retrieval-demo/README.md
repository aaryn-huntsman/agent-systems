# Manual + Run-Time Retrieval — Reference Demo

A small, self-contained, runnable demonstration of one architecture:

**an operation manual (the "how") + a database (the "what") + run-time
retrieval that selects the right slice of each, per task, before generation.**

This is retrieval-augmented generation in its structured, database-grounded
form: retrieval happens inside the system, at run time, in response to the
task — not by a human pasting facts into a chat. Python 3 standard library
only; runs fully offline; no external APIs.

## Architecture

```
  manual/operation-manual.md          data/prices.db
  standing instructions               sales records
       ("how")                           ("what")
          \                                 /
           \                               /
            v                             v
              retrieve.py  (the run-time engine)
                1. routes the task -> selects manual sections
                2. queries SQLite  -> retrieves the rows needed
                3. assembles the prompt (the augmentation)
                4. generates a grounded answer from the rows only
                          |
                          v
            prompt readout  +  grounded answer
```

- **Manual = how.** `manual/operation-manual.md` holds standing instructions
  in individually headed sections (Role & Scope, Data Rules, Analysis Steps,
  Output Format, Guardrails). It contains no prices.
- **Database = what.** `data/prices.db` holds the facts (a `price_history`
  table). The database here stands in for an external asset store — the
  "bucket" — kept local so the whole pattern is visible in one folder.
- **Retriever = run-time selection.** `retrieve.py` picks manual sections
  via a visible routing table and queries the DB with parameterized SQL for
  exactly the rows the task needs.
- **Assembled prompt = augmentation.** The run prints the full prompt a
  model would receive: selected manual sections + retrieved rows + task.
- **Answer = generation.** Computed deterministically in code from the
  retrieved rows only (trend percentages, averages, comparisons). A card
  with no rows gets the manual's no-data guardrail answer — nothing is
  invented.

## How this maps to the real systems

- **The card-price system (confirmed pattern):** an AI working under an
  operation manual authored for it, querying a trading-card price database
  on its own at run time and grounding its output in retrieved prices rather
  than model memory. This demo is that architecture, rebuilt small and
  inspectable: manual -> the "how," database lookups -> the "what."
- **The RBM Hub's design intent:** generators designed to point to a manual
  (blueprint) and retrieve data, with the blueprint assets pulled from a
  bucket at run time rather than stored in the repo. Here the "bucket" is
  simply the local `manual/` + `data/` folders, so nothing is hidden.

## Run it

```bash
python3 data/build_db.py            # build the sample database
python3 retrieve.py --type trend   --card "Ember Drake"
python3 retrieve.py --type compare --card-a "Ember Drake" --card-b "Tidal Serpent"
python3 retrieve.py --type lookup  --card "Solar Griffin"
python3 retrieve.py "price trend for Crystal Phoenix"   # no-data guardrail
python3 evals/run_evals.py          # 4 cases; exits non-zero on any failure
```

`output/example-run.txt` contains a captured full run plus the eval summary,
so the demo can be read without running anything.

## Honest scope note

- All prices in the database are **synthetic sample data** — fictional
  cards, sets, dates, and prices, labeled as such everywhere. Nothing here
  is a real market price.
- Retrieval is **structured/database-grounded**: deterministic section
  routing + parameterized SQL. There are **no embeddings and no vector
  search** in this demo. Adding the vector mechanism is a separate project
  (skill-plan Project 2), which will use this demo as its baseline: same
  tasks, same evals, retrieval layer swapped, results compared.
