# Claude Skill Setup Guide

This document guides you through setting up the JIRA to Markdown tool as a Claude Code skill.

## What is a Claude Skill?

A Claude skill is a way to extend Claude Code's capabilities by packaging functionality that Claude can invoke. This JIRA to Markdown skill allows Claude to:

- Fetch JIRA tickets and convert them to Markdown
- Query JIRA using JQL (JIRA Query Language)
- Download images from JIRA attachments
- List custom fields and metadata

## Prerequisites

Before setting up the skill, ensure you have:

### 1. Python Environment
- **Python 3.8 or higher** installed
- **uv** package manager (recommended)

Check your Python version:
```bash
python --version
# or
python3 --version
```

### 2. JIRA Access
- Access to a JIRA instance (Cloud or Server)
- JIRA API token (see instructions below)
- Permission to view tickets you want to export

### 3. Development Tools
- Git (for cloning/updating)
- Text editor for configuration
- Terminal/command line access

## Step-by-Step Setup

### Step 1: Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

Verify installation:
```bash
uv --version
```

### Step 2: Install Project Dependencies

Navigate to the project directory and install dependencies:

```bash
cd /Users/pengfeiren/Documents/Crains/JIRA_TO_MARKDOWN

# Install all dependencies (creates .venv automatically)
uv sync

# Or install with development dependencies
uv sync --extra dev
```

This creates a virtual environment in `.venv/` and installs all required packages.

### Step 3: Get Your JIRA API Token

