import pytest
from unittest.mock import Mock, patch
import tempfile
import os
from pathlib import Path

@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        'use_model': 'mock',
        'ocr': {'backend': 'mock'},
        'models': {'embedding_model': 'mock-model'}
    }

@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing"""
    return """
    John Doe
    Software Engineer
    john.doe@email.com
    (555) 123-4567
    
    EXPERIENCE
    Senior Software Engineer | Tech Corp | 2020-2023
    • Developed scalable web applications using Python and React
    • Led team of 5 engineers in agile development processes
    
    EDUCATION
    Master of Science in Computer Science | MIT | 2018
    Bachelor of Science in Computer Science | Stanford | 2016
    
    SKILLS
    Python, JavaScript, React, AWS, Docker
    """

@pytest.fixture
def sample_experience_text():
    """Sample experience section text for testing"""
    return """
    Senior Software Engineer | Tech Corp | 2020-2023
    • Developed scalable web applications using Python and React
    • Led team of 5 engineers in agile development processes
    • Improved system performance by 40% through optimization
    
    Junior Developer | StartupCo | 2018-2020
    • Built REST APIs using Python and Flask
    • Collaborated with product team on feature development
    """

@pytest.fixture
def sample_education_text():
    """Sample education section text for testing"""
    return """
    Master of Science in Computer Science | MIT | 2018
    GPA: 3.8/4.0
    Thesis: Machine Learning Applications in Software Engineering
    
    Bachelor of Science in Computer Science | Stanford | 2016
    GPA: 3.9/4.0
    Magna Cum Laude
    """

@pytest.fixture
def sample_skills_text():
    """Sample skills section text for testing"""
    return """
    Programming Languages: Python, JavaScript, Java, C++
    Frameworks: React, Django, Flask, Spring Boot
    Databases: PostgreSQL, MongoDB, Redis
    Cloud Platforms: AWS, Azure, Google Cloud
    Tools: Docker, Kubernetes, Git, Jenkins
    """

@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing"""
    with patch('resumix.utils.llm_client.LLMClient') as mock:
        mock_instance = Mock()
        mock_instance.invoke.return_value = "Mock LLM response"
        mock_instance.ainvoke.return_value = "Mock async LLM response"
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def temp_pdf_file():
    """Create temporary PDF file for testing"""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        # Create minimal PDF content
        tmp.write(b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000015 00000 n \n0000000060 00000 n \n0000000111 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n186\n%%EOF')
        yield tmp.name
    os.unlink(tmp.name)

@pytest.fixture
def mock_sentence_transformer():
    """Mock sentence transformer model"""
    with patch('sentence_transformers.SentenceTransformer') as mock_st:
        mock_model = Mock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_st.return_value = mock_model
        yield mock_model

@pytest.fixture
def mock_ocr_utils():
    """Mock OCR utilities"""
    with patch('resumix.utils.ocr_utils.OCRUtils') as mock_ocr:
        mock_instance = Mock()
        mock_instance.extract_text_from_pdf.return_value = "Sample extracted text"
        mock_ocr.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def sample_structured_experience():
    """Sample structured experience data"""
    return {
        'experiences': [
            {
                'position': 'Senior Software Engineer',
                'company': 'Tech Corp',
                'location': 'San Francisco, CA',
                'start_date': '2020-01',
                'end_date': '2023-12',
                'duration': '4 years',
                'highlights': [
                    'Developed scalable web applications using Python and React',
                    'Led team of 5 engineers in agile development processes',
                    'Improved system performance by 40% through optimization'
                ],
                'technologies': ['Python', 'React', 'PostgreSQL', 'AWS']
            },
            {
                'position': 'Junior Developer',
                'company': 'StartupCo',
                'location': 'Palo Alto, CA',
                'start_date': '2018-06',
                'end_date': '2020-01',
                'duration': '1.5 years',
                'highlights': [
                    'Built REST APIs using Python and Flask',
                    'Collaborated with product team on feature development'
                ],
                'technologies': ['Python', 'Flask', 'MySQL']
            }
        ],
        'total_experience': '5.5 years',
        'key_skills': ['Python', 'React', 'Flask', 'PostgreSQL', 'AWS']
    }

@pytest.fixture
def sample_structured_education():
    """Sample structured education data"""
    return {
        'education_entries': [
            {
                'degree': 'Master of Science',
                'field_of_study': 'Computer Science',
                'institution': 'MIT',
                'location': 'Cambridge, MA',
                'graduation_date': '2018',
                'gpa': 3.8,
                'honors': ['Magna Cum Laude'],
                'relevant_coursework': ['Machine Learning', 'Algorithms', 'Software Engineering'],
                'thesis_title': 'Machine Learning Applications in Software Engineering'
            },
            {
                'degree': 'Bachelor of Science',
                'field_of_study': 'Computer Science',
                'institution': 'Stanford',
                'location': 'Palo Alto, CA',
                'graduation_date': '2016',
                'gpa': 3.9,
                'honors': ['Magna Cum Laude'],
                'relevant_coursework': ['Data Structures', 'Operating Systems', 'Database Systems']
            }
        ],
        'highest_degree': 'Master of Science',
        'education_level_score': 5,
        'institutions': ['MIT', 'Stanford'],
        'fields_of_study': ['Computer Science']
    }

@pytest.fixture
def sample_job_description():
    """Sample job description text for testing"""
    return """
    Senior Software Engineer - Full Stack
    
    We are seeking a talented Senior Software Engineer to join our growing team. 
    
    Requirements:
    • 5+ years of experience in software development
    • Strong proficiency in Python and JavaScript
    • Experience with React and modern frontend frameworks
    • Knowledge of cloud platforms (AWS, Azure, or GCP)
    • Experience with databases (PostgreSQL, MongoDB)
    • Bachelor's degree in Computer Science or related field
    
    Responsibilities:
    • Design and implement scalable web applications
    • Lead technical architecture decisions
    • Mentor junior developers
    • Collaborate with product and design teams
    • Ensure code quality through reviews and testing
    
    Nice to have:
    • Experience with Kubernetes and Docker
    • Knowledge of machine learning frameworks
    • Contributions to open source projects
    """

# Test utility functions
def create_mock_section(name, raw_text, structured_data=None, confidence=1.0):
    """Helper function to create mock section objects"""
    mock_section = Mock()
    mock_section.name = name
    mock_section.raw_text = raw_text
    mock_section.structured_data = structured_data or {}
    mock_section.confidence = confidence
    mock_section.parse.return_value = None
    return mock_section