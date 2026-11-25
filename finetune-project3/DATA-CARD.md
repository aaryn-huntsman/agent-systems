# Project 3 — Fine-tuning dataset: DATA CARD

> **Public export note (2026-11-24):** This data card and the eval protocol below are
> published as evidence of method. The dataset itself — `train.jsonl`, `eval.jsonl`, and
> the per-case criteria file `cases.md` — is **not** included: the pairs are built from
> unpublished production scripts, and a held-out eval set only works if it stays held out.
> Absolute workspace paths in the original were generalized to descriptions. The results
> table at the bottom is the template the run will fill; it is intentionally blank because
> the fine-tune run has not happened yet.


**Purpose:** teach a small model the ChewyBits segment writer's STORY-pass *behavior* — how Aaryn's accepted edits transform a draft segment — so a tuned model performs the edit the way the production record shows it being done. Behavior only; see "What it deliberately does not teach."

**Built:** 2026-11-24, data prep only. No API calls made, no spend. The run (fine-tune + base-vs-tuned eval) happens only on Aaryn's explicit go.

## Contents

| File | Examples | Token estimate* |
|------|----------|-----------------|
| train.jsonl | 28 | ~17,200 |
| eval.jsonl (held out) | 10 | ~5,200 |

\*Estimate only: characters / 4, counted on the written JSONL files. Not a tokenizer count.

Format: OpenAI fine-tuning JSONL, chat messages (system / user / assistant). Every example uses one identical system prompt — the STORY-pass instruction, mirroring the production framing in the STORY script headers and `VOICE-FIRST-SCRIPTING.md` (production reference, private) ("the pass" rules) + `SEGMENT-FRAMEWORK.md`: natural story rhythm, breath units, delivery-only changes, facts/structure/title-weave untouched. The user message names the video and segment and gives the DRAFT passage; the assistant message is the accepted STORY passage.

## Pair counts and mix

- **Training: 28** — 23 full-segment rewrites (the STORY pass changed the text) + 5 preservation pairs (DRAFT and STORY identical; the correct edit was *no edit*).
- **Held-out eval: 10** — stratified by rule type: factual fix ×1, voice consistency ×1, breath units ×2, hook/voice fit ×1, voice/story rhythm ×1, refrain preservation ×2, hedge preservation ×2. No eval passage, and no passage from an eval segment, appears in training (checked programmatically at build time).
- Split ≈ 74/26 train/eval.

## Source for every pair

All script files live in the production deliverables folder (private — not included in this export). Every pair was extracted mechanically from the DRAFT and STORY files and verified verbatim — passage-level pairs were asserted as exact substrings of both files at build time. [CLIP] production annotations (present in DRAFT files, "NOT spoken") were stripped from inputs, matching how the STORY files present the narration.

### Training pairs

