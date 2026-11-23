
# Import AI service
from services.ai_service import ask_ai


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
