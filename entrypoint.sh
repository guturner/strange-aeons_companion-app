#!/usr/bin/env bash
set -e

# Load .env if present
if [ -f "/opt/app/.env" ]; then
  export $(grep -v '^#' /opt/app/.env | xargs)
fi

if [ -f "/opt/app/.env.local" ]; then
  export $(grep -v '^#' /opt/app/.env | xargs)
fi

exec python bot.py
