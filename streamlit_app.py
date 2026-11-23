
import streamlit as st

from services.ai_service import ask_ai
from database.db import (
    init_db,
    save_interaction,
    get_history,
    save_feedback,
    delete_conversation,
    clear_history
)


# Initialize database
init_db()


# Page configuration
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="centered"
)


# Application title
st.title("🤖 AI Assistant")
st.write("Your personal assistant for questions, summaries and creative content.")


# Sidebar
st.sidebar.title("Menu")

feature = st.sidebar.selectbox(
    "Choose a feature",
    [
        "Answer Questions",
        "Summarize Text",
        "Generate Creative Content",
        "Conversation History"
    ]
)


# ---------------- ANSWER QUESTIONS ----------------

if feature == "Answer Questions":

    st.subheader("Ask Your Question")

    question = st.text_area("Enter your question:")

    if st.button("Get Answer"):

        if question.strip():

            prompt = f"""
You are a helpful AI assistant.

Answer the user's question clearly and accurately.

User question:
{question}
"""

            with st.spinner("Generating answer..."):
                answer = ask_ai(prompt)

            save_interaction("Answer Questions", question, answer)

            st.session_state["latest_id"] = get_history()[0][0]
            st.session_state["latest_response"] = answer

    if "latest_response" in st.session_state:
        st.success("Answer:")
        st.write(st.session_state["latest_response"])


# ---------------- SUMMARIZATION ----------------

elif feature == "Summarize Text":

    st.subheader("Text Summarization")

    text = st.text_area("Enter the text you want to summarize:")

    if st.button("Summarize"):

        if text.strip():

            prompt = f"""
Summarize the following text.
Keep the important information and make the summary concise.

Text:
{text}
"""

            with st.spinner("Summarizing..."):
                summary = ask_ai(prompt)

            save_interaction("Summarize Text", text, summary)

            st.session_state["latest_id"] = get_history()[0][0]
            st.session_state["latest_response"] = summary

    if "latest_response" in st.session_state:
        st.success("Summary:")
        st.write(st.session_state["latest_response"])


# ---------------- CONTENT GENERATION ----------------

elif feature == "Generate Creative Content":

    st.subheader("Creative Content Generator")

    topic = st.text_input("Enter a topic:")

    if st.button("Generate Content"):

        if topic.strip():

            prompt = f"""
Generate creative and engaging content about the following topic.

Topic:
{topic}
"""

            with st.spinner("Creating content..."):
                content = ask_ai(prompt)

            save_interaction("Generate Creative Content", topic, content)

            st.session_state["latest_id"] = get_history()[0][0]
            st.session_state["latest_response"] = content

    if "latest_response" in st.session_state:
        st.success("Generated Content:")
        st.write(st.session_state["latest_response"])


# ---------------- FEEDBACK ----------------

if feature in [
    "Answer Questions",
    "Summarize Text",
    "Generate Creative Content"
]:

    if "latest_id" in st.session_state:

        st.write("Was this response helpful?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("👍 Helpful"):
                save_feedback(st.session_state["latest_id"], "Helpful")
                st.success("Thank you for your feedback!")

        with col2:
            if st.button("👎 Not Helpful"):
                save_feedback(st.session_state["latest_id"], "Not Helpful")
                st.success("Thank you for your feedback!")



# ---------------- CONVERSATION HISTORY ----------------

elif feature == "Conversation History":

    st.subheader("Your Previous Conversations")

    history = get_history()

    if history:

        if st.button("🗑️ Clear All History"):

            st.session_state["confirm_clear"] = True

        if st.session_state.get("confirm_clear", False):

            st.warning("Are you sure you want to delete all conversations?")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Yes, Delete All"):
                    clear_history()
                    st.session_state["confirm_clear"] = False
                    st.success("All conversations deleted!")
                    st.rerun()

            with col2:
                if st.button("Cancel"):
                    st.session_state["confirm_clear"] = False
                    st.rerun()

        for record in history:

            conversation_id, feature_name, user_input, response, feedback, created_at = record

            with st.expander(f"{feature_name} | {created_at}"):

                st.write("**Your Input:**")
                st.write(user_input)

                st.write("**Assistant Response:**")
                st.write(response)

                st.write("**Feedback:**")
                st.write(feedback if feedback else "Not provided yet")

                if st.button(
                    "🗑️ Delete Conversation",
                    key=f"delete_{conversation_id}"
                ):
                    delete_conversation(conversation_id)
                    st.success("Conversation deleted!")
                    st.rerun()

    else:
        st.info("No conversation history available yet.")
