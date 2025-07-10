from fastapi import APIRouter
from resumix.backend.service.score_service import ScoreService
from resumix.shared.model.schema.schema import (
    BaseResponse,
    BaseRequest,
)
from resumix.shared.utils.llm_client import LLMClient
from resumix.shared.utils.logger import logger
from resumix.shared.section.section_base import SectionBase


router = APIRouter(prefix="/score", tags=["score"])

score_service = ScoreService()


@router.post("/section", response_model=BaseResponse)
def score_section(req: BaseRequest):
    data = req.data
    section_data = data.get("section")
    jd_section_basic = data.get("jd_section_basic")
    jd_section_preferred = data.get("jd_section_preferred", None)

    if section_data is None or jd_section_basic is None:
        return BaseResponse(code=1, message="Missing required fields")

    try:
        section_obj = SectionBase(**section_data)
        jd_basic_obj = SectionBase(**jd_section_basic)
        jd_preferred_obj = (
            SectionBase(**jd_section_preferred) if jd_section_preferred else None
        )

        result = score_service.score_resume(
            resume_section=section_obj,
            jd_section_basic=jd_basic_obj,
            jd_section_preferred=jd_preferred_obj,
        )
        return BaseResponse(data=result)

    except Exception as e:
        return BaseResponse(code=2, message=f"Scoring failed: {e}")


@router.post("/sections", response_model=BaseResponse)
def score_sections(req: BaseRequest):
    data = req.data
    sections = data.get("sections", None)
    jd_section_basic = data.get("jd_section_basic", None)
    jd_section_preferred = data.get("jd_section_preferred", None)

    if sections is None:
        return BaseResponse(code=1)

    jd_section_basic_obj = SectionBase(**jd_section_basic)
    jd_section_preferred_obj = SectionBase(**jd_section_preferred)

    results = {}

    for section in sections:
        section_obj = SectionBase(**section)

        try:
            result = score_service.score_resume(
                resume_section=section_obj,
                jd_section_preferred=jd_section_preferred_obj,
                jd_section_basic=jd_section_basic_obj,
            )
        except Exception as e:
            result = {"error": str(e)}

        results[section["name"]] = result
    return BaseResponse(data=result)
