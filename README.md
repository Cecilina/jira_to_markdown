# JIRA to Markdown Converter

A Python command-line tool to convert JIRA tickets to Markdown files using the JIRA REST API.

## Features

- Fetch single tickets or multiple tickets using JQL queries
- Convert JIRA markup to Markdown format
- Export tickets with comprehensive information:
  - Metadata (status, priority, assignee, dates, etc.)
  - Description with formatted markup
  - Comments with authors and timestamps
  - Custom fields with friendly names
  - Attachments
  - Subtasks and issue links
- One markdown file per ticket for easy organization
- Configurable output format and content
- Progress tracking for bulk operations
- Resume capability (skip already exported tickets)

## Claude Code Skill

This tool can be used as a **Claude Code skill**, allowing you to interact with JIRA directly from Claude!

Once set up, you can ask Claude to:
- "Test my JIRA connection"
- "Fetch JIRA ticket PROJ-123 and convert it to markdown"
- "Get all tickets in project MYPROJECT that are in progress"
- "List available JIRA custom fields"

See [.claudeskills/README.md](.claudeskills/README.md) and [.claudeskills/USAGE.md](.claudeskills/USAGE.md) for full documentation on using this as a Claude skill.

### Quick Start as a Skill

```bash
# Test connection
.claudeskills/run.sh test-connection

# Fetch a ticket
.claudeskills/run.sh fetch PROJ-123

# Query tickets
.claudeskills/run.sh query "project = MYPROJECT"
```

## Installation

### Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- JIRA instance with API access
- JIRA API token (see [Getting JIRA API Token](#getting-jira-api-token))

### Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### Install the project

**Recommended: Using `uv sync` (with lock file)**

```bash
# Clone or navigate to the project directory
cd JIRA_TO_MARKDOWN

# Sync dependencies from lock file (creates .venv automatically)
uv sync

# Or sync with development dependencies
uv sync --extra dev

# Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

**Alternative: Using `uv pip` (manual installation)**

```bash
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package in development mode
uv pip install -e .

# Or install with development dependencies
uv pip install -e ".[dev]"
```

**Alternative: Using pip (legacy)**

```bash
# Install the package
pip install -e .
```

## Configuration

### 1. Set up credentials

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your JIRA credentials:

```
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-api-token-here
```

### 2. (Optional) Customize configuration

Create a configuration file:

```bash
cp config/config.yaml.example config/config.yaml
```

Edit `config/config.yaml` to customize:
- Output directory
- Filename format
- Markdown content options
- Logging settings

## Getting JIRA API Token

1. Go to [Atlassian Account Security](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a name (e.g., "JIRA to Markdown")
4. Copy the generated token
5. Add it to your `.env` file as `JIRA_API_TOKEN`

## Usage

### Test connection

Verify your credentials are working:

```bash
jira-to-md test-connection
```

### Fetch a single ticket

```bash
jira-to-md fetch PROJ-123
```

Output: `output/PROJ-123.md`

### Fetch tickets using JQL query

```bash
# All tickets in a project
jira-to-md query "project = MYPROJECT"

# Tickets with specific status
jira-to-md query "project = MYPROJECT AND status = 'In Progress'"

# Recent tickets
jira-to-md query "project = MYPROJECT ORDER BY created DESC" --max-results 50

# Save to custom directory
jira-to-md query "project = MYPROJECT" --output ./my-tickets/
```

### Fetch multiple specific tickets

```bash
# Multiple tickets as arguments
jira-to-md bulk PROJ-123 PROJ-124 PROJ-125

# From a file (one ticket key per line)
jira-to-md bulk --file tickets.txt

# With custom output directory
jira-to-md bulk PROJ-123 PROJ-124 --output ./export/
```

### List custom fields

See what custom fields are available in your JIRA instance:

```bash
jira-to-md list-fields
```

## Command Reference

### Global Options

```
--config PATH        Path to config file (default: config/config.yaml)
--verbose, -v        Enable verbose logging
--jira-url URL       Override JIRA URL from config
--username USER      Override username from config
--api-token TOKEN    Override API token from config
```

### Commands

#### `test-connection`

Test JIRA connection and credentials.

```bash
jira-to-md test-connection
```

#### `fetch`

Fetch a single ticket.

```bash
jira-to-md fetch TICKET-KEY [OPTIONS]

Options:
  --output, -o DIR     Output directory
  --overwrite          Overwrite existing files
```

#### `query`

Fetch tickets using JQL query.

```bash
jira-to-md query "JQL" [OPTIONS]

Options:
  --max-results, -n N  Maximum number of results
  --output, -o DIR     Output directory
  --overwrite          Overwrite existing files
```

#### `bulk`

Fetch multiple specific tickets.

```bash
jira-to-md bulk [TICKET-KEYS...] [OPTIONS]

Options:
  --file, -f PATH      Read ticket keys from file
  --output, -o DIR     Output directory
  --overwrite          Overwrite existing files
```

#### `list-fields`

List all custom fields in JIRA.

```bash
jira-to-md list-fields
```

## Output Format

Each ticket is exported as a markdown file with the following structure:

```markdown
# [PROJ-123] Ticket Summary

## Metadata

| Field | Value |
|-------|-------|
| **Key** | PROJ-123 |
| **Status** | In Progress |
| **Type** | Bug |
| **Priority** | High |
| **Assignee** | John Doe |
| **Reporter** | Jane Smith |
| **Created** | 2024-01-13 10:30:00 |
| **Updated** | 2024-01-14 15:45:00 |
| **Labels** | bug, critical |
| **Components** | Backend, API |

## Description

Ticket description with JIRA markup converted to Markdown...

## Comments

### John Doe - 2024-01-13 11:00:00

Comment text...

## Custom Fields

- **Story Points**: 5
- **Sprint**: Sprint 42

## Attachments

- [screenshot.png](https://...) (245 KB)

## Subtasks

- [ ] PROJ-124: Implement fix
- [ ] PROJ-125: Add tests

## Links

- **Parent Issue**: [PROJ-100](https://...)
- **View in JIRA**: [PROJ-123](https://...)

---
*Generated on 2024-01-14 16:00:00 by JIRA to Markdown Converter*
```

## Configuration File Reference

See `config/config.yaml.example` for all available options:

```yaml
jira:
  url: ""                    # Set via .env
  username: ""               # Set via .env
  api_token: ""              # Set via .env
  verify_ssl: true           # Verify SSL certificates

query:
  jql: "project = PROJ"      # Default JQL query
  max_results: 100           # Default max results
  fields: "*all"             # Fields to fetch

output:
  directory: "./output"      # Output directory
  filename_format: "{key}.md"  # Filename format
  overwrite: false           # Don't overwrite by default

markdown:
  include_metadata_table: true
  include_comments: true
  include_attachments: true
  include_subtasks: true
  include_links: true
  date_format: "%Y-%m-%d %H:%M:%S"
  convert_markup: true       # Convert JIRA markup to Markdown

logging:
  level: "INFO"              # Log level
  file: "./logs/jira_to_markdown.log"
  console: true
  console_level: "INFO"
```

## Troubleshooting

### Authentication fails

- Verify your JIRA URL is correct (e.g., `https://company.atlassian.net`)
- Ensure you're using your email address as the username
- Check that your API token is valid
- Try generating a new API token

### Ticket not found

- Verify the ticket key is correct (case-sensitive)
- Ensure you have permission to view the ticket
- Check that the ticket exists in JIRA

### Custom fields show as IDs

- Run `jira-to-md list-fields` to see field mappings
- The tool automatically maps custom field IDs to friendly names
- If a field is missing, check your JIRA permissions

### SSL certificate errors

Set `verify_ssl: false` in `config/config.yaml` (not recommended for production):

```yaml
jira:
  verify_ssl: false
```

### Rate limiting

If you encounter rate limiting:
- Reduce `max_results` in queries
- Add delays between bulk operations
- Contact your JIRA administrator

## Development

### Running tests

```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=jira_to_markdown --cov-report=html

# Run linting
ruff check jira_to_markdown/

# Format code
black jira_to_markdown/ tests/

# Type checking
mypy jira_to_markdown/
```

### Quick development workflow

**Using `uv sync` (recommended)**

```bash
# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup project with dev dependencies
uv sync --extra dev

# Activate virtual environment
source .venv/bin/activate

# Make changes, then test
pytest tests/

# Format and lint before committing
black jira_to_markdown/ tests/
ruff check --fix jira_to_markdown/

# Update lock file if you add dependencies
uv lock
```

**Using `uv pip` (alternative)**

```bash
# Setup project
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Make changes, then test
pytest tests/

# Format and lint before committing
black jira_to_markdown/ tests/
ruff check --fix jira_to_markdown/
```

### Project Structure

```
JIRA_TO_MARKDOWN/
├── jira_to_markdown/         # Main package
│   ├── cli.py                # Command-line interface
│   ├── config.py             # Configuration management
│   ├── jira_client.py        # JIRA API client
│   ├── ticket_fetcher.py     # Ticket retrieval
│   ├── markdown_converter.py # Markdown conversion
│   ├── file_writer.py        # File output
│   └── logger.py             # Logging setup
├── config/                   # Configuration files
├── tests/                    # Test files
├── output/                   # Default output directory
├── logs/                     # Log files
├── pyproject.toml            # Project configuration (uv/pip)
├── requirements.txt          # Legacy requirements file
├── .env.example              # Credential template
├── .gitignore                # Git ignore rules
└── README.md                 # Documentation
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.
