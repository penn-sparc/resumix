from sentence_transformers import SentenceTransformer
import threading
from resumix.config.config import Config

CONFIG = Config().config


class SentenceTransformerUtils:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(
        cls,
        model_name=CONFIG.SENTENCE_TRANSFORMER.USE_MODEL,
        cache_dir=CONFIG.SENTENCE_TRANSFORMER.DIRECTORY,
    ):
        if cls._instance is None:
            with cls._lock:  # 确保线程安全
                if cls._instance is None:
                    if model_name is None:
                        raise ValueError("首次调用必须提供 model_name")
                    cls._instance = SentenceTransformer(
                        model_name, cache_folder=cache_dir
                    )
        return cls._instance
