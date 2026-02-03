# Prompt Injection Library
# Lightweight Python container for CLI tool

FROM python:3.11-slim

LABEL maintainer="Prompt Injection Library"
LABEL description="CLI tool for managing and exploring prompt injection techniques"

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy application files
COPY prompt_injection_cli.py .
COPY injections.json .

# Set ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set the entrypoint to the CLI tool
ENTRYPOINT ["python", "prompt_injection_cli.py"]

# Default command shows help
CMD ["--help"]
