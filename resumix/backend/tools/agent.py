from langchain.agents import initialize_agent, AgentType
from langchain.agents.agent import AgentExecutor
from langchain.tools.render import render_text_description
from resumix.backend.tools.resume_parser_tool import ResumeParserTool
from resumix.shared.utils.llm_client import LLMClient, LLMWrapper


def test_resume_parser_tool():
    # ✅ 初始化工具和 LLM
    client = LLMClient()
    llm = LLMWrapper(client=client)
    tool = ResumeParserTool()

    # ✅ 构造 Agent
    agent = initialize_agent(
        tools=[tool],
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
    )

    # ✅ 构造 resume 文本（真实格式）
    resume_text = """张三  
联系方式：zhangsan@example.com  
教育背景：  
2015-2019 北京大学 计算机科学 本科  

技能：Python, PyTorch, TensorFlow"""

    # ✅ 提示词：清晰指定工具调用
    prompt = f"""
You are a helpful AI assistant that extracts structured resume information using the provided tools.

Please analyze the following resume:

\"\"\"{resume_text}\"\"\"

Use the `resume_parser` tool to extract information in structured form. 
Do not attempt to answer directly.
"""

    # ✅ 执行 Agent
    response = agent.run(prompt)

    print("\n==============================")
    print("✅ Tool Test Output:")
    print(response)
    print("==============================\n")


if __name__ == "__main__":
    test_resume_parser_tool()
