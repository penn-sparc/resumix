from typing import Optional
from resumix.frontend.components.cards.base_card import BaseCard
from resumix.shared.section.section_base import SectionBase
from resumix.shared.utils.logger import logger
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from resumix.shared.utils.session_utils import SessionUtils
from typing import Dict


class AgentCard(BaseCard):
    def __init__(
        self,
        title: str = "Parsing ",
        icon: str = "🤖",
        comment: Optional[str] = None,
        additional_content: Optional[str] = None,
    ):
        """
        Initialize an AgentCard for AI-powered resume optimization.

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
        self.sections = {}

    def render(self):
        sections = SessionUtils.get_resume_sections()
        jd_content = SessionUtils.get_jd_content()
        self._format_sections(sections, jd_content)

    # def _format_sections(self, sections: Dict[str, SectionBase], jd_content: str):
    #     futures = {}
    #     with ThreadPoolExecutor(max_workers=6) as executor:
    #         for section_name, section_obj in sections.items():

    #             if section_obj.json_text is not None:
    #                 logger.info(f"section_obj.json_text: {section_obj.json_text}")
    #                 continue

    #             if section_name not in self.skip_mask:
    #                 future = executor.submit(
    #                     format_section_api, section_obj, jd_content
    #                 )
    #                 futures[future] = section_name

    #     with st.spinner("🔄 Generating polished versions..."):
    #         for future in as_completed(futures):
    #             section_name = futures[future]
    #             section_obj = sections[section_name]
    #             try:
    #                 result = future.result()

    #                 json_text = result.get("rewritten_text", None)
    #                 if json_text is None:
    #                     logger.error(
    #                         f"Rewritten text is missing for section {section_name}"
    #                     )
    #                     section_obj.json_text = "⚠️ Missing rewritten text"
    #                 else:
    #                     section_obj.json_text = json_text

    #                 sections[section_name] = section_obj
    #                 logger.info(f"type of section_obj: {type(section_obj)}")
    #                 logger.info(f"section_obj.json_text: {section_obj.json_text}")

    #             except Exception as e:
    #                 logger.error(f"Failed to rewrite section {section_name}: {e}")
    #                 section_obj.rewritten_text = self.T["compare"][
    #                     "polishing_failed"
    #                 ].format(error=str(e))
