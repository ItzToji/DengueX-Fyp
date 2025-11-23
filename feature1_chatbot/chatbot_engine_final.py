import os
import json
import numpy as np

from sentence_transformers import SentenceTransformer

# Dengue-focused semantic retrieval engine with FAISS/SBERT, urgency detection, and optional typo correction.
# faiss optional import
try:
    import faiss
    HAS_FAISS = True
except Exception:
    faiss = None
    HAS_FAISS = False

# try to import typo correction (best-effort)
try:
    from feature1_chatbot_typo_correction import correct_typo as _correct_typo
    _HAS_TYPOMOD = True
except Exception:
    _correct_typo = lambda q: q
    _HAS_TYPOMOD = False

# paths & globals
BASE = os.path.dirname(__file__)
INDEX_DIR = os.path.join(BASE, "index")
MODEL = None
EMBEDDINGS = None         # numpy array of vectors (N x D)
META = []                 # list of vector-level meta entries
FAISS_INDEX = None

SIMILARITY_THRESHOLD = 0.65  # tuned for normalized inner product
TOP_K = 5

URGENT_KEYWORDS = set([
    "severe abdominal pain","persistent vomiting","vomit blood","vomiting blood",
    "difficulty breathing","faint","cold/clammy","black stool","lethargy","difficulty waking"
])

DENGUE_KEYWORDS = set([
    "dengue","mosquito","aedes","fever","platelet","rash","ns1","serology","dengue fever","dengue virus"
])

def _ensure_model(model_name="all-MiniLM-L6-v2"):
    global MODEL
    if MODEL is None:
        MODEL = SentenceTransformer(model_name)
    return MODEL

