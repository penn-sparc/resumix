# from paddleocr import PaddleOCR
import streamlit as st
import concurrent.futures
from pathlib import Path

# Initialize session state
if "lang" not in st.session_state:
    st.session_state.lang = "en"

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
from resumix.frontend.components.cards.score_card import ScoreCard
from resumix.frontend.components.cards.compare_card import CompareCard

# Import utilities
from resumix.shared.utils.llm_client import LLMClient, LLMWrapper
from resumix.shared.utils.session_utils import SessionUtils

from resumix.shared.utils.i18n import LANGUAGES
from resumix.backend.job_parser.resume_rewriter import ResumeRewriter
from resumix.shared.utils.logger import logger
from resumix.frontend.components.score_page import ScorePage
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

# Header section with logo and name
# st.markdown(
#     """
# <div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem; border-bottom: 1px solid #e2e8f0;">
#     <h1 style="font-size: 2.5rem; font-weight: 700; color: #1e293b; margin: 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">📄 RESUMIX</h1>
#     <p style="color: #64748b; font-size: 1rem; margin-top: 0.5rem; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">Hi, I'm your resume AI assistant !</p>
# </div>
# """,
#     unsafe_allow_html=True,
# )

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


</style>
""",
    unsafe_allow_html=True,
)

# Main navigation
tab_names = T["tabs"]
selected_tab = option_menu(
    menu_title=None,
    options=tab_names,
    icons=["file-text", "pencil", "robot", "bar-chart", "file-earmark-break"],
    orientation="horizontal",
)

# Sidebar components
with st.sidebar:
    # Add sidebar title
    st.markdown(
        """
    <div style="text-align: left; padding: 1rem 0 1.5rem 0; margin-bottom: 1rem;">
        <h2 style="font-size: 1.5rem; font-weight: 700; color: #1e293b; margin: 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">RESUMIX</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Resume upload
    with st.expander(T["upload_resume"], expanded=True):
        uploaded_file = st.file_uploader(T["upload_resume_title"], type=["pdf"])
        SessionUtils.upload_resume_file(uploaded_file)

    # Job description
    with st.expander(T["job_description"], expanded=True):
        jd_url = st.text_input(
            T["job_description_title"],
            placeholder="https://example.com/job-description",
            key="jd_url",
        )

    # Authentication
    with st.expander(T["user_login"], expanded=False):
        if not st.session_state.get("authenticated"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button(T["login_button"]):
                if username == "admin" and password == "123456":
                    st.session_state.authenticated = True
                    st.success(T["login_success"])
        else:
            st.success(T["logged_in"])
            if st.button(T["logout"]):
                st.session_state.authenticated = False

    # Language selection
    with st.expander(T["language"], expanded=False):
        selected_lang = st.selectbox(
            "Global",
            ["en", "zh"],
            index=["en", "zh"].index(st.session_state.lang),
        )
        if selected_lang != st.session_state.lang:
            st.session_state.lang = selected_lang
            st.rerun()


def prefetch_resume_sections():
    try:
        st.session_state.resume_sections = SessionUtils.get_resume_sections()
        logger.info("[后台] Resume section 提取完成")
    except Exception as e:
        logger.warning(f"[后台] 提取 resume_sections 失败: {e}")


def prefetch_jd_sections():
    try:
        st.session_state.jd_sections = SessionUtils.get_jd_sections()
        logger.info("[后台] JD section 提取完成")
    except Exception as e:
        logger.warning(f"[后台] 提取 jd_sections 失败: {e}")


if uploaded_file:
    # Initialize session data if not exists
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = SessionUtils.get_resume_text()

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

    # Background section extraction (non-blocking)
    if "resume_sections" not in st.session_state:
        executor.submit(prefetch_resume_sections)

    text = st.session_state.resume_text
    STRUCTED_SECTIONS = SessionUtils.get_resume_sections()
    jd_content = SessionUtils.get_job_description_content()

    # Tab routing with proper isolation to prevent cross-tab bleeding
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

            education_and_experience_sections = {}
            for section_name, section_obj in STRUCTED_SECTIONS.items():
                logger.info(f"Processing section: {section_name}")
                if section_name in ["education", "projects", "experience"]:
                    logger.info(f"Processing section: {section_name}")
                    education_and_experience_sections[section_name] = section_obj

            agent_card.set_sections(education_and_experience_sections)
            agent_card.render()
            # agent_card.render_options()
            # agent_card.render_agent_interaction(text, jd_content, agent)

    elif selected_tab == tab_names[3]:  # Score
        with st.container():
            ScorePage().render()
            # Alternatively, using ScoreCard for each section:
            # for section_name in STRUCTED_SECTIONS.keys():
            #     score_card = ScoreCard(section_name, sample_scores)
            #     score_card.render()

    elif selected_tab == tab_names[4]:  # Compare
        with st.container():
            compare_card = CompareCard()
            compare_card.render()
            compare_card.render_comparison(
                STRUCTED_SECTIONS, jd_content, RESUME_REWRITER
            )
else:
    st.info(T["please_upload"])
