#!/usr/bin/env python3
# feature1_chatbot/scripts/build_embeddings_variants.py
import os, json, argparse
import numpy as np
from sentence_transformers import SentenceTransformer

try:
    import faiss
except Exception:
    faiss = None


def iter_variants(kb_path):
    """
    Yield (vector_id, kb_id, title, canonical_answer, variant_text)
    for every question variant in KB.
    """
    vid = 0
    with open(kb_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            it = json.loads(line)
            kb_id = it.get("id") or it.get("kb_id") or it.get("uid")
            title = it.get("title", "")
            canonical = it.get("canonical_answer", "")
            variants = it.get("question_variants") or []

            if not variants:
                variants = [title]  # fallback for missing variants

            for v in variants:
                yield vid, kb_id, title, canonical, v
                vid += 1


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--kb", required=True)
    p.add_argument("--index-dir", default="feature1_chatbot/index")
    p.add_argument("--model", default="all-MiniLM-L6-v2")
    p.add_argument("--batch", type=int, default=128)
    args = p.parse_args()

    kb = args.kb
    index_dir = args.index_dir
    os.makedirs(index_dir, exist_ok=True)

    print("Loading model:", args.model)
    model = SentenceTransformer(args.model)

    # Collect vector variants
    print("Collecting variants...")
    variants = []
    for vid, kb_id, title, canonical, vtext in iter_variants(kb):
        variants.append((vid, kb_id, title, canonical, vtext))

    N = len(variants)
    if N == 0:
        raise RuntimeError("No variants found in KB file.")
    print(f"Found {N} variant vectors")

    # Prepare embedding matrix
    D = model.get_sentence_embedding_dimension()
    embeddings = np.zeros((N, D), dtype="float32")

    # Encode in batches
    b = args.batch
    for i in range(0, N, b):
        chunk = variants[i:i+b]
        texts = [c[4] for c in chunk]

        embs = model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True,
            normalize_embeddings=True
        )

        embeddings[i:i+len(chunk), :] = embs.astype("float32")
        print(f"Encoded {i+len(chunk)}/{N}")

    # Normalize embeddings
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    embeddings = embeddings / norms

    # Save embeddings
    emb_path = os.path.join(index_dir, "embeddings.npy")
    np.save(emb_path, embeddings)
    print("Saved embeddings ->", emb_path)

    # Save metadata
    meta_path = os.path.join(index_dir, "meta.jsonl")
    with open(meta_path, "w", encoding="utf-8") as out:
        for vid, kb_id, title, canonical, vtext in variants:
            meta = {
                "vector_id": int(vid),
                "kb_id": str(kb_id),
                "title": title,
                "canonical_answer": canonical,
                "variant_text": vtext
            }
            out.write(json.dumps(meta, ensure_ascii=False) + "\n")
    print("Saved meta ->", meta_path)

    # Save the model name
    open(os.path.join(index_dir, "model_name.txt"), "w", encoding="utf-8").write(args.model + "\n")

    # Build FAISS index if available
    if faiss is None:
        print("FAISS not installed. Skipping FAISS index build.")
        return

    print("Building FAISS index...")
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)
    index = faiss.IndexIDMap(index)

    ids = np.arange(0, N).astype("int64")
    index.add_with_ids(embeddings, ids)

    idx_path = os.path.join(index_dir, "index.faiss")
    faiss.write_index(index, idx_path)

    print("Saved FAISS Index ->", idx_path)
    print("Done.")


if __name__ == "__main__":
    main()
