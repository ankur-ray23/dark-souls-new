# app.py

import streamlit as st
from qa_chain import answer_question
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Dark Souls Graph QA", layout="wide")
st.title("🧠 Ask Questions About Dark Souls Lore")

st.markdown("Ask natural language questions based on the knowledge graph built from Dark Souls data.")

# Input box for the user to ask a question
user_question = st.text_input("Enter your question:")

# Submit button
if st.button("Ask"):
    if user_question.strip():
        with st.spinner("Thinking..."):
            try:
                result = answer_question(user_question)
                st.success("Answer:")
                st.write(result)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
    else:
        st.warning("Please enter a question to proceed.")
