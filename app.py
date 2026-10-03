import streamlit as st

from embed import build_index
from ask import ask

st.set_page_config(page_title="Ask My Project", page_icon="📊")
st.title("Ask My Project")
st.caption("Ask questions about my Apple Inc. financial valuation project (FY2023-FY2025).")


def show(text):
    """Display text; escape '$' so Streamlit does not treat it as a math formula."""
    st.markdown(text.replace("$", "\\$"))


@st.cache_resource
def load_index():
    """Build or load the embeddings once, not on every interaction."""
    return build_index()


index = load_index()

# Keep the chat history between interactions
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        show(message["content"])

question = st.chat_input("Ask a question about the project...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        show(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the project files..."):
            answer = ask(question, index)
        show(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})