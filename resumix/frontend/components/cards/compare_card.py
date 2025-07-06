# file: components/cards/compare_card.py
from streamlit_option_menu import option_menu
import streamlit as st
from loguru import logger
from typing import Dict, Optional
import json
import re
from resumix.shared.section.section_base import SectionBase
from resumix.shared.utils.i18n import LANGUAGES
from resumix.backend.rewriter.resume_rewriter import ResumeRewriter
from resumix.frontend.components.cards.section_render import SectionRender
from resumix.frontend.components.cards.base_card import BaseCard
import traceback


class CompareCard(BaseCard):
    def __init__(
        self,
        title: str = "Resume Compare",
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

    def parse_final_answer_json(self, text: str) -> Dict:
        """
        Parse the "Final Answer:" JSON response from LLM.
        
        Args:
            text: Raw text containing "Final Answer:" JSON
            
        Returns:
            Dict containing parsed JSON data
        """
        try:
            logger.info(f"🔍 Debug: Parsing text: {text[:200]}...")
            
            # Method 1: Extract JSON part after "Final Answer:"
            if "Final Answer:" in text:
                json_part = text.split("Final Answer:")[-1].strip()
                logger.info(f"🔍 Debug: JSON part after 'Final Answer:': {json_part[:200]}...")
                
                # Clean up the JSON string
                json_part = json_part.strip()
                if json_part.startswith('"') and json_part.endswith('"'):
                    json_part = json_part[1:-1]  # Remove surrounding quotes
                
                # Parse JSON
                parsed_data = json.loads(json_part)
                logger.info(f"🔍 Debug: Successfully parsed JSON: {parsed_data}")
                return parsed_data
                
            # Method 2: Look for JSON block in ```json format
            elif "```json" in text:
                json_match = re.search(r'```json\s*\n(.*?)\n```', text, re.DOTALL)
                if json_match:
                    json_part = json_match.group(1).strip()
                    logger.info(f"🔍 Debug: JSON from ```json block: {json_part[:200]}...")
                    parsed_data = json.loads(json_part)
                    logger.info(f"🔍 Debug: Successfully parsed JSON from block: {parsed_data}")
                    return parsed_data
                    
            # Method 3: Look for any JSON object in the text
            elif "{" in text and "}" in text:
                # Find the first complete JSON object
                brace_count = 0
                start_idx = text.find("{")
                if start_idx != -1:
                    for i, char in enumerate(text[start_idx:], start_idx):
                        if char == "{":
                            brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                json_part = text[start_idx:i+1]
                                logger.info(f"🔍 Debug: JSON object found: {json_part[:200]}...")
                                parsed_data = json.loads(json_part)
                                logger.info(f"🔍 Debug: Successfully parsed JSON object: {parsed_data}")
                                return parsed_data
                
            # Method 4: Try to parse the entire text as JSON
            else:
                logger.info(f"🔍 Debug: Trying to parse entire text as JSON")
                parsed_data = json.loads(text)
                logger.info(f"🔍 Debug: Successfully parsed entire text as JSON: {parsed_data}")
                return parsed_data
                
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            logger.warning(f"🔍 Debug: Failed to parse JSON from text: {e}")
            logger.warning(f"🔍 Debug: Raw text was: {text}")
            return {}
        
        logger.warning(f"🔍 Debug: No JSON found in text: {text}")
        return {}

    def render_personal_info_polished(self, data: Dict):
        """Render polished personal information with simple styling"""
        if data.get("name"):
            st.markdown(f"**Name:** {data['name']}")
        
        if data.get("email"):
            st.markdown(f"**Email:** {data['email']}")
        
        if data.get("phone"):
            st.markdown(f"**Phone:** {data['phone']}")
        
        if data.get("website"):
            st.markdown(f"**Website:** {data['website']}")
        
        if data.get("address"):
            st.markdown(f"**Address:** {data['address']}")

    def render_education_polished(self, data: Dict):
        """Render polished education with simple styling"""
        # Handle nested education data
        education_data = data.get("education", [])
        if isinstance(education_data, list) and education_data:
            for edu in education_data:
                if edu.get("institution"):
                    st.markdown(f"**Institution:** {edu['institution']}")
                
                if edu.get("degree"):
                    st.markdown(f"**Degree:** {edu['degree']}")
                
                if edu.get("studyType"):
                    st.markdown(f"**Study Type:** {edu['studyType']}")
                
                if edu.get("startDate") or edu.get("endDate"):
                    date_range = f"{edu.get('startDate', '')} - {edu.get('endDate', '')}"
                    st.markdown(f"**Duration:** {date_range}")
                
                if edu.get("gpa"):
                    st.markdown(f"**GPA:** {edu['gpa']}")
                
                if edu.get("courses"):
                    courses = ", ".join(edu["courses"]) if isinstance(edu["courses"], list) else edu["courses"]
                    st.markdown(f"**Courses:** {courses}")
                
                st.markdown("")  # Add spacing between education entries
        else:
            # Fallback to flat structure
            if data.get("degree"):
                st.markdown(f"**Degree:** {data['degree']}")
            
            if data.get("institution"):
                st.markdown(f"**Institution:** {data['institution']}")
            
            if data.get("graduation_date"):
                st.markdown(f"**Graduation:** {data['graduation_date']}")
            
            if data.get("gpa"):
                st.markdown(f"**GPA:** {data['gpa']}")

    def render_experience_polished(self, data: Dict):
        """Render polished experience with simple styling"""
        # Handle nested work experience data
        work_data = data.get("work", [])
        if isinstance(work_data, list) and work_data:
            for job in work_data:
                if job.get("company"):
                    st.markdown(f"**Company:** {job['company']}")
                
                if job.get("position"):
                    st.markdown(f"**Position:** {job['position']}")
                
                if job.get("startDate") or job.get("endDate"):
                    date_range = f"{job.get('startDate', '')} - {job.get('endDate', '')}"
                    st.markdown(f"**Duration:** {date_range}")
                
                if job.get("location"):
                    st.markdown(f"**Location:** {job['location']}")
                
                if job.get("highlights"):
                    highlights = job["highlights"]
                    st.markdown("**Highlights:**")
                    if isinstance(highlights, list):
                        for highlight in highlights:
                            st.markdown(f"• {highlight}")
                    else:
                        st.markdown(highlights)
                
                st.markdown("")  # Add spacing between job entries
        else:
            # Fallback to flat structure
            if data.get("position"):
                st.markdown(f"**Position:** {data['position']}")
            
            if data.get("company"):
                st.markdown(f"**Company:** {data['company']}")
            
            if data.get("duration"):
                st.markdown(f"**Duration:** {data['duration']}")
            
            if data.get("responsibilities"):
                st.markdown(f"**Responsibilities:**")
                st.markdown(data['responsibilities'])

    def render_skills_polished(self, data: Dict):
        """Render polished skills with simple styling"""
        # Handle nested skills data
        skills_data = data.get("skills", [])
        if isinstance(skills_data, list) and skills_data:
            for skill_group in skills_data:
                if skill_group.get("name"):
                    skill_name = skill_group["name"]
                    
                    if skill_group.get("keywords"):
                        keywords = skill_group["keywords"]
                        if isinstance(keywords, list):
                            keywords_text = ", ".join(keywords)
                        else:
                            keywords_text = keywords
                        st.markdown(f"**{skill_name}:** {keywords_text}")
                    else:
                        st.markdown(f"**{skill_name}:**")
        else:
            # Fallback to flat structure
            if data.get("technical_skills"):
                st.markdown(f"**Technical Skills:** {data['technical_skills']}")
            
            if data.get("soft_skills"):
                st.markdown(f"**Soft Skills:** {data['soft_skills']}")

    def render_projects_polished(self, data: Dict):
        """Render polished projects with simple styling"""
        # Handle nested projects data
        projects_data = data.get("projects", [])
        if isinstance(projects_data, list) and projects_data:
            for project in projects_data:
                if project.get("name"):
                    st.markdown(f"**Project Name:** {project['name']}")
                
                if project.get("description"):
                    st.markdown(f"**Description:** {project['description']}")
                
                if project.get("keywords"):
                    keywords = project["keywords"]
                    if isinstance(keywords, list):
                        keywords_text = ", ".join(keywords)
                    else:
                        keywords_text = keywords
                    st.markdown(f"**Technologies:** {keywords_text}")
                
                if project.get("url"):
                    st.markdown(f"**URL:** {project['url']}")
                
                st.markdown("")  # Add spacing between projects
        else:
            # Fallback to flat structure
            if data.get("project_name"):
                st.markdown(f"**Project Name:** {data['project_name']}")
            
            if data.get("description"):
                st.markdown(f"**Description:** {data['description']}")
            
            if data.get("technologies"):
                st.markdown(f"**Technologies:** {data['technologies']}")

    def render_generic_polished(self, data: Dict, section_name: str):
        """Render generic polished content with simple styling"""
        for key, value in data.items():
            if value:  # Only show non-empty values
                key_formatted = key.replace("_", " ").title()
                st.markdown(f"**{key_formatted}:** {value}")
                st.markdown("")  # Add spacing

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
                # Use original_lines if available, fallback to lines or raw_text
                original_lines = getattr(section_obj, "original_lines", None)
                if original_lines:
                    for line in original_lines:
                        st.markdown(line if line.strip() else "&nbsp;", unsafe_allow_html=True)
                elif section_obj.lines:
                    for line in section_obj.lines:
                        st.markdown(line if line.strip() else "&nbsp;", unsafe_allow_html=True)
                else:
                    st.markdown(section_obj.raw_text)
        except Exception as e:
            logger.error(f"Failed to render original section {section_name}: {e}")
            st.error(self.T['compare']['render_error'].format(section=section_name))

    def render_polished_section(self, section_name: str, section_obj: SectionBase):
        """
        Render the polished content column with beautiful styling.

        Args:
            section_name: Name of the section
            section_obj: SectionBase object containing original content
        """
        try:
            st.markdown(f"#### {self.T['compare']['polished']} - {section_name}")

            # Check if section has rewritten content
            if hasattr(section_obj, 'rewritten_text') and section_obj.rewritten_text:
                logger.info(f"🔍 Debug: Section {section_name} has rewritten_text: {section_obj.rewritten_text[:100]}...")
                
                # Parse the JSON from the rewritten text
                parsed_data = self.parse_final_answer_json(section_obj.rewritten_text)
                
                logger.info(f"🔍 Debug: Parsed data for {section_name}: {parsed_data}")
                
                if parsed_data:
                    # Use chat message style for polished content
                    with st.chat_message("assistant"):
                        st.write(self.T['compare']['polished_content'])
                        
                        # Render based on section type
                        if section_name.lower() in ['personal_info', 'personal', 'contact']:
                            self.render_personal_info_polished(parsed_data)
                        elif section_name.lower() in ['education', 'education_section']:
                            self.render_education_polished(parsed_data)
                        elif section_name.lower() in ['experience', 'work_experience', 'professional_experience']:
                            self.render_experience_polished(parsed_data)
                        elif section_name.lower() in ['skills', 'technical_skills']:
                            self.render_skills_polished(parsed_data)
                        elif section_name.lower() in ['projects', 'project_section']:
                            self.render_projects_polished(parsed_data)
                        else:
                            self.render_generic_polished(parsed_data, section_name)
                else:
                    logger.warning(f"🔍 Debug: No parsed data for {section_name}, showing raw text")
                    # Fallback to original rendering if JSON parsing fails
                    with st.chat_message("assistant"):
                        st.write(self.T['compare']['polished_content'])
                        st.markdown(section_obj.rewritten_text)
                        
            else:
                logger.warning(f"🔍 Debug: Section {section_name} has no rewritten_text")
                with st.chat_message("assistant"):
                    st.warning(self.T['compare']['no_polish_available'])

        except Exception as e:
            logger.error(f"Failed to render polished section {section_name}: {e}")
            st.error(self.T['compare']['polish_render_error'].format(error=str(e)))
            # Fallback to original rendering
            with st.chat_message("assistant"):
                st.markdown(getattr(section_obj, 'rewritten_text', 'No content available'))

    def render_section_comparison(self, section_name: str, section_obj: SectionBase):
        """
        Render comparison for a single section.

        Args:
            section_name: Name of the section
            section_obj: SectionBase object to compare
        """
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            self.render_original_section(section_name, section_obj)
        with col2:
            self.render_polished_section(section_name, section_obj)

    def render_sections_overview(self, sections: Dict[str, SectionBase]):
        """Render an overview of sections to be compared"""
        try:
            section_names = list(sections.keys())
            st.info(
                self.T["compare"]["comparing_sections"].format(
                    count=len(sections), sections=", ".join(section_names)
                )
            )
        except Exception as e:
            logger.error(f"Failed to render sections overview: {e}")

    def render_comparison(
        self,
        sections: Dict[str, SectionBase],
        jd_content: str,
        rewriter: ResumeRewriter,
    ):
        """Main comparison rendering logic"""
        logger.info("Comparing all resume sections using SectionRewriter")

        if not sections:
            st.warning(self.T['compare']['no_sections_to_compare'])
            return

        for section_name, section_obj in sections.items():
            try:
                # Rewrite section if not already rewritten
                if not getattr(section_obj, "rewritten_text", None):
                    with st.spinner(self.T['compare']['polishing_section'].format(section=section_name)):
                        try:
                            rewritten_section = rewriter.rewrite_section(section_obj, jd_content)
                            # Update the section object with rewritten content
                            if rewritten_section and hasattr(rewritten_section, 'rewritten_text'):
                                section_obj.rewritten_text = rewritten_section.rewritten_text
                        except ValueError as ve:
                            # Handle missing prompt gracefully
                            logger.warning(f"Skipping section {section_name}: {ve}")
                            section_obj.rewritten_text = self.T['compare']['section_not_supported'].format(reason=str(ve))
                        except Exception as re:
                            # Handle other rewriting errors
                            logger.error(f"Failed to rewrite section {section_name}: {re}")
                            section_obj.rewritten_text = self.T['compare']['polishing_failed'].format(error=str(re))

                self.render_section_comparison(section_name, section_obj)

            except Exception as e:
                logger.error(f"Failed to process section {section_name}: {e}")
                st.error(self.T['compare']['processing_failed'].format(section=section_name))
                # Show the original section even if processing fails
                with st.expander(self.T['compare']['original_content_label'].format(section=section_name)):
                    st.text(section_obj.raw_text)

    def render_card_body(self):
        """Render the main card body required by BaseCard"""
        try:
            # Get data from session state
            sections = st.session_state.get("resume_sections", {})

            if not sections:
                st.warning(self.T['compare']['upload_resume_first'])
                return

            st.info(self.T['compare']['page_description'])
            st.info(self.T['compare']['auto_polish_info'])

        except Exception as e:
            logger.error(f"Failed to render compare card body: {e}")
            st.error(self.T['compare']['display_error'])

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
    T = LANGUAGES[st.session_state.lang]
    card = CompareCard(
        comment=T['compare']['comment_sidebar'],
        additional_content=T['compare']['comment_description']
    )
    card.render()
    card.render_comparison(sections, jd_content, rewriter)
