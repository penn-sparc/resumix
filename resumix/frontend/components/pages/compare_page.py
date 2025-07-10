import streamlit as st
from resumix.frontend.components.cards.compare_card import CompareCard
from resumix.frontend.components.pages.base_page import BasePage
from resumix.shared.utils.session_utils import SessionUtils
from resumix.shared.utils.i18n import LANGUAGES

from resumix.shared.section.section_base import SectionBase
from resumix.shared.utils.logger import logger


class ComparePage(BasePage):

    def render(self):

        jd_content = SessionUtils.get_jd_sections()

        STRUCTED_SECTIONS = SessionUtils.get_resume_sections()

        with st.container():
            compare_card = CompareCard()
            compare_card.render()

            # Handle different types of jd_content
            if isinstance(jd_content, dict):
                jd_content_str = str(jd_content)
            elif jd_content is None:
                jd_content_str = "No job description provided"
            else:
                jd_content_str = str(jd_content)

            compare_card.render_comparison(STRUCTED_SECTIONS, jd_content_str)
