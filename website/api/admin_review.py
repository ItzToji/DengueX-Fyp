# website/api/admin_review.py
import os, csv, datetime
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional

REVIEW_FILE = os.environ.get("CHATBOT_REVIEW_FILE", "feature1_chatbot/review_queue.csv")
app = FastAPI(title="DengueX Admin Review API", version="1.0")

def read_review_rows():
    if not os.path.exists(REVIEW_FILE):
        return []
    rows = []
    with open(REVIEW_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

@app.get("/admin/review/peek")
def peek(limit: int = Query(50, gt=0, le=1000)):
    """Return most recent 'limit' review rows (as JSON)."""
    rows = read_review_rows()
    return {"count": len(rows), "recent": rows[-limit:]}

@app.post("/admin/review/mark")
def mark_review(index: int, reviewer: str):
    """
    Mark a row as reviewed by writing reviewer and datetime into the CSV row.
    'index' is zero-based row index in the CSV file (first data row = 0).
    """
    if not os.path.exists(REVIEW_FILE):
        raise HTTPException(status_code=404, detail="Review file not found")
    with open(REVIEW_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    if index < 0 or index >= len(reader):
        raise HTTPException(status_code=400, detail="Index out of range")
    reader[index]['reviewed_by'] = reviewer
    reader[index]['reviewed_at'] = datetime.datetime.utcnow().isoformat()
    # rewrite file
    with open(REVIEW_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=reader[0].keys())
        writer.writeheader()
        writer.writerows(reader)
    return {"status":"ok", "index": index}
