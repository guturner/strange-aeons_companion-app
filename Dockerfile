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

# Copy only dependency files first for build caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi

# Now copy the full application code
COPY . .

# Make entrypoint executable
RUN chmod +x ./entrypoint.sh

# Create unprivileged user
RUN useradd -ms /bin/bash botuser

# Ensure log file or directory exists and has correct permissions
RUN touch /opt/app/logs.log && \
    chown botuser:botuser /opt/app/logs.log

USER botuser

ENTRYPOINT ["./entrypoint.sh"]