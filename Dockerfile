FROM python:3.12.3-slim-bookworm

# Install build tools and PostgreSQL client libraries
RUN apt-get update && \
    apt-get install -y git build-essential libgomp1 libpq-dev python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN groupadd -r pl_user && useradd -r -m -g pl_user pl_user

WORKDIR /home/pl_user/app
COPY --chown=pl_user:pl_user . .

# Install Python dependencies from pyproject.toml
RUN pip install --no-cache-dir .[api]

# Create app data directories and set ownership
RUN mkdir -p /data /data/models && \
    chown -R pl_user:pl_user /data

USER pl_user

EXPOSE 8000
CMD ["python", "-m", "api.cli"]