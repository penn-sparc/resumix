import os
from dotenv import load_dotenv
from pathlib import Path
from loguru import logger
from config.config import Config


CONFIG = Config().config

# Load environment variables
load_dotenv()


class LLMConfig:
    @staticmethod
    # Use DeepSeek by default instead of local LLM
    def get_config():
        return {
            "url": CONFIG.LLM.DEEPSEEK.URL,
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "model": "deepseek-chat",
            "type": "deepseek",
        }