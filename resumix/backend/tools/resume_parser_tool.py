from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any
import json

from resumix.backend.job_parser.resume_parser import ResumeParser


class ResumeParserInput(BaseModel):
    text: str = Field(description="The text content of the resume to parse")


class ResumeParserTool(BaseTool):
    name: str = "resume_parser"
    description: str = (
        "Use this tool to analyze and extract structured information from unstructured resume text. "
        "It parses a resume into key sections such as personal information, education history, work experience, project experience, and technical skills. "
        "Each section is detected based on semantic cues and headings, and the raw text is structured for downstream processing, optimization, or evaluation tasks. "
        "Input should be a plain text version of the resume, such as OCR output or copied content. "
        "This tool is useful for resume understanding, screening, and intelligent optimization workflows."
    )

    args_schema: Type[BaseModel] = ResumeParserInput

    def _run(self, text: str) -> str:
        parser = ResumeParser()
        sections = parser.parse_resume(text)

        # 提取结构化信息（假设每个 SectionBase 都有 parsed_data 字段）
        parsed_result: Dict[str, Any] = {
            section: content.parsed_data for section, content in sections.items()
        }

        return result.model_dump_json(indent=2, ensure_ascii=False)

    def _arun(self, text: str):
        raise NotImplementedError("Async not supported for ResumeParserTool.")
