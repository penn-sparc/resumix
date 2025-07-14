# resumix/backend/service/agent_service.py

from resumix.shared.section.section_base import SectionBase
from resumix.backend.rewriter.resume_rewriter import ResumeRewriter
from resumix.shared.utils.llm_client import LLMClient
from resumix.backend.prompt.prompt_dispatcher import PromptDispatcher, PromptMode


class CompareService:

    def __init__(self):
        self.rewriter = ResumeRewriter(LLMClient())

    def format_resume(self, section: SectionBase, jd_content: str) -> SectionBase:

        try:
            rewritten_section = self.rewriter.rewrite_section(
                section, jd_content, PromptMode.DEFAULT
            )
            return rewritten_section
        except Exception as e:
            raise Exception(f"Failed to compare resume: {e}")

    def compare_resume(self, section: SectionBase, jd_content: str) -> SectionBase:

        try:
            rewritten_section = self.rewriter.rewrite_section(
                section, jd_content, PromptMode.TAILOR
            )
            return rewritten_section
        except Exception as e:
            raise Exception(f"Failed to compare resume: {e}")
