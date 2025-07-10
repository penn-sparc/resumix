# resumix/backend/controller/agent_controller.py

from fastapi import APIRouter
from resumix.backend.service.compare_service import CompareService
from resumix.shared.model.schema.schema import BaseResponse, BaseRequest

from resumix.shared.utils.logger import logger
from resumix.shared.section.section_base import SectionBase

router = APIRouter(prefix="/compare", tags=["compare"])
service = CompareService()


@router.post("/section", response_model=BaseResponse)
def compare_resume(req: BaseRequest):
    try:
        data = req.data

        section = data.get("section", None)
        section_obj = SectionBase(**section)
        logger.info(f"section: {section}")
        jd_content = data.get("jd_content", "")

        if section is None:
            raise Exception("Section is required")

        result = service.compare_resume(section_obj, jd_content)

        json = {"rewritten_text": result}

        return BaseResponse(data=json)
    except Exception as e:
        logger.error(f"Compare resume failed: {e}")
        return BaseResponse(code=1, message=str(e))
