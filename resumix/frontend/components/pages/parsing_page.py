import streamlit as st
from resumix.shared.utils.logger import logger
from typing import Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from resumix.frontend.components.pages.base_page import BasePage
from resumix.shared.utils.session_utils import SessionUtils
from resumix.shared.utils.i18n import LANGUAGES

from resumix.frontend.api.api import format_section_api
from resumix.shared.section.section_base import SectionBase
from resumix.shared.utils.logger import logger
from resumix.config.config import Config
from resumix.frontend.components.cards.compare_card import CompareCard

import json


class ParsingPage(BasePage):

    def __init__(self):
        self.T = SessionUtils.get_T()

    def render(self):
        sections = SessionUtils.get_resume_sections()
        jd_content = ""
        # self.test(sections)

        self._format_sections(sections, jd_content)
        self._render_section(sections)

    def test(self, sections):
        for section_name, section_obj in sections.items():
            try:
                # 第一步：先转换为 json-compatible dict
                json_data = section_obj.model_dump(mode="json", exclude_none=True)
                # 第二步：尝试 json.dumps（无 default） —— 完全模拟 requests.post 过程
                json.dumps(json_data)
                logger.info(f"✅ Section '{section_name}' is serializable.")
            except TypeError as e:
                logger.error(
                    f"❌ Section '{section_name}' is NOT serializable: {e}\nData: {json_data}"
                )

    def _render_section(self, sections: Dict[str, SectionBase]):
        for section_name, section_obj in sections.items():
            st.divider()
            st.markdown(f"### 📝 {section_name.replace('_', ' ').title()}")

            CompareCard()._render_json_section(section_name, section_obj)

    def _render_sections(self, sections: Dict[str, SectionBase]):
        containers = {}  # section_name -> st.empty() 容器
        section_names = list(sections.keys())  # 保证顺序

        # Step 1: 先顺序创建容器
        for section_name in section_names:
            containers[section_name] = st.empty()

        # Step 2: 并发处理所有 section 的渲染数据（例如解析 JSON、格式化内容等）
        def render_func(name: str, obj: SectionBase):
            return name, CompareCard()._render_json_section(
                name, obj
            )  # 假设你抽出数据准备逻辑为一个函数

        futures = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            for section_name in section_names:
                section_obj = sections[section_name]
                futures[executor.submit(render_func, section_name, section_obj)] = (
                    section_name
                )

            # Step 3: 等待结果，并按 section_name 取容器填充
            for future in as_completed(futures):
                section_name, content_html = future.result()
                with containers[section_name]:
                    st.markdown(f"### 📝 {section_name.replace('_', ' ').title()}")
                    st.markdown(content_html, unsafe_allow_html=True)

    def _format_sections(self, sections: Dict[str, SectionBase], jd_content: str):
        futures = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            for section_name, section_obj in sections.items():

                if section_obj.json_text is not None:
                    logger.info(f"section_obj.json_text: {section_obj.json_text}")
                    continue

                section_obj.parse()
                logger.warning(f"section_name: {section_name}")
                logger.warning(f"Type of section_obj: {type(section_obj)}")

                # if section_name not in self.skip_mask:
                future = executor.submit(format_section_api, section_obj, jd_content)
                futures[future] = section_name

        with st.spinner("🔄 Generating polished versions..."):
            for future in as_completed(futures):
                section_name = futures[future]
                section_obj = sections[section_name]
                try:
                    result = future.result()

                    json_text = result.get("rewritten_text", None)
                    if json_text is None:
                        logger.error(
                            f"Rewritten text is missing for section {section_name}"
                        )
                        section_obj.json_text = "⚠️ Missing rewritten text"
                    else:
                        section_obj.json_text = json_text

                    SessionUtils.get_resume_sections()[section_name] = section_obj
                    logger.info(f"type of section_obj: {type(section_obj)}")
                    logger.info(f"section_obj.json_text: {section_obj.json_text}")

                except Exception as e:
                    logger.error(f"Failed to rewrite section {section_name}: {e}")
                    section_obj.rewritten_text = self.T["compare"][
                        "polishing_failed"
                    ].format(error=str(e))
