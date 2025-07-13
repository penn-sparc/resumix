import streamlit as st
from loguru import logger
from typing import Dict
from resumix.shared.utils.session_utils import SessionUtils
from resumix.frontend.components.cards.score_card import ScoreCard
from resumix.backend.module.score_module import ScoreModule
from resumix.shared.section.section_base import SectionBase


class ScorePage:
    """Page for scoring resume sections against job description"""
    
    def __init__(self):
        self.score_module = ScoreModule()
    
    def _check_prerequisites(self):
        """Check if resume and JD URL are available"""
        # Check if resume is uploaded
        if "resume_text" not in st.session_state or not st.session_state.resume_text:
            st.warning("📄 Please upload a resume first in the sidebar.")
            return False
        
        # Check if JD URL is provided
        jd_url = st.session_state.get("jd_url", "")
        if not jd_url or not jd_url.strip():
            st.warning("🔗 Please provide a job description URL in the sidebar.")
            return False
        
        return True
    
    def _find_section_keys(self, jd_sections: Dict):
        """Find basic and preferred requirement sections from JD"""
        basic_key = None
        preferred_key = None
        
        # First, try exact matches
        for key in jd_sections.keys():
            key_lower = key.lower()
            if "basic" in key_lower and ("qualification" in key_lower or "requirement" in key_lower):
                basic_key = key
            elif "preferred" in key_lower and ("qualification" in key_lower or "requirement" in key_lower):
                preferred_key = key
        
        # If no exact match, try broader matching
        if not basic_key:
            for key in jd_sections.keys():
                key_lower = key.lower()
                if any(term in key_lower for term in ["requirement", "qualification", "skill", "must", "essential"]):
                    basic_key = key
                    break
        
        # Use any section as basic if we still don't have one
        if not basic_key and jd_sections:
            basic_key = list(jd_sections.keys())[0]
            st.warning(f"⚠️ Using '{basic_key}' as basic requirements section")
        
        return basic_key, preferred_key
    
    def _convert_to_section_base(self, jd_sections: Dict, key: str):
        """Convert JD section to SectionBase object"""
        if not key or key not in jd_sections:
            return None
        
        jd_obj = jd_sections[key]
        
        if hasattr(jd_obj, 'raw_text'):
            # Already a SectionBase object
            jd_text = getattr(jd_obj, 'raw_text', '')
        elif isinstance(jd_obj, list):
            jd_text = "\n".join(str(item) for item in jd_obj)
        elif isinstance(jd_obj, str):
            jd_text = jd_obj
        else:
            jd_text = str(jd_obj)
        
        return SectionBase(name=key, raw_text=jd_text)
    
    def _score_section(self, section_name: str, section_obj, jd_basic_section, jd_preferred_section):
        """Score a single resume section"""
        try:
            logger.info(f"Scoring section: {section_name}")
            
            score_result = self.score_module.score_resume(
                section_obj,
                jd_basic_section,
                jd_preferred_section
            )
            
            logger.info(f"Score result for {section_name}: {score_result}")
            
            # Check if we got a valid score result
            if isinstance(score_result, dict) and not score_result.get('error'):
                # Display individual section score
                score_card = ScoreCard(section_name, score_result)
                score_card.render()
                st.markdown("---")
                return True
            else:
                # Handle error case
                error_msg = score_result.get('error', 'Unknown error') if isinstance(score_result, dict) else str(score_result)
                st.error(f"❌ Scoring failed for {section_name}: {error_msg}")
                
                # Show test score card for this section
                test_scores = {
                    "Completeness": 5,
                    "Clarity": 5,
                    "Relevance": 5,
                    "Comment": f"Scoring failed for {section_name}: {error_msg}"
                }
                test_score_card = ScoreCard(section_name, test_scores)
                test_score_card.render()
                st.markdown("---")
                return False
                
        except Exception as e:
            logger.error(f"Failed to score section {section_name}: {e}")
            st.error(f"❌ Failed to score {section_name}: {e}")
            
            # Show test score card for this section
            test_scores = {
                "Completeness": 5,
                "Clarity": 5,
                "Relevance": 5,
                "Comment": f"Scoring failed for {section_name}: {e}"
            }
            test_score_card = ScoreCard(section_name, test_scores)
            test_score_card.render()
            st.markdown("---")
            return False
    
    def render(self):
        """Render the score page"""
        st.markdown("## 📊 Resume Scoring")
        
        # Check prerequisites
        if not self._check_prerequisites():
            # Show demo score card
            st.subheader("🧪 Demo Score Card")
            st.info("This is a demonstration of how scoring results will look:")
            
            demo_scores = {
                "Completeness": 8,
                "Clarity": 7,
                "Relevance": 6,
                "ProfessionalLanguage": 9,
                "AchievementOriented": 5,
                "QuantitativeSupport": 4,
                "Comment": "This is a demo score card showing how results will be displayed."
            }
            demo_card = ScoreCard("Demo Section", demo_scores)
            demo_card.render()
            return
        
        try:
            # Parse JD sections
            with st.spinner("Parsing job description..."):
                jd_sections = SessionUtils.get_jd_sections()
            
            # Show basic info about parsed sections
            st.success(f"✅ Job description parsed successfully! Found {len(jd_sections)} sections.")
            
            # Show sections in a more compact way
            with st.expander("📄 View Parsed JD Sections"):
                for key, value in jd_sections.items():
                    st.markdown(f"**{key}:**")
                    if hasattr(value, 'raw_text'):
                        content = getattr(value, 'raw_text', '')
                        st.text(content[:300] + "..." if len(content) > 300 else content)
                    elif isinstance(value, list):
                        st.text(str(value)[:300] + "..." if len(str(value)) > 300 else str(value))
                    elif isinstance(value, str):
                        st.text(value[:300] + "..." if len(value) > 300 else value)
                    else:
                        st.text(str(value)[:300] + "..." if len(str(value)) > 300 else str(value))
                    st.markdown("---")
            
            # Find section keys
            basic_key, preferred_key = self._find_section_keys(jd_sections)
            
            st.info(f"🎯 Selected sections - Basic: {basic_key}, Preferred: {preferred_key}")
            
            if not basic_key:
                st.warning("⚠️ No suitable JD sections found for scoring")
                st.info("📊 Available sections: " + ", ".join(jd_sections.keys()))
                
                # Show demo score card
                st.subheader("🧪 Demo Score Card")
                demo_scores = {
                    "Completeness": 8,
                    "Clarity": 7,
                    "Relevance": 6,
                    "ProfessionalLanguage": 9,
                    "AchievementOriented": 5,
                    "QuantitativeSupport": 4,
                    "Comment": "Demo score card - no suitable JD sections found for real scoring"
                }
                demo_card = ScoreCard("Demo Section", demo_scores)
                demo_card.render()
                return
            
            # Convert JD sections to SectionBase objects
            jd_basic_section = self._convert_to_section_base(jd_sections, basic_key) if basic_key else None
            jd_preferred_section = self._convert_to_section_base(jd_sections, preferred_key) if preferred_key else None
            
            if not jd_preferred_section:
                jd_preferred_section = SectionBase(name="requirements_preferred", raw_text="")
            
            # Get resume sections
            resume_sections = SessionUtils.get_resume_sections()
            
            if not resume_sections:
                st.error("❌ No resume sections found. Please upload a valid resume.")
                return
            
            # Show overall scoring progress
            st.success("✅ JD sections found! Starting resume scoring...")
            
            # Score each section
            section_scores = {}
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_sections = len(resume_sections)
            successful_scores = 0
            
            for i, (section_name, section_obj) in enumerate(resume_sections.items()):
                status_text.text(f"Scoring {section_name}... ({i+1}/{total_sections})")
                progress_bar.progress((i + 1) / total_sections)
                
                if self._score_section(section_name, section_obj, jd_basic_section, jd_preferred_section):
                    successful_scores += 1
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            if successful_scores > 0:
                st.success(f"✅ Resume scoring completed! Scored {successful_scores} sections successfully.")
            else:
                st.warning("⚠️ No sections were scored successfully. Please check your resume and job description.")
                
        except Exception as e:
            logger.error(f"Failed to get JD sections: {e}")
            st.error(f"⚠️ Job description parsing failed: {e}")
            st.info("📊 Please check your job description URL and try again.")
            
            # Show demo score card
            st.subheader("🧪 Demo Score Card")
            demo_scores = {
                "Completeness": 8,
                "Clarity": 7,
                "Relevance": 6,
                "ProfessionalLanguage": 9,
                "AchievementOriented": 5,
                "QuantitativeSupport": 4,
                "Comment": "Demo score card - JD parsing failed"
            }
            demo_card = ScoreCard("Demo Section", demo_scores)
            demo_card.render()
