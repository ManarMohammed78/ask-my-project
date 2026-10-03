import time

from google.genai import errors

from embed import build_index, search, client

# Models to try in order; if one is busy we move on to the next
MODELS = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]
TOP_K = 5

PROMPT = """You are an assistant that answers questions about an Apple Inc. financial valuation project.
Use ONLY the context below. Do not use outside knowledge and do not invent numbers.
If the answer is not in the context, say you could not find it in the project files.

Rules:
- Excel amounts are in millions of USD unless stated otherwise.
- Columns named "%" hold decimals (0.05 means 5%). Convert them to percentages when you show them.
- Mention which source (Word report or Excel sheet) the answer came from.
- You have no live market data. If the question asks for a "current", "today", or "latest" price, say you cannot provide live prices, then give only the figure recorded in the project files and state clearly that it is a snapshot from the files (include its date if the context shows one).

Context:
{context}

Question: {question}
"""


def generate_with_fallback(prompt):
    """Call Gemini; on temporary errors (busy or rate-limited) retry, then try the next model."""
    for model in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model, contents=prompt
                )
                return response.text
            except errors.APIError as err:
                # Only retry on temporary problems; raise anything else (e.g. a bad API key)
                if err.code not in (429, 500, 503):
                    raise
                print(f"[{model}] error {err.code}, retrying...")
                time.sleep(5 * (attempt + 1))
    return "Sorry, all models are busy right now. Please try again in a minute."


def ask(question, index):
    """Find the most relevant chunks, then ask Gemini to answer from them only."""
    results = search(question, index, top_k=TOP_K)
    context = "\n\n---\n\n".join(
        f"[{chunk['source']}]\n{chunk['text']}" for _, chunk in results
    )
    return generate_with_fallback(PROMPT.format(context=context, question=question))


if __name__ == "__main__":
    index = build_index()
    print("Ask a question about the Apple project (type 'exit' to quit).")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in ("exit", "quit"):
            break
        if not question:
            continue
        print("\nAnswer:", ask(question, index))