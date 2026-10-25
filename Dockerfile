FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Test stage: dev dependencies + unit tests, never shipped
FROM base AS test
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY app.py .
COPY templates/ templates/
COPY pytest.ini .
COPY tests/ tests/
RUN python -m pytest -v

# Runtime stage: only the application, non-root user
FROM base AS runtime
ENV APP_HOST=0.0.0.0 DATABASE=/app/data/notes.db
RUN useradd --create-home --shell /usr/sbin/nologin app \
    && mkdir -p /app/data && chown app:app /app/data
COPY app.py .
COPY templates/ templates/
USER app
EXPOSE 5000
HEALTHCHECK --interval=5s --timeout=3s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/healthz')"
CMD ["python", "app.py"]
