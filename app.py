import os
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------- DEMO MODE ----------------

def demo_response(prompt):
    prompt_lower = prompt.lower()

    # Question answering
    if "user question:" in prompt_lower:

        if "artificial intelligence" in prompt_lower or "what is ai" in prompt_lower:
            return (
                "Artificial Intelligence (AI) is a branch of computer science "
                "that enables machines to perform tasks that normally require "
                "human intelligence, such as learning, reasoning, problem-solving, "
                "and understanding language."
            )

        elif "machine learning" in prompt_lower:
            return (
                "Machine Learning is a subset of Artificial Intelligence in which "
                "computers learn patterns from data and use those patterns to make "
                "predictions or decisions."
            )

        else:
            return (
                "Demo Response: The AI Assistant received the question successfully. "
                "Real LLM-generated responses will be available when API credits "
                "are enabled."
            )

    # Summarization
    elif "summarize the following text" in prompt_lower:
        return (
            "Summary: The text explains that Artificial Intelligence "
            "enables computers to perform tasks that normally require "
            "human intelligence."
        )

    # Creative content
    elif "generate creative and engaging content" in prompt_lower:
        return (
            "Artificial Intelligence is transforming the modern world by "
            "helping people solve problems, automate tasks, and create "
            "innovative solutions across different fields."
        )

    return "Demo response generated successfully."

def ask_ai(prompt):
    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            input=prompt
        )

        return response.output_text

    except Exception:
        print("\n[Demo Mode: API credits unavailable]")
        return demo_response(prompt)

# ---------------- QUESTION ANSWERING ----------------

def answer_question():

    question = input("Enter your question: ")

    if not question.strip():
        print("Please enter a valid question.")
        return

    prompt = f"""
You are a helpful AI assistant.

Answer the user's question clearly and accurately.

User question:
{question}
"""

    print("\nAnswer:")
    print(ask_ai(prompt))


# ---------------- SUMMARIZATION ----------------

def summarize_text():

    text = input("Enter text to summarize: ")

    if not text.strip():
        print("Please enter some text.")
        return

    prompt = f"""
Summarize the following text.
Keep the important information and make the summary concise.

Text:
{text}
"""

    print("\nSummary:")
    print(ask_ai(prompt))


# ---------------- CONTENT GENERATION ----------------

def generate_content():

    topic = input("Enter a topic: ")

    if not topic.strip():
        print("Please enter a topic.")
        return

    prompt = f"""
Generate creative and engaging content about the following topic.

Topic:
{topic}
"""

    print("\nGenerated Content:")
    print(ask_ai(prompt))


# ---------------- FEEDBACK ----------------

def feedback():
    
    response = input("\nWas this response helpful? (yes/no): ")

    if response.lower() == "yes":
        print("Thank you for your feedback!")

    elif response.lower() == "no":
        print("Thank you. We will use your feedback for improvement.")

    else:
        print("Please enter yes or no.")


# ---------------- MAIN MENU ----------------

while True:

    print("\n===== AI Assistant =====")
    print("1. Answer Questions")
    print("2. Summarize Text")
    print("3. Generate Creative Content")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        answer_question()
        feedback()

    elif choice == "2":
        summarize_text()
        feedback()

    elif choice == "3":
        generate_content()
        feedback()

    elif choice == "4":
        print("Goodbye!")
        break

    else:
        print("Invalid choice!")