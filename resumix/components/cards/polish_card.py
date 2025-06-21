# components/cards/polish_card.py
import streamlit as st
from typing import Callable, Dict, Optional
from components.cards.base_card import BaseCard
from job_parser.resume_parser import ResumeParser
from utils.logger import logger

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
            additional_content=additional_content
        )
        self.parser = ResumeParser()
        
    def render_polish_result(self, result: str):
        """Render the polished result from LLM with improved formatting"""
        with st.chat_message("Resumix"):
            st.markdown("**Improved Version:**")
            st.write(result)
            st.markdown("---")
    
    def render_section_polish(self, section: str, content: str, llm_model: Callable):
        """Render polishing for a single section with loading state"""
        with st.expander(f"🔧 Improve {section}", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Original:**")
                st.write(content)
            
            with col2:
                with st.spinner(f"Polishing {section}..."):
                    prompt = f"""Improve this resume section while maintaining its original meaning.
                    Return only the improved version without additional commentary.
                    
                    Section: {section}
                    Content: {content}"""
                    
                    result = llm_model(prompt)
                    self.render_polish_result(result)
    
    def render_polishing(
        self,
        text: str,
        llm_model: Callable
    ):
        """Main polishing rendering logic with error handling"""
        try:
            logger.info("Starting resume polishing")
            
            if not text.strip():
                st.warning("Please provide resume content to polish")
                return
                
            sections = self.parser.parse_resume(text)
            
            if not sections:
                st.error("Could not parse any sections from the resume")
                return
                
            progress_bar = st.progress(0)
            total_sections = len(sections)
            
            for i, (section, content) in enumerate(sections.items()):
                self.render_section_polish(section, content, llm_model)
                progress_bar.progress((i + 1) / total_sections)
                
            st.success("Polish complete!")
            
        except Exception as e:
            logger.error(f"Polishing failed: {str(e)}")
            st.error(f"An error occurred during polishing: {str(e)}")
    
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