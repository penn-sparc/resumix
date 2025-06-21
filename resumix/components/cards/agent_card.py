import streamlit as st
from typing import Dict, Optional, Callable
from components.cards.base_card import BaseCard
from resumix.job_parser.resume_parser import ResumeParser
from resumix.utils.logger import logger

class AgentCard(BaseCard):
    def __init__(
        self,
        title: str = "AI Agent Assistant",
        icon: str = "🤖",
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
        
    def render_agent_response(self, result: str, section: str):
        """Enhanced response rendering with section context"""
        with st.chat_message("assistant"):
            st.markdown(f"**{section} Optimization**")
            st.write(result)
            st.markdown("---")
        
    def render_agent_interaction(self, text: str, jd_content: str, agent: Callable):
        """Improved agent interaction with error handling and progress tracking"""
        try:
            if not text.strip() or not jd_content.strip():
                st.warning("Please provide both resume content and job description")
                return
                
            with st.spinner("Analyzing resume and job description..."):
                sections = self.parser.parse_resume(text)
                
            if not sections:
                st.error("Could not parse any sections from the resume")
                return
                
            progress_bar = st.progress(0)
            total_sections = len(sections)
            
            st.subheader("AI Optimization Suggestions")
            with st.expander("Job Description Summary", expanded=False):
                st.write(jd_content[:500] + ("..." if len(jd_content) > 500 else ""))
            
            for i, (section, content) in enumerate(sections.items()):
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.markdown(f"**{section}**")
                        with st.expander("Original Content"):
                            st.write(content)
                    
                    with col2:
                        prompt = f"""As a resume optimization assistant, please improve this resume section based on the job description:

Job Description:
{jd_content[:2000]}... (truncated)

Resume Section ({section}):
{content}

Provide:
1. Specific improvements matching the job requirements
2. Quantifiable achievements where possible
3. Keywords from the job description
"""
                        with st.spinner(f"Optimizing {section}..."):
                            result = agent(prompt)
                            self.render_agent_response(result, section)
                
                progress_bar.progress((i + 1) / total_sections)
                
            st.success("AI optimization complete!")
            
        except Exception as e:
            logger.error(f"Agent interaction failed: {str(e)}")
            st.error(f"An error occurred: {str(e)}")
    
    def render(self):
        """Complete card rendering implementation"""
        self.render_header()
        
        if self.comment:
            with st.container():
                st.caption(self.comment)
                
        if self.additional_content:
            self.render_additional()
        
        return self  # Enable method chaining


def agent_card(text: str, jd_content: str, agent: Callable):
    """Modernized agent interface"""
    logger.info("Initializing AI Agent optimization")
    card = AgentCard(
        comment="AI-powered resume optimization based on job description",
        additional_content="Suggestions provided by Resumix AI Agent"
    )
    return card.render().render_agent_interaction(text, jd_content, agent)