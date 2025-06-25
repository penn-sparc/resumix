from langchain.tools import Tool
from utils.llm_client import LLMClient

# 初始化本地 LLM 客户端
llm_client = LLMClient()

# 包装为 LangChain 工具
llm_tool = Tool.from_function(
    name="local_llm_generate",
    func=llm_client,
    description=(
        "Use this tool to generate or improve text based on a given prompt using a locally hosted language model. "
        "The input should be a natural language string describing what needs to be generated or edited, such as rewriting a resume section, summarizing a paragraph, or translating text. "
        "This tool is useful for polishing, editing, generating ideas, or completing sentences and paragraphs."
    ),
)

# 可选：工具列表（方便后续传入 agent）
tool_list = [llm_tool]
