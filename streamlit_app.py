
import streamlit as st
from datetime import datetime
import re
import io
import html

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)

from services.ai_service import ask_ai, get_ai_mode

from database.db import (
    init_db,
    create_chat,
    add_message,
    update_message,
    get_chats,
    get_chat_messages,
    save_message_feedback,
    delete_chat,
    clear_chats,
    get_statistics,
    rename_chat
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

init_db()


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def format_timestamp(timestamp):

    if not timestamp:
        return ""

    try:
        date_time = datetime.strptime(
            timestamp,
            "%Y-%m-%d %H:%M:%S"
        )

        return date_time.strftime("%d %b %Y, %I:%M %p")

    except (ValueError, TypeError):
        return str(timestamp)


def load_messages(chat_id):

    database_messages = get_chat_messages(chat_id)

    return [
        {
            "id": message[0],
            "role": message[1],
            "content": message[2],
            "feedback": message[3],
            "created_at": message[4]
        }
        for message in database_messages
    ]


# --------------------------------------------------
# PDF GENERATION
# --------------------------------------------------

def create_conversation_pdf(
    messages,
    title="AI Assistant Conversation"
):

    pdf_buffer = io.BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.75 * inch
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=27,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#243b64"),
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=18
    )

    user_heading_style = ParagraphStyle(
        "UserHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1d4ed8"),
        spaceAfter=5
    )

    assistant_heading_style = ParagraphStyle(
        "AssistantHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#047857"),
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        "MessageBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=15,
        textColor=colors.HexColor("#263238"),
        alignment=TA_LEFT,
        splitLongWords=True
    )

    timestamp_style = ParagraphStyle(
        "Timestamp",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=6
    )

    story = []

    story.append(
        Paragraph(
            html.escape(title),
            title_style
        )
    )

    generated_time = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    story.append(
        Paragraph(
            f"Generated on: {html.escape(generated_time)}",
            subtitle_style
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#dbe3ef"),
            spaceBefore=3,
            spaceAfter=16
        )
    )

    for message in messages:

        role = message.get("role", "user")

        content = str(
            message.get("content", "")
        )

        timestamp = format_timestamp(
            message.get("created_at")
        )

        content = content.encode(
            "latin-1",
            errors="replace"
        ).decode("latin-1")

        escaped_content = html.escape(content)

        escaped_content = escaped_content.replace(
            "\n",
            "<br/>"
        )

        timestamp_text = (
            html.escape(timestamp)
            if timestamp
            else ""
        )

        if role == "user":

            heading = Paragraph(
                "USER QUESTION",
                user_heading_style
            )

            background_color = colors.HexColor("#eff6ff")
            border_color = colors.HexColor("#bfdbfe")

        else:

            heading = Paragraph(
                "AI ASSISTANT RESPONSE",
                assistant_heading_style
            )

            background_color = colors.HexColor("#ecfdf5")
            border_color = colors.HexColor("#a7f3d0")

        message_content = [heading]

        if timestamp_text:

            message_content.append(
                Paragraph(
                    timestamp_text,
                    timestamp_style
                )
            )

        message_content.append(
            Paragraph(
                escaped_content,
                body_style
            )
        )

        message_table = Table(
            [[message_content]],
            colWidths=[6.95 * inch],
            splitByRow=1,
            splitInRow=1
        )

        message_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    background_color
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    border_color
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    12
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    12
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                )
            ])
        )

        story.append(message_table)
        story.append(Spacer(1, 12))

    def draw_page(canvas, doc):

        canvas.saveState()

        page_width, page_height = A4

        canvas.setStrokeColor(
            colors.HexColor("#dbe3ef")
        )

        canvas.setLineWidth(0.6)

        canvas.line(
            0.65 * inch,
            0.55 * inch,
            page_width - 0.65 * inch,
            0.55 * inch
        )

        canvas.setFont(
            "Helvetica",
            8
        )

        canvas.setFillColor(
            colors.HexColor("#64748b")
        )

        canvas.drawString(
            0.65 * inch,
            0.37 * inch,
            "AI Assistant - Conversation Export"
        )

        canvas.drawRightString(
            page_width - 0.65 * inch,
            0.37 * inch,
            f"Page {doc.page}"
        )

        canvas.restoreState()

    document.build(
        story,
        onFirstPage=draw_page,
        onLaterPages=draw_page
    )

    pdf_buffer.seek(0)

    return pdf_buffer.getvalue()


