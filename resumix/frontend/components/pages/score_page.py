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

    # def laura_render():

    #     STRUCTED_SECTIONS = []
    #     # Check if we have JD sections for proper scoring
    #     try:
    #         jd_sections = SessionUtils.get_jd_sections()

    #         # Debug: Show what sections we actually got
    #         st.info(
    #             f"🔍 Debug: Found {len(jd_sections)} JD sections: {list(jd_sections.keys())}"
    #         )

    #         # Show JD content for debugging
    #         st.subheader("📄 JD Sections Content:")
    #         for key, value in jd_sections.items():
    #             with st.expander(f"Section: {key}"):
    #                 if hasattr(value, "raw_text") and hasattr(value, "raw_text"):
    #                     # SectionBase object
    #                     raw_text = getattr(value, "raw_text", "")
    #                     st.text(f"Type: SectionBase\nContent: {raw_text[:200]}...")
    #                 elif isinstance(value, list):
    #                     st.text(f"Type: List\nContent: {str(value)[:200]}...")
    #                 elif isinstance(value, str):
    #                     st.text(f"Type: String\nContent: {value[:200]}...")
    #                 else:
    #                     st.text(f"Type: {type(value)}\nContent: {str(value)[:200]}...")

    #         # Much more flexible section matching
    #         basic_key = None
    #         preferred_key = None

    #         # First, try exact matches
    #         for key in jd_sections.keys():
    #             key_lower = key.lower()
    #             if "basic" in key_lower and (
    #                 "qualification" in key_lower or "requirement" in key_lower
    #             ):
    #                 basic_key = key
    #             elif "preferred" in key_lower and (
    #                 "qualification" in key_lower or "requirement" in key_lower
    #             ):
    #                 preferred_key = key

    #         # If no exact match, try broader matching
    #         if not basic_key:
    #             for key in jd_sections.keys():
    #                 key_lower = key.lower()
    #                 if any(
    #                     term in key_lower
    #                     for term in [
    #                         "requirement",
    #                         "qualification",
    #                         "skill",
    #                         "must",
    #                         "essential",
    #                     ]
    #                 ):
    #                     basic_key = key
    #                     break

    #         # Use any section as basic if we still don't have one
    #         if not basic_key and jd_sections:
    #             basic_key = list(jd_sections.keys())[0]
    #             st.warning(f"⚠️ Using '{basic_key}' as basic requirements section")

    #         st.info(
    #             f"🎯 Selected sections - Basic: {basic_key}, Preferred: {preferred_key}"
    #         )

    #         if not basic_key:
    #             st.warning("⚠️ No suitable JD sections found for scoring")
    #             st.info("📊 Available sections: " + ", ".join(jd_sections.keys()))

    #             # Show simple dummy score for testing
    #             st.subheader("🧪 Test Score Card")
    #             test_scores = {
    #                 "Completeness": 8,
    #                 "Clarity": 7,
    #                 "Relevance": 6,
    #                 "ProfessionalLanguage": 9,
    #                 "AchievementOriented": 5,
    #                 "QuantitativeSupport": 4,
    #                 "Comment": "This is a test score card with dummy data",
    #             }
    #             test_score_card = ScoreCard("Test Section", test_scores)
    #             test_score_card.render()

    #         else:
    #             # Import SectionBase for JD section conversion

    #             # Convert JD sections to SectionBase objects using flexible keys
    #             jd_basic_obj = jd_sections[basic_key]
    #             if hasattr(jd_basic_obj, "raw_text") and getattr(
    #                 jd_basic_obj, "raw_text", ""
    #             ):
    #                 # Already a SectionBase object
    #                 jd_basic_text = getattr(jd_basic_obj, "raw_text", "")
    #             elif isinstance(jd_basic_obj, list):
    #                 jd_basic_text = "\n".join(str(item) for item in jd_basic_obj)
    #             elif isinstance(jd_basic_obj, str):
    #                 jd_basic_text = jd_basic_obj
    #             else:
    #                 jd_basic_text = str(jd_basic_obj)
    #             jd_basic_section = SectionBase(name=basic_key, raw_text=jd_basic_text)

    #             if preferred_key and jd_sections.get(preferred_key):
    #                 jd_preferred_obj = jd_sections[preferred_key]
    #                 if hasattr(jd_preferred_obj, "raw_text") and getattr(
    #                     jd_preferred_obj, "raw_text", ""
    #                 ):
    #                     # Already a SectionBase object
    #                     jd_preferred_text = getattr(jd_preferred_obj, "raw_text", "")
    #                 elif isinstance(jd_preferred_obj, list):
    #                     jd_preferred_text = "\n".join(
    #                         str(item) for item in jd_preferred_obj
    #                     )
    #                 elif isinstance(jd_preferred_obj, str):
    #                     jd_preferred_text = jd_preferred_obj
    #                 else:
    #                     jd_preferred_text = str(jd_preferred_obj)
    #                 jd_preferred_section = SectionBase(
    #                     name=preferred_key, raw_text=jd_preferred_text
    #                 )
    #             else:
    #                 # Create empty preferred section when not available
    #                 jd_preferred_section = SectionBase(
    #                     name="requirements_preferred", raw_text=""
    #                 )

    #             # Initialize scoring module
    #             score_module = ScoreModule()

    #             # Show overall scoring progress
    #             st.success("✅ JD sections found! Starting real scoring...")

    #             # Score each section
    #             section_scores = {}
    #             for section_name, section_obj in STRUCTED_SECTIONS.items():
    #                 try:
    #                     with st.spinner(f"Scoring {section_name}..."):
    #                         score_result = score_module.score_resume(
    #                             section_obj,
    #                             jd_basic_section,
    #                             jd_preferred_section,
    #                         )
    #                         section_scores[section_name] = score_result

    #                         # Display individual section score
    #                         score_card = ScoreCard(section_name, score_result)
    #                         score_card.render()
    #                         st.markdown("---")

    #                 except Exception as e:
    #                     logger.error(f"Failed to score section {section_name}: {e}")
    #                     st.error(f"Failed to score {section_name}: {e}")
    #                     # Show test score card for this section
    #                     test_scores = {
    #                         "Completeness": 8,
    #                         "Clarity": 7,
    #                         "Relevance": 6,
    #                         "Comment": f"Scoring failed for {section_name}: {e}",
    #                     }
    #                     test_score_card = ScoreCard(section_name, test_scores)
    #                     test_score_card.render()
    #                     st.markdown("---")

    #             if section_scores:
    #                 st.success("✅ Resume scoring completed!")

    #     except Exception as e:
    #         logger.error(f"Failed to get JD sections: {e}")
    #         st.error(f"⚠️ Job description parsing failed: {e}")
    #         st.info(
    #             "📊 Upload a resume and add a job description to see detailed scoring"
    #         )

    #         # Show simple dummy score for testing
    #         st.subheader("🧪 Test Score Card")
    #         test_scores = {
    #             "Completeness": 8,
    #             "Clarity": 7,
    #             "Relevance": 6,
    #             "ProfessionalLanguage": 9,
    #             "AchievementOriented": 5,
    #             "QuantitativeSupport": 4,
    #             "Comment": "This is a test score card with dummy data",
    #         }
    #         test_score_card = ScoreCard("Test Section", test_scores)
    #         test_score_card.render()

    def render(self):

        with st.container():
            RESUME_SECTIONS = SessionUtils.get_resume_sections()
            JD_SECTIONS = SessionUtils.get_jd_sections()

            if "requirements_basic" not in JD_SECTIONS:
                for section in JD_SECTIONS.values():
                    st.warning(f"section: {section}")
                st.warning("❗岗位描述缺少字段 requirements_basic，无法评分分析。")
                return

            with st.spinner("正在调用评分服务..."):
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
        每次调用评分 API 只处理一个 section，并发执行 + 即时展示
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

        # 使用线程池并发评分
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_name = {
                executor.submit(score_single, name, section): name
                for name, section in sections.items()
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
                    st.error(f"评分服务调用失败（{name}）: {e}")

                finished += 1
                progress_bar.progress(finished / total)

        return results
