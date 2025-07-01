import streamlit as st
from typing import Dict, Optional
from resumix.frontend.components.cards.base_card import BaseCard
from resumix.backend.job_parser.resume_parser import ResumeParser
from resumix.shared.utils.logger import logger
from resumix.shared.section.section_base import SectionBase
from resumix.shared.model.schema.schema import TechOptimizeRequest, TechOptimizeResponse, BaseRequest
from typing import List, Tuple
import requests
from config.config import Config
import traceback

CONFIG = Config().config

class AgentCard(BaseCard):
    def __init__(
        self,
        title: str = "AI Agent Assistant",
        icon: str = "🤖",
        comment: Optional[str] = None,
        additional_content: Optional[str] = None,
    ):
        """
        Initialize an AgentCard for AI-powered resume optimization.

        Args:
            title: Card title
            icon: Display icon for the card
            comment: Optional comment to display
            additional_content: Optional additional content
        """
        super().__init__(
            title=title,
            icon=icon,
            comment=comment,
            additional_content=additional_content,
        )
        self.parser = ResumeParser()
        self.sections = {}
    def set_sections(self, sections: Dict[str, SectionBase]):
        self.sections = sections


    # def parse_resume_sections(self, text: str) -> Dict[str, SectionBase]:
    #     """
    #     Parse the resume text into structured sections.

    #     Args:
    #         text: Raw resume text to parse

    #     Returns:
    #         Dictionary of section names to SectionBase objects
    #     """
    #     try:
    #         logger.info("Parsing resume text for agent processing")
    #         self.sections = self.parser.parse_resume(text)
    #         return self.sections
    #     except Exception as e:
    #         logger.error(f"Failed to parse resume for agent: {e}")
    #         st.error(f"❌ Resume parsing failed: {e}")
    #         return {}

#     def create_optimization_prompt(
#         self, section_name: str, section_content: str, jd_content: str
#     ) -> str:
#         """
#         Create an optimization prompt for the AI agent.

#         Args:
#             section_name: Name of the resume section
#             section_content: Content of the section
#             jd_content: Job description content

#         Returns:
#             Formatted prompt for the agent
#         """
#         prompt = f"""你是一个简历优化助手。请参考以下岗位描述，并优化简历内容：

#             岗位描述：{jd_content}

#             简历原文：
# \"\"\"{section_content}\"\"\"

# 请按照如下格式作答：
# Thought: ...
# Action: local_llm_generate
# Action Input: \"\"\"优化后的内容\"\"\"
# """
#         return prompt

#     def render_agent_response(self, result: str):
#         """
#         Render the agent's response.

