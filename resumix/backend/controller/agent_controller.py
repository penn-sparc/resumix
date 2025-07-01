from fastapi import APIRouter
from resumix.backend.service.agent_service import AgentService
from resumix.shared.model.schema.schema import (
    TechOptimizeResponse,
    TechOptimizeRequest,
    BaseResponse,
    BaseRequest,
)
from resumix.shared.utils.llm_client import LLMClient
from resumix.shared.utils.logger import logger
from resumix.shared.section.section_base import SectionBase



router = APIRouter(prefix="/agent", tags=["agent"])
service = AgentService(llm=LLMClient())



@router.post("/rewrite", response_model=BaseResponse)
def optimize_resume(req: BaseRequest):
    data = req.data
    
    section = data.get("section", None)
    tech_stack = data.get("tech_stack", None)
    
    section_obj = SectionBase(**section)
    
    logger.info(section_obj)
    logger.info(type(section_obj))
    
    if section is None or tech_stack is None:
        return BaseResponse(code=1)
    
    
    
    result = service.optimize_resume(section_obj, req.data["tech_stack"], req.data["job_positions"])
    return BaseResponse(data=result)

# class AgentController:
#     def __init__(self):
#         self.router = APIRouter(prefix="/agent", tags=["agent"])
#         self.service = AgentService()

#         # 手动注册路由到 self.router
#         self.router.add_api_route(
#             path="/rewrite",
#             endpoint=self.optimize_resume,
#             methods=["POST"],
#             response_model=TechOptimizeResponse,
#         )

#     def optimize_resume(self, req: TechOptimizeRequest) -> TechOptimizeResponse:
#         result = self.service.optimize_resume(req)
#         return TechOptimizeResponse(optimized_resume_text=result)