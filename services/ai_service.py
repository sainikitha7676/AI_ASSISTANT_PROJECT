
import os
import re
from dotenv import load_dotenv
from openai import OpenAI

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key) if api_key else None

api_available = False


# --------------------------------------------------
# AI MODE DETECTION
# --------------------------------------------------

def get_ai_mode():

    if api_available:
        return "Live API Mode"

    return "Demo Mode"


# --------------------------------------------------
# TOPIC DETECTION
# --------------------------------------------------

TOPICS = {
    "Python": [
        r"\bpython\b"
    ],
    "Artificial Intelligence": [
        r"\bartificial intelligence\b",
        r"\bwhat is ai\b",
        r"\bai technology\b"
    ],
    "Machine Learning": [
        r"\bmachine learning\b",
        r"\bml\b"
    ],
    "Database": [
        r"\bdatabases?\b",
        r"\bdbms\b"
    ],
    "SQL": [
        r"\bsql\b",
        r"\bstructured query language\b"
    ]
}


def detect_topic(text):

    text = text.lower()

    for topic, patterns in TOPICS.items():

        for pattern in patterns:

            if re.search(pattern, text):
                return topic

    return None


def get_previous_topic(conversation_history):

    if not conversation_history:
        return None

    for message in reversed(conversation_history):

        if message.get("role") == "user":

            topic = detect_topic(message.get("content", ""))

            if topic:
                return topic

    return None


# --------------------------------------------------
# FOLLOW-UP QUESTION DETECTION
# --------------------------------------------------

def detect_follow_up_intent(prompt):

    prompt = prompt.lower()

    if any(word in prompt for word in [
        "disadvantages",
        "drawbacks",
        "limitations",
        "weaknesses"
    ]):
        return "disadvantages"

    if any(word in prompt for word in [
        "advantages",
        "benefits",
        "strengths"
    ]):
        return "advantages"

    if any(word in prompt for word in [
        "applications",
        "application",
        "uses",
        "used for"
    ]):
        return "applications"

    if any(word in prompt for word in [
        "features",
        "characteristics",
        "properties"
    ]):
        return "features"

    if "examples" in prompt or "example" in prompt:
        return "examples"

    return None


# --------------------------------------------------
# CONTEXTUAL DEMO RESPONSES
# --------------------------------------------------

