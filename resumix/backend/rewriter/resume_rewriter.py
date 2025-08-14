from typing import Dict, List
from loguru import logger
from resumix.backend.prompt.prompt_dispatcher import PromptDispatcher, PromptMode
from resumix.shared.section.section_base import SectionBase
from resumix.backend.retriever.knowledge_retriever import KnowledgeRetriever


class BaseRewriter:
    def __init__(self, llm):
        self.llm = llm  # callable like: lambda prompt -> str
        self.retriever = KnowledgeRetriever()  # 用于知识检索


class ResumeRewriter(BaseRewriter):
    def __init__(self, llm):
        super().__init__(llm)

    def rewrite_section(
        self, section: SectionBase, jd_text: str = "", prompt_mode=PromptMode.DEFAULT
    ) -> str:
        # 获取针对该 section 的 prompt
        
        
        if prompt_mode == PromptMode.TAILOR:
            prompt = PromptDispatcher().get_section_tailoring_prompt(section, jd_text)
        else:
            prompt = PromptDispatcher().get_prompt(section, prompt_mode)
            logger.info(f"Rewriting section '{section.name}' with LLM...")

        # 调用 LLM 接口
        rewritten_text = self.llm(prompt)

        # 写入回 section 对象
        section.rewritten_text = rewritten_text.strip()
        return rewritten_text

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

        prompt = PromptDispatcher().get_tech_stack_prompt(
            section, tech_stacks, job_positions
        )

        result = self.llm(prompt)

        return result

    def rewrite_section_rag(
        self, section: SectionBase, tech_stacks: List[str], job_positions: List[str]
    ) -> SectionBase:
        """
        使用 RAG 模式重写简历段落
        """
        logger.info(
            f"🔍 RAG rewriting section '{section.name}' using tech stacks {tech_stacks} and positions {job_positions}."
        )
        # 1. 进行知识检索（可支持多轮/多source）
        retrieved_contexts = self.retriever.retrieve(
            section=section,
            tech_stacks=tech_stacks,
            job_positions=job_positions,
            top_k=3,  # 可调节
        )

        logger.debug(
            f"📚 Retrieved {len(retrieved_contexts)} context items for section '{section.name}'."
        )

        # 2. 拼接上下文信息为检索内容
        context_str = "\n---\n".join(retrieved_contexts)

        # 3. 构造增强型 prompt
        prompt = PromptDispatcher().get_rag_prompt(
            section=section,
            tech_stacks=tech_stacks,
            job_positions=job_positions,
            retrieved_context=context_str,
        )

        # 4. 调用 LLM
        logger.info(
            f"🤖 Calling LLM for section '{section.name}' with RAG-enhanced prompt."
        )
        result = self.llm(prompt)

        # 5. 写入 Section
        section.rewritten_text = result.strip()
        return section

    # def rewrite(self, text: str, tech_stack: List[str]) -> str:
    #     prompt = PromptDispatcher().get_tech_stack_prompt(text, tech_stack)
    #     rewritten_text = self.llm(prompt)
    #     return rewritten_text.strip()
