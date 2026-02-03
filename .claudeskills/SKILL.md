---
name: jira-to-md
description: Convert JIRA tickets to Markdown files using the JIRA REST API
argument-hint: [command] [args...]
allowed-tools: Bash, Read, Write
---

# JIRA to Markdown Converter

This skill converts JIRA tickets to Markdown files using the JIRA REST API.

## Setup Required

Before using this skill, ensure:
1. Python 3.8+ is installed
2. uv is installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. Set environment variable `JIRA_TO_MD_HOME` to your installation path:
   - Add to your `~/.zshrc` or `~/.bashrc`: `export JIRA_TO_MD_HOME="/Users/pengfeiren/Documents/Crains/JIRA_TO_MARKDOWN"`
   - Or run: `echo 'export JIRA_TO_MD_HOME="/Users/pengfeiren/Documents/Crains/JIRA_TO_MARKDOWN"' >> ~/.zshrc`
4. Dependencies are installed: `cd $JIRA_TO_MD_HOME && uv sync`
5. JIRA credentials are configured in `$JIRA_TO_MD_HOME/.env`:
   - JIRA_URL=https://your-company.atlassian.net
   - JIRA_USERNAME=your.email@example.com
   - JIRA_API_TOKEN=your_api_token_here

## Available Commands

The user invoked this skill with arguments: `$ARGUMENTS`

Based on the command, execute the appropriate action:

### test-connection
Test connection to JIRA instance.

**Action**: Run the command:
```bash
cd "$JIRA_TO_MD_HOME" && source .venv/bin/activate && jira-to-md test-connection
```

### fetch [ticket-key] [options]
Fetch a single JIRA ticket and convert to Markdown.

**Arguments**:
- `ticket-key`: Required - The JIRA ticket key (e.g., PROJ-123)
- `--output <dir>`: Optional - Output directory
- `--overwrite`: Optional - Overwrite existing files
- `--download-images`: Optional - Download images after conversion

**Action**: Run the command:
```bash
cd "$JIRA_TO_MD_HOME" && source .venv/bin/activate && jira-to-md fetch $ARGUMENTS
```

### query [jql-query] [options]
Fetch tickets using JQL query and convert to Markdown.

**Arguments**:
- `jql-query`: Required - JIRA Query Language string (e.g., "project = PROJ AND status = 'In Progress'")
- `--max-results <n>`: Optional - Maximum number of results
- `--output <dir>`: Optional - Output directory
- `--overwrite`: Optional - Overwrite existing files
- `--download-images`: Optional - Download images after conversion

**Action**: Run the command:
```bash
cd "$JIRA_TO_MD_HOME" && source .venv/bin/activate && jira-to-md query $ARGUMENTS
```

### bulk [ticket-keys...] [options]
Fetch multiple specific tickets and convert to Markdown.

**Arguments**:
- `ticket-keys`: Space-separated ticket keys (e.g., PROJ-123 PROJ-124)
- `--file <path>`: Path to file containing ticket keys (one per line)
- `--output <dir>`: Optional - Output directory
- `--overwrite`: Optional - Overwrite existing files
- `--download-images`: Optional - Download images after conversion

**Action**: Run the command:
```bash
cd "$JIRA_TO_MD_HOME" && source .venv/bin/activate && jira-to-md bulk $ARGUMENTS
```

### list-fields
List all custom fields available in JIRA.

**Action**: Run the command:
```bash
cd "$JIRA_TO_MD_HOME" && source .venv/bin/activate && jira-to-md list-fields
```

### download-images [options]
Download images from markdown files and update references.

**Arguments**:
- `--directory <dir>`: Directory containing markdown files
- `--images-dir <dir>`: Directory to save images
- `--dry-run`: Show what would be downloaded without downloading

**Action**: Run the command:
```bash
cd "$JIRA_TO_MD_HOME" && source .venv/bin/activate && jira-to-md download-images $ARGUMENTS
```

## Instructions

When this skill is invoked:

1. Parse the arguments to determine which command to run
2. If no arguments provided, show usage help with all available commands
3. Execute the appropriate bash command from above
4. Show the output to the user
5. If there's an error about missing .env or credentials, remind the user to set up their JIRA credentials

## Usage Examples

- `/jira-to-md test-connection` - Test JIRA connection
- `/jira-to-md fetch PROJ-123` - Fetch a single ticket
- `/jira-to-md query "project = MYPROJECT AND status = 'In Progress'" --max-results 50` - Query tickets
- `/jira-to-md bulk PROJ-123 PROJ-124 PROJ-125 --overwrite` - Bulk fetch multiple tickets
- `/jira-to-md list-fields` - List custom fields
- `/jira-to-md download-images --dry-run` - Preview image downloads

## Output

- Markdown files are saved to: `$JIRA_TO_MD_HOME/output/`
- Images are saved to: `$JIRA_TO_MD_HOME/output/images/`
- Logs are saved to: `$JIRA_TO_MD_HOME/logs/jira_to_markdown.log`
