FROM python:3.13.3

# Install system dependencies Poetry needs (git, curl, build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry (no virtualenvs inside containers)
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /opt/app

# Create unprivileged user early so we can assign file ownership to it
RUN useradd -ms /bin/bash botuser

# Copy only dependency files first for build caching (owned by botuser)
COPY --chown=botuser:botuser pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi

# Now copy the full application code (owned by botuser)
COPY --chown=botuser:botuser . .

# Make entrypoint executable
RUN chmod +x ./entrypoint.sh

# Ensure log file exists and has correct permissions
RUN touch /opt/app/logs.log && \
    chown botuser:botuser /opt/app/logs.log

USER botuser

ENTRYPOINT ["./entrypoint.sh"]