import streamlit as st
from resumix.frontend.components.cards.agent_card import AgentCard
from resumix.shared.utils.session_utils import SessionUtils


class AgentPage:
    """Page for agent-based resume optimization"""
    
    def __init__(self):
        self.agent_card = AgentCard()
    
    def render(self):
        """Render the agent page"""
        # Get resume sections
        try:
            sections = SessionUtils.get_resume_sections()
            self.agent_card.set_sections(sections)
            self.agent_card.render()
        except Exception as e:
            st.error(f"Error loading resume sections: {e}")
            st.info("Please upload a resume to use the agent features.")
