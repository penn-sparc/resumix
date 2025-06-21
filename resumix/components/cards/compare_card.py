# file: components/cards/compare_card.py
from streamlit_option_menu import option_menu
import streamlit as st
from loguru import logger
from typing import Dict, Optional, Callable
from resumix.section.section_base import SectionBase
from resumix.utils.i18n import LANGUAGES
from job_parser.resume_rewriter import ResumeRewriter
from components.cards.section_render import SectionRender
from components.cards.base_card import BaseCard
from typing import Optional 


class CompareCard(BaseCard):
    def __init__(
        self,
        title: str = "Resume Comparison",
        icon: str = "🔄",
        comment: Optional[str] = None,
        additional_content: Optional[str] = None,
    ):
        super().__init__(
            title=title,
            icon=icon,
            comment=comment,
            additional_content=additional_content
        )
        self.T = LANGUAGES.get(st.session_state.get('lang', 'en'), LANGUAGES['en'])
        self.section_render = SectionRender()
        
    def render_original_section(self, section_name: str, section_obj: SectionBase):
        """Render the original content column with enhanced formatting"""
        with st.container():
            st.markdown(f"##### ✍️ {self.T['compare'].get('original', 'Original')}")
            with st.chat_message("user"):
                st.caption(f"Section: {section_name}")
                for line in section_obj.original_lines:
                    st.markdown(line if line.strip() else "<br>", unsafe_allow_html=True)
    
    def render_polished_section(self, section_name: str, section_obj: SectionBase):
        """Render the polished content with error handling"""
        with st.container():
            st.markdown(f"##### ✨ {self.T['compare'].get('polished', 'Polished')}")
            with st.chat_message("assistant"):
                st.caption(f"Optimized: {section_name}")
                try:
                    if not hasattr(section_obj, 'rewritten_text') or not section_obj.rewritten_text:
                        st.warning("No optimized version available")
                    else:
                        self.section_render.render_section(section_obj)
                except Exception as e:
                    st.error(f"Rendering error: {str(e)}")
                    if hasattr(section_obj, 'rewritten_text'):
                        st.write(section_obj.rewritten_text)
    
    def render_section_comparison(self, section_name: str, section_obj: SectionBase):
        """Render comparison with tabs for better UX"""
        tab1, tab2 = st.tabs([
            f"Original {section_name}",
            f"Optimized {section_name}"
        ])
        
        with tab1:
            self.render_original_section(section_name, section_obj)
        with tab2:
            self.render_polished_section(section_name, section_obj)
        st.divider()
    
    def render_comparison(
        self,
        sections: Dict[str, SectionBase],
        jd_content: str,
        rewriter: ResumeRewriter,
    ):
        """Main comparison logic with progress tracking"""
        try:
            if not sections:
                st.warning("No resume sections provided for comparison")
                return
                
            st.subheader("🔍 Resume Comparison Tool")
            
            # Show job description context
            with st.expander("View Job Description Context", expanded=False):
                st.write(jd_content[:1000] + ("..." if len(jd_content) > 1000 else ""))
            
            progress_bar = st.progress(0)
            total_sections = len(sections)
            
            for i, (section_name, section_obj) in enumerate(sections.items()):
                # Ensure section is rewritten
                if not getattr(section_obj, "rewritten_text", None):
                    with st.spinner(f"Optimizing {section_name}..."):
                        rewriter.rewrite_section(section_obj, jd_content)
                
                self.render_section_comparison(section_name, section_obj)
                progress_bar.progress((i + 1) / total_sections)
                
            st.success("✅ Comparison completed!")
            
        except Exception as e:
            logger.error(f"Comparison error: {str(e)}")
            st.error(f"Comparison failed: {str(e)}")
    
    def render(self):
        """Complete implementation of abstract render method"""
        self.render_header()
        
        if self.comment:
            with st.container():
                st.caption(self.comment)
                
        if self.additional_content:
            self.render_additional()
        
        return self  # Enable method chaining


def compare_resume_sections(
    sections: Dict[str, SectionBase],
    jd_content: str,
    rewriter: ResumeRewriter,
) -> CompareCard:
    """Modernized interface for resume comparison
    
    Args:
        sections: Dictionary of resume sections
        jd_content: Job description text
        rewriter: ResumeRewriter instance
        
    Returns:
        CompareCard instance for method chaining
    """
    logger.info("Initializing resume comparison")
    card = CompareCard(
        comment="Compare original and optimized resume sections",
        additional_content="Powered by Resumix AI"
    )
    return card.render().render_comparison(sections, jd_content, rewriter)