CONTEXTUAL_RESPONSES = {

    "Python": {

        "advantages": (
            "Advantages of Python:\n\n"
            "1. Easy to learn: Python has simple and readable syntax.\n"
            "2. Versatile: It is used in web development, AI and data science.\n"
            "3. Large libraries: It provides many useful libraries.\n"
            "4. Cross-platform: Python works on Windows, Linux and macOS.\n"
            "5. Community support: It has a large developer community."
        ),

        "disadvantages": (
            "Disadvantages of Python:\n\n"
            "1. It can be slower than compiled languages.\n"
            "2. It may consume more memory.\n"
            "3. It is less commonly used for mobile app development.\n"
            "4. Dynamic typing can sometimes cause errors."
        ),

        "applications": (
            "Applications of Python:\n\n"
            "1. Web development\n"
            "2. Artificial Intelligence\n"
            "3. Machine Learning\n"
            "4. Data Science and Data Analysis\n"
            "5. Automation and scripting\n"
            "6. Software development"
        ),

        "features": (
            "Features of Python:\n\n"
            "1. Simple and readable syntax.\n"
            "2. Interpreted programming language.\n"
            "3. Object-oriented programming support.\n"
            "4. Large standard library.\n"
            "5. Cross-platform compatibility."
        ),

        "examples": (
            "Examples of Python applications:\n\n"
            "1. Chatbots and AI assistants.\n"
            "2. Websites using Django or Flask.\n"
            "3. Data analysis using Pandas.\n"
            "4. Machine Learning using Scikit-learn.\n"
            "5. Automation scripts."
        )
    },

    "Artificial Intelligence": {

        "advantages": (
            "Advantages of Artificial Intelligence:\n\n"
            "1. Automates repetitive tasks.\n"
            "2. Processes large amounts of data quickly.\n"
            "3. Supports better decision-making.\n"
            "4. Reduces human effort.\n"
            "5. Can operate continuously."
        ),

        "disadvantages": (
            "Disadvantages of Artificial Intelligence:\n\n"
            "1. High development and maintenance costs.\n"
            "2. Possible job displacement.\n"
            "3. Dependence on data quality.\n"
            "4. Privacy and security concerns.\n"
            "5. Lack of human emotions and judgment."
        ),

        "applications": (
            "Applications of Artificial Intelligence:\n\n"
            "1. Healthcare and medical diagnosis.\n"
            "2. Virtual assistants and chatbots.\n"
            "3. Self-driving vehicles.\n"
            "4. Fraud detection in banking.\n"
            "5. Recommendation systems.\n"
            "6. Robotics."
        ),

        "features": (
            "Features of Artificial Intelligence:\n\n"
            "1. Learning from data.\n"
            "2. Reasoning and problem-solving.\n"
            "3. Decision-making.\n"
            "4. Pattern recognition.\n"
            "5. Natural language processing."
        ),

        "examples": (
            "Examples of Artificial Intelligence:\n\n"
            "1. ChatGPT and virtual assistants.\n"
            "2. Face recognition systems.\n"
            "3. Recommendation systems.\n"
            "4. Self-driving vehicles.\n"
            "5. AI-powered medical tools."
        )
    },

    "Machine Learning": {

        "advantages": (
            "Advantages of Machine Learning:\n\n"
            "1. Learns patterns from data.\n"
            "2. Improves predictions over time.\n"
            "3. Automates data analysis.\n"
            "4. Supports better decision-making.\n"
            "5. Can handle large datasets."
        ),

        "disadvantages": (
            "Disadvantages of Machine Learning:\n\n"
            "1. Requires large amounts of quality data.\n"
            "2. Training can be time-consuming.\n"
            "3. Models may produce inaccurate predictions.\n"
            "4. Requires computing resources.\n"
            "5. Results can be difficult to interpret."
        ),

        "applications": (
            "Applications of Machine Learning:\n\n"
            "1. Email spam detection.\n"
            "2. Product recommendations.\n"
            "3. Fraud detection.\n"
            "4. Image and speech recognition.\n"
            "5. Medical predictions.\n"
            "6. Weather forecasting."
        ),

        "features": (
            "Features of Machine Learning:\n\n"
            "1. Learns from historical data.\n"
            "2. Identifies patterns.\n"
            "3. Makes predictions.\n"
            "4. Improves through training.\n"
            "5. Supports automated decision-making."
        ),

        "examples": (
            "Examples of Machine Learning:\n\n"
            "1. Email spam filters.\n"
            "2. Netflix and YouTube recommendations.\n"
            "3. Face recognition.\n"
            "4. Credit card fraud detection.\n"
            "5. Voice recognition systems."
        )
    },

    "Database": {

        "advantages": (
            "Advantages of Databases:\n\n"
            "1. Organized data storage.\n"
            "2. Easy data retrieval.\n"
            "3. Better data security.\n"
            "4. Reduced data duplication.\n"
            "5. Easier data management."
        ),

        "disadvantages": (
            "Disadvantages of Databases:\n\n"
            "1. Installation and maintenance costs.\n"
            "2. Requires technical knowledge.\n"
            "3. Needs regular backups.\n"
            "4. Database failures can affect applications."
        ),

        "applications": (
            "Applications of Databases:\n\n"
            "1. Banking systems.\n"
            "2. Hospital management.\n"
            "3. Student information systems.\n"
            "4. E-commerce websites.\n"
            "5. Railway reservation systems."
        ),

        "features": (
            "Features of Databases:\n\n"
            "1. Organized data storage.\n"
            "2. Data retrieval and updating.\n"
            "3. Data security.\n"
            "4. Backup and recovery.\n"
            "5. Data consistency."
        ),

        "examples": (
            "Examples of Database Systems:\n\n"
            "1. MySQL.\n"
            "2. PostgreSQL.\n"
            "3. Oracle Database.\n"
            "4. Microsoft SQL Server.\n"
            "5. SQLite."
        )
    },

    "SQL": {

        "advantages": (
            "Advantages of SQL:\n\n"
            "1. Easy to learn and use.\n"
            "2. Retrieves data efficiently.\n"
            "3. Supports data manipulation.\n"
            "4. Works with relational databases.\n"
            "5. Supports access control."
        ),

        "disadvantages": (
            "Disadvantages of SQL:\n\n"
            "1. Complex queries can be difficult to write.\n"
            "2. Different database systems have variations.\n"
            "3. Less suitable for unstructured data by itself.\n"
            "4. Performance depends on database design."
        ),

        "applications": (
            "Applications of SQL:\n\n"
            "1. Retrieving database records.\n"
            "2. Inserting and updating data.\n"
            "3. Managing customer information.\n"
            "4. Generating reports.\n"
            "5. Managing relational databases."
        ),

        "features": (
            "Features of SQL:\n\n"
            "1. Data retrieval using SELECT.\n"
            "2. Data insertion using INSERT.\n"
            "3. Data modification using UPDATE.\n"
            "4. Data deletion using DELETE.\n"
            "5. Table creation using CREATE."
        ),

        "examples": (
            "Examples of SQL commands:\n\n"
            "1. SELECT - Retrieves data.\n"
            "2. INSERT - Adds new records.\n"
            "3. UPDATE - Modifies records.\n"
            "4. DELETE - Removes records.\n"
            "5. CREATE - Creates database objects."
        )
    }
}


