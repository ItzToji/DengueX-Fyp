"""
chatbot_engine.py (embeddings + FAISS version)

Key functions:
 - init_index(index_dir)         # call once at startup
 - get_reply(text)               # main call: returns reply dict
 - add_kb_item(item)             # optional: add a new KB item to index (in-memory). Persist manually.
 - rebuild_index(...)            # helper to rebuild from KB file

Requirements:
 - sentence-transformers
 - faiss-cpu
 - numpy
"""
import os, json, numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# Adjustable params
INDEX_DIR = os.path.join(os.path.dirname(__file__), "index")  # expected index path
MODEL = None
FAISS_INDEX = None
META = []            # list of KB metadata (json objects) aligned with embeddings / index order
EMBEDDINGS = None    # numpy array
SIMILARITY_THRESHOLD = 0.45   # cosine similarity threshold (works with normalized embeddings & IP metric)
TOP_K = 5

# Basic intent/urgency keywords (keeps earlier functionality)
URGENT_KEYWORDS = set(["severe abdominal pain","persistent vomiting","bleeding","difficulty breathing","faint","cold/clammy","vomit blood","black stool","lethargy","difficulty waking"])
DENGUE_KEYWORDS = set(["dengue","mosquito","aedes","fever","platelet","rash","ns1","serology","dengue fever","dengue virus"])

