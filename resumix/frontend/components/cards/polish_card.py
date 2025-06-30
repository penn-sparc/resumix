# components/cards/polish_card.py
import streamlit as st
from typing import Callable, Dict, Optional
from resumix.frontend.components.cards.base_card import BaseCard
from resumix.backend.job_parser.resume_parser import ResumeParser
from resumix.shared.utils.logger import logger
from resumix.shared.section.section_base import SectionBase
from resumix.shared.utils.i18n import LANGUAGES


class PolishCard(BaseCard):
    def __init__(
        self,
        title: str = "Resume Polishing",
        icon: str = "✨",
        comment: Optional[str] = None,
        additional_content: Optional[str] = None,
    ):
        """
        Initialize a PolishCard for AI-powered resume polishing.

        Args:
            title: Card title
            icon: Display icon for the card
            comment: Optional comment to display
            additional_content: Optional additional content
        """
        super().__init__(
            title=title,
            icon=icon,
            comment=comment,
            additional_content=additional_content,
        )
        self.parser = ResumeParser()
        self.sections = {}

    def parse_resume_sections(self, text: str) -> Dict[str, SectionBase]:
        """
        Parse the resume text into structured sections.

        Args:
            text: Raw resume text to parse

        Returns:
            Dictionary of section names to SectionBase objects
        """
        try:
            logger.info("Parsing resume text for polishing")
            self.sections = self.parser.parse_resume(text)
            return self.sections
        except Exception as e:
            logger.error(f"Failed to parse resume for polishing: {e}")
            st.error(f"❌ Resume parsing failed: {e}")
            return {}

    def create_polish_prompt(self, section_name: str, section_content: str) -> str:
        """
        Create a polishing prompt for the LLM.

        Args:
            section_name: Name of the resume section
            section_content: Content of the section

        Returns:
            Formatted prompt for polishing
        """
        prompt = f"Please recommend improvements for the following resume section:\n\n{section_content}"
        return prompt

    def render_polish_result(self, result: str):
        """
        Render the polished result from LLM.

        Args:
            result: LLM response with polishing suggestions
        """
        try:
            st.chat_message("Resumix").write(result)
        except Exception as e:
            logger.error(f"Failed to render polish result: {e}")
            st.warning("Could not display polishing result")

    def render_section_polish(
        self, section_name: str, section_obj: SectionBase, llm_model: Callable
    ):
        """
        Render polishing for a single section.

        Args:
            section_name: Name of the section
            section_obj: SectionBase object containing section data
            llm_model: LLM model function for generating suggestions
        """
        try:
            st.subheader(section_name.upper())

            # Get section content
            content = getattr(section_obj, "original_lines", None)
            if content:
                content = "\n".join(content)
            else:
                content = section_obj.raw_text or "\n".join(section_obj.lines)

            T = LANGUAGES[st.session_state.lang]
            with st.spinner(T["polish"]["ai_polishing"].format(section=section_name)):
                prompt = self.create_polish_prompt(section_name, content)
                result = llm_model(prompt)
                self.render_polish_result(result)

        except Exception as e:
            logger.error(f"Failed to polish section {section_name}: {e}")
            st.error(f"❌ Failed to polish {section_name}: {e}")

    def render_sections_overview(self, sections: Dict[str, SectionBase]):
        """Render an overview of sections to be polished"""
        try:

            T = LANGUAGES[st.session_state.lang]
            section_names = list(sections.keys())
            st.info(
                T["polish"]["polishing_sections"].format(
                    count=len(sections), sections=", ".join(section_names)
                )
            )
        except Exception as e:
            logger.error(f"Failed to render sections overview: {e}")

    def render_polishing_content(self, text: str, llm_model: Callable):
        """
        Main polishing rendering logic.
        This incorporates the logic from polish_module.py

        Args:
            text: Resume text to polish
            llm_model: LLM model function for generating suggestions
        """
        logger.info("Handling Resume Polishing with provided resume text")

        # Parse resume sections
        sections = self.parse_resume_sections(text)

        if not sections:
            st.warning("Unable to parse resume sections for polishing.")
            return

        # Show overview
        self.render_sections_overview(sections)
        st.divider()

        # Polish each section
        for section_name, section_obj in sections.items():
            try:
                self.render_section_polish(section_name, section_obj, llm_model)
                st.divider()
            except Exception as e:
                logger.error(f"Failed to process section {section_name}: {e}")
                st.error(f"❌ 处理章节失败: {section_name}")

    def render_tech_stack_selection(self):
        """Render technology stack selection interface"""
        selected_tech_stacks = st.segmented_control(
            "🛠️ 选择你掌握的技术栈",
            options=[
                "PyTorch",
                "TensorFlow",
                "Kubernetes",
                "Docker",
                "Spark",
                "Redis",
                "RabbitMQ",
                "ONNX",
                "Kafka",
                "Elasticsearch",
                "MySQL",
                "PostgreSQL",
                "MongoDB",
            ],
            selection_mode="multi",
        )
        return selected_tech_stacks

    def render_job_position_selection(self):
        """Render job position selection interface"""
        selected_job_positions = st.segmented_control(
            "💼 选择你期望的职位类型",
            options=[
                "Backend",
                "Frontend",
                "Fullstack",
                "DevOps",
                "Data Engineer",
                "Data Scientist",
                "AI Engineer",
                "ML Engineer",
            ],
            selection_mode="multi",
        )
        return selected_job_positions

    def render_options(self):
        """
        Render user option selection interface for polishing preferences.
        """
        try:
            # Technology stack selection
            selected_tech_stacks = self.render_tech_stack_selection()

            # Job position selection
            selected_job_positions = self.render_job_position_selection()

            # Submit button and results
            if st.button("✅ Apply Polishing Preferences"):
                st.success("✅ Polishing preferences applied!")

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🛠️ Focus Tech Stack:")
                    if selected_tech_stacks:
                        for tech in selected_tech_stacks:
                            st.write(f"• {tech}")
                    else:
                        st.write("General polishing")

                with col2:
                    st.subheader("💼 Target Positions:")
                    if selected_job_positions:
                        for position in selected_job_positions:
                            st.write(f"• {position}")
                    else:
                        st.write("General optimization")

        except Exception as e:
            logger.error(f"Failed to render polishing options: {e}")
            st.error("❌ Could not display polishing options")

    def render_card_body(self):
        """
        Render the main polish card content with clean text hierarchy.
        """
        try:
            # Get resume text from session state
            resume_text = st.session_state.get("resume_text", "")

            T = LANGUAGES[st.session_state.lang]

            if not resume_text:
                st.warning(T["polish"]["please_upload"])
                return

            # For the unified approach, we need to handle LLM model differently
            st.info("💡 Use the Polish tab to AI-enhance your resume content")

        except Exception as e:
            logger.error(f"Failed to render polish card body: {e}")
            st.error("Could not display resume polishing interface")

    def render_comment(self):
        """Render the comment section"""
        if self.comment:
            st.markdown(f"*✨ {self.comment}*")

    def render(self):
        """
        Simple render method using the clean BaseCard structure.
        """
        logger.info("Rendering PolishCard")

        # Use the simplified BaseCard render method
        super().render()

    def render_polishing(self, text: str, llm_model: Callable):
        """
        Legacy method for backward compatibility.

        Args:
            text: Resume text to polish
            llm_model: LLM model function for generating suggestions
        """
        logger.info("Using legacy render_polishing method")
        self.render_polishing_content(text, llm_model)

    # Backward compatibility methods
    def redner_options(self):
        """Legacy method with typo - kept for backward compatibility"""
        self.render_options()


