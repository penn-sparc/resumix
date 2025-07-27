"""
PDF Resume Generator using ReportLab (Windows-compatible)

This module provides an alternative to the pylatex-based generator,
using ReportLab which is already included in the project dependencies.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib import colors
from typing import Dict, Any, List
import os
import tempfile
from datetime import datetime
from loguru import logger


class ReportLabResumeGenerator:
    """
    PDF Resume generator using ReportLab library.
    Compatible with the existing resume data format from GeneratorUtils.
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the resume"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ResumeTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50')
        ))

        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=HexColor('#34495e'),
            borderWidth=1,
            borderColor=HexColor('#bdc3c7'),
            borderPadding=5
        ))

        # Contact info style
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=20
        ))

        # Item style for lists
        self.styles.add(ParagraphStyle(
            name='ListItem',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=20
        ))

        # Job title style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=5,
            textColor=HexColor('#2980b9'),
            fontName='Helvetica-Bold'
        ))

    def generate_pdf_resume(self, resume_data: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate PDF resume from the structured resume data.
        
        Args:
            resume_data: Resume data in the format expected by generator.py
            output_path: Path for the output PDF (without .pdf extension)
            
        Returns:
            str: Path to the generated PDF file
        """
        logger.info("Starting PDF generation with ReportLab")
        
        if not output_path:
            # Create temporary file if no path specified
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, "resumix_resume")
        
        pdf_path = f"{output_path}.pdf"
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            
            # Add header (name and contact info)
            self._add_header(story, resume_data.get('basics', {}))
            
            # Add summary if available
            self._add_summary(story, resume_data.get('basics', {}))
            
            # Add sections in order
            section_order = ['work', 'education', 'skills', 'projects', 'awards']
            
            for section_name in section_order:
                section_data = resume_data.get(section_name, [])
                if section_data:  # Only add non-empty sections
                    if section_name == 'work':
                        self._add_work_experience(story, section_data)
                    elif section_name == 'education':
                        self._add_education(story, section_data)
                    elif section_name == 'skills':
                        self._add_skills(story, section_data)
                    elif section_name == 'projects':
                        self._add_projects(story, section_data)
                    elif section_name == 'awards':
                        self._add_awards(story, section_data)
            
            # Build PDF
            doc.build(story)
            logger.info(f"PDF generated successfully: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            raise

    def _add_header(self, story: List, basics: Dict[str, Any]):
        """Add name and contact information header"""
        name = basics.get('name', 'Your Name')
        label = basics.get('label', '')
        
        # Name and title
        if label:
            title_text = f"{name}<br/><i>{label}</i>"
        else:
            title_text = name
            
        story.append(Paragraph(title_text, self.styles['ResumeTitle']))
        
        # Contact information
        contact_parts = []
        if basics.get('email'):
            contact_parts.append(basics['email'])
        if basics.get('phone'):
            contact_parts.append(basics['phone'])
        if basics.get('website'):
            contact_parts.append(basics['website'])
        
        # Add location if available
        location = basics.get('location', {})
        if isinstance(location, dict):
            loc_parts = []
            if location.get('city'):
                loc_parts.append(location['city'])
            if location.get('region'):
                loc_parts.append(location['region'])
            if loc_parts:
                contact_parts.append(', '.join(loc_parts))
        elif isinstance(location, str):
            contact_parts.append(location)
        
        if contact_parts:
            contact_text = ' | '.join(contact_parts)
            story.append(Paragraph(contact_text, self.styles['ContactInfo']))

    def _add_summary(self, story: List, basics: Dict[str, Any]):
        """Add summary/objective section"""
        summary = basics.get('summary', '')
        if summary:
            story.append(Paragraph("Summary", self.styles['SectionHeading']))
            story.append(Paragraph(summary, self.styles['Normal']))
            story.append(Spacer(1, 12))

    def _add_work_experience(self, story: List, work_data: List[Dict[str, Any]]):
        """Add work experience section"""
        story.append(Paragraph("Work Experience", self.styles['SectionHeading']))
        
        for job in work_data:
            # Job title and company
            company = job.get('company', '')
            position = job.get('position', '')
            start_date = job.get('startDate', '')
            end_date = job.get('endDate', '')
            
            # Format date range
            date_range = f"{start_date} - {end_date}" if start_date or end_date else ""
            
            # Job header
            if position and company:
                job_header = f"<b>{position}</b> at {company}"
                if date_range:
                    job_header += f" ({date_range})"
            elif position:
                job_header = f"<b>{position}</b>"
                if date_range:
                    job_header += f" ({date_range})"
            elif company:
                job_header = f"<b>{company}</b>"
                if date_range:
                    job_header += f" ({date_range})"
            else:
                job_header = "Work Experience"
            
            story.append(Paragraph(job_header, self.styles['JobTitle']))
            
            # Job description/summary
            summary = job.get('summary', '')
            if summary:
                story.append(Paragraph(summary, self.styles['Normal']))
            
            story.append(Spacer(1, 8))

    def _add_education(self, story: List, education_data: List[Dict[str, Any]]):
        """Add education section"""
        story.append(Paragraph("Education", self.styles['SectionHeading']))
        
        for edu in education_data:
            institution = edu.get('institution', '')
            area = edu.get('area', '')
            study_type = edu.get('studyType', '')
            start_date = edu.get('startDate', '')
            end_date = edu.get('endDate', '')
            gpa = edu.get('gpa', '')
            
            # Education header
            edu_parts = []
            if area and study_type:
                edu_parts.append(f"{study_type} in {area}")
            elif area:
                edu_parts.append(area)
            elif study_type:
                edu_parts.append(study_type)
            
            if institution:
                edu_parts.append(f"from {institution}")
            
            # Date range
            if start_date or end_date:
                date_range = f"{start_date} - {end_date}"
                edu_parts.append(f"({date_range})")
            
            if gpa:
                edu_parts.append(f"GPA: {gpa}")
            
            edu_text = " ".join(edu_parts) if edu_parts else "Education"
            story.append(Paragraph(edu_text, self.styles['ListItem']))

    def _add_skills(self, story: List, skills_data: List[Dict[str, Any]]):
        """Add skills section"""
        story.append(Paragraph("Skills", self.styles['SectionHeading']))
        
        for skill_group in skills_data:
            name = skill_group.get('name', '')
            keywords = skill_group.get('keywords', [])
            
            if isinstance(keywords, list):
                keywords_text = ', '.join(keywords)
            else:
                keywords_text = str(keywords)
            
            if name and keywords_text:
                skill_text = f"<b>{name}:</b> {keywords_text}"
            elif keywords_text:
                skill_text = keywords_text
            else:
                continue
                
            story.append(Paragraph(skill_text, self.styles['ListItem']))

    def _add_projects(self, story: List, projects_data: List[Dict[str, Any]]):
        """Add projects section"""
        story.append(Paragraph("Projects", self.styles['SectionHeading']))
        
        for project in projects_data:
            name = project.get('name', '')
            description = project.get('description', '')
            keywords = project.get('keywords', [])
            
            # Project name
            if name:
                story.append(Paragraph(f"<b>{name}</b>", self.styles['JobTitle']))
            
            # Project description
            if description:
                story.append(Paragraph(description, self.styles['Normal']))
            
            # Technologies used
            if keywords:
                if isinstance(keywords, list):
                    tech_text = f"<i>Technologies: {', '.join(keywords)}</i>"
                else:
                    tech_text = f"<i>Technologies: {keywords}</i>"
                story.append(Paragraph(tech_text, self.styles['Normal']))
            
            story.append(Spacer(1, 8))

    def _add_awards(self, story: List, awards_data: List[Dict[str, Any]]):
        """Add awards section"""
        story.append(Paragraph("Awards & Achievements", self.styles['SectionHeading']))
        
        for award in awards_data:
            title = award.get('title', '')
            date = award.get('date', '')
            awarder = award.get('awarder', '')
            summary = award.get('summary', '')
            
            # Award header
            award_parts = []
            if title:
                award_parts.append(f"<b>{title}</b>")
            if awarder:
                award_parts.append(f"from {awarder}")
            if date:
                award_parts.append(f"({date})")
            
            if award_parts:
                award_text = " ".join(award_parts)
                story.append(Paragraph(award_text, self.styles['ListItem']))
            
            # Award description
            if summary:
                story.append(Paragraph(summary, self.styles['Normal']))


# Compatibility function that matches the existing generator.py interface
def generate_pdf_resume(json_resume: Dict[str, Any], output_path: str = "resume") -> str:
    """
    Generate PDF resume using ReportLab (compatible with existing interface).
    
    Args:
        json_resume: Resume data in generator format
        output_path: Output path without .pdf extension
        
    Returns:
        str: Path to generated PDF file
    """
    generator = ReportLabResumeGenerator()
    pdf_path = generator.generate_pdf_resume(json_resume, output_path)
    print(f"[SUCCESS] Resume generated: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    # Test with sample data
    sample_resume = {
        "basics": {
            "name": "张三",
            "label": "软件工程师",
            "email": "zhangsan@example.com",
            "phone": "+86 123-4567-8901",
            "website": "https://zhangsan.dev",
            "summary": "热爱系统设计，具备丰富的后端与AI Agent开发经验",
        },
        "education": [
            {
                "institution": "清华大学",
                "area": "计算机科学与技术",
                "studyType": "本科",
                "startDate": "2018-09",
                "endDate": "2022-07",
                "gpa": "3.8/4.0",
            }
        ],
        "work": [
            {
                "company": "字节跳动",
                "position": "后端实习生",
                "startDate": "2022-07",
                "endDate": "2022-12",
                "summary": "负责视频推荐系统的服务性能优化与缓存策略设计",
            }
        ],
        "skills": [
            {"name": "编程语言", "keywords": ["Python", "Go", "C++"]},
            {"name": "数据库", "keywords": ["PostgreSQL", "MongoDB", "Redis"]},
        ],
        "projects": [
            {
                "name": "AI 简历优化助手",
                "description": "基于 RAG 与向量数据库构建的简历内容增强系统，提升匹配度与可读性",
                "keywords": ["RAG", "FastAPI", "FAISS"],
            }
        ],
        "awards": [
            {
                "title": "ACM ICPC 区域赛铜奖",
                "date": "2021-12",
                "awarder": "ACM Asia",
                "summary": "在区域赛中获得优异成绩",
            }
        ],
    }
    
    generate_pdf_resume(sample_resume, "test_resume") 