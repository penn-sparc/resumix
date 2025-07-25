# dispatcher/prompt_dispatcher.py
from resumix.backend.prompt.prompt_templates import (
    PROMPT_MAP,
    SCORE_PROMPT_MAP,
    TECHSTACK_TAILORING_PROMPT,
    TAILORING_PROMPT,
)
from resumix.shared.section.section_base import SectionBase
from enum import Enum
from typing import List
from loguru import logger
import threading


class PromptMode(str, Enum):
    DEFAULT = "default"
    TAILOR = "tailor"
    OPTIMIZE = "optimize"
    TECH_STACK = "tech_stack"
    AGENT = "agent"


class PromptDispatcher:
    """
    将结构化 Section 转换为对应的 Prompt（单例）
    """

    _instance = None
    _lock = threading.Lock()  # 线程安全

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(PromptDispatcher, cls).__new__(cls)
                    cls._instance._init_internal()
        return cls._instance

    def _init_internal(self):
        self.prompt_templates = PROMPT_MAP

    def get_prompt(
        self, section: SectionBase, mode: PromptMode = PromptMode.DEFAULT
    ) -> str:
        """
        根据 section 名称选取 prompt，并将 raw_text 插入 <CV_TEXT>
        """
        prompt = self.prompt_templates.get(section.name)
        if not prompt and mode != "tailor":
            raise ValueError(f"No prompt found for section: {section.name}")

        if not prompt:
            raise ValueError(f"No prompt found for section: {section.name}")

        placeholder = "<CV_TEXT>"

        if mode == PromptMode.TAILOR:
            prompt_for_tailoring = self.get_tailoring_prompt(section.raw_text)
            prompt = prompt.replace(placeholder, prompt_for_tailoring)

            return prompt_for_tailoring + prompt

        return prompt.replace(placeholder, section.raw_text.strip())

    def get_score_prompt(
        self,
        section: SectionBase,
        jd_section_basic: SectionBase,
        jd_section_preferred: SectionBase,
    ) -> str:
        """
        用于评分的 prompt 构造
        """
        prompt = SCORE_PROMPT_MAP[section.name]
        placeholder = "<CV_TEXT>"
        jd_basic_placeholder = "<JD_BASIC_TEXT>"
        jd_preferred_placeholder = "<JD_PREFERRED_TEXT>"

        # 替换 CV 和 JD 的占位符
        prompt = prompt.replace(placeholder, section.raw_text.strip())

        prompt = prompt.replace(jd_basic_placeholder, jd_section_basic.raw_text.strip())

        if jd_section_preferred:
            prompt = prompt.replace(
                jd_preferred_placeholder, jd_section_preferred.raw_text.strip()
            )

        return prompt

    def get_tailoring_prompt(self, full_cv: str) -> str:
        """
        用于整体润色的 prompt 构造
        """
        prompt = self.prompt_templates["tailor"]
        return prompt.replace("<CV_TEXT>", full_cv.strip())

    def get_tech_stack_prompt(
        self, section: SectionBase, tech_stacks: List[str], job_positions: List[str]
    ) -> str:

        tech_stacks_str = ", ".join(tech_stacks)
        job_positions_str = ", ".join(job_positions)

        logger.info(section)
        logger.info(type(section))

        content = section.raw_text

        prompt = TECHSTACK_TAILORING_PROMPT.format(
            CV_TEXT=content, TECH_STACK=tech_stacks_str, JOB_POSITION=job_positions_str
        )

    def get_rag_prompt(
        self,
        section: SectionBase,
        tech_stacks: List[str],
        job_positions: List[str],
        retrieved_context: str,
    ) -> str:
        prompt = f"""
You are a professional resume rewriting assistant with deep understanding of technical hiring expectations.

Your task is twofold:
1. ✍️ If the resume section is relevant to the target job and tech stack, rewrite it to better showcase achievements, technical skills, and impact.
2. 📚 If the resume section does not sufficiently reflect the required skills or experience, suggest **what knowledge or experience the candidate should gain or highlight**, based on the job requirements and reference materials.

---

## 🎯 Target Job Positions:
{', '.join(job_positions)}

## 🧰 Relevant Tech Stack:
{', '.join(tech_stacks)}

## 📚 Reference Context (retrieved from job descriptions or exemplary resumes):
{retrieved_context.strip()}

---

Now process the following resume section accordingly.

## 📝 Original Resume Section:
{section.raw_text.strip()}

---

## ✨ Your Output Should Include:
- ✨ Rewritten Resume Section (if applicable)
- 📌 Suggestions for knowledge, tools, or experience the candidate can learn to better match the job (if needed)
"""

        return prompt