#         Args:
#             result: Agent response to display
#         """
#         try:
#             st.chat_message("Resumix").write(result)
#         except Exception as e:
#             logger.error(f"Failed to render agent response: {e}")
#             st.warning("Could not display agent response")

    # def render_section_optimization(
    #     self, section_name: str, section_obj: SectionBase, jd_content: str, agent
    # ):
    #     """
    #     Render optimization for a single resume section.

    #     Args:
    #         section_name: Name of the section
    #         section_obj: SectionBase object containing section data
    #         jd_content: Job description content
    #         agent: AI agent instance
    #     """
    #     try:
    #         st.subheader(f"🔧 Optimizing: {section_name.upper()}")

    #         # # Get section content
    #         # content = getattr(section_obj, "original_lines", None)
    #         # if content:
    #         #     content = "\n".join(content)
    #         # else:
    #         #     content = section_obj.raw_text or "\n".join(section_obj.lines)

    #         # Create and run optimization prompt
    #         with st.spinner(f"AI is optimizing {section_name}..."):
                
    #             # payload = TechOptimizeRquest(
    #             #     section_name=section,
                    
    #             #     jd_text=,
    #             #     tech_stack= 
                
                
                
    #             prompt = self.create_optimization_prompt(
    #                 section_name, content, jd_content
    #             )
    #             result = agent.run(prompt)
    #             self.render_agent_response(result)

    #     except Exception as e:
    #         logger.error(f"Failed to optimize section {section_name}: {e}")
    #         st.error(f"❌ Failed to optimize {section_name}: {e}")

    # def render_agent_interaction(self, text: str, jd_content: str, agent):
    #     """
    #     Main agent interaction rendering logic.
    #     This incorporates the logic from agent_module.py

    #     Args:
    #         text: Resume text to process
    #         jd_content: Job description content
    #         agent: AI agent instance
    #     """
    #     logger.info(
    #         "Handling AI Agent with provided resume text and job description content."
    #     )

    #     # Parse resume sections
    #     sections = self.parse_resume_sections(text)

    #     if not sections:
    #         st.warning("Unable to parse resume sections for optimization.")
    #         return

    #     # Show overview
    #     st.info(
    #         f"🤖 **Ready to optimize {len(sections)} sections:** {', '.join(sections.keys())}"
    #     )
    #     st.divider()

    #     # Process each section with the agent
    #     for section_name, section_obj in sections.items():
    #         self.render_section_optimization(
    #             section_name, section_obj, jd_content, agent
    #         )
    #         st.divider()

    def _render_tech_stack_selection(self):
        """Render technology stack selection interface"""
        selected_tech_stacks = st.segmented_control(
            "🛠️ 选择你掌握的技术栈",
            options=[
                "PyTorch",
                "TensorFlow",
                "Kubernetes",
                "Docker",
                "Spark",
                "Redis",
                "RabbitMQ",
                "ONNX",
                "Kafka",
                "Elasticsearch",
                "MySQL",
                "PostgreSQL",
                "MongoDB",
            ],
            selection_mode="multi",
        )
        return selected_tech_stacks

    def _render_job_position_selection(self):
        """Render job position selection interface"""
        selected_job_positions = st.segmented_control(
            "💼 选择你期望的职位类型",
            options=[
                "Backend",
                "Frontend",
                "Fullstack",
                "DevOps",
                "Data Engineer",
                "Data Scientist",
                "AI Engineer",
                "ML Engineer",
            ],
            selection_mode="multi",
        )
        return selected_job_positions

    def _render_options(self)-> Tuple[List[str], List[str]]:
        """
        Render user option selection interface.
        This replaces the misspelled 'redner_options' method.
        """
        try:
            # Technology stack selection
            selected_tech_stacks = self._render_tech_stack_selection()

            # Job position selection
            selected_job_positions = self._render_job_position_selection()

            return selected_tech_stacks, selected_job_positions

        except Exception as e:
            logger.error(f"Failed to render options: {e}")
            return [], []

    def render_card_body(self):
        """
        Render the main agent card content with clean text hierarchy.
        """
        pass
        # try:
        #     st.markdown("### 🤖 AI Assistant")
        #     st.markdown("Get personalized resume advice and suggestions")

        #     # Simple option selections
        #     st.markdown("#### 🛠️ Technology Preferences")
        #     selected_tech_stacks = self.render_tech_stack_selection()

        #     st.markdown("#### 💼 Target Positions")
        #     selected_job_positions = self.render_job_position_selection()

        #     if selected_tech_stacks or selected_job_positions:
        #         st.markdown("#### 💡 Recommendations")
        #         st.info(
        #             f"Based on your selections, consider highlighting experience with: {', '.join(selected_tech_stacks[:3])}"
        #         )

        # except Exception as e:
        #     logger.error(f"Failed to render agent card body: {e}")
        #     st.error("Could not display AI assistant interface")

    # def render_comment(self):
    #     """Render the comment section"""
    #     if self.comment:
    #         st.markdown(f"*🤖 {self.comment}*")
    
    def process(self, sections: Dict[str, SectionBase], tech_stacks: List[str], job_positions: List[str]):
        for section in sections.values():
            self.process_section(section, tech_stacks, job_positions)
            st.divider()
            
    def process_section(self, section: SectionBase, tech_stacks: List[str], job_positions: List[str]):
        with st.spinner(f"AI is optimizing {section.name}..."):
            result = self.process_section_api(section, tech_stacks, job_positions)
            st.chat_message("Resumix").write(result)
    
            
                
    def process_section_api(self, section: SectionBase, tech_stacks: List[str], job_positions: List[str]) -> str:
        payload = {
            "data": {
                "section": section.model_dump(),
                "tech_stack": tech_stacks,
                "job_positions": job_positions
            }
        }
        try:
            response = requests.post(CONFIG.BACKEND.HOST + "/agent/rewrite", json=payload)
            response.raise_for_status()
            return response.json().get("data", None)
        except requests.exceptions.RequestException as e:
                st.error(f"❌ Failed to optimize section {section.name}: {e}")
                logger.exception(f"❌ RequestException while optimizing section {section.name}")
        except Exception as e:
                st.error(f"❌ Failed to optimize section {section.name}: {e}")
                logger.exception(f"❌ Unexpected error while optimizing section {section.name}")

    def render(self):
        """
        Simple render method using the clean BaseCard structure.
        """
        logger.info("Rendering AgentCard")

        # Use the simplified BaseCard render method
        super().render()
        
        tech_stacks, job_positions = self._render_options()
        
        logger.info(type(self.sections))
        self.process(self.sections, tech_stacks, job_positions)

def agent_card(text: str):
    """
    Legacy function wrapper for backward compatibility.
    This maintains the same interface as agent_module.py
    """
    logger.info("Handling Resume Agent with provided resume text.")
    card = AgentCard(
        comment="AI-powered resume optimization assistant",
        additional_content="Select your preferences and let AI optimize your resume",
    )
    card.render()


def handle_agent(text: str, jd_content: str, agent):
    """
    Legacy function wrapper for backward compatibility.
    This maintains the same interface as agent_module.py
    """
    logger.info(
        "Handling AI Agent with provided resume text and job description content."
    )
    card = AgentCard(
        comment="AI-powered resume optimization in progress",
        additional_content="Each section will be optimized based on the job description",
    )
    card.render()
    card.render_agent_interaction(text, jd_content, agent)
