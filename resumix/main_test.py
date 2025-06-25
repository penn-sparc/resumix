# main_test.py
import streamlit as st
from components.cards.analysis_card import AnalysisCard
from components.cards.polish_card import polish_card
from components.cards.agent_card import agent_card, AgentCard
from resumix.utils.llm_client import LLMWrapper, LLMClient
from typing import Callable  # Add this import
from langchain.agents import initialize_agent, AgentType
from tool.tool import tool_list
from components.cards.score_card import ScoreCard
from components.cards.compare_card import CompareCard
from resumix.job_parser.resume_rewriter import ResumeRewriter
from section.section_base import SectionBase
from resumix.utils.i18n import LANGUAGES
# Sample text for testing
sections = {
    "Work Experience": "This is the work experience section content.",
    "Education": "This is the education section content.",
    "Skills": "This is the skills section content."
}
text = "This is a sample resume content for testing purposes."

st.set_page_config(layout="wide")  # Ensure proper page setup

def main():
    st.title("Resume Analysis Test")
    
    card = AnalysisCard(
        comment="This is a test analysis",
        additional_content="Analysis powered by Resumix"
    )
    
    # Chain the rendering calls
    card.render().render_analysis(text)

    llm_model = LLMClient()  # Your initialized LLM client
    rewriter = ResumeRewriter(llm=llm_model)  # Pass your LLM client to the rewriter
    llm_agent = initialize_agent(
    tools=tool_list,
    llm=LLMWrapper(client=llm_model),
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5,
)
    resume_text = "Your resume text here..."
    job_description = "The job description text..."


    polish_card(resume_text, llm_model)
    # agent_card(
    # text=resume_text,
    # jd_content=job_description,
    # agent=llm_agent
    # )

    # # Or with method chaining:
    # card = AgentCard()
    # card.render().render_agent_interaction(resume_text, job_description, llm_agent)


    # scores = {
    # "Completeness": 8,
    # "Clarity": 7, 
    # "Relevance": 6,
    # "Comment": "Good section overall"
    # }

    # score_card = ScoreCard("Work Experience", scores)
    # score_card.render()  # This will now work

    # Dummy test data - replace with your actual data
    jd_content = "Looking for Python developer with 3+ years experience..."
    sections: Dict[str, SectionBase] = {
        "Skills": SectionBase(original_lines=["Python", "Java", "SQL"]),
        "Experience": SectionBase(original_lines=["Data Analyst at ABC Inc (2020-2023)"])
    }
    
    # Render the comparison interface
    st.title("Resume Comparison Tool")
    
    # Method 1: Using the functional interface
    compare_resume_sections(
        sections=sections,
        jd_content=jd_content,
        rewriter=rewriter
    )

if __name__ == "__main__":
    main()  # Explicitly call main function