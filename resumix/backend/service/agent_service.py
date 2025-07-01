from resumix.backend.service.base_service import BaseService
from resumix.shared.section.section_base import SectionBase
from typing import List
from resumix.shared.utils.logger import logger
from resumix.backend.rewriter.resume_rewriter import TechRewriter
from resumix.shared.utils.llm_client import LLMClient


class AgentService(BaseService):
    def __init__(self, llm: LLMClient):
        super().__init__()
        self.llm = llm
        self.rewriter = TechRewriter(self.llm)


    def optimize_resume(
        self, sections: List[SectionBase], tech_stacks: List[str], job_positions: List[str]
    ) -> str:
        return self.rewriter.rewrite_section(sections, tech_stacks, job_positions)
