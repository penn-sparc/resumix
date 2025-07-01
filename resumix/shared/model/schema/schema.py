from pydantic import BaseModel, ConfigDict
from typing import List, Generic, TypeVar, Optional
from pydantic.generics import GenericModel
from resumix.shared.section.section_base import SectionBase


T = TypeVar("T")

class BaseResponse(GenericModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: Optional[T] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
class BaseRequest(BaseModel, Generic[T]):
    data: T
    model_config = ConfigDict(arbitrary_types_allowed=True)

class TechOptimizeRequest(BaseModel):
    resume_section: SectionBase
    jd_text: str
    tech_stack: List[str]


class TechOptimizeResponse(BaseModel):
    optimized_resume_text: str


