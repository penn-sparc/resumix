from resumix.section.jd_section.job_requirement import JobRequirement, JDRequirements
from resumix.utils.llm_client import LLMClient
from resumix.utils.json_parser import JsonParser

class JDExtractor:
    """
    JD Extractor Agent: Parses raw JD text into structured requirements using LLM.
    """
    def __init__(self, llm=None):
        self.llm = llm or LLMClient()

    def extract_requirements(self, jd_text: str) -> JDRequirements:
        """
        Given raw JD text, use LLM to extract structured requirements.
        Returns a JDRequirements object.
        """
        # Placeholder prompt; to be replaced with your engineered prompt
        prompt = (
            "You are an experienced technical recruiter and job posting analyst. "
            "Your task is to extract a structured summary of candidate requirements from the following job description. "
            "Your output must be in a well-formed JSON format.\n\n"
            f"Job Description:\n{jd_text}\n\n"
            "Instructions:\n"
            "Your JSON output should contain the following top-level keys: 'must_have_requirements', 'good_to_have_requirements', and 'additional_screening_criteria'.\n"
            "1. Under the 'must_have_requirements' key, create an object with the following sub-keys:\n"
            "    - 'technical_skills': An array of strings listing all essential technical skills.\n"
            "    - 'experience': A string specifying the minimum years and type of relevant experience (e.g., '5+ years in backend development').\n"
            "    - 'qualifications': An array of strings listing all mandatory degrees or certifications.\n"
            "    - 'core_responsibilities': An array of strings identifying key duties that are non-negotiable.\n"
            "2. Under the 'good_to_have_requirements' key, create an object with the following sub-keys:\n"
            "    - 'additional_skills': An array of strings listing all preferred but not mandatory technical skills.\n"
            "    - 'extra_qualifications': An array of strings listing any bonus educational degrees or certifications.\n"
            "    - 'bonus_experience': A string noting any extra experience that would add value.\n"
            "3. Under the 'additional_screening_criteria' key, create an array of strings listing any filtering statements that affect eligibility, such as work authorization status, location policies (e.g., 'remote,' 'hybrid,' 'onsite'), or availability constraints.\n"
        )
        response = self.llm(prompt)
        data = JsonParser.parse(response)
        return JDRequirements.from_dict(data) 