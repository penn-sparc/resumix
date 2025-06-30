import pytest
from resumix.section.section_base import SectionBase
from resumix.section.info_section import PersonalInfoSection
from resumix.section.experience_section import ExperienceSection
from resumix.section.education_section import EducationSection
from resumix.section.projects_section import ProjectsSection
from resumix.section.skills_section import SkillsSection


class TestSectionBase:
    """Test the base section class functionality"""
    
    def test_initialization(self):
        section = SectionBase("Test Section", "  Sample text  \n  with lines  \n")
        
        assert section.name == "Test Section"
        assert section.raw_text == "Sample text  \n  with lines"
        assert section.lines == ["Sample text", "with lines"]
        assert section.structured_data is None
        assert section.rewritten_text is None
    
    def test_clean_text_default(self):
        section = SectionBase("Test", "Sample text")
        assert section.clean_text() == "Sample text"
    
    def test_extract_items_default(self):
        section = SectionBase("Test", "Line 1\nLine 2\n\nLine 3")
        items = section.extract_items()
        assert items == ["Line 1", "Line 2", "Line 3"]
    
    def test_parse_not_implemented(self):
        section = SectionBase("Test", "Sample text")
        with pytest.raises(NotImplementedError):
            section.parse()
    
    def test_to_dict(self):
        section = SectionBase("Test Section", "Sample text\nAnother line")
        result = section.to_dict()
        
        expected = {
            "section": "Test Section",
            "content": "Sample text\nAnother line",
            "parsed": ["Sample text", "Another line"]
        }
        assert result == expected
    
    def test_to_dict_with_structured_data(self):
        section = SectionBase("Test", "Sample text")
        section.structured_data = {"key": "value"}
        result = section.to_dict()
        
        assert result["parsed"] == {"key": "value"}
    
    def test_to_json(self):
        section = SectionBase("Test", "Sample text")
        json_str = section.to_json()
        
        assert '"section": "Test"' in json_str
        assert '"content": "Sample text"' in json_str
    
    def test_to_markdown(self):
        section = SectionBase("Test Section", "Line 1\nLine 2")
        markdown = section.to_markdown()
        
        assert markdown.startswith("### Test Section")
        assert "Line 1" in markdown
        assert "Line 2" in markdown
    
    def test_validate_default(self):
        section = SectionBase("Test", "Sample text")
        assert section.validate() is True
    
    def test_str_representation(self):
        section = SectionBase("Test Section", "Sample text")
        str_repr = str(section)
        
        assert "== TEST SECTION ==" in str_repr
        assert "Sample text" in str_repr


class TestPersonalInfoSection:
    """Test personal information section parsing"""
    
    def test_parse_basic_contact_info(self, sample_resume_text):
        section = PersonalInfoSection("Personal Info", sample_resume_text)
        section.parse()
        
        assert hasattr(section, 'parsed_data')
        assert section.parsed_data['name'] == 'John Doe'
        assert section.parsed_data['email'] == 'john.doe@email.com'
        assert section.parsed_data['phone'] == '(555) 123-4567'
    
    def test_parse_empty_content(self):
        section = PersonalInfoSection("Personal Info", "")
        section.parse()
        
        assert section.parsed_data['name'] == ""
        assert section.parsed_data['email'] == ""
        assert section.parsed_data['phone'] == ""
    
    def test_parse_malformed_email(self):
        text = "John Doe\ninvalid-email-format\n123-456-7890"
        section = PersonalInfoSection("Personal Info", text)
        section.parse()
        
        assert section.parsed_data['name'] == 'John Doe'
        assert section.parsed_data['email'] == ""  # Should not match invalid email
        assert section.parsed_data['phone'] == '123-456-7890'
    
    def test_parse_valid_email(self):
        text = "Jane Smith\njane.smith@company.com\n(555) 987-6543"
        section = PersonalInfoSection("Personal Info", text)
        section.parse()
        
        assert section.parsed_data['email'] == 'jane.smith@company.com'
    
    def test_parse_phone_variations(self):
        # Test different phone number formats
        test_cases = [
            ("555-123-4567", "555-123-4567"),
            ("(555) 123-4567", "(555) 123-4567"), 
            ("555.123.4567", "555.123.4567"),
            ("5551234567", "5551234567")
        ]
        
        for phone_input, expected in test_cases:
            text = f"John Doe\njohn@email.com\n{phone_input}"
            section = PersonalInfoSection("Personal Info", text)
            section.parse()
            
            assert section.parsed_data['phone'] == expected
    
    def test_parse_multiple_emails_takes_first(self):
        text = "John Doe\nfirst@email.com\nsecond@email.com"
        section = PersonalInfoSection("Personal Info", text)
        section.parse()
        
        assert section.parsed_data['email'] == 'first@email.com'
    
    def test_parse_no_name_fallback(self):
        text = "john@email.com\n(555) 123-4567"
        section = PersonalInfoSection("Personal Info", text)
        section.parse()
        
        # Should not set email as name since it contains @
        assert section.parsed_data['name'] == ""
        assert section.parsed_data['email'] == 'john@email.com'


