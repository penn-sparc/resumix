import json
import numpy as np
import faiss
from resumix.shared.utils.sentence_transformer_utils import SentenceTransformerUtils
from pathlib import Path
from resumix.config.config import Config

CONFIG = Config().config


def build_faiss_index(
    data_save_path: str = CONFIG.RAG.DATA_PATH,
    index_save_path: str = CONFIG.RAG.INDEX_PATH,
):
    # 1. 加载语料

    # 🌟 打印出路径是怎么解析的
    print(f"📂 当前工作目录: {Path.cwd()}")
    print(f"📄 尝试保存 data.json 到: {Path(data_save_path).resolve()}")
    print(f"📄 尝试保存 index.json 到: {Path(index_save_path).resolve()}")

    data = [
        {
            "text": "Developed a distributed microservices backend using Golang and gRPC, achieving 99.9% uptime and supporting over 10 million daily requests."
        },
        {
            "text": "Deployed and managed Kubernetes clusters for staging and production environments, ensuring seamless CI/CD integration and blue-green releases."
        },
        {
            "text": "Built RESTful and gRPC APIs for internal services, including authentication, task scheduling, and data ingestion modules."
        },
        {
            "text": "Implemented monitoring and logging solutions using Prometheus and Grafana to improve system observability and reliability."
        },
        {
            "text": "Collaborated with product managers and frontend engineers to deliver scalable features under Agile development practices."
        },
        {
            "text": "Designed a message queue architecture using Kafka and Redis Stream to decouple services and improve throughput under high concurrency."
        },
        {
            "text": "Proficient in Golang, Docker, Kubernetes, MySQL, Redis, and Git; experienced in cloud-native backend system development."
        },
        {
            "text": "Job Requirement: Strong experience with Go or Java backend development; familiarity with container orchestration platforms like Kubernetes."
        },
        {
            "text": "Job Requirement: Ability to design and implement high-concurrency systems, optimize service latency, and handle distributed transactions."
        },
        {
            "text": "Job Requirement: Knowledge of microservices, API gateway, service mesh (e.g., Istio), and gRPC-based service-to-service communication."
        },
    ]

    texts = [entry["text"] for entry in data]

    # 2. 嵌入编码
    model = SentenceTransformerUtils.get_instance()
    embeddings = model.encode(texts, normalize_embeddings=True).astype(np.float32)

    # 3. 构建向量索引（使用点积作为相似度）
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    # 4. 保存索引
    faiss.write_index(index, index_save_path)
    print(f"✅ FAISS index saved to {index_save_path}")

    # ✅ 同时保存文本数据
    with open(data_save_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ FAISS index saved to {index_save_path}")
    print(f"✅ Text data saved to {data_save_path}")


# 用法示例
if __name__ == "__main__":
    import os

    print("当前工作目录是:", os.getcwd())
    build_faiss_index()
