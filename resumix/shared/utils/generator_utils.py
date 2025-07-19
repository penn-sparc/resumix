from resumix.shared.section.section_base import SectionBase
from typing import Dict, Any, Optional, List
from loguru import logger
import json
import re


class GeneratorUtils:
    """
    Utility class for converting parsed resume sections to generator-compatible format.
    
    This class handles the conversion between SectionBase objects (used in CompareCard)
    and the dictionary format expected by the resume generator.
    """

    @staticmethod
    def process_section(section: SectionBase) -> dict:
        """
        Process a single section and extract structured data.
        
        Args:
            section: SectionBase object containing section data
            
        Returns:
            dict: Processed section data in generator-compatible format
            
        Raises:
            ValueError: If section data cannot be processed
        """
        try:
            # Try to get JSON data from section, prioritizing rewritten content
            json_data = GeneratorUtils._extract_json_from_section(section)
            
            if json_data:
                logger.debug(f"Successfully extracted JSON data from section")
                return json_data
            else:
                logger.warning("No JSON data found, falling back to raw text processing")
                return GeneratorUtils._process_raw_text(section)
                
        except Exception as e:
            logger.error(f"Failed to process section: {e}")
            # Return a basic fallback structure
            return {"raw_content": getattr(section, 'raw_text', '')}

    @staticmethod
    def _extract_json_from_section(section: SectionBase) -> Optional[dict]:
        """
        Extract JSON data from section, trying multiple sources.
        
        Args:
            section: SectionBase object
            
        Returns:
            Optional[dict]: Parsed JSON data or None if not found
        """
        # Priority order: rewritten_text -> json_text -> raw_text
        sources = [
            getattr(section, 'rewritten_text', None),
            getattr(section, 'json_text', None),
            getattr(section, 'raw_text', None)
        ]
        
        for source in sources:
            if source:
                try:
                    # Try to parse as direct JSON
                    if source.strip().startswith('{'):
                        return json.loads(source)
                    
                    # Try to extract JSON from text using regex
                    json_match = re.search(r'\{.*\}', source, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                        
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.debug(f"Failed to parse JSON from source: {e}")
                    continue
        
        return None

    @staticmethod
    def _process_raw_text(section: SectionBase) -> dict:
        """
        Process raw text when JSON parsing fails.
        
        Args:
            section: SectionBase object
            
        Returns:
            dict: Basic structure with raw content
        """
        content = getattr(section, 'raw_text', '')
        if hasattr(section, 'lines') and section.lines:
            content = '\n'.join(section.lines)
        
        return {"content": content}

    @staticmethod
    def convert_sections_to_generator_format(sections: Dict[str, SectionBase]) -> dict:
        """
        Convert all sections to generator-compatible JSON resume format.
        
        Args:
            sections: Dictionary mapping section names to SectionBase objects
            
        Returns:
            dict: Complete resume data in generator.py expected format
        """
        logger.info(f"Converting {len(sections)} sections to generator format")
        
        # Initialize the resume structure with defaults
        resume_data = {
            "basics": {},
            "education": [],
            "work": [],
            "skills": [],
            "projects": [],
            "awards": []
        }
        
        # Section name mappings to standardize different naming conventions
        section_mappings = {
            # Personal info variations
            'personal_info': 'basics',
            'personal': 'basics',
            'contact': 'basics',
            'basics': 'basics',
            
            # Education variations
            'education': 'education',
            'education_section': 'education',
            
            # Work experience variations
            'experience': 'work',
            'work_experience': 'work',
            'professional_experience': 'work',
            'work': 'work',
            
            # Skills variations
            'skills': 'skills',
            'technical_skills': 'skills',
            
            # Projects variations
            'projects': 'projects',
            'project_section': 'projects',
            
            # Awards variations
            'awards': 'awards',
            'achievements': 'awards',
            'honors': 'awards'
        }
        
        for section_name, section_obj in sections.items():
            try:
                logger.debug(f"Processing section: {section_name}")
                
                # Normalize section name
                normalized_name = section_mappings.get(section_name.lower(), section_name.lower())
                
                # Process the section
                processed_data = GeneratorUtils.process_section(section_obj)
                
                # Map to the appropriate resume section
                if normalized_name == 'basics':
                    resume_data['basics'].update(GeneratorUtils._normalize_basics(processed_data))
                elif normalized_name == 'education':
                    education_list = GeneratorUtils._normalize_education(processed_data)
                    if isinstance(education_list, list):
                        resume_data['education'].extend(education_list)
                    else:
                        resume_data['education'].append(education_list)
                elif normalized_name == 'work':
                    work_list = GeneratorUtils._normalize_work(processed_data)
                    if isinstance(work_list, list):
                        resume_data['work'].extend(work_list)
                    else:
                        resume_data['work'].append(work_list)
                elif normalized_name == 'skills':
                    skills_list = GeneratorUtils._normalize_skills(processed_data)
                    if isinstance(skills_list, list):
                        resume_data['skills'].extend(skills_list)
                    else:
                        resume_data['skills'].append(skills_list)
                elif normalized_name == 'projects':
                    projects_list = GeneratorUtils._normalize_projects(processed_data)
                    if isinstance(projects_list, list):
                        resume_data['projects'].extend(projects_list)
                    else:
                        resume_data['projects'].append(projects_list)
                elif normalized_name == 'awards':
                    awards_list = GeneratorUtils._normalize_awards(processed_data)
                    if isinstance(awards_list, list):
                        resume_data['awards'].extend(awards_list)
                    else:
                        resume_data['awards'].append(awards_list)
                else:
                    logger.warning(f"Unknown section type: {section_name}, storing as raw content")
                    
            except Exception as e:
                logger.error(f"Failed to process section {section_name}: {e}")
                continue
        
        # Ensure basics has required fields
        if not resume_data['basics']:
            resume_data['basics'] = {
                "name": "未提供姓名",
                "label": "求职者",
                "email": "",
                "phone": "",
                "website": "",
                "summary": ""
            }
        
        logger.info("Successfully converted sections to generator format")
        return resume_data

    @staticmethod
    def _normalize_basics(data: dict) -> dict:
        """Normalize personal info/basics section."""
        if not isinstance(data, dict):
            return {"summary": str(data)}
        
        # PersonalInfoSection uses "address" not "location"
        location = data.get("location", {})
        if data.get("address") and not location:
            location = {"address": data["address"]}
        
        return {
            "name": data.get("name", ""),
            "label": data.get("label", data.get("title", "")),
            "email": data.get("email", ""),
            "phone": data.get("phone", ""),
            "website": data.get("website", data.get("url", "")),
            "summary": data.get("summary", data.get("content", "")),
            "location": location
        }

    @staticmethod
    def _normalize_education(data: dict) -> List[dict]:
        """Normalize education section."""
        if not isinstance(data, dict):
            return [{"institution": str(data)}]
        
        # If data already contains education list
        if "education" in data and isinstance(data["education"], list):
            return data["education"]
        
        # Single education entry - map "score" to "gpa" for generator.py compatibility
        return [{
            "institution": data.get("institution", ""),
            "area": data.get("area", data.get("degree", "")),
            "studyType": data.get("studyType", ""),
            "startDate": data.get("startDate", ""),
            "endDate": data.get("endDate", ""),
            "gpa": data.get("score", data.get("gpa", ""))  # Map score -> gpa
        }]

    @staticmethod
    def _normalize_work(data: dict) -> List[dict]:
        """Normalize work experience section."""
        if not isinstance(data, dict):
            return [{"summary": str(data)}]
        
        # If data already contains work list
        if "work" in data and isinstance(data["work"], list):
            return data["work"]
        
        # Single work entry - convert highlights array to summary string
        summary = ""
        if data.get("highlights") and isinstance(data["highlights"], list):
            # Convert highlights array to bullet-point summary string
            summary = "\n".join([f"• {highlight}" for highlight in data["highlights"]])
        else:
            summary = data.get("summary", data.get("description", data.get("content", "")))
        
        return [{
            "company": data.get("company", ""),
            "position": data.get("position", data.get("title", "")),
            "startDate": data.get("startDate", ""),
            "endDate": data.get("endDate", ""),
            "summary": summary
        }]

    @staticmethod
    def _normalize_skills(data: dict) -> List[dict]:
        """Normalize skills section."""
        # Handle flat list from SkillsSection.parsed_data (just an array of strings)
        if isinstance(data, list):
            return [{"name": "Skills", "keywords": data}]
        
        if not isinstance(data, dict):
            return [{"name": "Skills", "keywords": [str(data)]}]
        
        # If data already contains structured skills list
        if "skills" in data and isinstance(data["skills"], list):
            return data["skills"]
        
        # Convert flat skills to structured format
        skills_list = []
        for key, value in data.items():
            if isinstance(value, list):
                skills_list.append({"name": key, "keywords": value})
            elif isinstance(value, str):
                skills_list.append({"name": key, "keywords": value.split(", ")})
        
        return skills_list if skills_list else [{"name": "Skills", "keywords": []}]

    @staticmethod
    def _normalize_projects(data: dict) -> List[dict]:
        """Normalize projects section."""
        if not isinstance(data, dict):
            return [{"name": "Project", "description": str(data)}]
        
        # If data already contains projects list
        if "projects" in data and isinstance(data["projects"], list):
            return data["projects"]
        
        # Single project entry
        return [{
            "name": data.get("name", ""),
            "description": data.get("description", data.get("content", "")),
            "keywords": data.get("keywords", data.get("technologies", []))
        }]

    @staticmethod
    def _normalize_awards(data: dict) -> List[dict]:
        """Normalize awards section."""
        if not isinstance(data, dict):
            return [{"title": str(data)}]
        
        # If data already contains awards list
        if "awards" in data and isinstance(data["awards"], list):
            return data["awards"]
        
        # Single award entry
        return [{
            "title": data.get("title", data.get("name", "")),
            "date": data.get("date", ""),
            "awarder": data.get("awarder", ""),
            "summary": data.get("summary", data.get("description", ""))
        }]
