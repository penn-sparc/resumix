import json
import re
import ast
from typing import Union, Dict
from loguru import logger


class JsonParser:
    @staticmethod
    def parse(response: str) -> Union[Dict, None]:
        """
        安全解析 LLM 响应中的 JSON 字符串。

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

        # 解析 JSON：先 json 再 ast
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e_json:
            logger.warning(
                f"[json.loads] 解析失败: {e_json}, 尝试 fallback ast.literal_eval"
            )
            try:
                return ast.literal_eval(cleaned)
            except Exception as e_ast:
                logger.error(f"[ast.literal_eval] 解析仍失败: {e_ast}")
                return None
