import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import Dict, Any

# Import LLMClient from utils
from utils.llm_client import LLMClient
from section.jd_section.responsibilities_section import ResponsibilitiesSection, ResponsibilityItem
from section.jd_section.required_skills import RequiredSkillsSection, SkillItem
from section.jd_section.preferred_skills_section import PreferredSkillsSection
from section.jd_section.qualifications_section import QualificationsSection, QualificationItem


JD_PARSING_PROMPT_TEMPLATE = """
You are an expert technical recruiter and job posting analyst with over 15 years of experience. Your primary task is to meticulously analyze a job description and extract key information into a structured JSON format. You must be precise, distinguish between mandatory and preferred qualifications, and adhere strictly to the requested JSON schema.

**Job Description Text:**
\"\"\"
{jd_text}
\"\"\"

**Instructions:**
Your output must be a single, well-formed JSON object. Follow these steps:

1.  **Analyze the Job Description:** Carefully read the entire job description to understand the role, its requirements, and the company context. Pay close attention to language that implies requirements are mandatory (e.g., "must have," "required," "minimum of") versus desirable (e.g., "preferred," "a plus," "nice to have").

2.  **Extract Information:** Populate a JSON object according to the schema defined below. If a field is not mentioned, return an empty list or a sensible default.

3.  **Format the Output:** Ensure your final output is a single JSON object. Do not include any text or explanations outside of the JSON object itself.

**JSON Schema:**
{{
  "must_have_requirements": {{
    "technical_skills": ["<list of essential technical skills>"],
    "experience": "<string specifying minimum years and type of relevant experience>",
    "qualifications": ["<list of mandatory degrees or certifications>"]
  }},
  "good_to_have_requirements": {{
    "additional_skills": ["<list of preferred but not mandatory technical skills>"],
    "extra_qualifications": ["<list of bonus educational degrees or certifications>"],
    "bonus_experience": "<string noting any extra experience that would add value>"
  }},
  "core_responsibilities": ["<list of key duties>"],
  "additional_screening_criteria": {{
    "location": "<location policy: remote, hybrid, onsite>",
    "work_authorization": "<any mention of work authorization status>"
  }}
}}
"""


class JDParser:
    """
    Parses a job description from a URL into a structured format using an LLM.
    """

    def __init__(self, url: str):
        self.url = url
        self.llm_provider = LLMClient()
        self.raw_text = ""
        self.structured_data = {}

    def _fetch_content(self) -> bool:
        """Fetches and extracts clean text content from the URL."""
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            self.raw_text = " ".join(soup.stripped_strings)
            return True
        except requests.RequestException as e:
            logging.error(f"Error fetching URL {self.url}: {e}")
            return False

    def _create_prompt(self) -> str:
        """Creates the prompt for the LLM to parse the JD."""
        return JD_PARSING_PROMPT_TEMPLATE.format(jd_text=self.raw_text)

    def parse(self) -> Dict[str, Any]:
        """
        Orchestrates the fetching, parsing, and structuring of the job description.
        Returns a dictionary of populated SectionBase objects.
        """
        if not self._fetch_content():
            return None # Or raise an exception

        prompt = self._create_prompt()
        
        try:
            # Assuming the llm_provider returns a string that is a JSON object
            response_str = self.llm_provider(prompt)
            # Clean the response to ensure it's valid JSON
            json_response_str = response_str[response_str.find('{'):response_str.rfind('}')+1]
            llm_output = json.loads(json_response_str)

            # Create and populate section objects
            must_haves = llm_output.get("must_have_requirements", {})
            good_to_haves = llm_output.get("good_to_have_requirements", {})

            # Required Skills
            req_skills_section = RequiredSkillsSection(name="required_skills", raw_text=json.dumps(must_haves.get("technical_skills", [])))
            req_skills_section.parse_from_llm_response(must_haves.get("technical_skills", []))

            # Preferred Skills
            pref_skills_section = PreferredSkillsSection(name="preferred_skills", raw_text=json.dumps(good_to_haves.get("additional_skills", [])))
            pref_skills_section.parse_from_llm_response(good_to_haves.get("additional_skills", []))

            # Qualifications (combining must-have and good-to-have)
            quals = must_haves.get("qualifications", []) + good_to_haves.get("extra_qualifications", [])
            quals_section = QualificationsSection(name="qualifications", raw_text=json.dumps(quals))
            quals_section.parse_from_llm_response(quals)

            # Responsibilities
            responsibilities = llm_output.get("core_responsibilities", [])
            resp_section = ResponsibilitiesSection(name="responsibilities", raw_text=json.dumps(responsibilities))
            resp_section.parse_from_llm_response(responsibilities)

            self.structured_data = {
                "required_skills": req_skills_section,
                "preferred_skills": pref_skills_section,
                "qualifications": quals_section,
                "responsibilities": resp_section,
                "raw_llm_output": llm_output, # For debugging
            }
            return self.structured_data

        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode LLM response into JSON: {e}")
            logging.error(f"LLM Response was: {response_str}")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred during parsing: {e}")
            return None

    def parse_jd(self, jd_text: str) -> str:
        prompt = f"""
        请从下面的岗位描述中提取结构化信息：

        岗位描述：
            \"\"\"{jd_text}\"\"\"

            请输出：
            - 岗位名称：
            - 所属部门：
            - 岗位职责（分点）：
            - 任职要求（分点）：
            - 所需技能（技能列表）：
        """
        return self.llm_provider(prompt)

    def parse_from_url(self, url: str) -> str:
        jd_text = self._fetch_content()
        return self.parse_jd(jd_text)


if __name__ == "__main__":
    # 示例：使用本地 LLM 客户端
    from utils.llm_client import LLMClient

    llm = LLMClient()
    parser = JDParser(llm)

    # 示例 URL
    url = "https://cs.bit.edu.cn/zsjy/jyysxxx/133bda5a688f415ab96740027d974793.htm"
    structured_jd = parser.parse_from_url(url)
    print(structured_jd)
