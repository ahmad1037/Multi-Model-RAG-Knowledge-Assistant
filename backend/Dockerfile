FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

EXPOSE 8000

RUN groupadd \
      --system appgroup \
    && useradd \
      --system \
      --gid appgroup \
      --create-home \
      appuser

RUN chown -R \
    appuser:appgroup \
    /app

ENV HF_HOME=/home/appuser/.cache/huggingface

RUN mkdir -p /storage /home/appuser/.cache/huggingface \
    && chown -R \
       appuser:appgroup \
       /storage /home/appuser/.cache
USER appuser

CMD [ "uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