def init_index(index_dir=None):
    """
    Load prebuilt index (embeddings.npy, meta.jsonl, index.faiss, model_name.txt)
    Returns number of vectors loaded.
    """
    global MODEL, EMBEDDINGS, META, FAISS_INDEX
    idx_dir = index_dir or INDEX_DIR

    model_file = os.path.join(idx_dir, "model_name.txt")
    emb_path = os.path.join(idx_dir, "embeddings.npy")
    meta_path = os.path.join(idx_dir, "meta.jsonl")
    idx_path = os.path.join(idx_dir, "index.faiss")

    if not os.path.exists(emb_path) or not os.path.exists(meta_path):
        raise FileNotFoundError("Index files missing. Build them with scripts/build_embeddings_variants.py")

    model_name = "all-MiniLM-L6-v2"
    if os.path.exists(model_file):
        try:
            model_name = open(model_file,"r",encoding="utf-8").read().strip()
        except Exception:
            pass

    MODEL = _ensure_model(model_name)

    EMBEDDINGS = np.load(emb_path).astype("float32")
    # load meta
    META = []
    with open(meta_path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            META.append(json.loads(line))

    # try load faiss index
    if os.path.exists(idx_path):
        if not HAS_FAISS:
            raise ImportError("FAISS index found but faiss not installed. Install faiss-cpu or faiss-gpu.")
        FAISS_INDEX = faiss.read_index(idx_path)
    else:
        FAISS_INDEX = None

    # normalize embeddings to be safe (cosine equivalence for inner product)
    def normalize_rows(x):
        norms = np.linalg.norm(x, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return x / norms
    EMBEDDINGS[:] = normalize_rows(EMBEDDINGS)

    print(f"Index loaded: {len(META)} vectors (model: {model_name})")
    return len(META)

def _embed_text(text):
    global MODEL
    if MODEL is None:
        _ensure_model()
    emb = MODEL.encode([text], convert_to_numpy=True, normalize_embeddings=True)
    return emb[0].astype("float32")

def is_urgent(text):
    txt = (text or "").lower()
    matches = [kw for kw in URGENT_KEYWORDS if kw in txt]
    return (len(matches) > 0, matches)

def predict_intent(text):
    txt = (text or "").lower()
    score = sum(1 for k in DENGUE_KEYWORDS if k in txt)
    if score >= 1:
        return "dengue"
    if "fever" in txt and "mosquito" in txt:
        return "dengue"
    return "not-dengue"

def _retrieve_with_faiss(text, top_k=TOP_K):
    emb = _embed_text(text).reshape(1, -1)
    # search for more vectors to allow aggregation across variants
    D, I = FAISS_INDEX.search(emb, top_k * 3)
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

def _aggregate_by_kb(results):
    agg = {}
    for r in results:
        kb = str(r.get("kb_id") or r.get("id") or r.get("kbid") or r.get("uid") or r.get("vector_id"))
        score = float(r.get("vector_score", 0.0))
        if kb not in agg:
            agg[kb] = {"score_sum": score, "max_score": score, "example": r}
        else:
            agg[kb]["score_sum"] += score
            if score > agg[kb]["max_score"]:
                agg[kb]["max_score"] = score
                agg[kb]["example"] = r
    out = []
    for kb, info in agg.items():
        out.append((kb, info["score_sum"], info["max_score"], info["example"]))
    out.sort(key=lambda x: x[1], reverse=True)
    return out

def get_reply(text, debug=False):
    # urgent
    urgent_flag, urgent_matches = is_urgent(text)
    if urgent_flag:
        return {
            "reply": "This message contains warning signs. Seek immediate medical care or go to the nearest emergency department.",
            "kb_id": None,
            "sources": ["Emergency guidance - WHO"],
            "urgency": "urgent",
            "confidence": 1.0,
            "matched_warning_signs": urgent_matches
        }

    # typo corrected alternative
    corrected = _correct_typo(text) if _HAS_TYPOMOD else text
    # build queries; keep uniqueness preserving order
    queries = []
    for q in [text.strip(), corrected.strip()] if text else []:
        if q and q not in queries:
            queries.append(q)

    if debug:
        print("Queries:", queries)

    all_vector_results = []
    for q in queries:
        if FAISS_INDEX is not None:
            res = _retrieve_with_faiss(q)
        else:
            res = _retrieve_in_memory(q)
        for r in res:
            r['origin_query'] = q
        all_vector_results.extend(res)

    if not all_vector_results:
        return {
            "reply": "Please ask dengue-related questions only. I can help with symptoms, prevention, testing and treatment guidance.",
            "kb_id": None,
            "sources": [],
            "urgency": "non-urgent",
            "confidence": 0.0,
            "matched_warning_signs": []
        }

    kb_aggs = _aggregate_by_kb(all_vector_results)
    best_kb, score_sum, max_score, example = kb_aggs[0]

    # if top score low => decline
    if max_score < SIMILARITY_THRESHOLD:
        # look for explicit out_of_scope tags
        for m, s in [(x[3], x[2]) for x in kb_aggs]:
            if 'out_of_scope' in (m.get('tags') or []):
                return {
                    "reply": m.get("canonical_answer"),
                    "kb_id": m.get("kb_id") or m.get("id"),
                    "sources": m.get("sources", []),
                    "urgency": m.get("urgency", "non-urgent"),
                    "confidence": float(s),
                    "matched_warning_signs": []
                }
        return {
            "reply": "I don't have a confident dengue-related answer for that. Please rephrase or ask a different dengue question.",
            "kb_id": None,
            "sources": [],
            "urgency": "non-urgent",
            "confidence": float(max_score),
            "matched_warning_signs": []
        }

    canonical = example.get("canonical_answer") or example.get("answer") or ""
    sources = example.get("sources", []) or []
    urgency = example.get("urgency", "non-urgent")
    confidence = float(score_sum) / (len(all_vector_results) or 1)

    return {
        "reply": canonical + ("\n\nSource: " + ", ".join(sources) if sources else ""),
        "kb_id": best_kb,
        "sources": sources,
        "urgency": urgency,
        "confidence": confidence,
        "matched_warning_signs": []
    }

# small loader for legacy tests (loads KB and builds in-memory embeddings)
def load_kb(kb_path, model_name="all-MiniLM-L6-v2"):
    global META, EMBEDDINGS, FAISS_INDEX, MODEL
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
    rep_texts = []
    for it in META:
        rep = it.get("title","")
        variants = it.get("question_variants") or []
        if variants:
            rep += " || " + " || ".join(variants[:3])
        rep_texts.append(rep)
    if rep_texts:
        embs = MODEL.encode(rep_texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
        EMBEDDINGS = embs.astype("float32")
    else:
        EMBEDDINGS = np.zeros((0, MODEL.get_sentence_embedding_dimension()), dtype="float32")
    FAISS_INDEX = None
    return len(META)
