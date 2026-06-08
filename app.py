def answer_question():
    question = input("Enter your question: ")
    print("\nAnswer:")
    print("This is a sample answer for:", question)

def summarize_text():
    text = input("Enter text to summarize: ")
    print("\nSummary:")
    print(text[:100] + "...")

def generate_content():
    topic = input("Enter a topic: ")
    print("\nGenerated Content:")
    print(f"Once upon a time, there was a story about {topic}.")

def feedback():
    response = input("\nWas this response helpful? (yes/no): ")
    print("Thank you for your feedback!")

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