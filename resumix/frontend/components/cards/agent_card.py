import streamlit as st
from typing import Dict, Optional
from resumix.frontend.components.cards.base_card import BaseCard
from resumix.backend.job_parser.resume_parser import ResumeParser
from resumix.shared.utils.logger import logger
from resumix.shared.section.section_base import SectionBase
from resumix.frontend.api.api import process_section_api

from typing import List, Tuple
from resumix.config.config import Config

CONFIG = Config().config


class AgentCard(BaseCard):
    def __init__(
        self,
        title: str = "Resume Polisher",
        icon: str = "🤖",
        comment: Optional[str] = None,
        additional_content: Optional[str] = None,
    ):
        """
        Initialize an AgentCard for AI-powered resume optimization.

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

    def set_sections(self, sections: Dict[str, SectionBase]):
        self.sections = sections

    def _render_tech_stack_selection(self):
        """Render technology stack selection interface"""
        selected_tech_stacks = st.segmented_control(
            "🛠️ Select the technology stack directions you want to refine",
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

    def _render_job_position_selection(self):
        """Render job position selection interface"""
        selected_job_positions = st.segmented_control(
            "💼 Select your preferred job positions",
            options=[
                "Backend",
                "Frontend",
                "Fullstack",
                "DevOps",
                "Data Engineer",
                "Data Scientist",
                "AI Engineer",
                "ML Engineer",
                "Game Developer",
                "Product Manager",
            ],
            selection_mode="multi",
        )
        return selected_job_positions

    def _render_options(self) -> Tuple[List[str], List[str]]:
        """
        Render user option selection interface.
        This replaces the misspelled 'redner_options' method.
        """
        try:
            # Technology stack selection
            selected_tech_stacks = self._render_tech_stack_selection()

            # Job position selection
            selected_job_positions = self._render_job_position_selection()

            return selected_tech_stacks, selected_job_positions

        except Exception as e:
            logger.error(f"Failed to render options: {e}")
            return [], []

    def render_card_body(self):
        """
        Render the main agent card content with clean text hierarchy.
        """
        pass

    def process(
        self,
        sections: Dict[str, SectionBase],
        tech_stacks: List[str],
        job_positions: List[str],
    ):
        selected_sections = ["experience", "projects"]
        for section in sections.values():
            logger.info(f"Processing section: {section.name}")
            if section.name in selected_sections:
                logger.info(f"Start process: {section.name}")
                self.process_section(section, tech_stacks, job_positions)
                st.divider()

    def process_section(
        self, section: SectionBase, tech_stacks: List[str], job_positions: List[str]
    ):
        with st.spinner(f"AI is optimizing {section.name}..."):
            result = process_section_api(section, tech_stacks, job_positions)
            rewritten_text = result["rewritten_text"]
            st.chat_message("Resumix").write(rewritten_text)

    def render(self):
        """
        Simple render method using the clean BaseCard structure.
        """
        logger.info("Rendering AgentCard")

        # Use the simplified BaseCard render method
        super().render()

        tech_stacks, job_positions = self._render_options()

        with st.form("agent_process_form", clear_on_submit=False):
            submitted = st.form_submit_button(
                "Start Process", type="primary", use_container_width=True
            )

        if submitted:
            with st.spinner("Processing..."):
                logger.info(type(self.sections))
                self.process(self.sections, tech_stacks, job_positions)
            st.success("Success ✅")


def agent_card(text: str):
    """
    Legacy function wrapper for backward compatibility.
    This maintains the same interface as agent_module.py
    """
    logger.info("Handling Resume Agent with provided resume text.")
    card = AgentCard(
        comment="AI-powered resume optimization assistant",
        additional_content="Select your preferences and let AI optimize your resume",
    )
    card.render()


def handle_agent(text: str, jd_content: str, agent):
    """
    Legacy function wrapper for backward compatibility.
    This maintains the same interface as agent_module.py
    """
    logger.info(
        "Handling AI Agent with provided resume text and job description content."
    )
    card = AgentCard(
        comment="AI-powered resume optimization in progress",
        additional_content="Each section will be optimized based on the job description",
    )
    card.render()
    card.render_agent_interaction(text, jd_content, agent)
