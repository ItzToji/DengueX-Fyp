"""
build_embeddings.py
Builds sentence-transformer embeddings for each KB item and creates a FAISS index.

Usage (from project root):
    python feature1_chatbot/scripts/build_embeddings.py \
        --kb feature1_chatbot/dengue_kb_seed_1500.jsonl \
        --out-dir feature1_chatbot/index/

Outputs:
 - index.faiss          : FAISS index (flat L2 index or IVFFlat if you choose)
 - embeddings.npy       : numpy array of embeddings (num_entries x dim)
 - meta.jsonl           : metadata lines matching embeddings order (same format as KB entries)
 - model_name.txt       : name of the model used
"""
import os, argparse, json, pathlib, numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from tqdm import tqdm

def load_kb(kb_path):
    items = []
    with open(kb_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    return items

def build_embeddings(items, model_name="all-MiniLM-L6-v2", text_extractor=None):
    model = SentenceTransformer(model_name)
    texts = []
    for it in items:
        # choose representative text for retrieval: join title + variants
        variants = it.get("question_variants", []) or []
        rep = it.get("title","")
        if variants:
            rep = rep + " || " + " || ".join(variants[:3])
        texts.append(rep)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings, model_name

def build_faiss_index(embeddings, index_path, use_ivf=False, nlist=100):
    d = embeddings.shape[1]
    if use_ivf:
        quantizer = faiss.IndexFlatIP(d)
        index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_INNER_PRODUCT)
        index.train(embeddings)
        index.add(embeddings)
    else:
        # flat index, exact search (good for up to ~100k)
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
    faiss.write_index(index, index_path)
    return index

def save_meta(items, meta_path):
    with open(meta_path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kb", required=True, help="path to KB jsonl")
    parser.add_argument("--out-dir", required=True, help="output directory for index/embeddings")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="sentence-transformer model")
    parser.add_argument("--use-ivf", action="store_true", help="use IVF index (scales to large datasets)")
    parser.add_argument("--nlist", type=int, default=100, help="nlist for IVFFlat (if used)")
    args = parser.parse_args()

    kb_path = args.kb
    out_dir = args.out_dir
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)

    items = load_kb(kb_path)
    print(f"Loaded {len(items)} KB items from {kb_path}")

    embeddings, model_name = build_embeddings(items, model_name=args.model)
    emb_path = os.path.join(out_dir, "embeddings.npy")
    np.save(emb_path, embeddings)
    print("Saved embeddings to", emb_path)

    index_path = os.path.join(out_dir, "index.faiss")
    build_faiss_index(embeddings, index_path, use_ivf=args.use_ivf, nlist=args.nlist)
    print("Wrote FAISS index to", index_path)

    meta_path = os.path.join(out_dir, "meta.jsonl")
    save_meta(items, meta_path)
    print("Saved metadata to", meta_path)

    with open(os.path.join(out_dir,"model_name.txt"), "w", encoding="utf-8") as f:
        f.write(args.model + "\n")

    print("Build complete.")

if __name__ == "__main__":
    main()
