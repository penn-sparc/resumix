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

    # 🌟 打印出路径是怎么parsing的
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
        # -------------------- PyTorch --------------------
        {
            "text": "Trained and served PyTorch models with mixed precision and gradient checkpointing, reducing GPU memory by ~40% while keeping accuracy stable.",
            "tags": ["PyTorch"],
            "position": ["ML Engineer", "AI Engineer"],
            "category": "Achievement",
        },
        {
            "text": "Job Requirement: Experience exporting PyTorch models to TorchScript or ONNX and optimizing with quantization/TensorRT for low-latency inference.",
            "tags": ["PyTorch"],
            "position": ["ML Engineer"],
            "category": "Requirement",
        },
        # -------------------- TensorFlow --------------------
        {
            "text": "Migrated TensorFlow training to TF 2.x with tf.data pipelines and distributed strategy (Mirrored/TPU), improving input throughput by 2.3×.",
            "tags": ["TensorFlow"],
            "position": ["ML Engineer", "AI Engineer"],
            "category": "Achievement",
        },
        {
            "text": "Job Requirement: Solid understanding of Keras APIs, tf.data performance tuning, and SavedModel export for production serving.",
            "tags": ["TensorFlow"],
            "position": ["ML Engineer"],
            "category": "Requirement",
        },
        # -------------------- Kubernetes --------------------
        {
            "text": "Designed multi-tenant Kubernetes clusters with namespace isolation, PodSecurity admission, HPA/VPA, and Cluster Autoscaler for cost-efficient scaling.",
            "tags": ["Kubernetes"],
            "position": ["DevOps", "Backend"],
            "category": "Achievement",
        },
        {
            "text": "Job Requirement: Hands-on experience with Helm, Kustomize, and GitOps (Argo CD/Flux) to manage application releases across environments.",
            "tags": ["Kubernetes"],
            "position": ["DevOps"],
            "category": "Requirement",
        },
        # -------------------- Docker --------------------
        {
            "text": "Standardized Docker images with multi-stage builds and distroless base, shrinking image size by 65% and reducing CVE surface.",
            "tags": ["Docker"],
            "position": ["DevOps", "Backend"],
            "category": "Achievement",
        },
        {
            "text": "Job Requirement: Ability to write secure Dockerfiles, manage private registries, and implement image scanning & SBOM generation.",
            "tags": ["Docker"],
            "position": ["DevOps"],
            "category": "Requirement",
        },
        # -------------------- Spark --------------------
        {
            "text": "Built Spark ETL on Delta/Parquet with predicate pushdown and AQE, cutting end-to-end pipeline time from 90 min to 28 min.",
            "tags": ["Spark"],
            "position": ["Data Engineer"],
            "category": "Achievement",
        },
        {
            "text": "Job Requirement: Proficiency with Spark SQL, structured streaming, and optimizing joins/shuffles on large-scale datasets.",
            "tags": ["Spark"],
            "position": ["Data Engineer"],
            "category": "Requirement",
        },
        # -------------------- Redis --------------------
        {
            "text": "Deployed Redis as a read-through cache and distributed lock (RedLock), reducing DB read QPS by 70% and eliminating hot-key contention.",
            "tags": ["Redis"],
            "position": ["Backend", "DevOps"],
            "category": "Achievement",
        },
        {
            "text": "Job Requirement: Knowledge of Redis clustering, eviction policies, and designing cache-aside patterns with proper TTL and stampede control.",
            "tags": ["Redis"],
            "position": ["Backend"],
            "category": "Requirement",
        },
        # -------------------- RabbitMQ --------------------
        {
            "text": "Implemented reliable messaging with RabbitMQ (confirm/select + dead-letter exchange), achieving exactly-once semantics at consumer level.",
            "tags": ["RabbitMQ"],
            "position": ["Backend"],
            "category": "Achievement",
        },
        {
            "text": "Job Requirement: Familiar with exchange types, quorum queues, and back-pressure handling for bursty workloads.",
            "tags": ["RabbitMQ"],
            "position": ["Backend"],
            "category": "Requirement",
        },
        # -------------------- vLLM --------------------
        {
            "text": "Served LLMs via vLLM with PagedAttention and tensor parallelism, reaching 3–5× tokens/sec throughput and stable p95 latency under load.",
            "tags": ["vLLM"],
            "position": ["AI Engineer", "ML Engineer"],
            "category": "Achievement",
        },
        {
            "text": "Job Requirement: Experience configuring vLLM inference (GPU memory, tensor parallel), prompt caching, and OpenAI-compatible routing.",
            "tags": ["vLLM"],
            "position": ["AI Engineer"],
            "category": "Requirement",
        },
        # -------------------- Kafka --------------------
        {
            "text": "Built streaming pipelines on Kafka with idempotent producers and exactly-once semantics (EOSv2), ensuring lossless processing.",
            "tags": ["Kafka"],
            "position": ["Backend", "Data Engineer"],
            "category": "Achievement",
        },
        {
            "text": "Job Requirement: Strong knowledge of partitioning, consumer group rebalancing, and designing keys for ordering & scalability.",
            "tags": ["Kafka"],
            "position": ["Backend"],
            "category": "Requirement",
        },
        # -------------------- Elasticsearch --------------------
        {
            "text": "Designed Elasticsearch indices with ILM, custom analyzers, and searchable snapshots, cutting storage cost by ~40% while keeping query p95 < 200ms.",
            "tags": ["Elasticsearch"],
            "position": ["Backend", "Data Engineer"],
            "category": "Achievement",
        },
        {
            "text": "Job Requirement: Ability to tune ES queries/aggregations, manage shards/replicas, and design observability dashboards for cluster health.",
            "tags": ["Elasticsearch"],
            "position": ["Backend"],
            "category": "Requirement",
        },
        # -------------------- MySQL --------------------
        {
            "text": "Optimized MySQL with proper indexing, read-write splitting, and slow query tuning, improving critical path latency by 35%.",
            "tags": ["MySQL"],
            "position": ["Backend"],
            "category": "Achievement",
        },
        {
            "text": "Job Requirement: Proficiency in transaction isolation, deadlock analysis, and schema migration (pt-online-schema-change/gh-ost).",
            "tags": ["MySQL"],
            "position": ["Backend"],
            "category": "Requirement",
        },
        # -------------------- PostgreSQL --------------------
        {
            "text": "Leveraged PostgreSQL features (CTE, partial indexes, JSONB) and logical replication to support near-real-time analytics.",
            "tags": ["PostgreSQL"],
            "position": ["Backend", "Data Engineer"],
            "category": "Achievement",
        },
        {
            "text": "Job Requirement: Experience with vacuum/ANALYZE tuning, partitioning, and query planning (EXPLAIN/EXPLAIN ANALYZE).",
            "tags": ["PostgreSQL"],
            "position": ["Backend"],
            "category": "Requirement",
        },
        # -------------------- MongoDB --------------------
        {
            "text": "Modeled high-throughput workloads in MongoDB with shard keys and TTL indexes, achieving predictable latency under heavy writes.",
            "tags": ["MongoDB"],
            "position": ["Backend"],
            "category": "Achievement",
        },
        {
            "text": "Job Requirement: Understanding of schema design trade-offs (embedding vs referencing), sharding, and transaction boundaries.",
            "tags": ["MongoDB"],
            "position": ["Backend"],
            "category": "Requirement",
        },
        # -------------------- Cross-tech achievements --------------------
        {
            "text": "Implemented end-to-end observability (OpenTelemetry + Prometheus/Grafana), enabling trace-based SLOs and error budgets across microservices.",
            "tags": ["Kubernetes", "Kafka", "Redis"],
            "position": ["DevOps", "Backend"],
            "category": "Achievement",
        },
        {
            "text": "Built blue/green and canary releases with progressive delivery (Argo Rollouts), reducing change failure rate to <5%.",
            "tags": ["Kubernetes", "Docker"],
            "position": ["DevOps"],
            "category": "Achievement",
        },
        {
            "text": "Designed a hybrid search pipeline combining Elasticsearch BM25 with dense retrieval (FAISS/Vector DB) to boost top-1 accuracy by 12–18%.",
            "tags": ["Elasticsearch", "AI"],
            "position": ["AI Engineer", "Backend"],
            "category": "Achievement",
        },
        # -------------------- Roles / Positions --------------------
        {
            "text": "Backend: Design scalable APIs (REST/gRPC), own data models and persistence, and enforce reliability with retries, idempotency, and circuit breakers.",
            "tags": ["Backend"],
            "position": ["Backend"],
            "category": "Role",
        },
        {
            "text": "Frontend: Build accessible, responsive UIs; integrate API clients with caching and optimistic updates; maintain design system consistency.",
            "tags": ["Frontend"],
            "position": ["Frontend"],
            "category": "Role",
        },
        {
            "text": "Fullstack: Deliver end-to-end features across web UI, API, and data layer; automate tests and CI/CD for rapid iteration.",
            "tags": ["Fullstack"],
            "position": ["Fullstack"],
            "category": "Role",
        },
        {
            "text": "DevOps: Own IaC (Terraform), container orchestration, observability, incident response, and cost efficiency.",
            "tags": ["DevOps"],
            "position": ["DevOps"],
            "category": "Role",
        },
        {
            "text": "Data Engineer: Build batch/stream pipelines, manage data quality/lineage, and optimize storage formats & partitions.",
            "tags": ["Data Engineer"],
            "position": ["Data Engineer"],
            "category": "Role",
        },
        {
            "text": "Data Scientist: Run experiments, feature engineering, and model evaluation; communicate insights with clear metrics.",
            "tags": ["Data Scientist"],
            "position": ["Data Scientist"],
            "category": "Role",
        },
        {
            "text": "AI Engineer: Productionize LLM/ML systems with prompt engineering, retrieval (RAG), and serving on GPU-efficient stacks.",
            "tags": ["AI Engineer"],
            "position": ["AI Engineer"],
            "category": "Role",
        },
        {
            "text": "ML Engineer: Own model training/inference pipelines, MLOps, feature stores, and continuous evaluation.",
            "tags": ["ML Engineer"],
            "position": ["ML Engineer"],
            "category": "Role",
        },
        {
            "text": "Game Developer: Optimize rendering and physics; design ECS patterns and networking sync for stable FPS and latency.",
            "tags": ["Game Developer"],
            "position": ["Game Developer"],
            "category": "Role",
        },
        {
            "text": "Product Manager: Define problem statements and success metrics; prioritize roadmap and coordinate delivery across teams.",
            "tags": ["Product Manager"],
            "position": ["Product Manager"],
            "category": "Role",
        },
        # -------------------- Templates & prompts helpful for matching --------------------
        {
            "text": "Template: Designed and operated a {tech} based service handling {throughput}/s with p95 latency < {latency} ms and {availability}% availability.",
            "tags": ["Template"],
            "category": "Template",
        },
        {
            "text": "Template: Implemented {pattern} pattern on {queue/db}, enabling decoupled microservices and improving throughput by {delta}%.",
            "tags": ["Template"],
            "category": "Template",
        },
        {
            "text": "Interview: Explain trade-offs between at-least-once vs exactly-once delivery in Kafka and how to implement idempotency at consumer.",
            "tags": ["Kafka", "Interview"],
            "category": "Interview",
        },
        {
            "text": "Interview: How do you debug a memory leak in a long-running PyTorch training loop? What tooling and metrics do you check first?",
            "tags": ["PyTorch", "Interview"],
            "category": "Interview",
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
