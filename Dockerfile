# 使用 Python 官方 Slim 镜像作为基础
FROM python:3.9-slim-bullseye

# 设置工作目录
WORKDIR /app

# 设置环境变量（禁用缓存字节码 + 关闭交互）
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    CUDA_VISIBLE_DEVICES="" \
    GLOG_v=1


# Use standard Debian sources
RUN echo "deb http://deb.debian.org/debian bullseye main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bullseye-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git build-essential vim \
    bash-completion iputils-ping procps \
    libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# 拷贝项目文件
COPY . /app

# 安装 pip、poetry
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry lock \
    && poetry install --no-interaction --no-ansi

# 暴露 Streamlit 默认端口
EXPOSE 8501

# 启动应用服务
CMD bash -c "export PYTHONPATH=/app:\$PYTHONPATH && python3 resumix/server.py & streamlit run resumix/main.py --server.port=8501 --server.address=0.0.0.0"
