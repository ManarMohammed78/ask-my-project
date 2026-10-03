import os
import json
import time

import numpy as np
from dotenv import load_dotenv
from google import genai

from chunking import build_chunks

# Load the API key from the .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("GEMINI_API_KEY not found. Check your .env file.")

client = genai.Client(api_key=api_key)

EMBED_MODEL = "gemini-embedding-001"
CACHE_FILE = "embeddings.json"
BATCH_SIZE = 10


def embed_texts(texts):
    """Embed texts in small batches, with retries to respect free-tier limits."""
    vectors = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        for attempt in range(5):
            try:
                result = client.models.embed_content(
                    model=EMBED_MODEL, contents=batch
                )
                vectors.extend([e.values for e in result.embeddings])
                break
            except Exception as err:
                wait = 15 * (attempt + 1)
                print(f"Error: {err}\nRetrying in {wait} seconds...")
                time.sleep(wait)
        else:
            raise SystemExit("Embedding failed after 5 attempts.")
        print(f"Embedded {min(i + BATCH_SIZE, len(texts))}/{len(texts)}")
        time.sleep(3)
    return vectors


def build_index():
    """Return chunks with embeddings. Reuse the saved file if the text is unchanged."""
    chunks = build_chunks()

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cached = json.load(f)
        if [c["text"] for c in cached] == [c["text"] for c in chunks]:
            print("Loaded embeddings from cache.")
            return cached

    vectors = embed_texts([c["text"] for c in chunks])
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f)
    return chunks


def search(question, index, top_k=5):
    """Return the top_k chunks most similar to the question (cosine similarity)."""
    result = client.models.embed_content(model=EMBED_MODEL, contents=[question])
    q = np.array(result.embeddings[0].values)

    matrix = np.array([c["embedding"] for c in index])
    scores = matrix @ q / (np.linalg.norm(matrix, axis=1) * np.linalg.norm(q))

    best = np.argsort(scores)[::-1][:top_k]
    return [(float(scores[i]), index[i]) for i in best]


if __name__ == "__main__":
    index = build_index()
    print("Chunks indexed:", len(index))

    question = "What was Apple's total net sales in FY2025?"
    print("\nQuestion:", question)
    for score, chunk in search(question, index, top_k=3):
        print(f"\nScore: {score:.3f} | Source: {chunk['source']}")
        print(chunk["text"][:300])