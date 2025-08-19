from resumix.shared.section.section_base import SectionBase
from resumix.config.config import Config
import requests
from typing import Dict, Any, List
from resumix.shared.utils.logger import logger
import streamlit as st
import json

CONFIG = Config().config


def compare_section_api(section: SectionBase, jd_content: str):
    logger.info("Calling compare API")
    payload = {"data": {"section": section.to_dict(), "jd_content": jd_content}}

    response = requests.post(
        url=CONFIG.BACKEND.HOST + "/compare/section", json=payload, timeout=60
    )

    # logger.info(response.json())

    # logger.info(type(response.json().get("data", {})))

    return response.json().get("data", {})


def check_serializability(obj, prefix="root"):
    try:
        json.dumps(obj)
    except TypeError as e:
        if isinstance(obj, dict):
            for k, v in obj.items():
                check_serializability(v, prefix=f"{prefix}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_serializability(item, prefix=f"{prefix}[{i}]")
        else:
            logger.error(
                f"❌ Non-serializable value at {prefix}: {repr(obj)} ({type(obj)}) — {e}"
            )


def format_section_api(section: SectionBase, jd_content: str):
    try:
        logger.info("🚀 Calling compare API")

        # ✅ 正确地序列化 SectionBase 子类
        section_dict = section.model_dump(mode="json", exclude_none=True)

        logger.info(f"🧾 Section type: {type(section)}")

        # ✅ 这里只打印 section_dict，而不是 section 本体
        # try:
        #     logger.info(
        #         f"🧾 Section dict preview: {json.dumps(section_dict, indent=2, ensure_ascii=False)}"
        #     )
        # except Exception as e:
        #     logger.warning(f"⚠️ Failed to json.dumps section_dict: {e}")

        payload = {
            "data": {
                "section": section_dict,
                "jd_content": jd_content,
            }
        }

        check_serializability(payload)

        # ✅ 只打印真正是 dict 的 payload，不要含任何对象
        # try:
        #     logger.info(
        #         f"📦 Payload preview: {json.dumps(payload, indent=2, ensure_ascii=False)}"
        #     )
        # except Exception as e:
        #     logger.warning(f"⚠️ Failed to json.dumps payload: {e}")

        # ✅ 发送请求
        response = requests.post(
            url=CONFIG.BACKEND.HOST + "/compare/format", json=payload, timeout=60
        )

        # logger.info(f"✅ Response status code: {response.status_code}")
        # logger.info(f"📨 Response content: {response.text}")

        response_data = response.json().get("data", {})
        # logger.info(f"📦 Parsed data type: {type(response_data)}")

        return response_data

    except Exception as e:
        logger.error(f"❌ Failed to call compare/format API: {e}")
        raise


def score_section_api(
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    每次调用score API 只processing一个 section
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
        st.error(f"score服务调用失败: {str(e)}")


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
