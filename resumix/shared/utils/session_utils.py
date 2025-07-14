from resumix.shared.utils.ocr_utils import OCRUtils
from resumix.backend.section_parser.vector_parser import VectorParser
from resumix.backend.section_parser.jd_vector_parser import JDVectorParser
from resumix.shared.utils.logger import logger
from resumix.shared.utils.url_fetcher import UrlFetcher
import streamlit as st
from config.config import Config
import easyocr
from resumix.shared.utils.i18n import LANGUAGES
from paddleocr import PaddleOCR

CONFIG = Config().config


@st.cache_data(show_spinner="正在提取简历文本...")
def extract_text_from_pdf(file):
    logger.info("Extracting text from PDF file...")

    ocr_model = None

    # Force EasyOCR for better performance
    if CONFIG.OCR.USE_MODEL == "easyocr":
        logger.info("Using EasyOCR for text extraction")
        ocr_model = easyocr.Reader(
            ["en"],  # English only for better performance
            gpu=False,  # Force CPU for stability
            model_storage_directory=CONFIG.OCR.EASYOCR.DIRECTORY,
        )
    elif CONFIG.OCR.USE_MODEL == "paddleocr":
        logger.info("Using PaddleOCR for text extraction")
        try:
            # Try with default parameters first - use English for resumes
            ocr_model = PaddleOCR(use_angle_cls=True, lang="en")
        except AttributeError as e:
            if "set_mkldnn_cache_capacity" in str(e):
                # Fallback to alternative initialization for compatibility
                try:
                    ocr_model = PaddleOCR(use_angle_cls=False, lang="en", use_gpu=False)
                except Exception as fallback_error:
                    # If PaddleOCR still fails, fall back to EasyOCR
                    print(
                        f"PaddleOCR failed, falling back to EasyOCR: {fallback_error}"
                    )
                    ocr_model = easyocr.Reader(
                        ["en"],  # English only
                        gpu=False,
                        model_storage_directory="resumix/models/easyocr",
                    )
            else:
                raise e

    # Balanced OCR settings - moderate quality for better text extraction
    ocr = OCRUtils(ocr_model, dpi=75, keep_images=False)

    return ocr.extract_text(
        file, max_pages=3
    )  # Process up to 3 pages instead of just 1


def extract_job_description(jd_url):
    jd_parser = JDVectorParser()
    jd_content = jd_parser.parse(jd_url)
    return jd_content


class SessionUtils:
    @staticmethod
    @st.cache_data(show_spinner="提取简历文本")
    def get_resume_text():
        if "resume_text" not in st.session_state:
            if "uploaded_file" not in st.session_state:
                raise ValueError("No resume file uploaded.")
            else:
                st.session_state.resume_text = extract_text_from_pdf(
                    st.session_state.uploaded_file
                )
        return st.session_state.resume_text

    @staticmethod
    def upload_resume_file(file):
        st.session_state.uploaded_file = file

    @staticmethod
    def get_job_description_content():
        url = st.session_state.get("jd_url", "")
        cached_url = st.session_state.get("jd_cached_url", "")

        # 如果 URL 不存在或没有变化，不重新解析
        if "jd_content" not in st.session_state or url != cached_url:
            if not url:
                logger.info("No JD provided.")
                return "No job description URL provided."
            logger.info(f"Update JD URL to {url}")
            st.session_state.jd_content = extract_job_description(url)
            st.session_state.jd_cached_url = url  # 更新缓存 URL
        else:
            logger.info("Load JD from cache.")

        return st.session_state.jd_content

    @staticmethod
    @st.cache_data(show_spinner="提取简历段落")
    def get_resume_sections():
        if "resume_sections" not in st.session_state:
            text = SessionUtils.get_resume_text()
            parser = VectorParser()
            st.session_state.resume_sections = parser.parse_resume(text)
        return st.session_state.resume_sections

    @staticmethod
    def get_jd_sections():
        url = st.session_state.get("jd_url", "").strip()
        cached_url = st.session_state.get("jd_cached_url", "").strip()

        if not url:
            logger.warning("[SessionUtils] JD URL 未设置，跳过更新")
            st.session_state.jd_sections = {"overview": ["⚠️ 未提供岗位描述链接"]}
            st.session_state.jd_content = "⚠️ 未提供岗位描述链接"
            return st.session_state.jd_sections

        # if (
        #     url == cached_url
        #     and "jd_sections" in st.session_state
        #     and "jd_content" in st.session_state
        # ):
        #     logger.info(f"[SessionUtils] 当前url: {url}, 缓存url: {url}")
        #     logger.info("[SessionUtils] JD URL 未变化，使用缓存内容")
        #     for section in st.session_state.jd_sections.values():
        #         logger.info(f"[SessionUtils] section: {section}")
        #     return st.session_state.jd_sections
        try:
            logger.info(f"[SessionUtils] Fetching and parsing JD from: {url}")
            jd_text = UrlFetcher.fetch(url)
            st.session_state.jd_content = jd_text

            parser = JDVectorParser()
            st.session_state.jd_sections = parser.parse(jd_text)

            st.session_state.jd_cached_url = url  # 缓存 URL

            return st.session_state.jd_sections

        except Exception as e:
            logger.error(f"[SessionUtils] JD 更新失败: {e}")
            st.session_state.jd_sections = {"overview": [f"❌ 无法解析 JD 内容：{e}"]}
            st.session_state.jd_content = f"❌ 无法获取 JD 网页内容：{e}"
            return st.session_state.jd_sections

    @staticmethod
    def get_section_raw(section_name: str) -> str:
        sections = SessionUtils.get_resume_sections()
        return sections.get(section_name).raw_text if section_name in sections else ""

    @staticmethod
    def get_section_data(section_name: str) -> dict:
        sections = SessionUtils.get_resume_sections()
        return sections.get(section_name).to_dict() if section_name in sections else {}

    @staticmethod
    def get_language():
        if "lang" not in st.session_state:
            st.session_state.lang = "en"
        return st.session_state.lang

    @staticmethod
    def get_T():
        return LANGUAGES[SessionUtils.get_language()]
