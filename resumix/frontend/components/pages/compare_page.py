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


# 顶层 worker，必须放在module作用域，multiprocessing 才能 pickle 到
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

    def render(self):
        "检查是否满足所有前置条件"
        can_proceed, error = self._check_prerequisites()
        if not can_proceed:
            st.warning(error)
            return

        sections = self.sections
        jd_content = self._get_jd_content()  # 获取职位描述content

        # filter_sections = {}
        # filtered_sections = {}

        # for section_name, section_obj in sections.items():
        #     if section_name in filter_sections:
        #         logger.info(f"Skipping section {section_name} as per skip_mask")
        #         continue
        #     filtered_sections[section_name] = section_obj

        # 初始话 comparison_session
        if "comparison_session" not in st.session_state:
            st.session_state["comparison_session"] = {}

        if "sections_ready" not in st.session_state.comparison_session:
            st.session_state.comparison_session["sections_ready"] = False

        st.session_state.comparison_session.setdefault("jd_content", jd_content)
        st.session_state.comparison_session.setdefault("comparison_started", False)

        # 如果比较尚未开始，启动比较
        # if not st.session_state.comparison_session["comparison_started"]:
        #     if st.button("🚀 Start Comparison", type="primary"):
        #         st.session_state.comparison_session["comparison_started"] = True
        #         st.rerun()
        # else:
        # 开始processing和显示每个部分的比较result
        # if not st.session_state.comparison_session["sections_ready"]:
        st.session_state.comparison_session["sections_ready"] = True
        self._format_sections(sections, jd_content)
        self._ensure_sections_are_rewritten(sections, jd_content)

        self._render_section_comparisons(sections, jd_content)

        try:
            sections_copy = copy.deepcopy(sections)
        except Exception as e:
            logger.warning(f"deepcopy sections failed: {e}; fallback to shallow copy")
            sections_copy = {k: copy.copy(v) for k, v in sections.items()}

        for name, section in sections_copy.items():
            logger.info(
                f"Section {name} - raw_text: {section.raw_text}..."
            )  # 限制输出长度
            logger.info(f"Section {name} - json_text: {section.json_text}")
            logger.info(f"Section {name} - rewritten_text: {section.rewritten_text}")

        self._render_export_section(sections_copy)

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

    def _ensure_sections_are_rewritten(
        self, sections: Dict[str, SectionBase], jd_content: str
    ):

        logger.info("Ensuring all sections are rewritten with compare_section_api")
        futures = {}
        # 使用 ThreadPoolExecutor 并发重写resume各部分
        with ThreadPoolExecutor(max_workers=6) as executor:
            for section_name, section_obj in sections.items():
                # Only skip if both json_text and rewritten_text are populated
                if (
                    section_obj.json_text is not None
                    and section_obj.rewritten_text is not None
                ):
                    logger.info(
                        f"Skipping section {section_name} - both json_text and rewritten_text are populated"
                    )
                    continue

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
                section_obj = sections[section_name]
                try:
                    result = future.result()

                    # 获取重写文本，processing为空的情况
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
                    SessionUtils.get_resume_sections()[section_name] = section_obj

                except Exception as e:
                    logger.error(f"Failed to rewrite section {section_name}: {e}")
                    section_obj.rewritten_text = self.T["compare"][
                        "polishing_failed"
                    ].format(error=str(e))

    def _render_section_comparisons(
        self, sections: Dict[str, SectionBase], jd_content: str
    ):
        for section_name, section_obj in sections.items():
            # Ensure sections have at least some content for rendering
            if section_obj.json_text is None:
                section_obj.json_text = section_obj.raw_text or "⚠️ No content available"
            if section_obj.rewritten_text is None:
                logger.error(
                    f"Section {section_name} has no rewritten_text; using json_text as fallback"
                )

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

            # render用户选择的按钮
            choice = self._render_version_choice_buttons(
                section_name, left_version, right_version
            )
            if choice:
                # create the new section object
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
                # Remove from skip_mask if it exists (safe operation)
                if section_name in self.skip_mask:
                    self.skip_mask.remove(section_name)

                original_section = SessionUtils.get_resume_sections()[section_name]
                new_section = copy.deepcopy(original_section)

                # swap the raw_text and rewritten_text
                new_section.raw_text = original_section.rewritten_text
                new_section.json_text = original_section.rewritten_text
                new_section.rewritten_text = original_section.rewritten_text

                SessionUtils.get_resume_sections()[section_name] = new_section

                # update current version
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
            # 更新状态
            st.session_state.comparison_session["sections_ready"] = False
            st.rerun()

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

    def _gather_final_sections(self, sections) -> Dict[str, SectionBase]:
        """
        导出时强制使用右侧（polished）版本：
        优先 rewritten_text（右侧） -> 其次 json_text -> 再次 raw_text。
        最终把 chosen 文本回填到 json_text/rewritten_text，保证generate器统一读取的是右侧效果。
        """
        logger.info("Gathering sections (RIGHT-side polished) for export")

        # sections = SessionUtils.get_resume_sections()

        for name, sec in sections.items():
            # 确保每个 section 都有 raw_text，避免导出时出现空content
            logger.info(f"Processing section {name} for export")
            logger.info(f"re: {sec.rewritten_text}")
            logger.info(f"json: {sec.json_text}")
        # final_sections = {}

        # for name, sec in sections.items():
        #     # 右侧为 rewritten_text
        #     chosen = (
        #         getattr(sec, "rewritten_text", None)
        #         or getattr(sec, "json_text", None)
        #         or getattr(sec, "raw_text", None)
        #     )

        #     if not chosen:
        #         logger.warning(f"Section {name} has no content; skipping.")
        #         continue

        #     final_sections[name] = sec

        # logger.info(f"Prepared {len(final_sections)} sections for export (RIGHT side).")
        return sections

    # def _gather_final_sections(self) -> Dict[str, SectionBase]:
    #     """
    #     Gather all sections with their final selected versions.

    #     Note: The existing _handle_section_choice logic already updates section objects
    #     to contain the user's final selected content, so we just need to collect
    #     the completed sections.

    #     Returns:
    #         Dict mapping section names to their final selected SectionBase objects
    #     """
    #     logger.info("Gathering final selected sections for export")

    #     session = st.session_state.comparison_session
    #     sections = SessionUtils.get_resume_sections()
    #     final_sections = {}

    #     for section_name, section_obj in sections.items():
    #         final_version_key = f"{section_name}_final_version"

    #         if final_version_key in session:
    #             # The section object already contains the user's final selected content
    #             # thanks to the existing _handle_section_choice logic
    #             final_sections[section_name] = section_obj
    #             logger.info(f"Added {section_name} to final sections")
    #         else:
    #             logger.warning(
    #                 f"No final version selected for {section_name}, skipping"
    #             )

    #     logger.info(f"Gathered {len(final_sections)} final sections for export")
    #     return final_sections

    def _export_resume_pdf(self, sections) -> str:
        """
        Export the final selected resume sections as a PDF.
        Returns:
            str: Path to the generated PDF file
        """
        logger.info("Starting PDF export process")

        try:
            # 1) 收集最终content（右侧 polished）
            # final_sections = self._gather_final_sections(sections=sections)
            final_sections = sections
            if not final_sections:
                raise ValueError("No final sections available for export")

            # 2) 转换为generate器需要的数据结构
            logger.info("Converting sections to generator format")
            resume_data = GeneratorUtils.convert_sections_to_generator_format(
                final_sections
            )

            logger.warning(
                f"resume_data: {json.dumps(resume_data, ensure_ascii=False, indent=2)}"
            )

            # 3) generate临时输出目录和无扩展名的 base 路径
            temp_dir = tempfile.mkdtemp(prefix="resumix_export_")
            pdf_base = os.path.join(temp_dir, "resumix_final_resume")  # 不带 .pdf
            logger.info(f"Generating PDF at {pdf_base}")

            # 4) 使用多进程generate PDF（macOS/Linux，去掉所有 Windows 兼容）
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

            # 兜底：有的generate器/模板可能输出为固定名
            alt = os.path.join(temp_dir, "resume.pdf")
            if os.path.exists(alt) and os.path.getsize(alt) > 0:
                logger.info(f"PDF created at alternate path {alt}")
                return alt

            raise RuntimeError("PDF file was not created")

        except Exception as e:
            logger.error(f"Failed to export PDF: {e}")
            raise

    # def _export_resume_pdf(self) -> str:
    #     """
    #     Export the final selected resume sections as a PDF.

    #     Returns:
    #         str: Path to the generated PDF file
    #     """
    #     logger.info("Starting PDF export process")

    #     try:
    #         # Setup LaTeX environment for Windows (add MikTeX and Perl to PATH)
    #         current_env = os.environ.copy()
    #         miktex_path = "C:\\Program Files\\MiKTeX 2.9\\miktex\\bin\\x64"
    #         perl_path = "C:\\Strawberry\\perl\\bin"

    #         for path in [miktex_path, perl_path]:
    #             if path not in os.environ.get("PATH", ""):
    #                 os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + path

    #         # Gather final sections
    #         final_sections = self._gather_final_sections()

    #         if not final_sections:
    #             raise ValueError("No final sections available for export")

    #         # Convert to generator format using GeneratorUtils
    #         logger.info("Converting sections to generator format")
    #         resume_data = GeneratorUtils.convert_sections_to_generator_format(
    #             final_sections
    #         )

    #         # Create temporary file for PDF output
    #         temp_dir = tempfile.mkdtemp()
    #         pdf_filename = "resumix_final_resume"
    #         pdf_path = os.path.join(temp_dir, pdf_filename)

    #         logger.info(f"Generating PDF at {pdf_path}")

    #         # Generate PDF using the existing generator (unchanged!)
    #         try:
    #             import threading
    #             t = threading.Thread(
    #                 target=generate_pdf,
    #                 args=(resume_data, pdf_path),
    #             )
    #             generate_pdf(json_resume=resume_data, output_path=pdf_path)
    #         except Exception as e:
    #             # The original generator might "fail" due to Unicode warnings but still create the PDF
    #             logger.warning(
    #                 f"Generator reported error but PDF may still be created: {e}"
    #             )

    #         # Check if PDF was actually created (it usually is, despite warnings)
    #         pdf_file = f"{pdf_path}.pdf"
    #         if os.path.exists(pdf_file):
    #             logger.info(f"PDF successfully created at {pdf_file}")
    #             return pdf_file
    #         else:
    #             raise Exception("PDF file was not created")

    #     except Exception as e:
    #         logger.error(f"Failed to export PDF: {e}")
    #         raise

    def _render_export_section(self, sections: Dict[str, SectionBase]):
        """Render export section - always visible with different states based on readiness."""
        st.divider()
        st.markdown("### 📄 Export Resume")

        # Check export readiness
        # is_ready, message = self._check_export_readiness()
        is_ready, message = True, ""

        if is_ready:
            st.success(f"✅ {message}")

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
        else:
            # Show current status and disabled button
            st.info(f"📋 {message}")

            # Disabled export button with helpful message
            st.button(
                "📄 Export Final Resume PDF",
                type="secondary",
                disabled=True,
                help="Complete all section selections to enable export",
            )

            # Show progress
            if "comparison_session" in st.session_state:
                session = st.session_state.comparison_session
                sections = SessionUtils.get_resume_sections()

                completed_count = 0
                total_count = len(sections)

                for section_name in sections.keys():
                    final_version_key = f"{section_name}_final_version"
                    if final_version_key in session:
                        completed_count += 1

                if total_count > 0:
                    progress = completed_count / total_count
                    st.progress(
                        progress,
                        text=f"Progress: {completed_count}/{total_count} sections completed",
                    )

                    # Show which sections are remaining
                    pending_sections = []
                    for section_name in sections.keys():
                        final_version_key = f"{section_name}_final_version"
                        if final_version_key not in session:
                            pending_sections.append(
                                section_name.replace("_", " ").title()
                            )

                    if pending_sections:
                        st.caption(f"Remaining sections: {', '.join(pending_sections)}")
