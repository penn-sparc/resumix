import streamlit as st
from resumix.shared.utils.session_utils import SessionUtils
from resumix.shared.utils.i18n import LANGUAGES
from resumix.backend.rewriter.resume_rewriter import ResumeRewriter
from resumix.shared.utils.llm_client import LLMClient
from resumix.frontend.components.cards.section_render import SectionRender
from loguru import logger
from typing import Dict, List
from resumix.shared.section.section_base import SectionBase
import traceback
import copy


class ComparePage:
    """Page for comparing original vs polished resume content with iterative improvement"""
    
    def __init__(self):
        self.T = LANGUAGES[st.session_state.lang]
        self.llm_client = LLMClient()
        self.rewriter = ResumeRewriter(self.llm_client)
        self.section_render = SectionRender()
        
        # Initialize iterative session state
        if "comparison_session" not in st.session_state:
            st.session_state.comparison_session = {
                "is_iterative_mode": False,
                "jd_content": "",
                "comparison_started": False
            }
    
    def check_prerequisites(self):
        """Check if prerequisites are met for comparison"""
        # Check if resume is uploaded
        if not st.session_state.get("resume_text") or not st.session_state.get("resume_sections"):
            return False, "Please upload a resume to use the comparison features."
        
        return True, None
    
    def reset_comparison_session(self):
        """Reset the comparison session for a new comparison"""
        st.session_state.comparison_session = {
            "is_iterative_mode": False,
            "jd_content": "",
            "comparison_started": False
        }
    
    def render_version_choice_buttons(self, section_name: str, left_version, right_version):
        """Render choice buttons for selecting preferred version"""
        col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
        
        with col1:
            if st.button(f"← Choose Left", key=f"choose_left_{section_name}_{st.session_state.comparison_session.get(f'{section_name}_iterations', 0)}", use_container_width=True):
                return "left"
        
        with col2:
            st.markdown("<div style='text-align: center; padding-top: 0.5rem; font-size: 0.8rem;'>OR</div>", unsafe_allow_html=True)
            
        with col3:
            if st.button(f"Choose Right →", key=f"choose_right_{section_name}_{st.session_state.comparison_session.get(f'{section_name}_iterations', 0)}", use_container_width=True):
                return "right"
        
        with col4:
            if st.session_state.comparison_session.get(f"{section_name}_iterations", 0) > 0:
                if st.button("✅ Done", key=f"done_{section_name}", help="Finish polishing this section"):
                    return "done"
        
        return None

    def handle_section_choice(self, section_name: str, choice: str, left_version, right_version, jd_content: str):
        """Handle user choice for a specific section and generate next iteration"""
        session = st.session_state.comparison_session
        
        if choice == "done":
            # Mark section as completed
            session[f"{section_name}_completed"] = True
            st.success(f"✅ {section_name} polishing completed!")
            st.rerun()
            return
        
        # Determine chosen version
        if choice == "left":
            chosen_version = left_version
            st.success(f"✅ Left version chosen for {section_name}")
        else:
            chosen_version = right_version
            st.success(f"✅ Right version chosen for {section_name}")
        
        # Store the choice
        if f"{section_name}_versions" not in session:
            session[f"{section_name}_versions"] = []
        if f"{section_name}_iterations" not in session:
            session[f"{section_name}_iterations"] = 0
        
        # Add chosen version to history
        session[f"{section_name}_versions"].append(chosen_version)
        session[f"{section_name}_iterations"] += 1
        
        # Generate new polished version based on choice
        new_version = self.perform_iterative_polishing_for_section(section_name, chosen_version, jd_content)
        
        if new_version:
            # Store new version
            session[f"{section_name}_versions"].append(new_version)
            st.success(f"✨ Generated improved version {session[f'{section_name}_iterations'] + 1} for {section_name}")
            st.rerun()

    def perform_iterative_polishing_for_section(self, section_name: str, chosen_version_data, jd_content: str):
        """Perform iterative polishing for a specific section based on user's choice"""
        try:
            # Create a new section object based on the chosen version
            if chosen_version_data == "original":
                # User chose original, get the original section
                sections = SessionUtils.get_resume_sections()
                base_section = sections[section_name]
                base_content = base_section.raw_text
            else:
                # User chose a polished version
                base_section = copy.deepcopy(chosen_version_data["section_obj"])
                base_content = base_section.rewritten_text if hasattr(base_section, 'rewritten_text') else base_section.raw_text
            
            # Create improved prompt for iterative polishing
            iteration = st.session_state.comparison_session.get(f"{section_name}_iterations", 0)
            improved_prompt = f"""
Please further improve and polish this resume section. This is iteration {iteration + 2} for the {section_name} section.

Focus on making this version even better by:
- Enhanced clarity and stronger impact
- More powerful action verbs and quantifiable achievements  
- Improved structure and professional formatting
- More compelling and precise language
- Better keyword optimization for ATS systems

Current content to improve:
{base_content}

Job Description Context (if provided): {jd_content}

Please provide an improved version in the same JSON format, making meaningful enhancements while maintaining the core information.
"""
            
            # Create a temporary section for rewriting
            temp_section = copy.deepcopy(base_section)
            temp_section.raw_text = improved_prompt
            
            # Generate new polished version
            with st.spinner(f"🔄 Generating improved version for {section_name}..."):
                self.rewriter.rewrite_section(temp_section, jd_content)
                logger.info(f"Successfully generated iteration {iteration + 2} for section {section_name}")
                
                # Create version data
                version_data = {
                    "type": f"polished_v{iteration + 2}",
                    "iteration": iteration + 1,
                    "content": temp_section.rewritten_text,
                    "section_obj": temp_section
                }
                
                return version_data
                
        except Exception as e:
            logger.error(f"Failed to perform iterative polishing for section {section_name}: {e}")
            st.error(f"Failed to generate improved version for {section_name}: {str(e)}")
            return None

    def get_section_current_versions(self, section_name: str):
        """Get the current two versions to compare for a specific section"""
        session = st.session_state.comparison_session
        
        if f"{section_name}_versions" not in session:
            return "original", None
        
        versions = session[f"{section_name}_versions"]
        
        if len(versions) == 0:
            return "original", None
        elif len(versions) == 1:
            # First polished version
            return "original", versions[0]
        else:
            # Subsequent iterations: previous chosen vs new polished
            return versions[-2], versions[-1]

    def render_version_section(self, section_name: str, version_data, version_label: str):
        """Render a specific version of a section"""
        try:
            st.markdown(f"#### {version_label} - {section_name}")
            st.chat_message("assistant").write("这是润色后的内容：")
            
            if version_data == "original":
                # Handle original version
                sections = SessionUtils.get_resume_sections()
                if section_name in sections:
                    original_section = sections[section_name]
                    with st.chat_message("assistant"):
                        # Show original content in assistant format for consistency
                        original_lines = getattr(original_section, "original_lines", None)
                        if original_lines:
                            for line in original_lines:
                                st.markdown(line if line.strip() else "&nbsp;", unsafe_allow_html=True)
                        elif hasattr(original_section, 'lines') and original_section.lines:
                            for line in original_section.lines:
                                st.markdown(line if line.strip() else "&nbsp;", unsafe_allow_html=True)
                        else:
                            st.markdown(original_section.raw_text)
            else:
                # Handle polished version
                section_obj = version_data["section_obj"]
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
                        st.warning("No polished content available for this version")
        except Exception as e:
            logger.error(f"Failed to render version section {section_name}: {e}")
            st.error(f"Error rendering section {section_name}: {str(e)}")

    def render_iterative_section_comparison(self, section_name: str, sections: Dict[str, SectionBase], jd_content: str):
        """Render iterative comparison for a single section"""
        session = st.session_state.comparison_session
        
        # Check if section is completed
        if session.get(f"{section_name}_completed", False):
            st.success(f"✅ {section_name} polishing completed!")
            
            # Show final result
            versions = session.get(f"{section_name}_versions", [])
            if versions:
                final_version = versions[-1]
                st.markdown(f"#### ✨ Final Polished Version - {section_name}")
                self.render_version_section(section_name, final_version, "Final Version")
            
            if st.button(f"🔄 Restart {section_name}", key=f"restart_{section_name}"):
                # Reset this section
                session.pop(f"{section_name}_completed", None)
                session.pop(f"{section_name}_versions", None)
                session.pop(f"{section_name}_iterations", None)
                st.rerun()
            return
        
        # Get current versions for this section
        left_version, right_version = self.get_section_current_versions(section_name)
        
        # Initialize first polished version if needed
        if right_version is None:
            original_section = sections[section_name]
            if not getattr(original_section, "rewritten_text", None):
                with st.spinner(f"🔄 Generating first polished version for {section_name}..."):
                    try:
                        self.rewriter.rewrite_section(original_section, jd_content)
                        logger.info(f"Successfully generated first version for section {section_name}")
                    except Exception as e:
                        logger.error(f"Failed to generate first version for section {section_name}: {e}")
                        original_section.rewritten_text = f"Polishing failed: {str(e)}"
            
            # Store the first polished version
            first_version = {
                "type": "polished_v1",
                "iteration": 0,
                "content": original_section.rewritten_text,
                "section_obj": original_section
            }
            
            session[f"{section_name}_versions"] = [first_version]
            session[f"{section_name}_iterations"] = 0
            # Don't return here - continue to show the comparison
            right_version = first_version
        
        # Show iteration info
        iteration = session.get(f"{section_name}_iterations", 0)
        st.info(f"**{section_name}** - Iteration {iteration + 1}")
        
        # Render the two versions
        col1, col2 = st.columns(2)
        
        with col1:
            if left_version == "original":
                label = "📄 Original Version"
                self.render_version_section(section_name, left_version, label)
            else:
                label = f"✨ Chosen Version {left_version['iteration'] + 1}"
                self.render_version_section(section_name, left_version, label)
        
        with col2:
            if right_version:
                label = f"🆕 New Version {right_version['iteration'] + 1}"
                self.render_version_section(section_name, right_version, label)
        
        # Choice buttons
        choice = self.render_version_choice_buttons(section_name, left_version, right_version)
        
        if choice:
            self.handle_section_choice(section_name, choice, left_version, right_version, jd_content)
            # Don't return here - let the normal flow continue after handling the choice

    def perform_section_comparison(self, sections: Dict[str, SectionBase], jd_content: str):
        """Perform section-by-section iterative comparison"""
        logger.info("Starting section-by-section iterative comparison")
        
        if not sections:
            st.warning("No sections to compare")
            return

        session = st.session_state.comparison_session
        session["jd_content"] = jd_content
        session["is_iterative_mode"] = True

        # Render each section individually
        for section_name in sections.keys():
            st.divider()
            st.markdown(f"### 📝 {section_name.replace('_', ' ').title()}")
            
            try:
                self.render_iterative_section_comparison(section_name, sections, jd_content)
            except Exception as e:
                logger.error(f"Failed to render iterative comparison for section {section_name}: {e}")
                st.error(f"Failed to process section {section_name}: {str(e)}")
                with st.expander(f"Original Content - {section_name}"):
                    st.text(sections[section_name].raw_text)
        
        # Show overall progress and control buttons
        st.divider()
        completed_sections = sum(1 for section_name in sections.keys() 
                               if session.get(f"{section_name}_completed", False))
        total_sections = len(sections)
        
        st.markdown(f"### 📊 Overall Progress: {completed_sections}/{total_sections} sections completed")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if completed_sections == total_sections:
                if st.button("🎉 All Sections Complete!", type="primary", use_container_width=True):
                    st.balloons()
                    st.success("🎊 Congratulations! All sections have been polished to your satisfaction!")
        
        with col2:
            if st.button("🗑️ Reset All Sections", use_container_width=True):
                # Reset all sections
                for section_name in sections.keys():
                    session.pop(f"{section_name}_completed", None)
                    session.pop(f"{section_name}_versions", None)
                    session.pop(f"{section_name}_iterations", None)
                st.rerun()

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

            # Add JD URL input section in the Compare tab
            st.markdown("### 🔗 Add a job description to polish your resume")
            
            jd_url = st.text_input(
                "",
                placeholder="Job Description URL",
                key="compare_jd_url",
                help="Optional: Add a job description URL for more tailored resume polishing",
                label_visibility="collapsed"
            )

            # Get JD content based on input
            if jd_url and jd_url.strip():
                try:
                    # Store the URL in session state for SessionUtils
                    st.session_state["jd_url"] = jd_url
                    jd_content = SessionUtils.get_job_description_content()
                    if isinstance(jd_content, dict):
                        jd_content = str(jd_content)
                    elif jd_content is None:
                        jd_content = "No job description provided"
                    else:
                        jd_content = str(jd_content)
                    
                    st.success("✅ Job description loaded successfully!")
                    
                except Exception as e:
                    jd_content = f"Job description URL provided: {jd_url} (parsing failed: {str(e)})"
                    st.warning(f"⚠️ Failed to load job description: {str(e)}")
                    st.info("💡 You can still compare without a job description - comparison will use general improvements")
            else:
                jd_content = "No job description provided"

           
            
            # Check if comparison is already started
            session = st.session_state.comparison_session
            comparison_started = session.get("comparison_started", False)
            
            if not comparison_started:
               
                start_comparison = st.button("🚀 Start Comparison", type="primary", use_container_width=True)
                
                
                    

                if start_comparison:
                    # Mark comparison as started
                    session["comparison_started"] = True
                    session["jd_content"] = jd_content
                    st.rerun()
            else:
                # Show instruction
                st.info("💡 Make your choices below")

            # Show comparison content if started
            if comparison_started:
                stored_jd_content = session.get("jd_content", jd_content)
                self.perform_section_comparison(sections, stored_jd_content)

        except Exception as e:
            logger.error(f"Error in compare page: {e}")
            st.error(f"Error in compare page: {e}")
            st.info("Please upload a resume to use the comparison features.")
