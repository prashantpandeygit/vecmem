import os
import sqlite3
import faiss
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from fastmcp import FastMCP, tool

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "memory.db"
FAISS_PATH = DATA_DIR / "index.faiss"

app = FastMCP("vecmem")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

dim = 384  
if FAISS_PATH.exists():
    index = faiss.read_index(str(FAISS_PATH))
else:
    index = faiss.IndexFlatL2(dim)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    vector BLOB
)
""")
conn.commit()

def store_faiss():
    faiss.write_index(index, str(FAISS_PATH))

def to_bytes(vec):
    return faiss.vector_to_array(vec).tobytes()

def from_bytes(b):
    import numpy as np
    arr = np.frombuffer(b, dtype="float32")
    return arr.reshape(1, -1)

def embed(txt):
    return embedder.encode([txt], convert_to_numpy=True)


@tool("add_text", "Save text into vector memory")
def add_text(text: str):
    vec = embed(text)
    index.add(vec)
    cur.execute("INSERT INTO memory (text, vector) VALUES (?, ?)", (text, vec.tobytes()))
    conn.commit()
    store_faiss()
    return {"ok": True, "msg": f"Stored {len(text)} chars."}


@tool("search", "search through memory")
def search(query: str, top_k: int = 5):
    if index.ntotal == 0:
        return {"results": []}
    qv = embed(query)
    D, I = index.search(qv, top_k)
    out = []
    for idx in I[0]:
        cur.execute("SELECT id, text FROM memory WHERE id=?", (idx + 1,))
        row = cur.fetchone()
        if row:
            out.append({"id": row[0], "text": row[1]})
    return {"query": query, "matches": out}


@tool("reset_memory", "Clear FAISS index and database")
def reset_memory():
    global index
    cur.execute("DELETE FROM memory")
    conn.commit()
    if FAISS_PATH.exists():
        FAISS_PATH.unlink()
    index = faiss.IndexFlatL2(dim)
    return {"ok": True, "msg": "All memory cleared."}


if __name__ == "__main__":
    print("running vecmem locally ...")
    app.run()
