import streamlit as st
from resumix.shared.utils.session_utils import SessionUtils
from resumix.shared.utils.i18n import LANGUAGES
from resumix.backend.rewriter.resume_rewriter import ResumeRewriter
from resumix.shared.utils.llm_client import LLMClient
from resumix.frontend.components.cards.section_render import SectionRender
from loguru import logger
from typing import Dict
from resumix.shared.section.section_base import SectionBase
import traceback


class ComparePage:
    """Page for comparing original vs polished resume content"""
    
    def __init__(self):
        self.T = LANGUAGES[st.session_state.lang]
        self.llm_client = LLMClient()
        self.rewriter = ResumeRewriter(self.llm_client)
        self.section_render = SectionRender()
    
    def check_prerequisites(self):
        """Check if prerequisites are met for comparison"""
        # Check if resume is uploaded
        if not st.session_state.get("resume_text") or not st.session_state.get("resume_sections"):
            return False, "Please upload a resume to use the comparison features."
        
        return True, None
    
    def render_original_section(self, section_name: str, section_obj: SectionBase):
        """Render the original content column"""
        try:
            st.markdown(f"#### {self.T.get('compare', {}).get('original', 'Original')} - {section_name}")
            st.chat_message("user").write("以下是简历中的内容：")
            with st.chat_message("user"):
                # Use original_lines if available, fallback to lines or raw_text
                original_lines = getattr(section_obj, "original_lines", None)
                if original_lines:
                    for line in original_lines:
                        st.markdown(line if line.strip() else "&nbsp;", unsafe_allow_html=True)
                elif hasattr(section_obj, 'lines') and section_obj.lines:
                    for line in section_obj.lines:
                        st.markdown(line if line.strip() else "&nbsp;", unsafe_allow_html=True)
                else:
                    st.markdown(section_obj.raw_text)
        except Exception as e:
            logger.error(f"Failed to render original section {section_name}: {e}")
            st.error(f"Error rendering original section {section_name}")

    def render_polished_section(self, section_name: str, section_obj: SectionBase):
        """Render the polished content column"""
        try:
            st.markdown(f"#### {self.T.get('compare', {}).get('polished', 'Polished')} - {section_name}")
            st.chat_message("assistant").write("这是润色后的内容：")
            
            # Check if section has been rewritten
            if hasattr(section_obj, "rewritten_text") and section_obj.rewritten_text:
                try:
                    # Use SectionRender to render the polished content
                    self.section_render.render_section(section_obj)
                except Exception as e:
                    logger.error(f"Failed to render polished section {section_name}: {e}")
                    st.error(f"❌ 渲染出错：{e}")
                    st.text(traceback.format_exc())
                    # Fallback to raw text
                    with st.chat_message("assistant"):
                        st.markdown(section_obj.rewritten_text)
            else:
                with st.chat_message("assistant"):
                    st.warning("No polished content available for this section")
        except Exception as e:
            logger.error(f"Failed to render polished section {section_name}: {e}")
            st.error(f"Error rendering polished section {section_name}: {str(e)}")

    def render_section_comparison(self, section_name: str, section_obj: SectionBase):
        """Render comparison for a single section"""
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            self.render_original_section(section_name, section_obj)
        with col2:
            self.render_polished_section(section_name, section_obj)

    def perform_section_comparison(self, sections: Dict[str, SectionBase], jd_content: str):
        """Perform the actual comparison logic using ResumeRewriter directly"""
        logger.info("Comparing all resume sections using ResumeRewriter")

        if not sections:
            st.warning("No sections to compare")
            return

        # Process each section
        for section_name, section_obj in sections.items():
            try:
                # Rewrite section if not already rewritten
                if not getattr(section_obj, "rewritten_text", None):
                    with st.spinner(f"正在润色 [{section_name}] 模块..."):
                        try:
                            # Use ResumeRewriter directly
                            self.rewriter.rewrite_section(section_obj, jd_content)
                            logger.info(f"Successfully rewrote section {section_name}")
                        except Exception as e:
                            logger.error(f"Failed to rewrite section {section_name}: {e}")
                            section_obj.rewritten_text = f"Polishing failed: {str(e)}"

                # Render the comparison
                self.render_section_comparison(section_name, section_obj)

            except Exception as e:
                logger.error(f"Failed to process section {section_name}: {e}")
                st.error(f"Failed to process section {section_name}")
                with st.expander(f"Original Content - {section_name}"):
                    st.text(section_obj.raw_text)

    def render(self):
        """Render the compare page"""
        try:
            # Page header
            st.markdown("""
                <div style="text-align: center; margin-bottom: 2rem;">
                    <h1 style="color: #2d3748; margin-bottom: 0.5rem;">🔄 Resume Comparison</h1>
                    <p style="color: #64748b; font-size: 1.1rem;">Compare your original resume with AI-polished versions</p>
                </div>
            """, unsafe_allow_html=True)

            # Check prerequisites
            can_proceed, error_message = self.check_prerequisites()
            if not can_proceed:
                st.warning(error_message)
                st.info("Upload your resume in the sidebar to start comparing.")
                return

            # Get resume sections
            sections = SessionUtils.get_resume_sections()
            
            if not sections:
                st.warning("No resume sections found. Please upload a resume.")
                return

            # Show sections overview
            section_names = list(sections.keys())
            st.info(f"Found {len(sections)} sections to compare: {', '.join(section_names)}")

            # Get JD content
            jd_url = st.session_state.get("jd_url", "")
            if jd_url and jd_url.strip():
                try:
                    jd_content = SessionUtils.get_job_description_content()
                    if isinstance(jd_content, dict):
                        jd_content = str(jd_content)
                    elif jd_content is None:
                        jd_content = "No job description provided"
                    else:
                        jd_content = str(jd_content)
                    
                    st.success("✅ Using job description for tailored comparison")
                except Exception as e:
                    jd_content = f"Job description URL provided: {jd_url} (parsing failed: {str(e)})"
                    st.warning("⚠️ Job description parsing failed, using fallback")
            else:
                jd_content = "No job description provided"
                st.info("💡 Add a job description URL in the sidebar for better tailored comparisons")

            # Show comparison button
            if st.button("🚀 Start Comparison", type="primary", use_container_width=True):
                self.perform_section_comparison(sections, jd_content)

        except Exception as e:
            logger.error(f"Error in compare page: {e}")
            st.error(f"Error in compare page: {e}")
            st.info("Please upload a resume and optionally add a job description URL.")
