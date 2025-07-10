import json
from pydantic import BaseModel, field_validator, FieldValidationInfo
from typing import List, Optional, Dict, Any, Union


class SectionBase(BaseModel):
    name: str
    raw_text: str
    lines: List[str] = []
    structured_data: Optional[Dict[str, Any]] = None
    rewritten_text: Optional[str] = None
    original_lines: Optional[List[str]] = None
    parsed_data: Optional[Union[Dict[str, Any], str, int, float, List[Any]]] = (
        None  # 限制为 JSON 可序列化结构
    )

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
        return self.structured_data

    def to_markdown(self) -> str:
        return f"### {self.name.title()}\n" + "\n".join(self.extract_items())

    def validate(self) -> bool:
        return True

    def __str__(self):
        return f"== {self.name.upper()} ==\n" + self.raw_text

    def to_dict(self) -> dict:
        """推荐调用"""
        return self.model_dump()

    def to_json(self) -> str:
        return self.model_dump_json(indent=2, ensure_ascii=False)

    def __json__(self):
        return self.model_dump(mode="json", exclude_none=True)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            Any: lambda v: (
                v
                if isinstance(v, (dict, list, str, int, float, bool, type(None)))
                else str(v)
            )
        }
