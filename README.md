# Ask My Project

A small RAG (Retrieval-Augmented Generation) chatbot that answers questions about my Apple Inc. financial valuation project (FY2023-FY2025). It reads my Excel model and Word report, finds the most relevant parts for each question, and asks Gemini to answer using only those parts.

Live demo: PASTE_YOUR_STREAMLIT_LINK_HERE

## How it works

1. `load_data.py` reads the Word report and the Excel model.
2. `chunking.py` splits the text into chunks (Word by size, Excel by sheet).
3. `embed.py` turns each chunk into an embedding (`gemini-embedding-001`) and finds the closest chunks to a question using cosine similarity.
4. `ask.py` sends the top 5 chunks and the question to Gemini, with instructions to answer only from the project files and not to invent numbers.
5. `app.py` is the Streamlit chat interface.

## Setup

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project folder with your own Gemini API key:

```
GEMINI_API_KEY=your_key_here
```

The project files are in the `data` folder:
- `apple_financial_statements.xlsx`
- `apple_valuation_report.docx`

## Run

```
streamlit run app.py
```

Or ask questions in the terminal with `python ask.py`.

## Limitations

- The chunking is simple, so retrieval is not always perfect. Ask one question per message.
- It has no live market data. A price it shows is a snapshot recorded in the project files.
- It runs on the Gemini API free tier, so busy or rate-limited moments can happen. The code retries and falls back to other models.
- Answers should be checked against the source files.

Built by Manar Ebrahim, as a learning project.
