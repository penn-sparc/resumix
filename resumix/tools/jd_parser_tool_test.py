# test_jd_parser_tool.py

from langchain.agents import initialize_agent, AgentType
from resumix.tools.jd_parser_tool import JDParserTool
from resumix.utils.llm_client import LLMClient, LLMWrapper


def test_jd_parser_tool():
    # 初始化 LLM 和工具
    client = LLMClient()
    llm = LLMWrapper(client=client)
    jd_parser_tool = JDParserTool()

    # 初始化 Agent
    agent = initialize_agent(
        tools=[jd_parser_tool],
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
    )

    # ✅ 提示词：清晰指定工具调用
    # 示例 JD 文本（可以替换成更长的 JD）
    jd_text = """
    Job Title: AI Research Engineer
    Location: Beijing, China

    Responsibilities:
    - Build scalable ML pipelines for real-time data
    - Collaborate with cross-functional teams
    - Write clean and well-documented code

    Basic Qualifications:
    - Bachelor's in CS, EE, or related fields
    - 2+ years in ML or NLP development

    Preferred Qualifications:
    - Experience with PyTorch or TensorFlow
    - Publications in top-tier conferences
    """

    replaced_jd_text = jd_text.replace("\n", "\\n")

    # 组装提示：直接强制调用工具
    prompt = f"""
    You are an assistant helping to extract structured sections from a job description.

    Action: jd_parser
    Action Input: {{
        "text": "{replaced_jd_text}"
    }}
    """

    # 执行 Agent 流程
    result = agent.run(prompt)

    print("\n==============================")
    print("✅ JD Parser Tool Output:")
    print(result)
    print("==============================\n")


if __name__ == "__main__":
    test_jd_parser_tool()
