import streamlit as st
from typing import Dict, Optional, Callable
from components.cards.base_card import BaseCard
from resumix.job_parser.resume_parser import ResumeParser
from resumix.utils.logger import logger
from streamlit_option_menu import option_menu
from streamlit_tags import st_tags


class AgentCard(BaseCard):
    def __init__(
        self,
        title: str = "AI Agent Assistant",
        icon: str = "🤖",
        comment: Optional[str] = None,
        additional_content: Optional[str] = None,
    ):
        super().__init__(
            title=title,
            icon=icon,
            comment=comment,
            additional_content=additional_content,
        )
        self.parser = ResumeParser()

    def render_agent_response(self, result: str):
        st.chat_message("Resumix").write(result)

    def render_agent_interaction(self, text: str, jd_content: str, agent):
        sections = self.parser.parse_resume(text)
        for section, content in sections.items():
            prompt = f"""你是一个简历优化助手。请参考以下岗位描述，并优化简历内容：

                岗位描述：{jd_content}

                简历原文：
\"\"\"{content}\"\"\"

请按照如下格式作答：
Thought: ...
Action: local_llm_generate
Action Input: \"\"\"优化后的内容\"\"\"
"""
            result = agent.run(prompt)
            self.render_agent_response(result)

    def render(self):
        """Complete card rendering implementation"""
        self.render_header()
        
        if self.comment:
            self.render_comment()
        self.render_additional()

    def redner_options(self):

        # 技术栈多选
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
                "PyTorch",
                "TensorFlow",
                "Kubernetes",
                "Docker",
                "Spark",
                "Redis",
                "RabbitMQ",
                "Kafka",
                "Elasticsearch",
                "MySQL",
                "PostgreSQL",
                "MongoDB",
                "Redis",
                "RabbitMQ",
            ],
            selection_mode="multi",
        )

        # 职位多选
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

        # 提交按钮
        if st.button("✅ Submit"):
            st.subheader("你选择的技术栈：")
            st.write(selected_tech_stacks)

            st.subheader("你期望的职位：")
            st.write(selected_job_positions)


def agent_card(text: str):
    """Legacy function wrapper for backward compatibility"""
    logger.info("Handling Resume Agent with provided resume text.")
    card = AgentCard()
    card.render()


def handle_agent(text: str, jd_content: str, agent):
    """Legacy function wrapper for backward compatibility"""
    logger.info(
        "Handling AI Agent with provided resume text and job description content."
    )
    card = AgentCard()
    card.render()
    card.render_agent_interaction(text, jd_content, agent)
