
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None


def demo_response(prompt):

    prompt_lower = prompt.lower()

    # Question answering
    if "user question:" in prompt_lower:

        if "python" in prompt_lower:
            return (
                "Python is a high-level programming language. "
                "It is popular for its simple syntax and is used in "
                "web development, automation, data science and AI."
            )

        elif "artificial intelligence" in prompt_lower or "what is ai" in prompt_lower:
            return (
                "Artificial Intelligence (AI) enables machines to perform "
                "tasks that normally require human intelligence, such as "
                "learning, reasoning and problem-solving."
            )

        elif "machine learning" in prompt_lower:
            return (
                "Machine Learning is a branch of AI where computers learn "
                "patterns from data and use them to make predictions."
            )

        return (
            "Demo Response: Your question was received successfully. "
            "A live AI model is required for a detailed answer."
        )

    # Summarization
    elif "summarize the following text" in prompt_lower:

        text = prompt.split("Text:", 1)[-1].strip()
        sentences = text.replace("\n", " ").split(".")
        summary = ". ".join(s.strip() for s in sentences[:2] if s.strip())

        if summary:
            return "Demo Summary: " + summary + "."

        return "Please provide text to summarize."

    # Creative content
    elif "generate creative and engaging content" in prompt_lower:

        topic = prompt.split("Topic:", 1)[-1].strip()

        return (
            f"Explore the fascinating world of {topic}! "
            f"{topic} brings new opportunities, encourages creativity, "
            "and helps us imagine innovative possibilities."
        )

    return "Demo response generated successfully."


def ask_ai(prompt):

    if client is None:
        return demo_response(prompt)

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            input=prompt
        )

        return response.output_text

    except Exception:
        return demo_response(prompt)