# --------------------------------------------------
# SMART CONVERSATION TITLE GENERATOR
# --------------------------------------------------

def get_chat_title(prompt):

    text = prompt.strip()

    if not text:
        return "New Chat"

    cleaned_text = re.sub(
        r"[^\w\s+#.]",
        " ",
        text
    )

    cleaned_text = re.sub(
        r"\s+",
        " ",
        cleaned_text
    ).strip()

    lower_text = cleaned_text.lower()

    topics = {
        "Python Programming": [
            "python", "list", "tuple", "dictionary",
            "function", "loop", "programming"
        ],
        "Java Programming": [
            "java", "jvm", "class", "object",
            "inheritance", "interface"
        ],
        "Artificial Intelligence": [
            "artificial intelligence", "ai"
        ],
        "Machine Learning": [
            "machine learning", "ml", "training data",
            "prediction model"
        ],
        "Deep Learning": [
            "deep learning", "neural network",
            "cnn", "rnn"
        ],
        "SQL": [
            "sql", "mysql", "database",
            "joins", "query", "queries"
        ],
        "Data Structures": [
            "data structures", "stack", "queue",
            "linked list", "tree", "graph"
        ],
        "Operating Systems": [
            "operating system", "os",
            "process", "thread", "deadlock"
        ],
        "Computer Networks": [
            "computer network", "networking",
            "tcp", "ip address", "http"
        ],
        "Web Development": [
            "html", "css", "javascript",
            "website", "web development"
        ],
        "Generative AI": [
            "generative ai", "genai",
            "large language model", "llm",
            "prompt engineering"
        ],
        "Cloud Computing": [
            "cloud computing", "aws",
            "azure", "cloud"
        ],
        "Cybersecurity": [
            "cybersecurity", "encryption",
            "hacking", "network security"
        ],
        "Data Science": [
            "data science", "data analysis",
            "data analytics"
        ],
        "Internet of Things": [
            "internet of things", "iot",
            "arduino", "raspberry pi"
        ]
    }

    for topic, keywords in topics.items():

        for keyword in keywords:

            pattern = r"\b" + re.escape(keyword) + r"\b"

            if re.search(pattern, lower_text):

                return topic

    stop_words = {
        "what", "is", "are", "the", "a", "an",
        "how", "why", "when", "where", "who",
        "explain", "tell", "me", "about", "please",
        "can", "you", "give", "show", "with",
        "in", "simple", "words", "examples",
        "example", "and", "of", "to", "for"
    }

    words = cleaned_text.split()

    useful_words = [
        word for word in words
        if word.lower() not in stop_words
    ]

    if not useful_words:
        useful_words = words

    title = " ".join(useful_words[:5])

    if len(title) > 40:
        title = title[:40].rsplit(" ", 1)[0]

    return title.title() if title else "New Chat"


# --------------------------------------------------
# PROMPT PREPARATION
# --------------------------------------------------

def prepare_prompt(mode, user_input):

    if mode == "Ask AI":

        return f"User Question: {user_input}"

    elif mode == "Summarize Text":

        return (
            "Summarize the following text in simple and clear language.\n\n"
            f"Text: {user_input}"
        )

    elif mode == "Generate Content":

        return (
            "Generate creative and engaging content about the following topic.\n\n"
            f"Topic: {user_input}"
        )

    return user_input


# --------------------------------------------------
# REGENERATE RESPONSE CALLBACK
# --------------------------------------------------

