FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

## Debian 12 换成国内源
#RUN sed -i 's@deb.debian.org@mirror.sjtu.edu.cn@g' /etc/apt/sources.list.d/debian.sources

# 安装curl tk等必要的软件
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    tk \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 复制应用文件到容器中
COPY . /app

# 安装依赖，使用清华大学的 PyPI 镜像
RUN pip install --no-cache-dir -r requirements.txt # -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 暴露 Streamlit 使用的默认端口
EXPOSE 8501

# 运行 Streamlit 应用
CMD ["streamlit", "run", "check_info_webapp.py"]

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8501/ || exit 1
