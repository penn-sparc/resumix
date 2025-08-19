import json
import re
import ast
from typing import Union, Dict, Any
from loguru import logger


class JsonParser:
    @staticmethod
    def parse(response: str) -> Union[Dict, None]:
        """
        安全parsing LLM 响应中的 JSON 字符串。

        优先使用 json.loads，失败时回退至 ast.literal_eval。
        如果均失败，返回 None。
        """

        logger.info(f"Parsing JSON: {response}")

        if not isinstance(response, str):
            logger.warning("LLM 响应不是字符串")
            return None

        # 移除 Final Answer 等前缀（支持中英文冒号）
        response = re.sub(r"(?i)^final answer[:：]\s*", "", response.strip())

        # 提取 markdown 中的 JSON
        pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
        match = re.search(pattern, response, re.DOTALL)
        cleaned = match.group(1) if match else response.strip()

        # 替换常见中文标点为合法字符
        replacements = {
            "“": '"',
            "”": '"',
            "‘": "'",
            "’": "'",
            "…": "...",
        }
        for bad, good in replacements.items():
            cleaned = cleaned.replace(bad, good)

        # 去除非法控制字符
        cleaned = re.sub(r"[\x00-\x1F\x7F]", "", cleaned)

        # 删除对象或数组中的尾部逗号： {"a": 1,} -> {"a": 1}
        cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)

        logger.info(f"cleaned: {cleaned}")

        # parsing JSON：先 json 再 ast
        try:
            result = json.loads(cleaned)
            logger.info(f"JSON parsing成功: {result}")
            return result
        except json.JSONDecodeError as e_json:
            logger.warning(
                f"[json.loads] parsing失败: {e_json}, 尝试 fallback ast.literal_eval"
            )
            try:
                return ast.literal_eval(cleaned)
            except Exception as e_ast:
                logger.error(f"[ast.literal_eval] parsing仍失败: {e_ast}")
                return {}

    @staticmethod
    def _strip_markdown_code_fence(text: str) -> str:
        # 清除 markdown code block 头尾
        lines = text.strip().splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()

    @staticmethod
    def parse_string(section_json: str) -> Dict[str, Any]:
        try:
            section_json = JsonParser._strip_markdown_code_fence(section_json)
            logger.info(f"Section JSON: {section_json}")
            data = JsonParser.parse(section_json)
            return data
        except json.JSONDecodeError:
            logger.error("⚠️ JSON parsing失败，原始数据如下：")
            logger.error(section_json)
            return {}
