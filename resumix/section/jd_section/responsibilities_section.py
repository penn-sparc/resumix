from section.section_base import SectionBase
from pydantic import BaseModel
from typing import List


class ResponsibilityItem(BaseModel):
    """Represents a single responsibility or duty."""

    description: str


class ResponsibilitiesSection(SectionBase):
    """A section of a job description detailing responsibilities."""

    items: List[ResponsibilityItem] = []

    def parse_from_llm_response(self, response: List[str]):
        """
        Populates the section with a list of responsibilities from an LLM response.
        """
        self.items = [
            ResponsibilityItem(description=item) for item in response
        ]
        self.structured_data = self.items
