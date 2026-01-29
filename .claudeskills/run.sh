#!/usr/bin/env bash

# JIRA to Markdown Skill Entry Point
# This script provides a unified interface for Claude to invoke the jira-to-md CLI

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"

# Change to project root
cd "${PROJECT_ROOT}"

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "Error: Virtual environment not found. Run 'uv sync' to install dependencies."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please copy .env.example and configure your JIRA credentials."
    exit 1
fi

# Parse command and arguments
COMMAND="${1:-}"
shift || true

# Execute the appropriate command
case "${COMMAND}" in
    test-connection)
        jira-to-md test-connection "$@"
        ;;

    fetch)
        jira-to-md fetch "$@"
        ;;

    query)
        jira-to-md query "$@"
        ;;

    bulk)
        jira-to-md bulk "$@"
        ;;

    list-fields)
        jira-to-md list-fields "$@"
        ;;

    download-images)
        jira-to-md download-images "$@"
        ;;

    help|--help|-h|"")
        cat <<EOF
JIRA to Markdown Skill

Usage: $0 <command> [options]

Commands:
  test-connection              Test connection to JIRA
  fetch <ticket-key>           Fetch a single ticket
  query "<jql-query>"          Fetch tickets using JQL
  bulk <keys...>               Fetch multiple tickets
  list-fields                  List custom fields
  download-images              Download images from markdown files
  help                         Show this help message

Examples:
  $0 test-connection
  $0 fetch PROJ-123
  $0 query "project = MYPROJECT AND status = 'In Progress'"
  $0 bulk PROJ-123 PROJ-124 PROJ-125
  $0 bulk --file tickets.txt
  $0 list-fields
  $0 download-images --dry-run

For more information, see .claudeskills/README.md
EOF
        ;;

    *)
        echo "Error: Unknown command '${COMMAND}'"
        echo "Run '$0 help' for usage information."
        exit 1
        ;;
esac
