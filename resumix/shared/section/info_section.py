import re
from typing import Optional, Dict
from pydantic import Field

from resumix.shared.section.section_base import SectionBase


class PersonalInfoSection(SectionBase):
    parsed_data: Optional[Dict[str, str]] = Field(default_factory=dict)

    def parse(self):
        name = ""
        phone = ""
        email = ""

        lines = self.raw_text.splitlines()
        for line in lines:
            if re.search(r"@\w+", line):
                email = line.strip()
            elif re.search(r"\d{3,}", line):
                phone = line.strip()
            elif not name:
                name = line.strip()

        # ✅ 注意：赋值到 self.parsed_data（Pydantic 字段）
        self.parsed_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "website": "",
            "address": "",
        }

    def to_dict(self):
        return self.model_dump()

    def to_json(self):
        return self.model_dump_json(indent=2, ensure_ascii=False)

    def __str__(self):
        return f"== {self.name.upper()} ==\n" + self.raw_text
