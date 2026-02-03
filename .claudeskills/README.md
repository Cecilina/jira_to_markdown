# JIRA to Markdown Claude Skill

A Claude skill for converting JIRA tickets to Markdown files using the JIRA REST API.

## Overview

This skill wraps the `jira-to-md` CLI tool, allowing Claude to fetch JIRA tickets and convert them to well-formatted Markdown files. It supports single ticket fetch, bulk operations, JQL queries, and image downloading.

## Prerequisites

Before using this skill, ensure you have:

1. **Python 3.8+** installed
2. **uv** package manager installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. **JIRA credentials** configured in `.env` file (see Setup below)

## Setup

### For Global Skill Usage (Recommended)

1. **Install the tool:**
   ```bash
   # Navigate to your chosen installation directory
   cd /path/to/your/installation
   git clone <repository-url> JIRA_TO_MARKDOWN
   cd JIRA_TO_MARKDOWN
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Set up environment variable:**

   Add to your shell configuration (`~/.zshrc` or `~/.bashrc`):
   ```bash
   export JIRA_TO_MD_HOME="/path/to/your/JIRA_TO_MARKDOWN"
   ```

   Then reload your shell:
   ```bash
   source ~/.zshrc  # or source ~/.bashrc
   ```

4. **Create global skill symlink:**
   ```bash
   mkdir -p ~/.claude/skills
   ln -s "$JIRA_TO_MD_HOME/.claudeskills" ~/.claude/skills/jira-to-md
   ```

5. **Configure JIRA credentials:**
   ```bash
   cd "$JIRA_TO_MD_HOME"
   cp .env.example .env
   ```

6. **Edit `.env` with your JIRA information:**
   ```env
   JIRA_URL=https://your-company.atlassian.net
   JIRA_USERNAME=your.email@example.com
   JIRA_API_TOKEN=your_api_token_here
   ```

   To get your JIRA API token:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Click "Create API token"
   - Copy the token to your `.env` file

7. **Test the connection:**
   ```bash
   cd "$JIRA_TO_MD_HOME"
   source .venv/bin/activate
   jira-to-md test-connection
   ```

Once set up, you can use the skill from any directory in Claude Code!

## Available Commands

### test-connection
Test connection to your JIRA instance.

**Example:**
```
/jira-to-md test-connection
```

### fetch
Fetch a single JIRA ticket and convert to Markdown.

**Parameters:**
- `ticket_key` (required): The JIRA ticket key (e.g., PROJ-123)
- `output` (optional): Output directory
- `overwrite` (optional): Set to "true" to overwrite existing files
- `download_images` (optional): Set to "true" to download images

**Example:**
```
/jira-to-md fetch ticket_key=PROJ-123 overwrite=true
```

### query
Fetch tickets using JQL query and convert to Markdown.

**Parameters:**
- `jql_query` (required): JIRA Query Language string
- `max_results` (optional): Maximum number of results
- `output` (optional): Output directory
- `overwrite` (optional): Set to "true" to overwrite existing files
- `download_images` (optional): Set to "true" to download images

**Example:**
```
/jira-to-md query jql_query="project = MYPROJECT AND status = 'In Progress'" max_results=50
```

### bulk
Fetch multiple specific tickets and convert to Markdown.

**Parameters:**
- `ticket_keys` (optional): Space-separated ticket keys
- `file` (optional): Path to file containing ticket keys (one per line)
- `output` (optional): Output directory
- `overwrite` (optional): Set to "true" to overwrite existing files
- `download_images` (optional): Set to "true" to download images

**Example:**
```
/jira-to-md bulk ticket_keys="PROJ-123 PROJ-124 PROJ-125" overwrite=true
```

Or with a file:
```
/jira-to-md bulk file=/path/to/tickets.txt
```

### list-fields
List all custom fields available in your JIRA instance.

**Example:**
```
/jira-to-md list-fields
```

### download-images
Download images from markdown files and update references to use local paths.

**Parameters:**
- `directory` (optional): Directory containing markdown files
- `images_dir` (optional): Directory to save images
- `dry_run` (optional): Set to "true" to preview without downloading

**Example:**
```
/jira-to-md download-images dry_run=true
```

## Configuration

The skill uses configuration from:
1. `.env` file (for credentials)
2. `config/config.yaml` (for output settings)
3. Command-line options (highest priority)

### Default Output

- Markdown files are saved to: `$JIRA_TO_MD_HOME/output/`
- Images are saved to: `$JIRA_TO_MD_HOME/output/images/`
- Logs are saved to: `$JIRA_TO_MD_HOME/logs/jira_to_markdown.log`

## Architecture

The skill is organized in layers:

```
CLI Layer (cli.py)
    ↓
Configuration Layer (config.py)
    ↓
JIRA Client Layer (jira_client.py)
    ↓
Data Extraction Layer (ticket_fetcher.py)
    ↓
Conversion Layer (markdown_converter.py)
    ↓
Output Layer (file_writer.py)
```

## Markdown Output Format

Generated markdown files include:

- **Metadata table**: Key, Type, Status, Priority, Reporter, Assignee, Created, Updated
- **Description**: Converted from JIRA markup to Markdown
- **Comments**: All comments with author and timestamp
- **Attachments**: List of files with download links
- **Subtasks**: List of related subtasks
- **Linked Issues**: Related tickets with relationship type
- **Custom Fields**: Any custom fields configured in your JIRA instance

## Troubleshooting

### Authentication Errors
- Verify your `.env` file has correct credentials
- Ensure your API token is still valid
- Check that your JIRA URL is correct (include https://)

### Connection Errors
- Test connection: `jira-to-md test-connection`
- Verify you can access JIRA in a web browser
- Check if your network requires a proxy

### Missing Fields
- Run `jira-to-md list-fields` to see available custom fields
- Update `config/config.yaml` to include specific custom fields

## Development

To modify or extend the skill:

1. Code is in `jira_to_markdown/` directory
2. Tests are in `tests/` directory
3. Run tests: `pytest tests/`
4. Format code: `black jira_to_markdown/`
5. Lint code: `ruff check jira_to_markdown/`

## Support

For issues or questions:
- Check the main README.md
- Review CLAUDE.md for developer guidance
- Check logs in `logs/jira_to_markdown.log`

## License

MIT License - See LICENSE file for details
