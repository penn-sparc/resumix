import streamlit as st
from resumix.frontend.components.cards.agent_card import AgentCard
from resumix.frontend.components.pages.base_page import BasePage
from resumix.shared.utils.session_utils import SessionUtils
from resumix.shared.utils.i18n import LANGUAGES

from resumix.shared.section.section_base import SectionBase
from resumix.shared.utils.logger import logger
from resumix.config.config import Config


CONFIG = Config().config


class AgentPage(BasePage):
    
    def render(self):

        STRUCTED_SECTIONS = SessionUtils.get_resume_sections()

        with st.container():
            agent_card = AgentCard()
            agent_card.set_sections(STRUCTED_SECTIONS)
            agent_card.render()
