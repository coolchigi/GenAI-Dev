# AgentCore REQUIRES linux/arm64. On an x86 Mac, buildx cross-builds via QEMU.
FROM --platform=linux/arm64 python:3.11-slim

WORKDIR /app

# Install deps first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY agent.py ./

# AgentCore always talks to port 8080
EXPOSE 8080

# BedrockAgentCoreApp.run() serves /invocations + /ping on 8080
CMD ["python", "agent.py"]
