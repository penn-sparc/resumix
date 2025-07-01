from typing import Dict, List
from resumix.shared.utils import logger
from resumix.backend.prompt.prompt_dispatcher import PromptDispatcher, PromptMode
from resumix.shared.section.section_base import SectionBase


class BaseRewriter:
    def __init__(self, llm):
        self.llm = llm  # callable like: lambda prompt -> str


class ResumeRewriter(BaseRewriter):
    def __init__(self, llm):
        super().__init__(llm)

    def rewrite_section(self, section: SectionBase, jd_text: str = "") -> SectionBase:
        # 获取针对该 section 的 prompt
        prompt = PromptDispatcher().get_prompt(section)
        logger.info(f"Rewriting section '{section.name}' with LLM...")

        # 调用 LLM 接口
        rewritten_text = self.llm(prompt)

        # 写入回 section 对象
        section.rewritten_text = rewritten_text.strip()

    def rewrite_all(
        self, sections: Dict[str, SectionBase], jd_text: str = ""
    ) -> Dict[str, SectionBase]:
        rewritten = {}
        for name, section in sections.items():
            rewritten[name] = self.rewrite_section(section, jd_text)
        return rewritten


class TechRewriter(BaseRewriter):
    def __init__(self, llm):
        super().__init__(llm)

    def rewrite_section(
        self, section: SectionBase, tech_stacks: List[str], job_positions: List[str]
    ) -> SectionBase:
        
        
        prompt = PromptDispatcher().get_tech_stack_prompt(section, tech_stacks, job_positions)

        result = self.llm(prompt)

        return result

    # def rewrite(self, text: str, tech_stack: List[str]) -> str:
    #     prompt = PromptDispatcher().get_tech_stack_prompt(text, tech_stack)
    #     rewritten_text = self.llm(prompt)
    #     return rewritten_text.strip()
