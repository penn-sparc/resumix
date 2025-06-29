# file: components/cards/compare_card.py
from streamlit_option_menu import option_menu
import streamlit as st
from loguru import logger
from typing import Dict, Optional
from resumix.section.section_base import SectionBase
from resumix.utils.i18n import LANGUAGES
from resumix.rewriter.resume_rewriter import ResumeRewriter
from resumix.components.cards.section_render import SectionRender
from resumix.components.cards.base_card import BaseCard
import traceback


class CompareCard(BaseCard):
    def __init__(
        self,
        title: str = "Resume Comparison",
        icon: str = "🔄",
        comment: Optional[str] = None,
        additional_content: Optional[str] = None,
    ):
        """
        Initialize a CompareCard for resume original vs polished comparison.
        
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
        self.T = LANGUAGES[st.session_state.lang]
        self.section_renderer = SectionRender()

    def render_original_section(self, section_name: str, section_obj: SectionBase):
        """
        Render the original content column.
        
        Args:
            section_name: Name of the section
            section_obj: SectionBase object containing original content
        """
        try:
            st.markdown(f"#### {self.T['compare']['original']} - {section_name}")
            st.chat_message("user").write(self.T['compare']['original_content'])
            with st.chat_message("user"):
                # Use original_lines if available (dynamically added by parser)
                original_lines = getattr(section_obj, 'original_lines', None)
                if original_lines:
                    for line in original_lines:
                        st.markdown(
                            line if line.strip() else "&nbsp;", unsafe_allow_html=True
                        )
                else:
                    # Fallback to section lines or raw text
                    lines = section_obj.lines or [section_obj.raw_text]
                    for line in lines:
                        st.markdown(
                            line if line.strip() else "&nbsp;", unsafe_allow_html=True
                        )
        except Exception as e:
            logger.error(f"Failed to render original section {section_name}: {e}")
            st.error(f"❌ 无法显示原始内容: {section_name}")

    def render_polished_section(self, section_name: str, section_obj: SectionBase, cached_polish_result: Optional[str] = None):
        """
        Render the polished content column using cached results from polish tab.
        
        Args:
            section_name: Name of the section
            section_obj: SectionBase object containing original content
            cached_polish_result: Cached polish result from the polish tab
        """
        try:
            st.markdown(f"#### {self.T['compare']['polished']} - {section_name}")
            
            if cached_polish_result:
                st.chat_message("assistant").write(self.T['compare']['polished_content'])
                st.chat_message("assistant").write(cached_polish_result)
            else:
                st.warning(self.T['compare']['no_polish_available'])
                st.info(self.T['compare']['switch_to_polish'])
            
        except Exception as e:
            logger.error(f"Failed to render polished section {section_name}: {e}")
            st.error(f"❌ 渲染出错：{e}")
            st.text(traceback.format_exc())

    def render_section_comparison(self, section_name: str, section_obj: SectionBase, cached_polish_results: Dict[str, str]):
        """
        Render comparison for a single section using cached polish results.
        
        Args:
            section_name: Name of the section
            section_obj: SectionBase object to compare
            cached_polish_results: Dictionary of cached polish results from polish tab
        """
        try:
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                self.render_original_section(section_name, section_obj)
                
            with col2:
                cached_result = cached_polish_results.get(section_name)
                self.render_polished_section(section_name, section_obj, cached_result)
                
        except Exception as e:
            logger.error(f"Failed to render comparison for {section_name}: {e}")
            st.error(f"❌ 比较渲染失败: {section_name}")



    def render_sections_overview(self, sections: Dict[str, SectionBase]):
        """Render an overview of sections to be compared"""
        try:
            section_names = list(sections.keys())
            st.info(self.T['compare']['comparing_sections'].format(
                count=len(sections), 
                sections=', '.join(section_names)
            ))
        except Exception as e:
            logger.error(f"Failed to render sections overview: {e}")

    def get_cached_polish_results(self) -> Dict[str, str]:
        """
        Get cached polish results from session state.
        
        Returns:
            Dictionary of cached polish results, empty dict if none found
        """
        # Look for cached polish results in session state
        resume_text = st.session_state.get("resume_text", "")
        if not resume_text:
            return {}
            
        # Generate the same cache key as used in polish_card function
        import hashlib
        text_hash = hashlib.md5(resume_text.encode()).hexdigest()[:8]
        cache_key = f"polish_results_{text_hash}"
        
        return st.session_state.get(cache_key, {})

    def render_comparison_content(
        self,
        sections: Dict[str, SectionBase],
        jd_content: str,
        rewriter: ResumeRewriter,
    ):
        """
        Main comparison rendering logic using cached polish results.
        No longer makes API calls - uses results from polish tab.
        
        Args:
            sections: Dictionary of section names to SectionBase objects
            jd_content: Job description content for context (not used for API calls)
            rewriter: ResumeRewriter instance (not used for API calls)
        """
        logger.info("Comparing all resume sections using cached polish results")
        
        if not sections:
            st.warning("⚠️ No sections available for comparison")
            return
        
        # Get cached polish results
        cached_polish_results = self.get_cached_polish_results()
        
        # Show overview
        self.render_sections_overview(sections)
        
        if not cached_polish_results:
            st.warning(self.T['compare']['no_results_found'])
            st.info(self.T['compare']['polish_tab_info'])
            return
        
        st.success(self.T['compare']['using_cached_results'].format(count=len(cached_polish_results)))
        
        # Process each section
        for section_name, section_obj in sections.items():
            try:
                # Render the comparison using cached results
                self.render_section_comparison(section_name, section_obj, cached_polish_results)
                
            except Exception as e:
                logger.error(f"Failed to process section {section_name}: {e}")
                st.error(f"❌ 处理章节失败: {section_name}")

    def render_card_body(self):
        """
        Render the main compare card content with clean text hierarchy.
        """
        try:
            # Get data from session state
            sections = st.session_state.get("resume_sections", {})
            cached_polish_results = self.get_cached_polish_results()
            
            if not sections:
                st.warning(self.T['compare']['please_upload'])
                return
                
            # Show status of cached polish results
            if cached_polish_results:
                st.success(self.T['compare']['ready_to_compare'].format(count=len(cached_polish_results)))
                st.info("💡 Use the Compare tab to see original vs AI-enhanced resume versions")
            else:
                st.warning(self.T['compare']['no_polish_results'])
                st.info(self.T['compare']['visit_polish_first'])
                
        except Exception as e:
            logger.error(f"Failed to render compare card body: {e}")
            st.error("Could not display comparison interface")

    def render_comment(self):
        """Render the comment section"""
        if self.comment:
            st.markdown(f"*🔄 {self.comment}*")

    def render(self):
        """
        Simple render method using the clean BaseCard structure.
        """
        logger.info("Rendering CompareCard")
        
        # Use the simplified BaseCard render method
        super().render()

    def render_comparison(
        self,
        sections: Dict[str, SectionBase],
        jd_content: str,
        rewriter: ResumeRewriter,
    ):
        """
        Public method to render comparison using cached polish results.
        No longer makes API calls - uses cached results from polish tab.
        
        Args:
            sections: Dictionary of section names to SectionBase objects  
            jd_content: Job description content (not used for API calls)
            rewriter: ResumeRewriter instance (not used for API calls)
        """
        logger.info("Using render_comparison method with cached polish results")
        self.render_comparison_content(sections, jd_content, rewriter)


def compare_resume_sections(
    sections: Dict[str, SectionBase],
    jd_content: str,
    rewriter: ResumeRewriter,
):
    """
    Legacy function wrapper for backward compatibility.
    This maintains the same interface as compare_module.py
    """
    logger.info("Comparing all resume sections using SectionRewriter")
    card = CompareCard(
        comment="Side-by-side comparison of original vs AI-polished content",
        additional_content="Each section is automatically optimized based on the job description"
    )
    card.render()
    card.render_comparison(sections, jd_content, rewriter)
