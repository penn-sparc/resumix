from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class JobRequirement:
    text: str
    # Optionally, add more metadata fields later (e.g., type, source, etc.)

@dataclass
class JDRequirements:
    must_have_technical_skills: List[JobRequirement] = field(default_factory=list)
    must_have_experience: Optional[str] = None
    must_have_qualifications: List[JobRequirement] = field(default_factory=list)
    must_have_core_responsibilities: List[JobRequirement] = field(default_factory=list)

    good_to_have_additional_skills: List[JobRequirement] = field(default_factory=list)
    good_to_have_extra_qualifications: List[JobRequirement] = field(default_factory=list)
    good_to_have_bonus_experience: Optional[str] = None

    additional_screening_criteria: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JDRequirements':
        # Defensive: handle missing keys and convert lists of strings to JobRequirement
        must = data.get('must_have_requirements', {})
        good = data.get('good_to_have_requirements', {})
        addl = data.get('additional_screening_criteria', [])
        return cls(
            must_have_technical_skills=[JobRequirement(text=s) for s in must.get('technical_skills', [])],
            must_have_experience=must.get('experience'),
            must_have_qualifications=[JobRequirement(text=s) for s in must.get('qualifications', [])],
            must_have_core_responsibilities=[JobRequirement(text=s) for s in must.get('core_responsibilities', [])],
            good_to_have_additional_skills=[JobRequirement(text=s) for s in good.get('additional_skills', [])],
            good_to_have_extra_qualifications=[JobRequirement(text=s) for s in good.get('extra_qualifications', [])],
            good_to_have_bonus_experience=good.get('bonus_experience'),
            additional_screening_criteria=addl if isinstance(addl, list) else [],
        ) 