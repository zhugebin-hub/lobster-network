FROM python:3.12-slim

WORKDIR /app

# 安装依赖
RUN pip install --no-cache-dir openpyxl

# 复制应用
COPY . .

# 创建必要目录
RUN mkdir -p /app/data /app/versions /app/logs /app/static

# 环境变量
ENV HOST=0.0.0.0
ENV PORT=8765
ENV DORM_API_TOKEN=""

EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8765/api/health')"

CMD ["python3", "server.py"]
