#!/usr/bin/env python3
"""Find-It demo pipeline: embed the Blue Ridge Outfitters catalog, score it.

Semantic product search over a fictional demo shop (dataset.py):
each product and buying-guide passage is one chunk. Chunks and the
8 preset shopper questions are embedded with the same settings as
../vector-rag-demo/pipeline.py — google/embeddinggemma-2, built-in
document/query task prompts, 768 dims Matryoshka-truncated to 256,
L2-renormalized — with the same all-MiniLM-L6-v2 fallback, recorded
in META either way.

The embedded chunk text is "Name. Description" — the name is part of
what a real store's search index would see. Question text is embedded
as the shopper typed it.

Gold chunks were hand-labeled (see dataset.py rationales). Score:
hit@5 = at least one gold chunk in the vector top 5.

Outputs: results.json (full-precision audit) and findit-data.js
(rounded vectors — the live demo site serves this file).
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
OUT_JS = HERE / "findit-data.js"


def l2norm(mat):
    n = np.linalg.norm(mat, axis=1, keepdims=True)
    return mat / np.maximum(n, 1e-12)


def load_embeddings(chunks, questions):
    """Return (chunk_vecs, query_vecs, meta). Same settings as the vector demo."""
    from sentence_transformers import SentenceTransformer

    texts = [f"{c['name']}. {c['text']}" for c in chunks]
    qs = [q["q"] for q in questions]
    try:
        model = SentenceTransformer("google/embeddinggemma-2")
        prompts = getattr(model, "prompts", {}) or {}
        if "query" in prompts and "document" in prompts:
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
    questions = json.loads((HERE / "questions.json").read_text(encoding="utf-8"))
    doc_vecs, query_vecs, meta = load_embeddings(chunks, questions)

    results = {"meta": meta, "questions": []}
    hits = 0
    for qi, q in enumerate(questions):
        sims = doc_vecs @ query_vecs[qi]
        ranked = sorted(range(len(chunks)), key=lambda i: (-sims[i], i))[:5]
        top = [{"id": chunks[i]["id"], "score": float(sims[i])} for i in ranked]
        hit = any(t["id"] in q["gold"] for t in top)
        hits += hit
        results["questions"].append({
            "q": q["q"], "gold": q["gold"], "top5": top, "hit": hit,
        })
        gold_ranks = [next((r + 1 for r, t in enumerate(top) if t["id"] == g), None)
                      for g in q["gold"]]
        print(f"Q{qi+1} {'HIT ' if hit else 'MISS'} | gold ranks {gold_ranks} "
              f"| #1 {top[0]['id']} ({top[0]['score']:.3f}) | {q['q'][:60]}")
    results["hit_at_5"] = f"{hits}/{len(questions)}"
    print(f"\nVector hit@5: {hits}/{len(questions)}")
    print(f"Model: {meta['model']} | dims shipped: {meta['dims']} | chunks: {len(chunks)}")
    (HERE / "results.json").write_text(json.dumps(results, indent=1), encoding="utf-8")

    n_products = sum(1 for c in chunks if c["kind"] == "product")
    n_guides = sum(1 for c in chunks if c["kind"] == "guide")
    data = {
        "META": {
            **meta,
            "shop": "Blue Ridge Outfitters — a fictional demo shop. Every product, price, and guide is invented for this demonstration.",
            "chunk_count": len(chunks),
            "product_count": n_products,
            "guide_count": n_guides,
            "hit_at_5": results["hit_at_5"],
            "method_notes": [
                "Catalog: a fictional demo shop (Blue Ridge Outfitters) — 36 invented products and 4 buying guides, each one chunk.",
                "Embedded text is the product name plus its description — what a real store's search index would see.",
                "Vectors were computed locally and are shipped rounded to 4 decimals; your browser re-ranks by cosine similarity live.",
                "Questions are presets because the embedding model itself does not run in a browser.",
                "hit@5: at least one hand-labeled gold chunk appears in the top 5. Gold labels were chosen as the answer a knowledgeable shop assistant would give, with the reason recorded per chunk.",
                "Small-catalog demonstration (40 chunks), not a benchmark.",
            ],
        },
        "chunks": [{"id": c["id"], "kind": c["kind"], "name": c["name"],
                    "category": c["category"], "price": c["price"], "text": c["text"]}
                   for c in chunks],
        "vectors": [rounded(v) for v in doc_vecs],
        "questions": [{"q": q["q"], "gold": list(q["gold"].keys()), "rationale": q["gold"],
                       "vector": rounded(query_vecs[i]),
                       "python_top5": [t["id"] for t in results["questions"][i]["top5"]]}
                      for i, q in enumerate(questions)],
    }
    OUT_JS.parent.mkdir(parents=True, exist_ok=True)
    OUT_JS.write_text("const FI_DATA = " + json.dumps(data) + ";\n", encoding="utf-8")
    print(f"wrote {OUT_JS} ({OUT_JS.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
