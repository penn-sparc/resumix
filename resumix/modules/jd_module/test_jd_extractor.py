import unittest
from unittest.mock import MagicMock
from resumix.modules.jd_module.jd_extractor import JDExtractor
from resumix.section.jd_section.job_requirement import JDRequirements

class TestJDExtractor(unittest.TestCase):
    def setUp(self):
        # Prepare a mock LLMClient
        self.mock_llm = MagicMock()
        self.extractor = JDExtractor(llm=self.mock_llm)

    def test_extract_requirements(self):
        # Mock LLM response
        mock_response = """
        {
            "must_have_requirements": {
                "technical_skills": ["Python", "Django"],
                "experience": "3+ years in web development",
                "qualifications": ["Bachelor's in Computer Science"],
                "core_responsibilities": ["Lead backend development"]
            },
            "good_to_have_requirements": {
                "additional_skills": ["React", "AWS"],
                "extra_qualifications": ["Master's degree"],
                "bonus_experience": "Experience with microservices"
            },
            "additional_screening_criteria": ["Must be eligible to work in the US", "Remote work available"]
        }
        """
        self.mock_llm.return_value = mock_response

        # Call the method
        result = self.extractor.extract_requirements("Sample JD text")

        # Verify the result
        self.assertIsInstance(result, JDRequirements)
        self.assertEqual(len(result.must_have_technical_skills), 2)
        self.assertEqual(result.must_have_technical_skills[0].text, "Python")
        self.assertEqual(result.must_have_experience, "3+ years in web development")
        self.assertEqual(len(result.good_to_have_additional_skills), 2)
        self.assertEqual(result.good_to_have_additional_skills[0].text, "React")
        self.assertEqual(len(result.additional_screening_criteria), 2)

if __name__ == '__main__':
    unittest.main() 