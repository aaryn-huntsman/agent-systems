#!/usr/bin/env python3
"""Vector-RAG demo pipeline: embed the chunked manuals, run the eval.

Two retrieval methods over the same 8 preset questions:
  (a) VECTOR: cosine similarity over L2-normalized embeddings.
      Model: google/embeddinggemma-2 (768 dims, Matryoshka-truncated to
      256, renormalized). Fallback: all-MiniLM-L6-v2 (384 dims) if the
      Gemma model cannot be loaded on this VM — recorded in META.
  (b) STRUCTURED: deterministic keyword routing in the spirit of
      retrieve.py — score every manual SECTION by question-word overlap
      (heading matches weigh 3x), route to the best section, rank its
      chunks by the same overlap. No embeddings involved.

Gold chunks were labeled by hand against the manual text (each gold
chunk was read and confirmed to contain the answer). Score: hit@5 =
at least one gold chunk in the returned top 5.

Outputs: results.json (full-precision audit) and vector-data.js
(rounded vectors, shippable — the live demo site serves this file).
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
OUT_JS = HERE / "vector-data.js"

QUESTIONS = [
    {"q": "What should the card-price agent do when it finds no sales records for a card?",
     "gold": ["operation-manual-002"]},
    {"q": "How is the percentage change for a price trend calculated?",
     "gold": ["operation-manual-003"]},
    {"q": "How does the series expert answer questions about a series without spoiling later books?",
     "gold": ["chewybits-series-expert-003"]},
    {"q": "Can a wiki or other outside source ever count as verified against the books themselves?",
     "gold": ["chewybits-series-expert-012", "chewybits-series-expert-014"]},
    {"q": "What does registering a business for A2P 10DLC texting involve?",
     "gold": ["rbm-service-delivery-002"]},
    {"q": "When must a review reply be stopped and handed to a human instead of posted?",
     "gold": ["rbm-service-delivery-012"]},
    {"q": "What makes a good opening hook for a short video?",
     "gold": ["chewybits-scriptwriter-011"]},
    {"q": "How are the Stripe payment links checked, and what result means the payment stage is healthy?",
     "gold": ["rbm-funnel-operator-003"]},
]

STOPWORDS = set("""a an the and or of to in on for with without is are was were be been do does did
should must can could what when how why which who it its if no not any all per into from by at as
that this these those than then so such ever out about against between through during before after
up down over under again once here there where other only also""".split())


def content_words(text):
    toks = re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in toks if len(t) >= 2 and t not in STOPWORDS}


def structured_top5(question, chunks):
    """Keyword routing: best section wins, its chunks ranked by overlap."""
    qw = content_words(question)
    sections = {}
    order = []
    for i, c in enumerate(chunks):
        key = (c["source"], c["heading"])
        if key not in sections:
            sections[key] = []
            order.append(key)
        sections[key].append(i)
    best_key, best_score, best_ranked = None, -1, []
    for key in order:
        idxs = sections[key]
        heading_hits = len(qw & content_words(key[1]))
        body_words = set()
        for i in idxs:
            body_words |= content_words(chunks[i]["text"])
        score = 3 * heading_hits + len(qw & body_words)
        if score > best_score:
            ranked = sorted(idxs, key=lambda i: (-len(qw & content_words(chunks[i]["text"])), i))
            best_key, best_score, best_ranked = key, score, ranked
    return [chunks[i]["id"] for i in best_ranked[:5]], {"section": list(best_key), "score": best_score}


def l2norm(mat):
    n = np.linalg.norm(mat, axis=1, keepdims=True)
    return mat / np.maximum(n, 1e-12)


def load_embeddings(chunks, questions):
    """Return (chunk_vecs, query_vecs, meta). Tries EmbeddingGemma-2 first."""
    from sentence_transformers import SentenceTransformer

    texts = [c["text"] for c in chunks]
    qs = [q["q"] for q in questions]
    try:
        model = SentenceTransformer("google/embeddinggemma-2")
        prompts = getattr(model, "prompts", {}) or {}
        kw = {}
        if "query" in prompts and "document" in prompts:
            kw = {"prompt_name_docs": "document", "prompt_name_q": "query"}
        if kw:
            doc = np.asarray(model.encode(texts, prompt_name="document"), dtype=np.float64)
            qry = np.asarray(model.encode(qs, prompt_name="query"), dtype=np.float64)
            prompt_note = "Model's built-in 'document'/'query' task prompts applied."
        else:
            doc = np.asarray(model.encode(texts), dtype=np.float64)
            qry = np.asarray(model.encode(qs), dtype=np.float64)
            prompt_note = "No task prompts applied (model config exposes none)."
        full_dims = int(doc.shape[1])
        doc = l2norm(doc[:, :256])
        qry = l2norm(qry[:, :256])
        meta = {
            "model": "EmbeddingGemma 2 (google/embeddinggemma-2)",
            "model_id": "google/embeddinggemma-2",
            "full_dims": full_dims,
            "dims": 256,
            "truncation": f"Matryoshka truncation: first 256 of {full_dims} dims kept, then L2-renormalized.",
            "prompts": prompt_note,
            "fallback": None,
        }
        return doc, qry, meta
    except Exception as exc:  # noqa: BLE001 - fallback is the documented path
        print(f"EmbeddingGemma-2 failed ({type(exc).__name__}: {exc}); falling back to MiniLM", file=sys.stderr)
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        doc = l2norm(np.asarray(model.encode(texts), dtype=np.float64))
        qry = l2norm(np.asarray(model.encode(qs), dtype=np.float64))
        meta = {
            "model": "all-MiniLM-L6-v2 (sentence-transformers)",
            "model_id": "sentence-transformers/all-MiniLM-L6-v2",
            "full_dims": int(doc.shape[1]),
            "dims": int(doc.shape[1]),
            "truncation": "None — full-width vectors shipped.",
            "prompts": "No task prompts (MiniLM has none).",
            "fallback": f"google/embeddinggemma-2 could not be loaded on this VM ({type(exc).__name__}).",
        }
        return doc, qry, meta


def rounded(vec):
    return [0.0 if round(float(x), 4) == 0 else round(float(x), 4) for x in vec]


def main():
    chunks = json.loads((HERE / "chunks.json").read_text(encoding="utf-8"))
    doc_vecs, query_vecs, meta = load_embeddings(chunks, QUESTIONS)

    results = {"meta": meta, "questions": []}
    v_hits = s_hits = 0
    for qi, q in enumerate(QUESTIONS):
        sims = doc_vecs @ query_vecs[qi]
        ranked = sorted(range(len(chunks)), key=lambda i: (-sims[i], i))[:5]
        v_top = [{"id": chunks[i]["id"], "score": float(sims[i])} for i in ranked]
        s_top, s_info = structured_top5(q["q"], chunks)
        v_hit = any(t["id"] in q["gold"] for t in v_top)
        s_hit = any(t in q["gold"] for t in s_top)
        v_hits += v_hit
        s_hits += s_hit
        results["questions"].append({
            "q": q["q"], "gold": q["gold"],
            "vector_top5": v_top, "vector_hit": v_hit,
            "structured_top5": s_top, "structured_hit": s_hit,
            "structured_route": s_info,
        })
        print(f"Q{qi+1} vector {'HIT ' if v_hit else 'MISS'} | structured {'HIT ' if s_hit else 'MISS'}"
              f" | gold {q['gold']} | vector#1 {v_top[0]['id']} ({v_top[0]['score']:.3f})"
              f" | routed {s_info['section'][1][:40]}")
    results["vector_hit_at_5"] = f"{v_hits}/{len(QUESTIONS)}"
    results["structured_hit_at_5"] = f"{s_hits}/{len(QUESTIONS)}"
    print(f"\nVector hit@5: {v_hits}/{len(QUESTIONS)} | Structured hit@5: {s_hits}/{len(QUESTIONS)}")
    print(f"Model: {meta['model']} | dims shipped: {meta['dims']} | chunks: {len(chunks)}")
    (HERE / "results.json").write_text(json.dumps(results, indent=1), encoding="utf-8")

    sources = []
    for c in chunks:
        if c["source"] not in sources:
            sources.append(c["source"])
    data = {
        "META": {
            **meta,
            "chunk_count": len(chunks),
            "corpus_sources": sources,
            "vector_hit_at_5": results["vector_hit_at_5"],
            "structured_hit_at_5": results["structured_hit_at_5"],
            "method_notes": [
                "Corpus: Aaryn's own operations manuals only — no lore database, no book text.",
                "Chunks are manual sections (split at ~380 estimated tokens, tiny fragments merged).",
                "Vectors were computed locally and are shipped rounded to 4 decimals; your browser re-ranks by cosine similarity live.",
                "Questions are presets because the embedding model itself does not run in a browser.",
                "Structured baseline: deterministic keyword routing — section scored by question-word overlap (heading x3), best section's chunks returned.",
                "hit@5: at least one hand-labeled gold chunk appears in the top 5. Gold labels were verified by reading each chunk.",
                "Small-corpus demonstration (under 100 chunks), not a benchmark.",
            ],
        },
        "chunks": [{"id": c["id"], "source": c["source"], "heading": c["heading"],
                    "heading_path": c["heading_path"], "text": c["text"]} for c in chunks],
        "vectors": [rounded(v) for v in doc_vecs],
        "questions": [{"q": q["q"], "gold": q["gold"], "vector": rounded(query_vecs[i]),
                       "structured_top5": results["questions"][i]["structured_top5"],
                       "python_vector_top5": [t["id"] for t in results["questions"][i]["vector_top5"]]}
                      for i, q in enumerate(QUESTIONS)],
    }
    OUT_JS.parent.mkdir(parents=True, exist_ok=True)
    OUT_JS.write_text("const VX_DATA = " + json.dumps(data) + ";\n", encoding="utf-8")
    print(f"wrote {OUT_JS} ({OUT_JS.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
