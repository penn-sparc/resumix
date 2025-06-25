from section.section_base import SectionBase
from section.jd_section.required_skills import SkillItem
from pydantic import BaseModel
from typing import List


class PreferredSkillsSection(SectionBase):
    """A section of a job description detailing preferred skills."""

    items: List[SkillItem] = []

    def parse_from_llm_response(self, response: List[str]):
        """
        Populates the section with a list of preferred skills from an LLM response.
        """
        self.items = [SkillItem(name=item) for item in response]
        self.structured_data = self.items
