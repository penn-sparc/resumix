import streamlit as st
from resumix.shared.utils.session_utils import SessionUtils
from resumix.shared.section.section_base import SectionBase
from resumix.frontend.components.cards.compare_card import CompareCard
from resumix.frontend.api.api import compare_section_api, format_section_api
from loguru import logger
from typing import Dict
import copy
import json
from resumix.shared.utils.i18n import LANGUAGES
from concurrent.futures import ThreadPoolExecutor, as_completed


class ComparePage:

    def __init__(self):
        self.T = LANGUAGES[st.session_state.lang]

        if "versions" not in st.session_state:
            st.session_state["versions"] = {}
        self.versions = st.session_state["versions"]

        if "skip_mask" not in st.session_state:
            st.session_state["skip_mask"] = set()
        self.skip_mask = st.session_state["skip_mask"]
        self.skip_mask.clear()

    def render(self):
        # 检查是否满足所有前置条件
        can_proceed, error = self._check_prerequisites()
        if not can_proceed:
            st.warning(error)
            return

        sections = SessionUtils.get_resume_sections()  # 获取简历各个部分
        jd_content = self._get_jd_content()  # 获取职位描述内容

        # 初始话 comparison_session
        if "comparison_session" not in st.session_state:
            st.session_state["comparison_session"] = {}
        st.session_state.comparison_session.setdefault("jd_content", jd_content)
        st.session_state.comparison_session.setdefault("comparison_started", False)

        # 如果比较尚未开始，启动比较
        if not st.session_state.comparison_session["comparison_started"]:
            if st.button("🚀 Start Comparison", type="primary"):
                st.session_state.comparison_session["comparison_started"] = True
                st.rerun()
        else:
            # 开始处理和显示每个部分的比较结果
            self._format_sections(sections, jd_content)
            self._ensure_sections_are_rewritten(sections, jd_content)
            self._render_section_comparisons(sections, jd_content)

    def _check_prerequisites(self):
        if not st.session_state.get("resume_text") or not st.session_state.get(
            "resume_sections"
        ):
            return False, "Please upload a resume to use the comparison features."
        return True, None

    def _get_jd_content(self) -> str:
        jd_url = st.text_input("Job Description URL (optional)", key="compare_jd_url")
        if jd_url.strip():
            try:
                # Directly use jd_url without modifying session_state here
                jd_content = SessionUtils.get_job_description_content()
                return str(jd_content) if jd_content else "No job description provided"
            except Exception as e:
                st.warning(f"Failed to fetch JD: {e}")
                return f"Job description URL provided: {jd_url} (parse failed)"
        return "No job description provided"

    def _format_sections(self, sections: Dict[str, SectionBase], jd_content: str):
        futures = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            for section_name, section_obj in sections.items():

                if section_obj.json_text is not None:
                    logger.info(f"section_obj.json_text: {section_obj.json_text}")
                    continue

                if section_name not in self.skip_mask:
                    future = executor.submit(
                        format_section_api, section_obj, jd_content
                    )
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

                    sections[section_name] = section_obj
                    logger.info(f"type of section_obj: {type(section_obj)}")
                    logger.info(f"section_obj.json_text: {section_obj.json_text}")

                except Exception as e:
                    logger.error(f"Failed to rewrite section {section_name}: {e}")
                    section_obj.rewritten_text = self.T["compare"][
                        "polishing_failed"
                    ].format(error=str(e))

    def _ensure_sections_are_rewritten(
        self, sections: Dict[str, SectionBase], jd_content: str
    ):

        futures = {}
        # 使用 ThreadPoolExecutor 并发重写简历各部分
        with ThreadPoolExecutor(max_workers=6) as executor:
            for section_name, section_obj in sections.items():
                if section_name not in self.skip_mask:
                    logger.info(section_name)
                    logger.info(self.skip_mask)
                    logger.warning(f"redo {section_name}")
                    # 将任务提交到 executor 中
                    future = executor.submit(
                        compare_section_api, section_obj, jd_content
                    )
                    # 将 Future 对象存储到 futures 字典中
                    futures[future] = section_name
                    self.skip_mask.add(section_name)  # 标记该段已被处理

        with st.spinner("🔄 Generating polished versions..."):
            for future in as_completed(futures):
                section_name = futures[future]
                section_obj = sections[section_name]
                try:
                    result = future.result()

                    # 获取重写文本，处理为空的情况
                    rewritten_text = result.get("rewritten_text", None)
                    if rewritten_text is None:
                        logger.error(
                            f"Rewritten text is missing for section {section_name}"
                        )
                        section_obj.rewritten_text = "⚠️ Missing rewritten text"
                    else:
                        section_obj.rewritten_text = rewritten_text

                    logger.info(
                        f"section_obj.rewritten_text: {section_obj.rewritten_text}"
                    )

                    self.versions[section_name] = self.versions.get(
                        section_name, {"version": 0}
                    )
                    # st.session_state[f"{section_name}_rewritten"] = True
                    sections[section_name] = section_obj
                    logger.info(f"type of section_obj: {type(section_obj)}")

                except Exception as e:
                    logger.error(f"Failed to rewrite section {section_name}: {e}")
                    section_obj.rewritten_text = self.T["compare"][
                        "polishing_failed"
                    ].format(error=str(e))

    def _render_section_comparisons(
        self, sections: Dict[str, SectionBase], jd_content: str
    ):
        for section_name, section_obj in sections.items():
            st.divider()
            st.markdown(f"### 📝 {section_name.replace('_', ' ').title()}")

            # 获取当前版本的原文和重写版本
            left_version, right_version = self._get_section_current_versions(
                section_name
            )

            # 使用 Streamlit 的两列布局显示左侧原文和右侧重写版本
            col1, col2 = st.columns(2)
            with col1:
                version = left_version["version"]

                logger.warning(f"left_version: {version}")

                # CompareCard().render_version_section(
                #     section_name, section_obj, version_label=version
                # )
                CompareCard()._render_json_section(section_name, section_obj)

            with col2:
                version = right_version["version"]
                # CompareCard().render_version_section(
                #     section_name, section_obj, version_label=version
                # )
                CompareCard()._render_polished_section(section_name, section_obj)

            # 渲染用户选择的按钮
            choice = self._render_version_choice_buttons(
                section_name, left_version, right_version
            )
            if choice:
                self._handle_section_choice(
                    section_name, choice, left_version, right_version, jd_content
                )

    def _render_version_choice_buttons(self, section_name, left_version, right_version):
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            if st.button(
                "Keep polishing with this version", key=f"choose_left_{section_name}"
            ):
                return "left"
            if st.button(
                "✅ I'm happy with this version", key=f"done_left_{section_name}"
            ):
                return "done_left"
        with col2:
            st.markdown(
                "<div style='text-align: center; padding-top: 0.5rem; font-size: 0.8rem;'>OR</div>",
                unsafe_allow_html=True,
            )
        with col3:
            if st.button(
                "Keep polishing with this version", key=f"choose_right_{section_name}"
            ):
                return "right"
            if st.button(
                "✅ I'm happy with this version", key=f"done_right_{section_name}"
            ):
                return "done_right"
        return None

    def _handle_section_choice(
        self, section_name, choice, left_version, right_version, jd_content
    ):
        session = st.session_state.comparison_session
        if choice.startswith("done"):
            # st.session_state[f"{section_name}_rewritten"] = False
            session_rewritten = st.session_state.get(f"{section_name}_rewritten", False)
            logger.info(f"{section_name} session_rewritten: {session_rewritten}")
            # 如果选择了左侧版本（原始文本）
            if "left" in choice:
                final = left_version
            else:
                # 如果选择了右侧版本（重写文本）
                final = right_version
                # 将 rewritten_text 设置为 raw_text
                self.skip_mask.remove(section_name)

                original_section = SessionUtils.get_resume_sections()[section_name]
                new_section = copy.deepcopy(original_section)
                new_section.raw_text = original_section.rewritten_text
                new_section.json_text = original_section.rewritten_text
                SessionUtils.get_resume_sections()[section_name] = new_section

                self.versions[section_name]["version"] += 1

                logger.warning(
                    f"raw text: {SessionUtils.get_resume_sections()[section_name].raw_text}"
                )
                logger.warning(
                    f"rewritten text: {SessionUtils.get_resume_sections()[section_name].rewritten_text}"
                )

            session[f"{section_name}_completed"] = True
            session[f"{section_name}_final_version"] = final
            st.success(f"✅ {section_name} polishing completed!")

            self.rerun()

    def _get_section_current_versions(self, section_name):
        sections = SessionUtils.get_resume_sections()
        section_obj = sections.get(section_name)

        # 如果没有重写文本，返回 original 和 polished_v1 版本
        # session_rewritten = st.session_state.get(f"{section_name}_rewritten", False)
        # logger.warning(f"{section_name} session_rewritten: {session_rewritten}")

        if self.versions[section_name]["version"] == 0:
            return {"type": "original", "version": 0}, {
                "type": "polished_v1",
                "version": 1,
            }

        else:
            return {
                "type": "polished_v" + str(self.versions[section_name]["version"]),
                "version": self.versions[section_name]["version"],
            }, {
                "type": "polished_v" + str(self.versions[section_name]["version"]),
                "version": self.versions[section_name]["version"] + 1,
            }
