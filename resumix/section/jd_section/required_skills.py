from section.section_base import SectionBase
from pydantic import BaseModel
from typing import List


class SkillItem(BaseModel):
    """Represents a single skill."""

    name: str
    # Optional: could add proficiency or years of experience later
    # proficiency: str = "Not specified"


class RequiredSkillsSection(SectionBase):
    """A section of a job description detailing required skills."""

    items: List[SkillItem] = []

    def parse_from_llm_response(self, response: List[str]):
        """
        Populates the section with a list of required skills from an LLM response.
        """
        self.items = [SkillItem(name=item) for item in response]
        self.structured_data = self.items