# --------------------------------------------------
# DEMO RESPONSE GENERATOR
# --------------------------------------------------

def demo_response(prompt, conversation_history=None):

    prompt_lower = prompt.lower()

    # Check whether the current question mentions a topic.
    current_topic = detect_topic(prompt)

    # Otherwise, use the previous conversation topic.
    previous_topic = get_previous_topic(conversation_history)

    topic = current_topic or previous_topic

    # Detect follow-up question type.
    intent = detect_follow_up_intent(prompt)

    # Generate contextual response.
    if topic and intent:

        response = CONTEXTUAL_RESPONSES.get(topic, {}).get(intent)

        if response:
            return response

    # Ask AI
    if "user question:" in prompt_lower:

        if current_topic == "Python":
            return (
                "Python is a high-level programming language. "
                "It has simple syntax and is widely used in "
                "web development, automation, data science and AI."
            )

        elif current_topic == "Artificial Intelligence":
            return (
                "Artificial Intelligence (AI) enables machines to "
                "perform tasks that normally require human intelligence, "
                "such as learning, reasoning and problem-solving."
            )

        elif current_topic == "Machine Learning":
            return (
                "Machine Learning is a branch of AI where computers "
                "learn patterns from data and use them to make predictions."
            )

        elif current_topic == "Database":
            return (
                "A database is an organized collection of data. "
                "It helps users store, manage, retrieve and update information."
            )

        elif current_topic == "SQL":
            return (
                "SQL stands for Structured Query Language. "
                "It is used to create, manage and retrieve data "
                "from relational databases."
            )

        return (
            "Demo Response: Your question was received successfully. "
            "Connect a working AI API to receive more detailed responses."
        )

    # Summarize Text
    elif "summarize the following text" in prompt_lower:

        text = prompt.split("Text:", 1)[-1].strip()

        if not text:
            return "Please provide some text to summarize."

        sentences = [
            sentence.strip()
            for sentence in text.replace("\n", " ").split(".")
            if sentence.strip()
        ]

        summary = ". ".join(sentences[:3])

        if summary:
            return "Demo Summary:\n\n" + summary + "."

        return "Please provide valid text to summarize."

    # Generate Content
    elif "generate creative and engaging content" in prompt_lower:

        topic = prompt.split("Topic:", 1)[-1].strip()

        if not topic:
            return "Please enter a topic for content generation."

        return (
            f"Introduction to {topic}\n\n"
            f"{topic} is an interesting subject with many opportunities "
            "for learning and development.\n\n"
            "Importance:\n"
            f"Understanding {topic} helps us explore new ideas, "
            "improve our knowledge and develop creative solutions.\n\n"
            "Conclusion:\n"
            f"{topic} has the potential to create new possibilities "
            "and encourage innovation."
        )

    return "Demo response generated successfully."


# --------------------------------------------------
# MAIN AI FUNCTION WITH CONVERSATION HISTORY
# --------------------------------------------------

def ask_ai(prompt, conversation_history=None):

    global api_available

    # Use Demo Mode when API key is unavailable.
    if client is None:

        api_available = False

        return demo_response(prompt, conversation_history)

    try:

        # Prepare conversation history.
        input_messages = []

        if conversation_history:

            for message in conversation_history:

                role = message.get("role")
                content = message.get("content")

                if role in ["user", "assistant"] and content:

                    input_messages.append({
                        "role": role,
                        "content": content
                    })

        # Add the current user question.
        input_messages.append({
            "role": "user",
            "content": prompt
        })

        # Send conversation to OpenAI API.
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=input_messages
        )

        api_available = True

        return response.output_text

    except Exception as error:

        api_available = False

        print(f"AI API Error: {error}")

        return demo_response(prompt, conversation_history)
