# file: components/cards/analysis_card.py
import streamlit as st
from typing import Dict
from components.cards.base_card import BaseCard
from typing import Optional 
from resumix.job_parser.resume_parser import ResumeParser
from resumix.utils.logger import logger

class AnalysisCard(BaseCard):
    def __init__(
        self,
        title: str = "Resume Analysis",
        icon: str = "📄",
        comment: Optional[str] = None,
        additional_content: Optional[str] = None,
    ):
        super().__init__(
            title=title,
            icon=icon,
            comment=comment,
            additional_content=additional_content
        )
        self.parser = ResumeParser()  # Make sure this is properly imported
        
    def render_section_content(self, section: str, content: str):
        with st.expander(section.upper()):
            st.write(content)
    
    def render_analysis(self, text: str):
        try:
            sections = self.parser.parse_resume(text)
            if not sections:
                st.warning("No sections could be parsed from the resume")
                return
                
            for section, content in sections.items():
                self.render_section_content(section, content)
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
    
    def render(self):  # Properly implement the abstract method
        self.render_header()
        if self.comment:
            st.caption(self.comment)
        return self  # Allows method chaining


def analysis_card(text: str):
    """Modernized legacy function wrapper"""
    logger.info("Initializing resume analysis")
    card = AnalysisCard(
        comment="AI-powered resume analysis",
        additional_content="Detailed breakdown of your resume sections"
    )
    return card.render().render_analysis(text)
    