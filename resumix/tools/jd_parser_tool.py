from typing import Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from resumix.section_parser.jd_vector_parser import JDVectorParser
import json
from resumix.utils.logger import logger


class JDParserInput(BaseModel):
    text: str = Field(
        ..., description="Raw job description text (e.g., from website or JD document)"
    )


class JDParserTool(BaseTool):
    name: str = "jd_parser"
    description: str = (
        "Parses a raw job description into structured sections, such as Overview, Responsibilities, "
        "Basic Requirements, and Preferred Requirements. Uses LLM with vector fallback."
    )
    args_schema: Type[BaseModel] = JDParserInput

    def _run(self, text: str) -> str:
        parser = JDVectorParser()
        sections = parser.parse(text)

        result = {
            key: value.parsed_data.get("raw", "") for key, value in sections.items()
        }

        logger.info(f"JDParserTool result: {result}")
        return json.dumps(result, ensure_ascii=False, indent=2)

    def _arun(self, text: str):
        raise NotImplementedError("JDParserTool does not support async")
