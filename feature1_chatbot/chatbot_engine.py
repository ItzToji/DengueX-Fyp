# feature1_chatbot/chatbot_engine.py
"""
Chatbot engine updated for one-vector-per-variant index.
- load_kb(kb_path): legacy loader (builds representative embeddings for tests)
- init_index(index_dir): loads index built by build_embeddings_variants.py
- get_reply(text): retrieves top-k vectors, aggregates scores by kb_id, returns canonical_answer for best kb_id
"""
import os, json, numpy as np

# sentence-transformers
from sentence_transformers import SentenceTransformer

# optional faiss
try:
    import faiss
    HAS_FAISS = True
except Exception:
    faiss = None
    HAS_FAISS = False

INDEX_DIR = os.path.join(os.path.dirname(__file__), "index")
MODEL = None

# In-memory fallback structures (used by load_kb and by retrieval fallback)
EMBEDDINGS = None
META = []          # when load_kb used: list of kb items; when index loaded: list of vector meta entries
FAISS_INDEX = None

SIMILARITY_THRESHOLD = 0.45
TOP_K = 5

# --- helpers ---
def _ensure_model(model_name="all-MiniLM-L6-v2"):
    global MODEL
    if MODEL is None:
        MODEL = SentenceTransformer(model_name)
    return MODEL

def _rep_text_for_item(it):
    title = it.get("title","")
    variants = it.get("question_variants",[]) or []
    rep = title
    if variants:
        rep += " || " + " || ".join(variants[:3])
    return rep

def _normalize_rows(x):
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms[norms==0] = 1.0
    return x / norms

