# from paddleocr import PaddleOCR
import streamlit as st
import concurrent.futures
from pathlib import Path

# Initialize session state
if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "resumix_started" not in st.session_state:
    st.session_state.resumix_started = False

import concurrent.futures
from pathlib import Path
from langchain.agents import initialize_agent, AgentType
from resumix.backend.tools.tool import tool_list
from resumix.shared.utils.llm_client import LLMWrapper, LLMClient
from resumix.backend.rewriter.resume_rewriter import ResumeRewriter

from config.config import Config

from streamlit_option_menu import option_menu

# Import card components
from resumix.frontend.components.cards.analysis_card import AnalysisCard
from resumix.frontend.components.cards.polish_card import PolishCard, polish_card
from resumix.frontend.components.cards.agent_card import AgentCard
from resumix.frontend.components.cards.compare_card import CompareCard
from resumix.frontend.components.pages.score_page import ScorePage


# Import utilities
from resumix.shared.utils.llm_client import LLMClient, LLMWrapper
from resumix.shared.utils.session_utils import SessionUtils

from resumix.shared.utils.i18n import LANGUAGES
from loguru import logger
from resumix.config.config import Config
from langchain.agents import initialize_agent, AgentType

# Config setup
CONFIG = Config().config
CURRENT_DIR = Path(__file__).resolve().parent
ASSET_DIR = CURRENT_DIR / "assets" / "logo.png"

T = LANGUAGES[st.session_state.lang]

# Initialize LLM and agent
llm_model = LLMClient()
agent = initialize_agent(
    tools=tool_list,
    llm=LLMWrapper(client=llm_model),
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5,
)

RESUME_REWRITER = ResumeRewriter(llm_model)

