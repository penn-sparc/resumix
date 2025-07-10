from resumix.shared.section.section_base import SectionBase
from resumix.config.config import Config
import requests
from typing import Dict, Any, List
from resumix.shared.utils.logger import logger
import streamlit as st


CONFIG = Config().config


def compare_section_api(section: SectionBase, jd_content: str):
    logger.info("Calling compare API")
    payload = {"data": {"section": section.model_dump(), "jd_content": jd_content}}

    response = requests.post(
        url=CONFIG.BACKEND.HOST + "/compare/section", json=payload, timeout=60
    )

    logger.info(response.json())

    logger.info(type(response.json().get("data", {})))

    return response.json().get("data", {})


def score_section_api(
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    每次调用评分 API 只处理一个 section
    """

    logger.info("Calling score API")
    try:
        response = requests.post(
            url=CONFIG.BACKEND.HOST + "/score/section",
            json=payload,
            timeout=60,
        )

        response.raise_for_status()

        return response.json().get("data", {})

    except requests.exceptions.RequestException as e:
        logger.exception("❌ Failed to call score API")
        st.error(f"评分服务调用失败: {str(e)}")


def process_section_api(
    section: SectionBase, tech_stacks: List[str], job_positions: List[str]
) -> str:

    logger.info("Calling process API")

    payload = {
        "data": {
            "section": section.model_dump(),
            "tech_stack": tech_stacks,
            "job_positions": job_positions,
        }
    }
    try:
        response = requests.post(CONFIG.BACKEND.HOST + "/agent/rewrite", json=payload)
        response.raise_for_status()
        return response.json().get("data", None)
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to optimize section {section.name}: {e}")
        logger.exception(f"❌ RequestException while optimizing section {section.name}")
    except Exception as e:
        st.error(f"❌ Failed to optimize section {section.name}: {e}")
        logger.exception(f"❌ Unexpected error while optimizing section {section.name}")