# --- legacy loader for tests (keeps previous behavior) ---
def load_kb(kb_path, model_name="all-MiniLM-L6-v2"):
    """
    Load KB (JSONL of kb items) and build representative in-memory embeddings.
    Returns count of kb items loaded.
    """
    global META, EMBEDDINGS, MODEL, FAISS_INDEX
    MODEL = _ensure_model(model_name)

    items = []
    with open(kb_path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try:
                it = json.loads(line)
            except Exception:
                continue
            items.append(it)
    META = items
    rep_texts = [_rep_text_for_item(it) for it in META]
    if rep_texts:
        embs = MODEL.encode(rep_texts, convert_to_numpy=True, show_progress_bar=False, normalize_embeddings=True)
        EMBEDDINGS = embs.astype("float32")
    else:
        EMBEDDINGS = np.zeros((0, MODEL.get_sentence_embedding_dimension()), dtype="float32")
    FAISS_INDEX = None
    return len(META)

# --- init index built with build_embeddings_variants.py ---
def init_index(index_dir=INDEX_DIR):
    """
    Load index files from index_dir created by build_embeddings_variants.py
    """
    global MODEL, EMBEDDINGS, META, FAISS_INDEX
    model_file = os.path.join(index_dir, "model_name.txt")
    emb_path = os.path.join(index_dir, "embeddings.npy")
    meta_path = os.path.join(index_dir, "meta.jsonl")
    idx_path = os.path.join(index_dir, "index.faiss")

    if not os.path.exists(model_file) or not os.path.exists(emb_path) or not os.path.exists(meta_path):
        raise FileNotFoundError("Index files missing. Run build_embeddings_variants.py first.")

    model_name = open(model_file,"r",encoding="utf-8").read().strip()
    MODEL = _ensure_model(model_name)

    EMBEDDINGS = np.load(emb_path).astype("float32")
    # load vector-level meta (one entry per vector)
    META = []
    with open(meta_path,"r",encoding="utf-8") as f:
        for line in f:
            if line.strip():
                META.append(json.loads(line))

    if os.path.exists(idx_path):
        if not HAS_FAISS:
            raise ImportError("FAISS index file exists but faiss not installed in this environment.")
        FAISS_INDEX = faiss.read_index(idx_path)
    else:
        FAISS_INDEX = None

    # ensure normalized
    EMBEDDINGS[:] = _normalize_rows(EMBEDDINGS)
    return len(META)

# --- embedding helper ---
def _embed_text(text):
    global MODEL
    if MODEL is None:
        MODEL = _ensure_model()
    emb = MODEL.encode([text], convert_to_numpy=True, normalize_embeddings=True)
    return emb[0].astype("float32")

# --- retrieval helpers ---
def _retrieve_with_faiss(text, top_k=TOP_K):
    emb = _embed_text(text).reshape(1,-1)
    D, I = FAISS_INDEX.search(emb, top_k*3)  # search more vectors to allow aggregation
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0 or idx >= len(META):
            continue
        m = META[idx].copy()
        m['vector_score'] = float(score)
        m['vector_index'] = int(idx)
        results.append(m)
    return results

def _retrieve_in_memory(text, top_k=TOP_K):
    if EMBEDDINGS is None or EMBEDDINGS.shape[0] == 0:
        return []
    q_emb = _embed_text(text).astype("float32")
    scores = np.dot(EMBEDDINGS, q_emb)
    idxs = np.argsort(-scores)[:top_k*3]
    results = []
    for idx in idxs:
        if idx < 0 or idx >= len(META):
            continue
        m = META[idx].copy()
        m['vector_score'] = float(scores[idx])
        m['vector_index'] = int(idx)
        results.append(m)
    return results

# --- aggregation: group vectors by kb_id and aggregate scores ---
def _aggregate_by_kb(results):
    # results: list of vector-level meta with vector_score and kb_id
    agg = {}
    for r in results:
        kb = str(r.get("kb_id"))
        score = float(r.get("vector_score", 0.0))
        # aggregate by sum and track best vector meta
        if kb not in agg:
            agg[kb] = {"score_sum": score, "max_score": score, "example": r}
        else:
            agg[kb]["score_sum"] += score
            if score > agg[kb]["max_score"]:
                agg[kb]["max_score"] = score
                agg[kb]["example"] = r
    # convert to list sorted by score_sum desc
    out = []
    for kb, info in agg.items():
        out.append((kb, info["score_sum"], info["max_score"], info["example"]))
    out.sort(key=lambda x: x[1], reverse=True)
    return out

# --- simple urgency detector (same as before) ---
URGENT_KEYWORDS = set([
    "severe abdominal pain","persistent vomiting","vomit blood","vomiting blood",
    "difficulty breathing","faint","cold/clammy","black stool","lethargy","difficulty waking"
])

def is_urgent(text):
    txt = (text or "").lower()
    matches = [kw for kw in URGENT_KEYWORDS if kw in txt]
    return (len(matches) > 0, matches)

# --- main get_reply ---
def get_reply(text):
    # urgent check
    urgent_flag, urgent_matches = is_urgent(text)
    if urgent_flag:
        return {
            "reply": "This message contains warning signs. Seek immediate medical care or go to the nearest emergency department. If you are in immediate danger call local emergency services.",
            "kb_id": None,
            "sources": ["Emergency guidance - WHO"],
            "urgency": "urgent",
            "confidence": 1.0,
            "matched_warning_signs": urgent_matches
        }

    # choose retrieval method
    if FAISS_INDEX is not None:
        vector_results = _retrieve_with_faiss(text, top_k=TOP_K)
    else:
        vector_results = _retrieve_in_memory(text, top_k=TOP_K)

    if not vector_results:
        return {
            "reply": "Please ask dengue-related questions only. I can help with symptoms, prevention, testing, treatment, and mosquito control.",
            "kb_id": None,
            "sources": ["system-rule"],
            "urgency": "non-urgent",
            "confidence": 0.0,
            "matched_warning_signs": []
        }

    # aggregate vector-level results to kb-level
    kb_aggs = _aggregate_by_kb(vector_results)
    # pick top kb
    best_kb, score_sum, max_score, example = kb_aggs[0]

    # find canonical answer for that kb: example contains canonical_answer
    canonical = example.get("canonical_answer") or ""
    sources = example.get("sources", [])
    urgency = example.get("urgency", "non-urgent")

    # simple confidence mapping
    confidence = float(score_sum) / (len(vector_results) or 1)

    return {
        "reply": canonical,
        "kb_id": best_kb,
        "sources": sources or [],
        "urgency": urgency,
        "confidence": confidence,
        "matched_warning_signs": []
    }

# --- optional helper to add a KB item at runtime (not covering vector-index bookkeeping) ---
def add_kb_item(item, embedding_text=None):
    raise NotImplementedError("add_kb_item not implemented for vector-per-variant index. Re-run build_embeddings_variants.py to update index.")
