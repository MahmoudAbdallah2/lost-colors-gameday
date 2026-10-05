FROM public.ecr.aws/docker/library/python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd --create-home --uid 1000 bedrock_agentcore

COPY requirements.txt .
RUN pip install --no-cache-dir --requirement requirements.txt

COPY --chown=bedrock_agentcore:bedrock_agentcore . .

USER bedrock_agentcore

EXPOSE 8000

CMD ["python", "-m", "server"]