def polish_card(text: str, llm_model: Callable):
    """
    Legacy function wrapper for backward compatibility with caching.
    This maintains the same interface as polish_module.py but adds result caching.
    """
    logger.info("Handling Resume Polishing with provided resume text.")

    # Create a unique cache key based on resume text hash
    import hashlib

    text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    cache_key = f"polish_results_{text_hash}"

    # Check if we have cached results for this resume
    if cache_key in st.session_state:
        logger.info("Using cached polishing results")
        st.markdown("### ✨ Resume Polishing")

        T = LANGUAGES[st.session_state.lang]
        st.info(T["polish"]["using_cached"])

        # Display cached results
        cached_results = st.session_state[cache_key]
        for section_name, result in cached_results.items():
            st.subheader(section_name.upper())
            st.chat_message("Resumix").write(result)
            st.divider()
        return

    # If no cache, run the AI polishing and store results
    st.markdown("### ✨ Resume Polishing")

    # Create card and get sections
    card = PolishCard(
        comment="AI-powered resume improvement suggestions",
        additional_content="Each section will be analyzed and optimized by AI",
    )

    # Parse resume sections
    sections = card.parse_resume_sections(text)

    if not sections:
        st.warning("Unable to parse resume sections for polishing.")
        return

    # Show overview
    card.render_sections_overview(sections)
    st.divider()

    # Initialize cache for this session
    polish_results = {}

    # Process each section and cache results
    for section_name, section_obj in sections.items():
        try:
            st.subheader(section_name.upper())

            # Get section content
            content = getattr(section_obj, "original_lines", None)
            if content:
                content = "\n".join(content)
            else:
                content = section_obj.raw_text or "\n".join(section_obj.lines)

            # Create and execute polishing prompt

            T = LANGUAGES[st.session_state.lang]
            with st.spinner(T["polish"]["ai_polishing"].format(section=section_name)):
                prompt = card.create_polish_prompt(section_name, content)
                result = llm_model(prompt)

                # Cache the result
                polish_results[section_name] = result

                # Display the result
                st.chat_message("Resumix").write(result)

            st.divider()

        except Exception as e:
            logger.error(f"Failed to process section {section_name}: {e}")
            st.error(f"❌ 处理章节失败: {section_name}")

    # Store all results in session state
    if polish_results:

        T = LANGUAGES[st.session_state.lang]
        st.session_state[cache_key] = polish_results
        st.success(T["polish"]["results_cached"])

        # Add a button to clear cache and regenerate
        if st.button(
            T["polish"]["regenerate_button"], help=T["polish"]["regenerate_help"]
        ):
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            st.rerun()
