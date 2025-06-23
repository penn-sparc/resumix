from section.section_base import SectionBase
from pydantic import BaseModel
from typing import List


class QualificationItem(BaseModel):
    """Represents a single qualification, such as a degree or certification."""

    description: str


class QualificationsSection(SectionBase):
    """A section of a job description detailing qualifications."""

    items: List[QualificationItem] = []

    def parse_from_llm_response(self, response: List[str]):
        """
        Populates the section with a list of qualifications from an LLM response.
        """
        self.items = [
            QualificationItem(description=item) for item in response
        ]
        self.structured_data = self.items 