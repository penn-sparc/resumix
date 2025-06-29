# file: components/cards/analysis_card.py
import streamlit as st
from loguru import logger
from typing import Dict, Optional
from resumix.components.cards.base_card import BaseCard
from resumix.job_parser.resume_parser import ResumeParser
from resumix.section.section_base import SectionBase


class AnalysisCard(BaseCard):
    def __init__(
        self,
        title: str = "Resume Analysis",
        icon: str = "📄",
        comment: Optional[str] = None,
        additional_content: Optional[str] = None,
    ):
        """
        Initialize an AnalysisCard for resume parsing and analysis.
        
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

    def parse_resume_text(self, text: str) -> Dict[str, SectionBase]:
        """
        Parse the resume text into structured sections.
        
        Args:
            text: Raw resume text to parse
            
        Returns:
            Dictionary of section names to SectionBase objects
        """
        try:
            logger.info("Parsing resume text into sections")
            self.sections = self.parser.parse_resume(text)
            return self.sections
        except Exception as e:
            logger.error(f"Failed to parse resume: {e}")
            st.error(f"❌ Resume parsing failed: {e}")
            return {}

    def render_section_content(self, section_name: str, section_obj: SectionBase):
        """
        Render a single resume section with improved formatting and hierarchy.
        
        Args:
            section_name: Name of the section
            section_obj: SectionBase object containing section data
        """
        try:
            # Section header with icon
            section_icons = {
                'personal_info': '👤',
                'education': '🎓', 
                'experience': '💼',
                'projects': '🚀',
                'skills': '⚡',
                'awards': '🏆'
            }
            icon = section_icons.get(section_name, '📄')
            
            st.markdown(f"### {icon} {section_name.replace('_', ' ').title()}")
            
            # Get content lines
            content_lines = getattr(section_obj, 'original_lines', None)
            if not content_lines:
                content_lines = section_obj.raw_text.split('\n') if section_obj.raw_text else []
            
            if not content_lines:
                st.info("No content detected for this section")
                return
            
            # Clean and format content
            formatted_content = self._format_section_content(content_lines, section_name)
            
            # Display in a styled container
            with st.container():
                st.markdown(formatted_content, unsafe_allow_html=True)
                
        except Exception as e:
            logger.error(f"Failed to render section {section_name}: {e}")
            st.warning(f"Could not display section: {section_name}")

    def _format_section_content(self, lines: list, section_name: str) -> str:
        """
        Format section content with proper hierarchy and styling.
        
        Args:
            lines: List of content lines
            section_name: Name of the section for context-specific formatting
            
        Returns:
            Formatted markdown content
        """
        if not lines:
            return ""
        
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('---'):  # Skip empty lines and page markers
                continue
                
            # Apply formatting based on content type
            if self._is_section_header(line):
                formatted_lines.append(f"**{line}**")
            elif self._is_subsection_or_title(line, section_name):
                formatted_lines.append(f"#### {line}")
            elif self._is_detail_line(line):
                formatted_lines.append(f"- {line}")
            else:
                formatted_lines.append(line)
        
        # Join with proper spacing
        content = "\n\n".join(formatted_lines) if formatted_lines else "No content available"
        
        # Wrap in a styled container
        return f"""
        <div style="
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #2563eb;
            margin: 0.5rem 0;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        ">
            {content}
        </div>
        """
    
    def _is_section_header(self, line: str) -> bool:
        """Check if line is a section header"""
        headers = ['personal information', 'education', 'work experience', 'project experience', 
                  'technical skills', 'certifications', 'awards', 'programming languages']
        return any(header in line.lower() for header in headers)
    
    def _is_subsection_or_title(self, line: str, section_name: str) -> bool:
        """Check if line is a subsection title or job/project title"""
        # Job titles, company names, project names, degree names
        title_indicators = ['engineer', 'developer', 'manager', 'analyst', 'intern', 
                           'university', 'college', 'bachelor', 'master', 'phd',
                           'project', 'platform', 'application', 'system']
        
        # Skip very short lines or lines with mostly symbols
        if len(line) < 3 or len([c for c in line if c.isalpha()]) < 3:
            return False
            
        return any(indicator in line.lower() for indicator in title_indicators)
    
    def _is_detail_line(self, line: str) -> bool:
        """Check if line should be formatted as a detail/bullet point"""
        # Lines that start with action words or describe skills/technologies
        detail_starters = ['developed', 'implemented', 'designed', 'led', 'managed', 'created',
                          'improved', 'optimized', 'technologies:', 'skills:', 'coursework:']
        
        return (any(line.lower().startswith(starter) for starter in detail_starters) or
                ':' in line and len(line.split(':')) == 2)

    def render_sections_overview(self):
        """Render an overview of detected sections with visual cards"""
        if self.sections:
            st.markdown(f"### 📋 Resume Analysis Summary")
            st.success(f"**Successfully detected {len(self.sections)} sections from your resume!**")
            
            # Create columns for section badges
            cols = st.columns(min(len(self.sections), 4))
            section_icons = {
                'personal_info': '👤',
                'education': '🎓', 
                'experience': '💼',
                'projects': '🚀',
                'skills': '⚡',
                'awards': '🏆'
            }
            
            for i, section_name in enumerate(self.sections.keys()):
                with cols[i % 4]:
                    icon = section_icons.get(section_name, '📄')
                    display_name = section_name.replace('_', ' ').title()
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 0.75rem;
                        border-radius: 8px;
                        text-align: center;
                        margin: 0.25rem 0;
                        font-weight: 600;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    ">
                        {icon} {display_name}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No sections detected in the resume")

    def _get_section_emoji(self, section_name: str) -> str:
        """Get emoji for section name"""
        emoji_map = {
            'personal_info': '👤',
            'education': '🎓', 
            'experience': '💼',
            'projects': '🚀',
            'skills': '⚡',
            'awards': '🏆',
            'certifications': '📜',
            'languages': '🌐'
        }
        return emoji_map.get(section_name, '📄')
    
    def _format_content_simple(self, content: str) -> str:
        """Format section content with proper text hierarchy and paragraph styling"""
        if not content:
            return "*No content available*"
            
        # Clean up the content
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        formatted_lines = []
        for line in lines:
            if len(line) > 3:  # Skip very short lines
                # Detect and format different types of content
                if self._is_header_line(line):
                    # Make headers bold
                    formatted_lines.append(f"**{line}**")
                elif self._is_list_item(line):
                    # Keep existing bullet points or add them
                    if not line.startswith(('•', '-', '*')):
                        formatted_lines.append(f"• {line}")
                    else:
                        formatted_lines.append(line)
                elif self._contains_key_info(line):
                    # Highlight key information
                    formatted_lines.append(f"**{line}**")
                else:
                    # Regular content
                    formatted_lines.append(line)
        
        return '\n\n'.join(formatted_lines) if formatted_lines else "*Content parsing in progress...*"
    
    def _is_header_line(self, line: str) -> bool:
        """Check if line appears to be a header/title"""
        header_indicators = [
            'experience', 'education', 'skills', 'projects', 'work experience',
            'project experience', 'technical skills', 'certifications', 'awards',
            'personal information', 'background'
        ]
        return any(indicator in line.lower() for indicator in header_indicators)
    
    def _is_list_item(self, line: str) -> bool:
        """Check if line should be formatted as a list item"""
        # Lines that start with action words or technologies
        action_words = ['developed', 'implemented', 'designed', 'created', 'built', 'managed', 'led', 'improved']
        return (any(line.lower().startswith(word) for word in action_words) or 
                ':' in line or 
                line.startswith(('•', '-', '*')))
    
    def _contains_key_info(self, line: str) -> bool:
        """Check if line contains key information that should be highlighted"""
        key_indicators = ['university', 'degree', 'bachelor', 'master', 'certification', 'award']
        return any(indicator in line.lower() for indicator in key_indicators)

    def render_analysis_content(self, resume_text: str):
        """
        Handle Resume Analysis with provided resume text using clean formatting.
        """
        logger.info("Handling Resume Analysis with provided resume text")
        
        try:
            # Parse resume into sections
            sections = self.parse_resume_text(resume_text)
            
            if not sections:
                st.warning("📄 No sections detected in the resume")
                return
            
            # Show section overview as bullet points
            from resumix.utils.i18n import LANGUAGES
            T = LANGUAGES[st.session_state.lang]
            st.markdown(f"### 📋 {T['analysis']['sections_detected']}")
            
            for section_name in sections.keys():
                emoji = self._get_section_emoji(section_name)
                section_title = section_name.replace('_', ' ').title()
                st.markdown(f"• {emoji} **{section_title}**")
            
            st.markdown("---")
            
            # Display each section with enhanced formatting
            for section_name, content in sections.items():
                content_str = str(content) if content else ""
                if content_str and content_str.strip():
                    emoji = self._get_section_emoji(section_name)
                    st.markdown(f"#### {emoji} {section_name.replace('_', ' ').title()}")
                    
                    # Format content with enhanced hierarchy
                    formatted_content = self._format_content_simple(content_str)
                    st.markdown(formatted_content)
                    st.markdown("")  # Add spacing between sections
                    
        except Exception as e:
            logger.error(f"Failed to render analysis content: {e}")
            st.error("Could not parse resume sections")

    def render_comment(self):
        """Render the comment section if available"""
        if self.comment:
            st.markdown(f"📄 **Analysis Note:** {self.comment}")

    def render_card_body(self):
        """
        Render the main analysis card content with clean text hierarchy.
        """
        try:
            # Get resume text from session state
            resume_text = st.session_state.get("resume_text", "")
            
            if not resume_text:
                from resumix.utils.i18n import LANGUAGES
                T = LANGUAGES[st.session_state.lang]
                st.warning(T['analysis']['please_upload'])
                return
            
            # Parse and render analysis content
            self.render_analysis_content(resume_text)
            
        except Exception as e:
            logger.error(f"Failed to render analysis card body: {e}")
            st.error("Could not display resume analysis")

    def render(self):
        """
        Simple render method using the clean BaseCard structure.
        """
        logger.info("Rendering AnalysisCard")
        # Use the simplified BaseCard render method
        super().render()

    def render_analysis(self, text: str):
        """
        Legacy method for backward compatibility.
        
        Args:
            text: Resume text to analyze
        """
        logger.info("Using legacy render_analysis method")
        self.render_analysis_content(text)


def analysis_card(text: str):
    """
    Legacy function wrapper for backward compatibility.
    This maintains the same interface as analysis_module.py
    """
    logger.info("Handling Resume Analysis with provided resume text.")
    card = AnalysisCard(
        comment="AI-powered resume section analysis",
        additional_content="Parsed using advanced NLP techniques"
    )
    card.render()
    card.render_analysis(text) 