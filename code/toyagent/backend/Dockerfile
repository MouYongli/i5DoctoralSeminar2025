# ============================================
# Backend Dockerfile - Python FastAPI
# ============================================

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --no-dev

# Copy source code
COPY src ./src

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uv", "run", "uvicorn", "i5_agents.main:app", "--host", "0.0.0.0", "--port", "8000"]