# Page configuration
st.set_page_config(
    page_title="RESUMIX",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add styling for sidebar
st.markdown(
    """
<style>
/* Sidebar styling */
.stSidebar .stVerticalBlock .stExpander {
    border-radius: 8px !important;
    margin-bottom: 8px !important;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px 0 rgba(0, 0, 0, 0.03) !important;
    transition: all 0.3s ease !important;
    background-color: white !important;
}

.stSidebar .stVerticalBlock .stExpander:hover {
    box-shadow: 0 2px 6px 0 rgba(0, 0, 0, 0.06), 0 2px 4px 0 rgba(0, 0, 0, 0.04) !important;
    background-color: white !important;
}

.stSidebar .stVerticalBlock .stExpander details {
    border-radius: 8px !important;
    box-shadow: none !important;
    background-color: white !important;
}

.stSidebar .stVerticalBlock .stExpander summary {
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    background-color: white !important;
}

.stSidebar .stVerticalBlock .stExpander summary:hover {
    background-color: white !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
}

.stSidebar .stVerticalBlock .stExpander div[data-testid="stExpanderDetails"] {
    background-color: white !important;
}

/* Add visible border to text input boxes */
.stSidebar input[type="text"] {
    border: 1px solid #d1d5db !important;
    border-radius: 6px !important;
}

.stSidebar input[type="text"]:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1) !important;
}

.stSidebar div[data-testid="stTextInputRootElement"] > div {
    border: 1px solid #d1d5db !important;
    border-radius: 6px !important;
}

.stSidebar div[data-testid="stTextInputRootElement"]:focus-within > div {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1) !important;
}

/* Remove border from file uploader */
.stSidebar .stFileUploader {
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem !important;
}

.stSidebar section[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed #d1d5db !important;
    border-radius: 6px !important;
}

.stSidebar div[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed #d1d5db !important;
    border-radius: 6px !important;
}

.stSidebar .stFileUploader:hover {
    border: none !important;
}

/* Make sidebar widget labels bold */
.stSidebar label[data-testid="stWidgetLabel"] p {
    font-weight: bold !important;
}

.stSidebar div[data-testid="stMarkdownContainer"] p {
    font-weight: bold !important;
}

/* SPECIAL GRADIENT BUTTON FOR START RESUMIX - Updated 2025 */
.start-resumix-button .stButton > button,
.start-resumix-button button[kind="primary"],
.start-resumix-button div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    transform: translateY(0) !important;
    width: 100% !important;
}

.start-resumix-button .stButton > button:hover,
.start-resumix-button button[kind="primary"]:hover,
.start-resumix-button div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
}

.start-resumix-button .stButton > button:active,
.start-resumix-button button[kind="primary"]:active,
.start-resumix-button div[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 10px rgba(102, 126, 234, 0.4) !important;
}

.start-resumix-button .stButton > button:focus,
.start-resumix-button button[kind="primary"]:focus,
.start-resumix-button div[data-testid="stButton"] > button:focus {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    outline: none !important;
}

</style>
""",
    unsafe_allow_html=True,
)

# Sidebar components with guided instructions - MOVED TO TOP
with st.sidebar:
    # Add sidebar title
    st.markdown(
        """
    <div style="text-align: left; padding: 1rem 0 1.5rem 0; margin-bottom: 1rem;">
        <h2 style="font-size: 1.5rem; font-weight: 700; color: #2d3748; margin: 0; font-family: 'Inter', sans-serif;">RESUMIX Setup</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Step 1: Resume upload with instruction
    st.markdown(
        """
    <div style="margin-bottom: 1rem; padding: 0.75rem; background: #f7fafc; border-left: 4px solid #4facfe; border-radius: 4px;">
        <p style="margin: 0; font-weight: 600; color: #2d3748; font-size: 0.9rem;">
            📄 Step 1: Please upload a resume PDF file to get started.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    with st.expander("📄 Upload Resume", expanded=True):
        uploaded_file = st.file_uploader(
            "Select your resume PDF", type=["pdf"], label_visibility="collapsed"
        )
        SessionUtils.upload_resume_file(uploaded_file)

        if uploaded_file:
            st.success("✅ Resume uploaded successfully!")

    # Step 2: Job description with instruction
    st.markdown(
        """
    <div style="margin: 1.5rem 0 1rem 0; padding: 0.75rem; background: #f7fafc; border-left: 4px solid #667eea; border-radius: 4px;">
        <p style="margin: 0; font-weight: 600; color: #2d3748; font-size: 0.9rem;">
            🔗 Step 2: Please enter a job description link for comparison.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    with st.expander("🔗 Job Description", expanded=True):
        jd_url = st.text_input(
            "Job Description URL",
            placeholder="https://example.com/job-description",
            key="jd_url",
            label_visibility="collapsed",
        )

        if jd_url:
            st.success("✅ Job description URL added!")

    # Start Resumix Button
    st.markdown("<br>", unsafe_allow_html=True)

    # Check if user can start (has uploaded resume)
    can_start = uploaded_file is not None

    # Add CSS for gradient button - target by position in sidebar
    st.markdown(
        """
    <style>
    /* Target the Start Resumix button specifically */
    .stSidebar div[data-testid="stVerticalBlock"] > div:nth-last-child(3) button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        width: 100% !important;
    }
    
    .stSidebar div[data-testid="stVerticalBlock"] > div:nth-last-child(3) button[kind="primary"]:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    .stSidebar div[data-testid="stVerticalBlock"] > div:nth-last-child(3) button[kind="primary"]:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.4) !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Single button with conditional behavior
    if can_start:
        if st.button("🚀 Start Resumix", type="primary", use_container_width=True):
            st.session_state.resumix_started = True
            st.rerun()
    else:
        st.button(
            "🚀 Start Resumix",
            disabled=True,
            use_container_width=True,
            help="Please upload a resume first",
        )

    # Divider
    st.markdown("---")

    # Additional options (collapsed by default)
    with st.expander("⚙️ Advanced Settings", expanded=False):
        # Authentication
        if not st.session_state.get("authenticated"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if username == "admin" and password == "123456":
                    st.session_state.authenticated = True
                    st.success("✅ Logged in successfully!")
        else:
            st.success("✅ Logged in")
            if st.button("Logout"):
                st.session_state.authenticated = False

        # Language selection
        selected_lang = st.selectbox(
            "Language",
            ["en", "zh"],
            index=["en", "zh"].index(st.session_state.lang),
        )
        if selected_lang != st.session_state.lang:
            st.session_state.lang = selected_lang
            st.rerun()

# Main content area - show welcome or cards based on state
if not st.session_state.resumix_started:
    # Show welcome screen with logo and instructions
    st.markdown(
        """
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; text-align: center;">
            <div style="font-size: 5rem; margin-bottom: 1rem;">📄</div>
            <h1 style="font-size: 3rem; font-weight: 700; color: #2d3748; margin: 0; font-family: 'Inter', sans-serif;">RESUMIX</h1>
            <p style="font-size: 1.2rem; color: #64748b; margin: 1rem 0 2rem 0; max-width: 600px; line-height: 1.6;">
                Your AI-powered resume enhancement platform. Upload your resume and get started with intelligent analysis, polishing, and optimization.
            </p>
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-top: 1rem;">
                <p style="margin: 0; font-weight: 500;">👈 Follow the steps in the sidebar to get started</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # Show the main application interface
    # Clean interface - no header, just tabs and content

    # Main navigation
    tab_names = T["tabs"]

    # Auto-select first tab (Analysis) when user starts Resumix
    if "selected_tab_index" not in st.session_state:
        st.session_state.selected_tab_index = 0

    selected_tab = option_menu(
        menu_title=None,
        options=tab_names,
        icons=["file-text", "pencil", "robot", "bar-chart", "file-earmark-break"],
        orientation="horizontal",
        default_index=st.session_state.selected_tab_index,
    )

    # NOW uploaded_file is available from the sidebar processing above
    if uploaded_file:
        # Initialize session data if not exists
        if "resume_text" not in st.session_state:
            st.session_state.resume_text = SessionUtils.get_resume_text()

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

        # Background section extraction (non-blocking)
        if "resume_sections" not in st.session_state:
            try:
                st.session_state.resume_sections = SessionUtils.get_resume_sections()
                logger.info("[Backend] Resume section extraction completed")
            except Exception as e:
                logger.warning(f"[Backend] Resume section extraction failed: {e}")

        text = st.session_state.resume_text
        STRUCTED_SECTIONS = SessionUtils.get_resume_sections()

        # Handle JD content gracefully (optional for auto-parsing)
        jd_url = st.session_state.get("jd_url", "")
        if jd_url and jd_url.strip():
            try:
                jd_content = SessionUtils.get_job_description_content()
            except Exception as e:
                # JD parsing failed, use fallback
                jd_content = f"Job description URL provided: {jd_url} (parsing failed)"
        else:
            # No JD URL provided, use default
            jd_content = "No job description provided"

        # Tab routing with container styling
        if selected_tab == tab_names[0]:  # Analysis
            with st.container():
                analysis_card = AnalysisCard()
                analysis_card.render()

        elif selected_tab == tab_names[1]:  # Polish
            with st.container():
                polish_card(text, llm_model)

        elif selected_tab == tab_names[2]:  # Agent
            with st.container():
                agent_card = AgentCard()
                agent_card.set_sections(STRUCTED_SECTIONS)
                agent_card.render()

        elif selected_tab == tab_names[3]:  # Score
            with st.container():
                score_page = ScorePage()
                score_page.render()

        elif selected_tab == tab_names[4]:  # Compare
            with st.container():
                compare_card = CompareCard()
                compare_card.render()

                # Handle different types of jd_content
                if isinstance(jd_content, dict):
                    jd_content_str = str(jd_content)
                elif jd_content is None:
                    jd_content_str = "No job description provided"
                else:
                    jd_content_str = str(jd_content)

                compare_card.render_comparison(
                    STRUCTED_SECTIONS, jd_content_str, RESUME_REWRITER
                )
    else:
        # Show message that resume is needed
        st.markdown(
            """
            <div style="text-align: center; margin-top: 4rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>
                <p style="color: #94a3b8;">Upload your resume in the sidebar to start using the AI-powered features.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