def regenerate_last_response():

    chat_id = st.session_state.chat_id
    messages = st.session_state.messages

    if chat_id is None or not messages:

        st.session_state.regenerate_error = (
            "No conversation is available to regenerate."
        )

        return

    assistant_index = None

    for index in range(len(messages) - 1, -1, -1):

        if messages[index]["role"] == "assistant":

            assistant_index = index
            break

    if assistant_index is None:

        st.session_state.regenerate_error = (
            "No AI response is available to regenerate."
        )

        return

    user_index = None

    for index in range(assistant_index - 1, -1, -1):

        if messages[index]["role"] == "user":

            user_index = index
            break

    if user_index is None:

        st.session_state.regenerate_error = (
            "The original question could not be found."
        )

        return

    latest_user_message = messages[user_index]

    selected_mode = st.session_state.get(
        "assistant_mode",
        "Ask AI"
    )

    formatted_prompt = prepare_prompt(
        selected_mode,
        latest_user_message["content"]
    )

    conversation_history = messages[:user_index]

    try:

        with st.spinner("🔄 Generating a new response..."):

            new_response = ask_ai(
                formatted_prompt,
                conversation_history=conversation_history
            )

        updated = update_message(
            messages[assistant_index]["id"],
            new_response
        )

        if updated:

            st.session_state.messages = load_messages(chat_id)

            st.session_state.regenerate_success = (
                "A new response was generated successfully!"
            )

            st.session_state.regenerate_error = ""

        else:

            st.session_state.regenerate_error = (
                "Could not update the previous response."
            )

    except Exception as error:

        st.session_state.regenerate_error = (
            "Unable to regenerate the response. Please try again."
        )

        print(f"Regeneration Error: {error}")


# --------------------------------------------------
# NAVIGATION CALLBACKS
# --------------------------------------------------

def start_new_chat():

    st.session_state.chat_id = None
    st.session_state.messages = []
    st.session_state.confirm_clear_current = False
    st.session_state.page = "Chat"
    st.session_state.regenerate_error = ""
    st.session_state.regenerate_success = ""


def open_chat(chat_id):

    st.session_state.chat_id = chat_id
    st.session_state.messages = load_messages(chat_id)
    st.session_state.confirm_clear_current = False
    st.session_state.page = "Chat"
    st.session_state.regenerate_error = ""
    st.session_state.regenerate_success = ""


def save_renamed_chat(chat_id):

    new_title = st.session_state.get(
        f"rename_input_{chat_id}",
        ""
    ).strip()

    if not new_title:

        st.session_state.rename_error = (
            "Conversation title cannot be empty."
        )

        return

    if rename_chat(chat_id, new_title):

        st.session_state.rename_success = (
            "Conversation renamed successfully."
        )

        st.session_state.rename_active = None

    else:

        st.session_state.rename_error = (
            "Unable to rename this conversation."
        )


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "chat_id" not in st.session_state:
    st.session_state.chat_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False

if "confirm_clear_current" not in st.session_state:
    st.session_state.confirm_clear_current = False

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "rename_active" not in st.session_state:
    st.session_state.rename_active = None

if "rename_error" not in st.session_state:
    st.session_state.rename_error = ""

if "rename_success" not in st.session_state:
    st.session_state.rename_success = ""

if "regenerate_error" not in st.session_state:
    st.session_state.regenerate_error = ""

if "regenerate_success" not in st.session_state:
    st.session_state.regenerate_success = ""


# --------------------------------------------------
# CUSTOM CSS - LIGHT THEME FIX
# --------------------------------------------------