| # | Kind | Rule | Source pair (deliverables/) |
|---|------|------|------------------------------|
| 1 | segment | voice/rhythm rewrite | full-03-awakening-stones-script-DRAFT.md → full-03-awakening-stones-script-STORY.md (seg 1) |
| 2 | segment | voice/rhythm rewrite | full-03-awakening-stones-script-DRAFT.md → full-03-awakening-stones-script-STORY.md (seg 3) |
| 3 | segment | voice/rhythm rewrite | full-03-awakening-stones-script-DRAFT.md → full-03-awakening-stones-script-STORY.md (seg 4) |
| 4 | segment | voice/rhythm rewrite | full-03-awakening-stones-script-DRAFT.md → full-03-awakening-stones-script-STORY.md (seg 6) |
| 5 | segment | voice/rhythm rewrite | full-03-awakening-stones-script-DRAFT.md → full-03-awakening-stones-script-STORY.md (seg 7) |
| 6 | segment | voice/rhythm rewrite | full-03-awakening-stones-script-DRAFT.md → full-03-awakening-stones-script-STORY.md (seg 9) |
| 7 | segment | voice/rhythm rewrite | full-01-confluence-script-DRAFT.md → full-01-confluence-script-STORY.md (seg 1) |
| 8 | segment | voice/rhythm rewrite | full-01-confluence-script-DRAFT.md → full-01-confluence-script-STORY.md (seg 2) |
| 9 | segment | voice/rhythm rewrite | full-01-confluence-script-DRAFT.md → full-01-confluence-script-STORY.md (seg 3) |
| 10 | segment | voice/rhythm rewrite | full-01-confluence-script-DRAFT.md → full-01-confluence-script-STORY.md (seg 7) |
| 11 | segment | voice/rhythm rewrite | full-01-confluence-script-DRAFT.md → full-01-confluence-script-STORY.md (seg 9) |
| 12 | segment | voice/rhythm rewrite | full-02-achievement-economy-script-DRAFT.md → full-02-achievements-script-STORY.md (seg 2) |
| 13 | segment | voice/rhythm rewrite | full-02-achievement-economy-script-DRAFT.md → full-02-achievements-script-STORY.md (seg 3) |
| 14 | segment | voice/rhythm rewrite | full-02-achievement-economy-script-DRAFT.md → full-02-achievements-script-STORY.md (seg 4) |
| 15 | segment | voice/rhythm rewrite | full-02-achievement-economy-script-DRAFT.md → full-02-achievements-script-STORY.md (seg 6) |
| 16 | segment | voice/rhythm rewrite | full-02-achievement-economy-script-DRAFT.md → full-02-achievements-script-STORY.md (seg 9) |
| 17 | segment | voice/rhythm rewrite | full-04-hoarder-script-DRAFT.md → full-04-hoarder-script-STORY.md (seg 2) |
| 18 | segment | voice/rhythm rewrite | full-04-hoarder-script-DRAFT.md → full-04-hoarder-script-STORY.md (seg 4) |
| 19 | segment | voice/rhythm rewrite | full-04-hoarder-script-DRAFT.md → full-04-hoarder-script-STORY.md (seg 5) |
| 20 | segment | voice/rhythm rewrite | full-04-hoarder-script-DRAFT.md → full-04-hoarder-script-STORY.md (seg 6) |
| 21 | segment | voice/rhythm rewrite | full-04-hoarder-script-DRAFT.md → full-04-hoarder-script-STORY.md (seg 7) |
| 22 | segment | voice/rhythm rewrite | full-04-hoarder-script-DRAFT.md → full-04-hoarder-script-STORY.md (seg 8) |
| 23 | segment | voice/rhythm rewrite | full-04-hoarder-script-DRAFT.md → full-04-hoarder-script-STORY.md (seg 10) |
| 24 | segment | refrain preservation | full-05-party-build-script-DRAFT.md → full-05-party-build-script-STORY.md (seg 10) |
| 25 | segment | hedge preservation | gap-04-third-floor-gamble-script-DRAFT.md → gap-04-third-floor-gamble-script-STORY.md (seg 9) |
| 26 | segment | mechanism preservation | gap-02-jason-character-sheet-script-DRAFT.md → gap-02-jason-character-sheet-script-STORY.md (seg 5) |
| 27 | segment | preservation | gap-03-fame-stat-script-DRAFT.md → gap-03-fame-stat-script-STORY.md (seg 2) |
| 28 | segment | preservation | full-00-what-is-litrpg-script-DRAFT.md → full-00-what-is-litrpg-script-STORY.md (seg 3) |

### Held-out eval pairs

| # | Kind | Rule | Source pair (deliverables/) |
|---|------|------|------------------------------|
| 1 | passage | factual fix | full-03-awakening-stones-script-DRAFT.md → full-03-awakening-stones-script-STORY.md (seg 2) |
| 2 | passage | voice consistency | full-00-what-is-litrpg-script-DRAFT.md → full-00-what-is-litrpg-script-STORY.md (seg 1) |
| 3 | passage | breath units | full-04-hoarder-script-DRAFT.md → full-04-hoarder-script-STORY.md (seg 1) |
| 4 | passage | breath units | full-04-hoarder-script-DRAFT.md → full-04-hoarder-script-STORY.md (seg 3) |
| 5 | segment | hook / voice fit | full-02-achievement-economy-script-DRAFT.md → full-02-achievements-script-STORY.md (seg 1) |
| 6 | segment | voice / story rhythm | full-01-confluence-script-DRAFT.md → full-01-confluence-script-STORY.md (seg 5) |
| 7 | segment | refrain preservation | full-05-party-build-script-DRAFT.md → full-05-party-build-script-STORY.md (seg 1) |
| 8 | segment | refrain preservation | full-05-party-build-script-DRAFT.md → full-05-party-build-script-STORY.md (seg 6) |
| 9 | segment | hedge preservation | gap-04-third-floor-gamble-script-DRAFT.md → gap-04-third-floor-gamble-script-STORY.md (seg 5) |
| 10 | segment | hedge preservation | gap-04-third-floor-gamble-script-DRAFT.md → gap-04-third-floor-gamble-script-STORY.md (seg 8) |

Detail on each eval pair's pass criteria: `cases.md` (private companion file, held with the dataset).

## What behavior the set teaches

