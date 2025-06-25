# components/cards/polish_card.py
import streamlit as st
from typing import Callable, Dict, Optional
from components.cards.base_card import BaseCard
from job_parser.resume_parser import ResumeParser
from utils.logger import logger
from typing import Callable, Dict
from components.cards.base_card import BaseCard
from typing import Optional


class PolishCard(BaseCard):
    def __init__(
        self,
        title: str = "Resume Polishing",
        icon: str = "✨",
        comment: Optional[str] = None,
        additional_content: Optional[str] = None,
    ):
        super().__init__(
            title=title,
            icon=icon,
            comment=comment,
            additional_content=additional_content,
        )
        self.parser = ResumeParser()

    def render_polish_result(self, result: str):
        """Render the polished result from LLM"""
        st.chat_message("Resumix").write(result)

    def render_section_polish(self, section: str, content: str, llm_model: Callable):
        """Render polishing for a single section"""
        prompt = f"Please recommend improvements for the following resume section:\n\n{content}"
        result = llm_model(prompt)
        self.render_polish_result(result)

    def render_polishing(self, text: str, llm_model: Callable):
        """Main polishing rendering logic"""
        logger.info("Polishing all resume sections using LLM")
        sections = self.parser.parse_resume(text)

        for section, content in sections.items():
            st.subheader(section)
            self.render_section_polish(section, content, llm_model)
            st.divider()

    def redner_options(self):

        # 技术栈多选
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
                "PyTorch",
                "TensorFlow",
                "Kubernetes",
                "Docker",
                "Spark",
                "Redis",
                "RabbitMQ",
                "Kafka",
                "Elasticsearch",
                "MySQL",
                "PostgreSQL",
                "MongoDB",
                "Redis",
                "RabbitMQ",
            ],
            selection_mode="multi",
        )

        # 职位多选
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

        # 提交按钮
        if st.button("✅ Submit"):
            st.subheader("你选择的技术栈：")
            st.write(selected_tech_stacks)

            st.subheader("你期望的职位：")
            st.write(selected_job_positions)

    def render(self):
        """Full card rendering implementation"""
        self.render_header()
        
        if self.comment:
            with st.container():
                st.caption(self.comment)
                
        if self.additional_content:
            self.render_additional()
        
        return self  # Enable method chaining


def polish_card(text: str, llm_model: Callable):
    """Modernized legacy function wrapper"""
    logger.info("Initializing resume polishing")
    card = PolishCard(
        comment="AI-powered resume improvements",
        additional_content="Suggestions provided by Resumix AI"
    )
    return card.render().render_polishing(text, llm_model)