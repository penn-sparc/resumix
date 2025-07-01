import json

from pydantic import BaseModel, field_validator, FieldValidationInfo
from typing import List, Optional, Dict, Any


class SectionBase(BaseModel):
    name: str
    raw_text: str
    lines: List[str] = []
    structured_data: Optional[dict] = None
    rewritten_text: Optional[str] = None
    original_lines: Optional[List[str]] = None
    parsed_data: Optional[Any] = None


    # 自动生成 lines 字段
    @field_validator("lines", mode="before")
    @classmethod
    def generate_lines(cls, v, info: FieldValidationInfo):
        raw_text = info.data.get("raw_text", "")
        return [line.strip() for line in raw_text.splitlines() if line.strip()]
    
    def clean_text(self) -> str:
        return self.raw_text

    def extract_items(self) -> List[str]:
        return self.lines

    def parse(self):
        raise NotImplementedError

    def to_markdown(self) -> str:
        return f"### {self.name.title()}\n" + "\n".join(self.extract_items())

    def validate(self) -> bool:
        return True

    def __str__(self):
        return f"== {self.name.upper()} ==\n" + self.raw_text

    class Config:
        arbitrary_types_allowed = True
