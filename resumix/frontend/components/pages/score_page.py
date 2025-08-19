import streamlit as st
from resumix.shared.utils.logger import logger
from typing import Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from resumix.frontend.components.cards.score_card import ScoreCard
from resumix.frontend.components.pages.base_page import BasePage
from resumix.shared.utils.session_utils import SessionUtils
from resumix.shared.utils.i18n import LANGUAGES

from resumix.shared.section.section_base import SectionBase
from resumix.shared.utils.logger import logger
from resumix.config.config import Config

from resumix.frontend.api.api import score_section_api

from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

CONFIG = Config().config


class ScorePage(BasePage):
    def __init__(self):
        super().__init__()

    def set_sections(self, sections: Dict[str, Any]):
        self.sections = sections

    def render(self):

        with st.container():
            RESUME_SECTIONS = SessionUtils.get_resume_sections()
            JD_SECTIONS = SessionUtils.get_jd_sections()

            if "requirements_basic" not in JD_SECTIONS:
                for section in JD_SECTIONS.values():
                    st.warning(f"section: {section}")
                st.warning("❗job描述缺少字段 requirements_basic，无法score分析。")
                return

            with st.spinner("Scoring resume sections..."):
                try:
                    results = self._render_sections(
                        sections=RESUME_SECTIONS,
                        jd_basic=JD_SECTIONS["requirements_basic"],
                        jd_preferred=JD_SECTIONS.get("requirements_preferred"),
                        max_workers=5,  # 可调整并发数量
                    )
                except Exception as e:
                    st.error(f"❌ 请求失败: {e}")
                    return

            st.success("所有简历段落评分完成 ✅")

    def _render_sections(
        self,
        sections: Dict[str, SectionBase],
        jd_basic: SectionBase,
        jd_preferred: Optional[SectionBase] = None,
        max_workers: int = 5,
    ) -> Dict[str, Any]:
        """
        每次调用score API 只processing一个 section，并发执行 + 即时展示
        """
        results = {}

        # 准备 JD 数据
        jd_basic.parse()
        jd_basic_data = jd_basic.model_dump()

        jd_preferred_data = None
        if jd_preferred:
            jd_preferred.parse()
            jd_preferred_data = jd_preferred.model_dump()

        def score_single(name: str, section: SectionBase) -> Tuple[str, Dict[str, Any]]:
            section.parse()
            payload = {
                "data": {
                    "section": section.model_dump(),
                    "jd_section_basic": jd_basic_data,
                    "jd_section_preferred": jd_preferred_data,
                }
            }
            try:
                result = score_section_api(payload)
                return name, result
            except Exception as e:
                logger.exception(f"❌ Failed to score {name}")
                return name, {"error": str(e)}

        selected = ["experience", "skills", "projects"]
        # 使用线程池并发评分
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_name = {
                executor.submit(score_single, name, section): name
                for name, section in sections.items()
                if name in selected
            }

            finished = 0
            total = len(sections)
            progress_bar = st.progress(0)

            for future in as_completed(future_to_name):
                name = future_to_name[future]
                try:
                    name, result = future.result()
                    results[name] = result
                    with st.spinner(f"正在展示 {sections[name].name}..."):
                        score_card = ScoreCard(sections[name].name, result)
                        score_card.render()
                        st.markdown("---")
                except Exception as e:
                    logger.exception(f"❌ Exception in future for {name}")
                    results[name] = {"error": str(e)}
                    st.error(f"score服务调用失败（{name}）: {e}")

                finished += 1
                progress_bar.progress(finished / total)

        return results