1. Go to [Atlassian Account Security](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Log in with your Atlassian account
3. Click "Create API token"
4. Give it a descriptive name (e.g., "JIRA to Markdown Tool")
5. Copy the generated token (you won't be able to see it again!)

### Step 4: Configure Credentials

Create a `.env` file with your JIRA credentials:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file
nano .env  # or use your preferred editor
```

Add your credentials:

```env
# Your JIRA instance URL (must include https://)
JIRA_URL=https://your-company.atlassian.net

# Your JIRA username (usually your email address)
JIRA_USERNAME=your.email@example.com

# Your JIRA API token (from Step 3)
JIRA_API_TOKEN=your_api_token_here
```

**Important:**
- Use `https://` in the JIRA_URL
- For Atlassian Cloud, the URL format is: `https://your-domain.atlassian.net`
- For JIRA Server, use your organization's JIRA URL
- Keep your `.env` file secure (it's in `.gitignore` by default)

### Step 5: Test the Installation

Activate the virtual environment and test the connection:

```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Test JIRA connection
jira-to-md test-connection
```

You should see:
```
Testing JIRA connection...
✓ Connection successful!
Connected to: https://your-company.atlassian.net
```

If you get an error, see [Troubleshooting](#troubleshooting) below.

### Step 6: Test the Skill Wrapper

Test the skill entry point:

```bash
# Test using the skill wrapper
.claudeskills/run.sh test-connection

# Test fetching a ticket (replace with a real ticket key)
.claudeskills/run.sh fetch PROJ-123

# Test listing fields
.claudeskills/run.sh list-fields
```

### Step 7: Verify Skill Structure

Ensure all skill files are in place:

```bash
ls -la .claudeskills/
```

You should see:
- `manifest.json` - Skill metadata and configuration
- `skill.yaml` - Detailed skill definition
- `run.sh` - Skill entry point (executable)
- `README.md` - Skill documentation
- `USAGE.md` - Usage guide
- `SETUP.md` - This file

## Configuration Options

### Basic Configuration (config/config.yaml)

You can customize the tool's behavior by creating a config file:

```bash
cp config/config.yaml.example config/config.yaml
```

Key options:

```yaml
# Output settings
output:
  directory: "./output"           # Where to save markdown files
  filename_format: "{key}.md"     # Filename format
  overwrite: false                # Overwrite existing files

# Markdown content
markdown:
  include_metadata_table: true    # Include metadata table
  include_comments: true          # Include comments
  include_attachments: true       # Include attachment list
  include_subtasks: true          # Include subtasks
  include_links: true             # Include linked issues
  date_format: "%Y-%m-%d %H:%M:%S"  # Date format

# Images
images:
  download: false                 # Auto-download images
  directory: "./output/images"    # Images directory

# Logging
logging:
  level: "INFO"                   # Log level
  file: "./logs/jira_to_markdown.log"
  console: true
```

### Advanced Configuration

For more advanced options, see `config/config.yaml.example` in the project.

## Using the Skill

### With Claude Code

When working with Claude Code in this directory:

1. **Natural Language**: Just ask Claude to perform JIRA operations
   ```
   "Fetch JIRA ticket PROJ-123"
   "Get all in-progress tickets from MYPROJECT"
   "List available custom fields"
   ```

2. **Direct Invocation**: Use the skill wrapper directly
   ```bash
   .claudeskills/run.sh fetch PROJ-123
   .claudeskills/run.sh query "project = MYPROJECT"
   ```

### Standalone Usage

You can also use the tool directly without Claude:

```bash
# Activate virtual environment
source .venv/bin/activate

# Use the CLI directly
jira-to-md fetch PROJ-123
jira-to-md query "project = MYPROJECT"
jira-to-md bulk PROJ-123 PROJ-124 PROJ-125
```

## Common Tasks

### Fetch a Single Ticket

```bash
.claudeskills/run.sh fetch PROJ-123
```

Output: `./output/PROJ-123.md`

### Query Multiple Tickets

```bash
.claudeskills/run.sh query "project = MYPROJECT AND status = 'In Progress'"
```

Output: Multiple markdown files in `./output/`

### Bulk Fetch Specific Tickets

```bash
.claudeskills/run.sh bulk PROJ-123 PROJ-124 PROJ-125
```

### List Custom Fields

```bash
.claudeskills/run.sh list-fields
```

This shows all custom fields available in your JIRA instance.

### Download Images

```bash
# Dry run (preview only)
.claudeskills/run.sh download-images --dry-run

# Actually download
.claudeskills/run.sh download-images
```

## Troubleshooting

### Error: "Virtual environment not found"

**Solution:**
```bash
cd /Users/pengfeiren/Documents/Crains/JIRA_TO_MARKDOWN
uv sync
```

### Error: ".env file not found"

**Solution:**
```bash
cp .env.example .env
# Then edit .env with your credentials
```

### Error: "Authentication failed"

**Possible causes:**
1. **Wrong API token**: Generate a new one at [Atlassian Security](https://id.atlassian.com/manage-profile/security/api-tokens)
2. **Wrong username**: Use your email address
3. **Wrong URL**: Include `https://` and verify the domain

**Debug steps:**
```bash
# Check your .env file
cat .env

# Verify the URL is accessible
curl https://your-company.atlassian.net

# Test with verbose logging
source .venv/bin/activate
jira-to-md test-connection -v
```

### Error: "Connection failed"

**Possible causes:**
1. **Network issues**: Check internet connection
2. **Firewall/proxy**: Configure proxy if needed
3. **Invalid URL**: Verify JIRA URL is correct

### Error: "Ticket not found"

**Possible causes:**
1. **Typo in ticket key**: Ticket keys are case-sensitive
2. **Insufficient permissions**: You can only fetch tickets you have access to
3. **Ticket doesn't exist**: Verify ticket exists in JIRA

### Error: "SSL certificate verify failed"

**Solution (not recommended for production):**

Edit `config/config.yaml`:
```yaml
jira:
  verify_ssl: false
```

### Permission denied on run.sh

**Solution:**
```bash
chmod +x .claudeskills/run.sh
```

### Import errors or missing modules

**Solution:**
```bash
# Reinstall dependencies
uv sync --reinstall

# Or with pip
pip install -e .
```

### Skill not found by Claude

**Possible causes:**
1. Not in the project directory
2. Skill files not properly set up
3. `run.sh` not executable

**Debug steps:**
```bash
# Verify you're in the right directory
pwd

# Check skill files exist
ls -la .claudeskills/

# Make run.sh executable
chmod +x .claudeskills/run.sh

# Test directly
.claudeskills/run.sh help
```

## Updating the Skill

To update dependencies or the tool:

```bash
cd /Users/pengfeiren/Documents/Crains/JIRA_TO_MARKDOWN

# Pull latest changes (if using git)
git pull

# Update dependencies
uv sync

# Or force reinstall
uv sync --reinstall
```

## Next Steps

1. Read [USAGE.md](./USAGE.md) for detailed usage examples
2. Read [README.md](./README.md) for main documentation
3. Explore [CLAUDE.md](../CLAUDE.md) for developer guidance
4. Try fetching your first ticket!

## Getting Help

- **Documentation**: See README.md and USAGE.md
- **Logs**: Check `logs/jira_to_markdown.log`
- **Issues**: Report bugs on GitHub
- **JIRA API**: Consult [Atlassian JIRA API docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)

## Security Best Practices

1. **Never commit `.env`**: It's in `.gitignore` by default
2. **Rotate API tokens**: Regularly generate new tokens
3. **Use read-only tokens**: If possible, use tokens with minimal permissions
4. **Keep uv/pip updated**: Regular security updates
5. **Review permissions**: Only grant JIRA access to necessary users

## Skill Files Overview

- **manifest.json**: Machine-readable skill metadata
- **skill.yaml**: Human-readable skill definition with all commands
- **run.sh**: Entry point that activates venv and routes commands
- **README.md**: General skill documentation
- **USAGE.md**: Detailed usage guide with examples
- **SETUP.md**: This file - setup instructions

## Support

For additional help:

1. Check the troubleshooting section above
2. Review logs in `logs/jira_to_markdown.log`
3. Enable verbose mode: `jira-to-md <command> -v`
4. Consult the main README.md
5. Check JIRA API token is still valid

## License

MIT License - See LICENSE file for details