st.markdown(
    """
    <style>

    /* MAIN APP */

    .stApp {
        background-color: #f7f9fc !important;
        color: #263238 !important;
    }

    .main .block-container {
        color: #263238 !important;
    }

    /* SIDEBAR */

    [data-testid="stSidebar"] {
        background-color: #eef2f8 !important;
    }

    [data-testid="stSidebar"] * {
        color: #263238;
    }

    [data-testid="stSidebar"] h1 {
        color: #243b64 !important;
    }

    /* TITLES */

    .main-title {
        font-size: 34px;
        font-weight: 700;
        color: #243b64 !important;
    }

    .subtitle {
        color: #64748b !important;
        font-size: 15px;
    }

    /* METRICS */

    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e5eaf2;
        color: #263238 !important;
    }

    [data-testid="stMetric"] * {
        color: #263238 !important;
    }

    /* HEADER AND TOOLBAR */

    [data-testid="stHeader"] {
        background-color: #f7f9fc !important;
    }

    [data-testid="stToolbar"] {
        background-color: #f7f9fc !important;
        color: #263238 !important;
    }

    [data-testid="stDecoration"] {
        background-color: #f7f9fc !important;
    }

    header {
        background-color: #f7f9fc !important;
    }

    /* BOTTOM CHAT INPUT AREA */

    [data-testid="stBottom"] {
        background-color: #f7f9fc !important;
    }

    [data-testid="stBottom"] > div {
        background-color: #f7f9fc !important;
    }

    [data-testid="stChatInput"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
    }

    [data-testid="stChatInput"] > div {
        background-color: #ffffff !important;
    }

    [data-testid="stChatInput"] textarea {
        background-color: #ffffff !important;
        color: #263238 !important;
        -webkit-text-fill-color: #263238 !important;
        caret-color: #263238 !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
    }

    /* TEXT INPUTS */

    input,
    textarea {
        background-color: #ffffff !important;
        color: #263238 !important;
        -webkit-text-fill-color: #263238 !important;
        caret-color: #263238 !important;
    }

    input::placeholder,
    textarea::placeholder {
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
    }

    /* DROPDOWNS */

    [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #263238 !important;
    }

    [data-baseweb="select"] * {
        color: #263238 !important;
    }

    [data-baseweb="popover"] {
        background-color: #ffffff !important;
    }

    [data-baseweb="popover"] * {
        color: #263238 !important;
    }

    [role="listbox"] {
        background-color: #ffffff !important;
    }

    [role="option"] {
        background-color: #ffffff !important;
        color: #263238 !important;
    }

    /* BUTTONS */

    .stButton button,
    .stDownloadButton button {
        background-color: #292724 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border-radius: 8px !important;
        border: 1px solid #292724 !important;
    }

    .stButton button:hover,
    .stDownloadButton button:hover {
        background-color: #41404a !important;
        color: #ffffff !important;
        border-color: #41404a !important;
    }

    .stButton button:disabled {
        background-color: #d1d5db !important;
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
    }

    /* CHAT MESSAGES */

    [data-testid="stChatMessage"] {
        color: #263238 !important;
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        color: #263238 !important;
    }

    /* EXPANDERS */

    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #dbe3ef !important;
        color: #263238 !important;
    }

    [data-testid="stExpander"] summary {
        color: #263238 !important;
    }

    /* CAPTIONS AND LABELS */

    .stCaption,
    [data-testid="stCaptionContainer"] {
        color: #64748b !important;
    }

    label {
        color: #263238 !important;
    }

    /* DIVIDERS */

    hr {
        border-color: #dbe3ef !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("🤖 AI Assistant")

    st.caption("Your personal AI workspace")

    current_mode = get_ai_mode()

    if current_mode == "Live API Mode":
        st.success("🟢 Live API Mode")
    else:
        st.info("🔵 Demo Mode")

    st.divider()

    st.button(
        "➕ New Chat",
        use_container_width=True,
        on_click=start_new_chat
    )

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Chat",
            "Conversation History"
        ],
        key="page"
    )

    st.divider()

    st.subheader("⚙️ Assistant Mode")

    mode = st.selectbox(
        "Choose a feature",
        [
            "Ask AI",
            "Summarize Text",
            "Generate Content"
        ],
        key="assistant_mode"
    )

    st.divider()

    st.subheader("🔍 Search Conversations")

    search_query = st.text_input(
        "Search chats",
        placeholder="Search by title or message..."
    )

    all_chats = get_chats()

    filtered_chats = []

    for chat in all_chats:

        recent_chat_id = chat[0]
        chat_title = chat[1]

        messages = get_chat_messages(recent_chat_id)

        searchable_text = chat_title.lower()

        for message in messages:
            searchable_text += " " + str(message[2]).lower()

        if search_query.lower() in searchable_text:
            filtered_chats.append(chat)

    st.subheader("Recent Conversations")

    if filtered_chats:

        for chat in filtered_chats[:8]:

            recent_chat_id = chat[0]
            recent_chat_title = chat[1]

            st.button(
                f"💬 {recent_chat_title}",
                key=f"recent_chat_{recent_chat_id}",
                use_container_width=True,
                on_click=open_chat,
                args=(recent_chat_id,)
            )

    else:

        st.caption("No conversations found.")


# --------------------------------------------------
# DASHBOARD PAGE
# --------------------------------------------------

if page == "Dashboard":

    st.markdown(
        '<div class="main-title">📊 Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Overview of your AI Assistant usage and activity.</div>',
        unsafe_allow_html=True
    )

    st.write("")

    st.subheader("🤖 AI Operating Mode")

    current_mode = get_ai_mode()

    if current_mode == "Live API Mode":

        st.success(
            "🟢 Live API Mode – Connected successfully"
        )

    else:

        st.info(
            "🔵 Demo Mode – Using predefined responses"
        )

    st.divider()

    stats = get_statistics()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Conversations",
            stats["total_conversations"]
        )

    with col2:
        st.metric(
            "Total Messages",
            stats["total_messages"]
        )

    with col3:
        st.metric(
            "User Questions",
            stats["total_questions"]
        )

    st.write("")

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(
            "Assistant Responses",
            stats["total_responses"]
        )

    with col5:
        st.metric(
            "Helpful Feedback",
            stats["helpful_feedback"]
        )

    with col6:
        st.metric(
            "Not Helpful Feedback",
            stats["not_helpful_feedback"]
        )

    st.divider()

    st.subheader("📈 Feedback Overview")

    feedback_data = {
        "Feedback": [
            "Helpful",
            "Not Helpful"
        ],
        "Count": [
            stats["helpful_feedback"],
            stats["not_helpful_feedback"]
        ]
    }

    st.bar_chart(
        feedback_data,
        x="Feedback",
        y="Count"
    )

    st.divider()

    st.subheader("📌 Quick Overview")

    if stats["total_conversations"] == 0:

        st.info(
            "No conversations yet. Start a new chat to begin!"
        )

    else:

        st.success(
            f"You have started {stats['total_conversations']} "
            f"conversations and exchanged "
            f"{stats['total_messages']} messages."
        )


# --------------------------------------------------
# CHAT PAGE
# --------------------------------------------------

elif page == "Chat":

    st.markdown(
        '<div class="main-title">💬 AI Assistant Chat</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Ask questions, summarize text, or generate content.</div>',
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2 = st.columns([4, 1])

    with col2:

        if st.button(
            "🗑️ Clear Chat",
            use_container_width=True,
            disabled=not bool(st.session_state.messages)
        ):

            st.session_state.confirm_clear_current = True

    if st.session_state.confirm_clear_current:

        st.warning(
            "Are you sure you want to clear this conversation? "
            "It will be removed from Conversation History. "
            "Other conversations will not be affected."
        )

        confirm_col1, confirm_col2 = st.columns(2)

        with confirm_col1:

            if st.button(
                "Yes, Clear Chat",
                type="primary",
                use_container_width=True
            ):

                current_chat_id = st.session_state.chat_id

                if current_chat_id is not None:
                    delete_chat(current_chat_id)

                st.session_state.chat_id = None
                st.session_state.messages = []
                st.session_state.confirm_clear_current = False

                st.rerun()

        with confirm_col2:

            if st.button(
                "Cancel",
                use_container_width=True
            ):

                st.session_state.confirm_clear_current = False

                st.rerun()

    if st.session_state.regenerate_success:

        st.success(st.session_state.regenerate_success)
        st.session_state.regenerate_success = ""

    if st.session_state.regenerate_error:

        st.error(st.session_state.regenerate_error)
        st.session_state.regenerate_error = ""

    st.divider()

    assistant_indexes = [
        index
        for index, item in enumerate(st.session_state.messages)
        if item["role"] == "assistant"
    ]

    latest_assistant_index = (
        assistant_indexes[-1]
        if assistant_indexes
        else -1
    )

    for index, message in enumerate(st.session_state.messages):

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            timestamp = format_timestamp(
                message.get("created_at")
            )

            if timestamp:
                st.caption(timestamp)

            if message["role"] == "user":

                question_pdf = create_conversation_pdf(
                    [message],
                    title="User Question"
                )

                st.download_button(
                    label="📕 Download Question as PDF",
                    data=question_pdf,
                    file_name=f"User_Question_{message['id']}.pdf",
                    mime="application/pdf",
                    key=f"download_user_question_pdf_{message['id']}"
                )

            if message["role"] == "assistant":

                with st.expander("📋 Copy AI Response"):

                    st.code(
                        message["content"],
                        language=None,
                        wrap_lines=True
                    )

                response_filename = (
                    f"AI_Response_{message['id']}.txt"
                )

                st.download_button(
                    label="📄 Download This Response",
                    data=message["content"],
                    file_name=response_filename,
                    mime="text/plain",
                    key=f"download_response_{message['id']}"
                )

                response_pdf_data = create_conversation_pdf(
                    [message],
                    title="AI Assistant Response"
                )

                st.download_button(
                    label="📕 Download Response as PDF",
                    data=response_pdf_data,
                    file_name=f"AI_Response_{message['id']}.pdf",
                    mime="application/pdf",
                    key=f"download_response_pdf_{message['id']}"
                )

                if index == latest_assistant_index:

                    st.button(
                        "🔄 Regenerate Response",
                        key=f"regenerate_{message['id']}",
                        on_click=regenerate_last_response
                    )

    # EXPORT ENTIRE CONVERSATION

    if st.session_state.messages:

        current_chat_title = "AI Assistant Conversation"

        if st.session_state.chat_id is not None:

            for saved_chat in get_chats():

                if saved_chat[0] == st.session_state.chat_id:
                    current_chat_title = saved_chat[1]
                    break

        default_filename = re.sub(
            r"[^A-Za-z0-9 _-]",
            "",
            current_chat_title
        ).strip()

        default_filename = default_filename.replace(" ", "_")

        if not default_filename:
            default_filename = "AI_Assistant_Conversation"

        custom_filename = st.text_input(
            "📁 Choose a filename for your conversation",
            value=default_filename,
            key=f"export_filename_{st.session_state.chat_id or 'new'}"
        )

        safe_filename = re.sub(
            r'[<>:"/\\|?*]',
            "",
            custom_filename
        ).strip().strip(".")

        if not safe_filename:
            safe_filename = default_filename

        safe_filename = safe_filename[:80]

        export_text = f"{current_chat_title}\n"
        export_text += "=" * 40 + "\n\n"

        for message in st.session_state.messages:

            role = message["role"].capitalize()

            timestamp = format_timestamp(
                message.get("created_at")
            )

            export_text += f"{role} ({timestamp}):\n"
            export_text += message["content"] + "\n\n"

        st.download_button(
            label="📥 Export Conversation",
            data=export_text,
            file_name=f"{safe_filename}.txt",
            mime="text/plain",
            key="export_entire_conversation"
        )

        pdf_data = create_conversation_pdf(
            st.session_state.messages,
            title=current_chat_title
        )

        st.download_button(
            label="📄 Download Formatted Conversation PDF",
            data=pdf_data,
            file_name=f"{safe_filename}.pdf",
            mime="application/pdf",
            key="export_conversation_pdf"
        )

    # FEEDBACK

    assistant_messages = [
        message
        for message in st.session_state.messages
        if message["role"] == "assistant"
    ]

    if assistant_messages:

        latest_message = assistant_messages[-1]

        st.divider()

        st.write("Was this response helpful?")

        if latest_message.get("feedback"):

            st.success(
                f"Your feedback: {latest_message['feedback']}"
            )

        else:

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "👍 Helpful",
                    key=f"helpful_{latest_message['id']}"
                ):

                    save_message_feedback(
                        latest_message["id"],
                        "Helpful"
                    )

                    latest_message["feedback"] = "Helpful"

                    st.rerun()

            with col2:

                if st.button(
                    "👎 Not Helpful",
                    key=f"not_helpful_{latest_message['id']}"
                ):

                    save_message_feedback(
                        latest_message["id"],
                        "Not Helpful"
                    )

                    latest_message["feedback"] = "Not Helpful"

                    st.rerun()

    # CHAT INPUT

    placeholders = {
        "Ask AI": "Ask me anything...",
        "Summarize Text": "Paste the text you want to summarize...",
        "Generate Content": "Enter a topic for content generation..."
    }

    user_input = st.chat_input(
        placeholder=placeholders[mode]
    )

    if user_input:

        if st.session_state.chat_id is None:

            title = get_chat_title(user_input)

            st.session_state.chat_id = create_chat(title)

        chat_id = st.session_state.chat_id

        conversation_history = list(
            st.session_state.messages
        )

        add_message(
            chat_id,
            "user",
            user_input
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        formatted_prompt = prepare_prompt(
            mode,
            user_input
        )

        with st.chat_message("assistant"):

            with st.spinner("🤖 AI Assistant is thinking..."):

                try:

                    response = ask_ai(
                        formatted_prompt,
                        conversation_history=conversation_history
                    )

                except Exception as error:

                    response = (
                        "Sorry, something went wrong while generating "
                        "the response. Please try again."
                    )

                    print(f"Assistant Error: {error}")

            st.markdown(response)

            with st.expander("📋 Copy AI Response"):

                st.code(
                    response,
                    language=None,
                    wrap_lines=True
                )

            st.download_button(
                label="📄 Download This Response",
                data=response,
                file_name="AI_Assistant_Response.txt",
                mime="text/plain",
                key="download_new_response"
            )

        add_message(
            chat_id,
            "assistant",
            response
        )

        st.session_state.messages = load_messages(
            chat_id
        )

        st.rerun()


# --------------------------------------------------
# CONVERSATION HISTORY PAGE
# --------------------------------------------------

elif page == "Conversation History":

    st.markdown(
        '<div class="main-title">📚 Conversation History</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">View, reopen, rename, and manage your previous conversations.</div>',
        unsafe_allow_html=True
    )

    st.write("")

    if st.session_state.rename_success:

        st.success(st.session_state.rename_success)
        st.session_state.rename_success = ""

    if st.session_state.rename_error:

        st.error(st.session_state.rename_error)
        st.session_state.rename_error = ""

    chats = get_chats()

    if chats:

        if st.button(
            "🗑️ Clear All Conversations",
            type="secondary"
        ):

            st.session_state.confirm_clear = True

        if st.session_state.confirm_clear:

            st.warning(
                "Are you sure you want to delete all conversations? "
                "This action cannot be undone."
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "Yes, Clear All",
                    type="primary"
                ):

                    clear_chats()

                    st.session_state.chat_id = None
                    st.session_state.messages = []
                    st.session_state.confirm_clear = False
                    st.session_state.confirm_clear_current = False
                    st.session_state.rename_active = None

                    st.success(
                        "All conversations deleted."
                    )

                    st.rerun()

            with col2:

                if st.button("Cancel"):

                    st.session_state.confirm_clear = False

                    st.rerun()

        st.divider()

        for chat in chats:

            chat_id = chat[0]
            chat_title = chat[1]
            created_at = chat[2]

            with st.container():

                col1, col2, col3 = st.columns(
                    [5, 2, 2]
                )

                with col1:

                    st.subheader(
                        f"💬 {chat_title}"
                    )

                    st.caption(
                        f"Created: {format_timestamp(created_at)}"
                    )

                with col2:

                    st.button(
                        "Open Chat",
                        key=f"open_{chat_id}",
                        use_container_width=True,
                        on_click=open_chat,
                        args=(chat_id,)
                    )

                with col3:

                    if st.button(
                        "✏️ Rename",
                        key=f"rename_{chat_id}",
                        use_container_width=True
                    ):

                        if st.session_state.rename_active == chat_id:
                            st.session_state.rename_active = None
                        else:
                            st.session_state.rename_active = chat_id

                        st.session_state.rename_error = ""
                        st.session_state.rename_success = ""

                        st.rerun()

                if st.session_state.rename_active == chat_id:

                    st.text_input(
                        "New conversation title",
                        value=chat_title,
                        key=f"rename_input_{chat_id}"
                    )

                    save_col, cancel_col = st.columns(2)

                    with save_col:

                        st.button(
                            "💾 Save Title",
                            key=f"save_rename_{chat_id}",
                            type="primary",
                            use_container_width=True,
                            on_click=save_renamed_chat,
                            args=(chat_id,)
                        )

                    with cancel_col:

                        if st.button(
                            "Cancel",
                            key=f"cancel_rename_{chat_id}",
                            use_container_width=True
                        ):

                            st.session_state.rename_active = None
                            st.session_state.rename_error = ""

                            st.rerun()

                    if st.session_state.rename_error:

                        st.error(st.session_state.rename_error)

                if st.button(
                    "🗑️ Delete Conversation",
                    key=f"delete_{chat_id}",
                    use_container_width=True
                ):

                    delete_chat(chat_id)

                    if st.session_state.chat_id == chat_id:

                        st.session_state.chat_id = None
                        st.session_state.messages = []

                    if st.session_state.rename_active == chat_id:
                        st.session_state.rename_active = None

                    st.rerun()

                messages = load_messages(chat_id)

                with st.expander("View conversation"):

                    if messages:

                        for message in messages:

                            with st.chat_message(message["role"]):

                                st.markdown(
                                    message["content"]
                                )

                                timestamp = format_timestamp(
                                    message.get("created_at")
                                )

                                if timestamp:
                                    st.caption(timestamp)

                                if (
                                    message["role"] == "assistant"
                                    and message.get("feedback")
                                ):

                                    st.caption(
                                        f"Feedback: {message['feedback']}"
                                    )

                    else:

                        st.caption(
                            "No messages in this conversation."
                        )

                st.divider()

    else:

        st.info(
            "No conversation history available. Start a new chat!"
        )