def init_index(index_dir=INDEX_DIR):
    global MODEL, FAISS_INDEX, META, EMBEDDINGS
    # load model name
    model_file = os.path.join(index_dir, "model_name.txt")
    if not os.path.exists(model_file):
        raise FileNotFoundError("Model file not found. Run build_embeddings.py first.")
    model_name = open(model_file,"r",encoding="utf-8").read().strip()
    MODEL = SentenceTransformer(model_name)

    emb_path = os.path.join(index_dir, "embeddings.npy")
    meta_path = os.path.join(index_dir, "meta.jsonl")
    index_path = os.path.join(index_dir, "index.faiss")

    if not os.path.exists(emb_path) or not os.path.exists(meta_path) or not os.path.exists(index_path):
        raise FileNotFoundError("Missing index files. Build them with build_embeddings.py")

    EMBEDDINGS = np.load(emb_path)
    # load meta
    META = []
    with open(meta_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                META.append(json.loads(line))

    # load FAISS index
    FAISS_INDEX = faiss.read_index(index_path)

    # ensure embeddings normalized if using inner-product search
    # NB: build_embeddings wrote normalized embeddings; but double-check
    def normalize_rows(x):
        norms = np.linalg.norm(x, axis=1, keepdims=True)
        norms[norms==0] = 1.0
        return x / norms
    EMBEDDINGS[:] = normalize_rows(EMBEDDINGS)

    print(f"Index loaded: {len(META)} items, model: {model_name}")

def _embed_text(text):
    global MODEL
    if MODEL is None:
        raise RuntimeError("Model not initialized. Call init_index() first.")
    emb = MODEL.encode([text], convert_to_numpy=True, normalize_embeddings=True)
    return emb[0]

def predict_intent(text):
    # simple keyword fallback; we will also rely on retrieval for final decision
    txt = text.lower()
    score = sum(1 for k in DENGUE_KEYWORDS if k in txt)
    if score >= 1:
        return 'dengue'
    if 'fever' in txt and 'mosquito' in txt:
        return 'dengue'
    return 'not-dengue'

def is_urgent(text):
    txt = text.lower()
    matches = []
    for kw in URGENT_KEYWORDS:
        if kw in txt:
            matches.append(kw)
    return (len(matches) > 0, matches)

def find_top_k(text, top_k=TOP_K):
    emb = _embed_text(text).astype('float32').reshape(1,-1)
    # FAISS inner product expects normalized embeddings for cosine similarity equivalence
    D, I = FAISS_INDEX.search(emb, top_k)  # returns distances (scores) and indices
    # D are inner product scores (since embeddings normalized)
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0 or idx >= len(META):
            continue
        meta = META[idx].copy()
        meta['score'] = float(score)
        results.append((meta, float(score)))
    return results

def get_reply(text):
    # urgent check first (quick)
    urgent_flag, urgent_matches = is_urgent(text)
    if urgent_flag:
        return {
            'reply': 'This message contains warning signs. Seek immediate medical care or go to the nearest emergency department. If you are in immediate danger call local emergency services.',
            'kb_id': None,
            'sources': ['Emergency guidance - WHO'],
            'urgency': 'urgent',
            'confidence': 1.0,
            'matched_warning_signs': urgent_matches
        }

    intent = predict_intent(text)

    # retrieval
    results = find_top_k(text, top_k=TOP_K)
    if not results:
        # fallback: TF-IDF or uncertain reply
        return {
            'reply': "I'm not sure I understand. Can you rephrase? I can only answer dengue-related questions.",
            'kb_id': None,
            'sources': [],
            'urgency': 'non-urgent',
            'confidence': 0.0,
            'matched_warning_signs': []
        }

    best_meta, best_score = results[0]

    # if best score below threshold treat as unknown / ask for rephrase
    if best_score < SIMILARITY_THRESHOLD:
        # If the best matched KB is an out_of_scope rejection entry, prefer it
        # but generally we'll decline
        # check if any returned candidate was an explicit out_of_scope match
        for m,s in results:
            if 'out_of_scope' in m.get('tags',[]):
                return {
                    'reply': m.get('canonical_answer'),
                    'kb_id': m.get('id'),
                    'sources': m.get('sources', []),
                    'urgency': m.get('urgency','non-urgent'),
                    'confidence': float(s),
                    'matched_warning_signs': []
                }
        return {
            'reply': "I don't have a confident answer for that. Please rephrase, ask a different dengue question, or consult a health professional.",
            'kb_id': None,
            'sources': [],
            'urgency': 'non-urgent',
            'confidence': float(best_score),
            'matched_warning_signs': []
        }

    # If the returned entry is an out_of_scope entry, return its canonical answer
    if 'out_of_scope' in best_meta.get('tags', []):
        return {
            'reply': best_meta.get('canonical_answer'),
            'kb_id': best_meta.get('id'),
            'sources': best_meta.get('sources', []),
            'urgency': best_meta.get('urgency','non-urgent'),
            'confidence': float(best_score),
            'matched_warning_signs': []
        }

    # otherwise return canonical answer with source and meta
    reply = best_meta.get('canonical_answer','')
    sources = best_meta.get('sources', [])
    return {
        'reply': reply + ("\n\nSource: " + ", ".join(sources) if sources else ""),
        'kb_id': best_meta.get('id'),
        'sources': sources,
        'urgency': best_meta.get('urgency','non-urgent'),
        'confidence': float(best_score),
        'matched_warning_signs': []
    }

# Optional: add_kb_item for live updates (in-memory only)
def add_kb_item(item, embedding_text=None):
    """
    Add a KB item (dict) to in-memory META and FAISS index.
    item must contain keys: id, title, question_variants, canonical_answer, tags, sources, urgency
    embedding_text: optional string used for embedding; otherwise uses title + variants
    """
    global META, EMBEDDINGS, FAISS_INDEX
    if EMBEDDINGS is None:
        raise RuntimeError("Index not initialized or embeddings not loaded")
    if embedding_text is None:
        variants = item.get("question_variants", []) or []
        rep = item.get("title","")
        if variants:
            rep = rep + " || " + " || ".join(variants[:3])
    else:
        rep = embedding_text
    emb = _embed_text(rep).astype('float32')
    # append embedding and meta
    EMBEDDINGS = np.vstack([EMBEDDINGS, emb[None,:]])
    META.append(item)
    # add vector to FAISS index (must be same type)
    FAISS_INDEX.add(emb[None,:])
    return True

# Optional: persist changes - not implemented here. For production, re-run build_embeddings.py on the updated KB file.

# Quick initialization if file run as script
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--index-dir", default=INDEX_DIR)
    parser.add_argument("--threshold", type=float, default=SIMILARITY_THRESHOLD)
    args = parser.parse_args()
    SIMILARITY_THRESHOLD = args.threshold
    init_index(args.index_dir)
    print("Ready. Use get_reply(text) to query.")
