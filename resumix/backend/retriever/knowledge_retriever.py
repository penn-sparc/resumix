from typing import List
from resumix.shared.utils.sentence_transformer_utils import SentenceTransformerUtils
import faiss
import numpy as np
import json
import os
from resumix.config.config import Config

CONFIG = Config().config


class KnowledgeRetriever:
    def __init__(
        self,
        data_path: str = CONFIG.RAG.DATA_PATH,
        index_path: str = CONFIG.RAG.INDEX_PATH,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        """
        :param index_path: FAISS index 文件路径
        :param data_path: 与 index 对应的原始文本文件（JSON list，每个 entry 有 'text' 字段）
        :param model_name: 嵌入模型名称
        """
        self.index = faiss.read_index(index_path) if index_path else None
        self.data = self._load_data(data_path)
        self.init()

    def init(self):
        self.model = SentenceTransformerUtils.get_instance()

    def _load_data(self, path: str) -> List[dict]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def retrieve(
        self, section, tech_stacks: List[str], job_positions: List[str], top_k=5
    ) -> List[str]:
        """
        给定简历段落、技术栈、岗位名称，检索相关上下文
        """
        # 1. 构造查询语句（可以更复杂）

        query_text = (
            f"Resume section: {section.raw_text.strip()}\n"
            f"Target job positions: {', '.join(job_positions)}\n"
            f"Relevant technologies: {', '.join(tech_stacks)}\n"
            f"Please retrieve reference resume descriptions or job requirement phrases that match this content."
        )

        query_embedding = self.model.encode(
            [query_text], normalize_embeddings=True
        )  # shape: (1, dim)

        # 2. 检索
        distances, indices = self.index.search(
            query_embedding.astype(np.float32), top_k
        )

        # 3. 返回原始文本
        results = []
        for i in indices[0]:
            if 0 <= i < len(self.data):
                results.append(self.data[i]["text"])
        return results