1. **Breath-unit splitting** — long nested sentences come back as short, one-idea sentences (splits at em dashes, asides promoted to sentences, minimal glue words).
2. **Story rhythm over song formula** — conversational voice, contractions, direct address; a thesis lands naturally in varied words, never chanted.
3. **Delivery-only discipline** — facts, claims, structure, segment order, and title-weave hook phrases do not change; word-count drift stays small.
4. **Preservation judgment** — intentional refrains ("The party is the build.") and hedged, attributed claims ("as far as the record shows") are carried *verbatim*; the pass must know when the right edit is no edit.
5. **Trip-wire defusing** — numbers spelled as spoken ("chapter ten," not "chapter 10"), no parentheticals in narration, no ALL-CAPS in spoken text.
6. **Factual self-check on numbers claims** — the one arithmetic pair (3 essences × 5 slots) shows a wrong count being caught and corrected, not merely rephrased.

## What it deliberately does not teach

- **No facts in the weights.** Every lore claim in these passages was grounded at production time by retrieval from the series vaults (FOUNDER > TEXT > WIKI > SECONDARY > VERIFY). The tuned model learns *how to phrase and when not to touch*, never *what is true*. At run time, facts still come from the source packet / retrieval — fine-tune for behavior, retrieve for facts.
- **No new-content generation.** All pairs are edits of existing drafts, not topic→script creation.
- **No Vanessa-era anything.** Rejected builds in the retired narrator's voice are excluded (see Case 11 below).

## Exclusions (from the 12 candidate eval cases, `evals-test-cases-draft-segment-writer.md`)

| Case | Disposition | Reason |
|------|-------------|--------|
| 01 V3 locked doors | **In eval** (passage pair) | Both sides verbatim in the script files. |
| 02 Doorway runtime claim | Excluded | Accepted-with-flag; DRAFT and STORY carry the line identically — there is no edit to learn. The flag concerns the finished video's 5:49 runtime vs the spoken "ten minutes," a production check, not a text behavior. |
| 03 Doorway "I'm Vanessa." | **In eval** (passage pair) | Both sides verbatim. |
| 04 Thesis-Chorus ×3 | Excluded as a standalone pair | The rejected side is a *described pattern* in the case file, never a quoted passage in any file. The doctrine sentence it quotes is an instruction, not narration. The V1 DRAFT→STORY segment rewrites in training are its closest verbatim embodiment. |
| 05 V4 Seg 1 split | **In eval** (passage pair) | Both sides verbatim. |
| 06 V4 Seg 3 split | **In eval** (passage pair) | Both sides verbatim. |
| 07 V5 refrain | **In eval** (segments 1 & 6) | Accepted text verbatim; no rejected side exists by design (contrast case). |
| 08 Gap-04 hedges | **In eval** (segments 5 & 8) | Same — preservation case, both "sides" are the accepted text. |
| 09 Gap-02 mechanism | **In training** (segment 5, preservation) | Mechanism verified correct and carried unchanged; used as a preservation example rather than held out. |
| 10 V2 hook | **In eval** (segment 1) | DRAFT and STORY both on file. |
| 11 Short-01 Vanessa build | Excluded | A voice/media rejection, not a text edit: the accepted History rebuild exists as an audio master, with no accepted script text on file to pair against the rejected draft. |
| 12 V1 §10 Five Rules card | Excluded | The drift is between narration and a *slide card* (visual), not between two text passages. No text pair exists. |

**Other material held back (not exclusions of cases):** 50 of the 55 identical DRAFT=STORY segment pairs were not used — a dataset dominated by copy-through pairs would teach passivity; 5 representative preservation pairs carry that signal. The full segments containing eval passages (V3 Seg 2, V4 Segs 1 & 3, Doorway Seg 1) were kept out of training so no held-out answer leaks. Nine further rewritten segments (V1 Segs 4/6/8, V2 Segs 5/7/8/10, V3 Segs 8/10) are a reserve pool for a v2 expansion.

## Base-vs-tuned eval protocol (for the run — not yet executed)

1. Take the 10 prompts from `eval.jsonl` exactly as written (same system prompt, same user messages).
2. Run each against **base `gpt-4o-mini`** and against the **fine-tuned model**, temperature 0, one completion each.
3. Score each output against the plain-language pass criteria in `cases.md` (per case: pass / fail + the criterion that decided it). Verbatim-line criteria (refrains, hedges, "twelve locked doors") are checked as exact strings.
4. Record results in the table below. The claim the run may make is limited to what this table shows: behavior on these 10 held-out production cases, nothing broader.

| Case | Rule | Base gpt-4o-mini | Tuned | Deciding criterion |
|------|------|------------------|-------|--------------------|
| 1 | factual fix | — | — | |
| 2 | voice consistency | — | — | |
| 3 | breath units | — | — | |
| 4 | breath units | — | — | |
| 5 | hook / voice fit | — | — | |
| 6 | voice / story rhythm | — | — | |
| 7 | refrain preservation | — | — | |
| 8 | refrain preservation | — | — | |
| 9 | hedge preservation | — | — | |
| 10 | hedge preservation | — | — | |

*Results table intentionally blank — filled only by the actual run, on Aaryn's go.*
