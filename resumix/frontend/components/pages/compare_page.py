import streamlit as st
from resumix.shared.utils.session_utils import SessionUtils
from resumix.shared.section.section_base import SectionBase
from resumix.frontend.components.cards.compare_card import CompareCard
from resumix.frontend.api.api import compare_section_api, format_section_api
from loguru import logger
from typing import Dict, Tuple
import copy
import json
from resumix.shared.utils.i18n import LANGUAGES
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import for PDF generation
from resumix.shared.utils.generator_utils import GeneratorUtils
from resumix.backend.resume_generator.generator import generate_pdf_resume
from resumix.backend.resume_generator.resume_generator import generate_pdf
import tempfile
import os
from pathlib import Path


# 顶层 worker，必须放在模块作用域，multiprocessing 才能 pickle 到
def _pdf_worker(resume_data, pdf_base_no_ext):
    import os

    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    try:
        # 在子进程内部再导入，避免主进程状态污染
        from resumix.backend.resume_generator.resume_generator import generate_pdf

        generate_pdf(json_resume=resume_data, output_path=pdf_base_no_ext)
    except Exception:
        # 将错误写到旁路文件，父进程可读取
        import traceback

        with open(pdf_base_no_ext + ".err.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise


class ComparePage:

    def __init__(self):
        self.T = LANGUAGES[st.session_state.lang]

        if "versions" not in st.session_state:
            st.session_state["versions"] = {}
        self.versions = st.session_state["versions"]

        if "skip_mask" not in st.session_state:
            st.session_state["skip_mask"] = set()
        self.skip_mask = st.session_state["skip_mask"]
        # self.skip_mask.clear()
        self.sections = SessionUtils.get_resume_sections()
        self.right_sections = {}

        # filtred_sections = {}
        self.selected = {
            "skills",
            "projects",
            "experience",
            # "education",
            # "personal_info",
            # "awards",
        }
        # # selected = {"projects"}
        # for section_name, section_obj in self.sections.items():
        #     if section_name in selected:
        #         filtred_sections[section_name] = section_obj

        # self.sections = filtred_sections

        self.unselected = {}

        for section_name, section_obj in self.sections.items():
            if section_name not in self.selected:
                self.unselected[section_name] = copy.deepcopy(section_obj)

        for section_name, section_obj in self.sections.items():
            self.right_sections[section_name] = copy.deepcopy(section_obj)

    def render(self):
        # "检查是否满足所有前置条件"
        # can_proceed, error = self._check_prerequisites()
        # if not can_proceed:
        #     st.warning(error)
        #     return

        self.sections = st.session_state.get("sections", copy.deepcopy(self.sections))
        sections = self.sections

        self.right_sections = st.session_state.get(
            "right_sections", copy.deepcopy(self.right_sections)
        )

        jd_content = self._get_jd_content()  # 获取职位描述内容

        if "comparison_session" not in st.session_state:
            st.session_state["comparison_session"] = {}

        if "sections_ready" not in st.session_state.comparison_session:
            st.session_state.comparison_session["sections_ready"] = False

        # st.session_state.comparison_session.setdefault("jd_content", jd_content)
        # st.session_state.comparison_session.setdefault("comparison_started", False)

        # 如果比较尚未开始，启动比较
        # if not st.session_state.comparison_session["comparison_started"]:
        #     if st.button("🚀 Start Comparison", type="primary"):
        #         st.session_state.comparison_session["comparison_started"] = True
        #         st.rerun()
        # else:
        # 开始处理和显示每个部分的比较结果
        if not st.session_state.comparison_session["sections_ready"]:
            self._format_sections(sections, jd_content)
            st.session_state.comparison_session["sections_ready"] = True

        self._ensure_sections_are_rewritten_v2(sections, jd_content)

        self._render_section_comparisons_v2(sections, jd_content)

        result_sections = copy.deepcopy(self.right_sections)

        for section_name, section_obj in self.unselected.items():
            if section_name not in self.selected:
                # 如果未选中，直接使用原始内容

                if section_obj.json_text is None:
                    section_obj.json_text = (
                        section_obj.raw_text or "⚠️ No content available"
                    )
                section_obj.rewritten_text = (
                    section_obj.json_text or "⚠️ No content available"
                )
                section_obj.raw_text = section_obj.json_text or "⚠️ No content available"

                result_sections[section_name] = copy.deepcopy(section_obj)
        self._render_export_section(result_sections)

    def _check_prerequisites(self):
        if not st.session_state.get("resume_text") or not st.session_state.get(
            "resume_sections"
        ):
            return False, "Please upload a resume to use the comparison features."
        return True, None

    def _get_jd_content(self) -> str:
        # jd_url = st.text_input("Job Description URL (optional)", key="compare_jd_url")
        # if jd_url.strip():
        try:
            # Directly use jd_url without modifying session_state here
            jd_content = SessionUtils.get_job_description_content()
            return str(jd_content) if jd_content else "No job description provided"
        except Exception as e:
            st.warning(f"Failed to fetch JD: {e}")
            return f"Job description URL provided: (parse failed)"

    def _format_sections(self, sections: Dict[str, SectionBase], jd_content: str):
        futures = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            for section_name, section_obj in sections.items():
                # Only skip if json_text is already populated
                if section_obj.json_text is not None:
                    logger.info(
                        f"Skipping format for {section_name} - json_text already populated"
                    )
                    continue

                logger.info(f"Formatting section {section_name}")
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

                    sections[section_name] = section_obj
                    logger.info(f"type of section_obj: {type(section_obj)}")
                    logger.info(f"section_obj.json_text: {section_obj.json_text}")

                except Exception as e:
                    logger.error(f"Failed to rewrite section {section_name}: {e}")
                    section_obj.rewritten_text = self.T["compare"][
                        "polishing_failed"
                    ].format(error=str(e))

    def _ensure_sections_are_rewritten_v2(
        self, sections: Dict[str, SectionBase], jd_content: str
    ):
        ### This method set the new sectinons to the right_sections
        logger.info("Ensuring all sections are rewritten with compare_section_api")
        futures = {}

        rewritten = {}
        for section_name, section_obj in sections.items():

            # self.right_sections[section_name] = copy.deepcopy(section_obj)
            need_to_rewrite = st.session_state.get(f"{section_name}_rewritten", True)
            # self.right_sections[section_name] = copy.deepcopy(section_obj)
            if need_to_rewrite:
                rewritten[section_name] = True

        # 使用 ThreadPoolExecutor 并发重写简历各部分
        with ThreadPoolExecutor(max_workers=6) as executor:
            for section_name, section_obj in sections.items():

                # if section_name not in self.selected:
                #     logger.info(f"Skipping section {section_name} - not selected")
                #     continue

                if section_name not in rewritten:
                    logger.info(f"Skipping section {section_name} - not rewritten")
                    continue

                # rewritten = st.session_state.get(f"{section_name}_rewritten", True)

                # if not rewritten:
                #     logger.info(f"Skipping section {section_name} - not rewritten")
                #     continue

                logger.warning(f"REWRITE section_name: {section_name}")

                # st.session_state[f"{section_name}_rewritten"] = False

                # Process the section if it's not fully complete
                logger.info(f"Processing section {section_name}")
                logger.info(f"json_text present: {section_obj.json_text is not None}")
                logger.info(
                    f"rewritten_text present: {section_obj.rewritten_text is not None}"
                )

                future = executor.submit(compare_section_api, section_obj, jd_content)
                futures[future] = section_name

        with st.spinner("🔄 Generating polished versions..."):
            for future in as_completed(futures):
                section_name = futures[future]

                new_section_obj = copy.deepcopy(sections[section_name])

                try:
                    result = future.result()

                    # 获取重写文本，处理为空的情况
                    rewritten_text = result.get(
                        "rewritten_text", "Rewritten text not found"
                    )

                    new_section_obj.rewritten_text = rewritten_text
                    new_section_obj.json_text = rewritten_text
                    new_section_obj.raw_text = rewritten_text

                    self.right_sections[section_name] = copy.deepcopy(new_section_obj)

                except Exception as e:
                    logger.error(f"Failed to rewrite section {section_name}: {e}")
                    new_section_obj.rewritten_text = self.T["compare"][
                        "polishing_failed"
                    ].format(error=str(e))
                    new_section_obj.json_text = "⚠️ Missing rewritten text"
                    new_section_obj.raw_text = "⚠️ Missing rewritten text"
                    self.right_sections[section_name] = copy.deepcopy(new_section_obj)

    def _render_section_comparisons_v2(
        self, sections: Dict[str, SectionBase], jd_content
    ):
        """
        Render the comparison sections with Streamlit's two-column layout.
        Each section will show the original and polished versions side by side.
        """
        for section_name, section_obj in self.sections.items():
            if section_name not in self.selected:

                logger.info(f"Skipping section {section_name} - not selected")
                continue

            # Ensure sections have at least some content for rendering
            if section_obj.json_text is None:
                section_obj.json_text = section_obj.raw_text or "⚠️ No content available"
            if section_obj.rewritten_text is None:
                logger.error(
                    f"Section {section_name} has no rewritten_text; using json_text as fallback"
                )

            logger.info("EQUALITY CHECK:")
            logger.warning(f"{self.right_sections[section_name] == section_obj}")
            logger.info("LEFT PAGE:")
            logger.warning(f"section_obj.json_text: {section_obj.json_text}")
            logger.info(f"section_obj.rewritten_text: {section_obj.rewritten_text}")
            logger.info("RIGHT PAGE:")
            logger.warning(
                f"self.right_sections[section_name].json_text: {self.right_sections[section_name].json_text}"
            )
            logger.info(
                f"self.right_sections[section_name].rewritten_text: {self.right_sections[section_name].rewritten_text}"
            )

            # 使用 Streamlit 的两列布局显示左侧原文和右侧重写版本

            if section_name in self.selected:
                st.divider()
                st.markdown(f"### 📝 {section_name.replace('_', ' ').title()}")
                col1, col2 = st.columns(2)

                with col1:

                    CompareCard()._render_json_section(section_name, section_obj)

                with col2:
                    CompareCard()._render_json_section(
                        section_name, self.right_sections[section_name]
                    )

            logger.debug("Check equality:")
            logger.debug(f"{self.right_sections[section_name] == section_obj}")

            choice = self._render_choice_buttons(section_name)

            logger.debug(
                f"after choice: {self.right_sections[section_name] == section_obj}"
            )

            # session_rewritten = st.session_state.get(f"{section_name}_rewritten", False)

            if choice is not None:
                # create the new section object
                self._handle_section_choice_v3(section_name, choice, jd_content)

                # session[f"{section_name}_rewritten"] = False

        st.session_state.sections = copy.deepcopy(self.sections)
        st.session_state.right_sections = copy.deepcopy(self.right_sections)

    def _render_choice_buttons(self, section_name):
        # col1, col2, col3 = st.columns([2, 1, 2])
        col1, col2 = st.columns([2, 2])
        st.session_state[f"{section_name}_rewritten"] = False
        with col1:
            if st.button(
                "Keep polishing with this version", key=f"choose_left_{section_name}"
            ):
                # st.session_state[f"{section_name}_rewritten"] = True
                return "left"
            # if st.button(
            #     "✅ I'm happy with this version", key=f"done_left_{section_name}"
            # ):
            #     return "done_left"
        # with col2:
        #     st.markdown(
        #         "<div style='text-align: center; padding-top: 0.5rem; font-size: 0.8rem;'>OR</div>",
        #         unsafe_allow_html=True,
        #     )
        with col2:
            if st.button(
                "Keep polishing with this version", key=f"choose_right_{section_name}"
            ):
                # st.session_state[f"{section_name}_rewritten"] = True

                logger.warning("Handling RIGHT choice")
                logger.debug(
                    f"{self.sections[section_name] == self.right_sections[section_name]}"
                )
                logger.warning(
                    f"Current left section: {self.sections[section_name].json_text}..."
                )
                logger.warning(
                    f"Current right section: {self.right_sections[section_name].json_text}..."
                )

                self.sections[section_name] = copy.deepcopy(
                    self.right_sections[section_name]
                )
                self.right_sections[section_name] = copy.deepcopy(
                    self.right_sections[section_name]
                )

                logger.warning(
                    f"Updated sections: {self.sections[section_name].json_text}..."
                )
                logger.warning(
                    f"Updated right_sections: {self.right_sections[section_name].json_text}..."
                )

                return "right"
        return None

    def _handle_section_choice_v3(self, section_name, choice, jd_content):
        logger.debug("Check equality:")
        logger.debug(
            f"{self.right_sections[section_name] == self.sections[section_name]}"
        )

        # session[f"{section_name}_rewritten"] = True

        st.session_state[f"{section_name}_rewritten"] = True

        st.success(f"✅ {section_name} polishing completed!")
        st.rerun()

    def _check_export_readiness(self) -> Tuple[bool, str]:
        """
        Check if all sections have final versions selected and ready for export.

        Returns:
            tuple: (is_ready, message)
        """
        if "comparison_session" not in st.session_state:
            return False, "Comparison session not started"

        session = st.session_state.comparison_session
        sections = SessionUtils.get_resume_sections()

        completed_sections = []
        pending_sections = []

        for section_name in sections.keys():
            final_version_key = f"{section_name}_final_version"
            if final_version_key in session:
                completed_sections.append(section_name)
            else:
                pending_sections.append(section_name)

        if pending_sections:
            return (
                False,
                f"Please complete selection for: {', '.join(pending_sections)}",
            )

        if not completed_sections:
            return False, "No sections have been processed yet"

        return True, f"Ready to export! {len(completed_sections)} sections completed"

    def _export_resume_pdf(self, sections) -> str:
        """
        Export the final selected resume sections as a PDF.
        Returns:
            str: Path to the generated PDF file
        """
        logger.info("Starting PDF export process")

        try:
            # 1) 收集最终内容（右侧 polished）
            final_sections = sections
            if not final_sections:
                raise ValueError("No final sections available for export")

            # 2) 转换为生成器需要的数据结构
            logger.info("Converting sections to generator format")
            resume_data = GeneratorUtils.convert_sections_to_generator_format(
                final_sections
            )

            logger.warning(
                f"resume_data: {json.dumps(resume_data, ensure_ascii=False, indent=2)}"
            )

            # 3) 生成临时输出目录和无扩展名的 base 路径
            temp_dir = tempfile.mkdtemp(prefix="resumix_export_")
            pdf_base = os.path.join(temp_dir, "resumix_final_resume")  # 不带 .pdf
            logger.info(f"Generating PDF at {pdf_base}")

            # 4) 使用多进程生成 PDF（macOS/Linux，去掉所有 Windows 兼容）
            from multiprocessing import get_context

            ctx = get_context("spawn")  # 更稳妥，避免 fork 带来的库状态问题

            proc = ctx.Process(
                target=_pdf_worker, args=(resume_data, pdf_base), daemon=True
            )
            proc.start()
            proc.join(timeout=300)  # 可按需调整超时秒数

            if proc.is_alive():
                proc.terminate()
                raise TimeoutError("PDF generation timed out in child process")

            if proc.exitcode != 0:
                # 子进程失败，读取错误详情
                err_file = pdf_base + ".err.txt"
                details = ""
                if os.path.exists(err_file):
                    try:
                        with open(err_file, "r", encoding="utf-8") as f:
                            details = "\n" + f.read()
                    except Exception:
                        pass
                raise RuntimeError(
                    f"PDF generator process failed (exitcode={proc.exitcode}).{details}"
                )

            # 5) 确认 PDF 实际落盘（稳健查找）
            pdf_file = pdf_base + ".pdf"
            if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 0:
                logger.info(f"PDF successfully created at {pdf_file}")
                return pdf_file

            # 兜底：有的生成器/模板可能输出为固定名
            alt = os.path.join(temp_dir, "resume.pdf")
            if os.path.exists(alt) and os.path.getsize(alt) > 0:
                logger.info(f"PDF created at alternate path {alt}")
                return alt

            raise RuntimeError("PDF file was not created")

        except Exception as e:
            logger.error(f"Failed to export PDF: {e}")
            raise

    def _render_export_section(self, sections: Dict[str, SectionBase]):
        """Render export section - always visible with different states based on readiness."""
        st.divider()
        # st.markdown("### 📄 Export Resume")

        # Check export readiness
        # is_ready, message = self._check_export_readiness()
        # is_ready, message = True, ""

        # if is_ready:
        # st.success(f"✅ {message}")

        # Export button when ready
        if st.button("📄 Export Final Resume PDF", type="primary"):
            try:
                with st.spinner("Generating PDF..."):
                    pdf_path = self._export_resume_pdf(sections=sections)

                # Provide download
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="⬇️ Download Resume PDF",
                            data=pdf_file.read(),
                            file_name="my_final_resume.pdf",
                            mime="application/pdf",
                        )
                    st.success("✅ PDF generated successfully!")
                else:
                    st.error("PDF generation failed")

            except Exception as e:
                st.error(f"Export failed: {str(e)}")
                logger.error(f"PDF generation error: {e}")
        # else:
        #     # Show current status and disabled button
        #     st.info(f"📋 {message}")

        #     # Disabled export button with helpful message
        #     st.button(
        #         "📄 Export Final Resume PDF",
        #         type="secondary",
        #         disabled=True,
        #         help="Complete all section selections to enable export",
        #     )

        #     # Show progress
        #     if "comparison_session" in st.session_state:
        #         session = st.session_state.comparison_session
        #         sections = SessionUtils.get_resume_sections()

        #         completed_count = 0
        #         total_count = len(sections)

        #         for section_name in sections.keys():
        #             final_version_key = f"{section_name}_final_version"
        #             if final_version_key in session:
        #                 completed_count += 1

        #         if total_count > 0:
        #             progress = completed_count / total_count
        #             st.progress(
        #                 progress,
        #                 text=f"Progress: {completed_count}/{total_count} sections completed",
        #             )

        #             # Show which sections are remaining
        #             pending_sections = []
        #             for section_name in sections.keys():
        #                 final_version_key = f"{section_name}_final_version"
        #                 if final_version_key not in session:
        #                     pending_sections.append(
        #                         section_name.replace("_", " ").title()
        #                     )

        #             if pending_sections:
        #                 st.caption(f"Remaining sections: {', '.join(pending_sections)}")
