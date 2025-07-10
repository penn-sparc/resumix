# resumix/backend/service/agent_service.py

from resumix.shared.section.section_base import SectionBase
from resumix.backend.rewriter.resume_rewriter import ResumeRewriter
from resumix.shared.utils.llm_client import LLMClient


class CompareService:

    def __init__(self):
        self.rewriter = ResumeRewriter(LLMClient())

    def compare_resume(self, section: SectionBase, jd_content: str) -> SectionBase:

        try:
            rewritten_section = self.rewriter.rewrite_section(section, jd_content)
            return rewritten_section
        except Exception as e:
            raise Exception(f"Failed to compare resume: {e}")