class TestExperienceSection:
    """Test experience section parsing"""
    
    def test_parse_work_experience(self, sample_experience_text):
        section = ExperienceSection("Experience", sample_experience_text)
        section.parse()
        
        assert hasattr(section, 'parsed_data')
        assert len(section.parsed_data) == 2
        
        # Check first experience
        first_exp = section.parsed_data[0]
        assert first_exp['company'] == 'Tech Corp'
        assert first_exp['position'] == 'Senior Software Engineer'
        assert len(first_exp['highlights']) >= 1
        
        # Check second experience  
        second_exp = section.parsed_data[1]
        assert second_exp['company'] == 'StartupCo'
        assert second_exp['position'] == 'Junior Developer'
    
    def test_parse_single_experience(self):
        text = """
        TechCorp Inc.
        Senior Software Engineer | 2020-2023
        - Developed scalable web applications
        - Led team of 5 engineers
        """
        section = ExperienceSection("Experience", text)
        section.parse()
        
        assert len(section.parsed_data) == 1
        experience = section.parsed_data[0]
        assert experience['company'] == 'TechCorp Inc.'
        assert experience['position'] == 'Senior Software Engineer | 2020-2023'
        assert len(experience['highlights']) == 2
    
    def test_parse_experience_with_no_highlights(self):
        text = """
        Company A
        Developer | 2019-2020
        """
        section = ExperienceSection("Experience", text)
        section.parse()
        
        assert len(section.parsed_data) == 1
        experience = section.parsed_data[0]
        assert experience['company'] == 'Company A'
        assert experience['highlights'] == []
    
    def test_parse_multiple_experiences(self):
        text = """
        TechCorp Inc.
        Senior Engineer | 2020-2023
        - Built scalable systems
        
        StartupCo
        Junior Developer | 2018-2020
        - Developed REST APIs
        - Improved test coverage
        """
        section = ExperienceSection("Experience", text)
        section.parse()
        
        assert len(section.parsed_data) == 2
        
        first_exp = section.parsed_data[0]
        assert first_exp['company'] == 'TechCorp Inc.'
        assert len(first_exp['highlights']) == 1
        
        second_exp = section.parsed_data[1]
        assert second_exp['company'] == 'StartupCo'
        assert len(second_exp['highlights']) == 2
    
    def test_parse_empty_experience(self):
        section = ExperienceSection("Experience", "")
        section.parse()
        
        assert section.parsed_data == []
    
    def test_highlights_formatting(self):
        text = """
        Company
        Position | 2020-2021
        - First highlight
        -   Second highlight with extra spaces  
        - Third highlight
        """
        section = ExperienceSection("Experience", text)
        section.parse()
        
        highlights = section.parsed_data[0]['highlights']
        assert highlights == [
            'First highlight',
            'Second highlight with extra spaces',
            'Third highlight'
        ]


class TestSkillsSection:
    """Test skills section parsing"""
    
    def test_parse_skills_comma_separated(self, sample_skills_text):
        section = SkillsSection("Skills", sample_skills_text)
        section.parse()
        
        assert hasattr(section, 'parsed_data')
        assert isinstance(section.parsed_data, list)
        assert len(section.parsed_data) > 0
        
        # Check that some expected skills are present
        skills_str = ' '.join(section.parsed_data).lower()
        assert 'python' in skills_str
        assert 'javascript' in skills_str
    
    def test_parse_skills_various_separators(self):
        text = "Python, JavaScript; Java，Go；React"
        section = SkillsSection("Skills", text)
        section.parse()
        
        expected_skills = ['Python', 'JavaScript', 'Java', 'Go', 'React']
        assert section.parsed_data == expected_skills
    
    def test_parse_skills_multiline(self):
        text = """
        Programming: Python, JavaScript, Java
        Frameworks: React, Django, Flask
        Databases: PostgreSQL, MongoDB
        """
        section = SkillsSection("Skills", text)
        section.parse()
        
        # Should extract all skills from all lines
        skills = section.parsed_data
        skills_str = ' '.join(skills).lower()
        assert 'python' in skills_str
        assert 'react' in skills_str
        assert 'postgresql' in skills_str
    
    def test_parse_skills_with_extra_whitespace(self):
        text = "  Python  ,   JavaScript   ;   React  "
        section = SkillsSection("Skills", text)
        section.parse()
        
        expected_skills = ['Python', 'JavaScript', 'React']
        assert section.parsed_data == expected_skills
    
    def test_parse_empty_skills(self):
        section = SkillsSection("Skills", "")
        section.parse()
        
        assert section.parsed_data == []
    
    def test_parse_skills_with_empty_entries(self):
        text = "Python,,JavaScript,,,React"
        section = SkillsSection("Skills", text)
        section.parse()
        
        # Should filter out empty entries
        expected_skills = ['Python', 'JavaScript', 'React']
        assert section.parsed_data == expected_skills
    
    def test_parse_single_skill(self):
        text = "Python"
        section = SkillsSection("Skills", text)
        section.parse()
        
        assert section.parsed_data == ['Python']


class TestEducationSection:
    """Test education section parsing"""
    
    def test_parse_basic_education(self, sample_education_text):
        section = EducationSection("Education", sample_education_text)
        section.parse()
        
        # Should not raise an error and should have parsed_data
        assert hasattr(section, 'parsed_data')
    
    def test_parse_empty_education(self):
        section = EducationSection("Education", "")
        section.parse()
        
        # Should handle empty input gracefully
        assert hasattr(section, 'parsed_data')


class TestProjectsSection:
    """Test projects section parsing"""
    
    def test_parse_basic_projects(self):
        text = """
        E-commerce Platform
        - Built using React and Node.js
        - Implemented payment processing
        
        Mobile App
        - Developed with React Native
        - Published on App Store
        """
        section = ProjectsSection("Projects", text)
        section.parse()
        
        # Should not raise an error and should have parsed_data
        assert hasattr(section, 'parsed_data')
    
    def test_parse_empty_projects(self):
        section = ProjectsSection("Projects", "")
        section.parse()
        
        # Should handle empty input gracefully
        assert hasattr(section, 'parsed_data')