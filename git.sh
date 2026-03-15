#!/bin/bash
# Bash wrapper skripts GitHub -> GitLab sync

PYTHON_BIN="/home/python/myenv/bin/python"
SCRIPT="/home/python/git.py"
LOG_DIR="/home/python/logs"

mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOG_DIR/git_sync_$TIMESTAMP.log"

$PYTHON_BIN $SCRIPT > "$LOG_FILE" 2>&1
