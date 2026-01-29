# JIRA to Markdown Claude Skill - Documentation Index

Welcome to the JIRA to Markdown Claude Skill documentation!

## Quick Links

- **[Setup Guide](SETUP.md)** - First-time installation and configuration
- **[Usage Guide](USAGE.md)** - Detailed command reference and examples
- **[Skill README](README.md)** - General overview and feature list
- **[Main Project README](../README.md)** - Full project documentation
- **[Developer Guide](../CLAUDE.md)** - For developers working on the codebase

## What is This?

This is a **Claude Code skill** that allows Claude to fetch JIRA tickets and convert them to Markdown files. It wraps the `jira-to-md` CLI tool and exposes it through a simple interface.

## Get Started in 3 Steps

### 1. Install Dependencies
```bash
cd /Users/pengfeiren/Documents/Crains/JIRA_TO_MARKDOWN
uv sync
```

### 2. Configure Credentials
```bash
cp .env.example .env
# Edit .env with your JIRA URL, username, and API token
```

### 3. Test Connection
```bash
.claudeskills/run.sh test-connection
```

See [SETUP.md](SETUP.md) for detailed instructions.

## Quick Reference

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `test-connection` | Test JIRA connection | `.claudeskills/run.sh test-connection` |
| `fetch` | Fetch a single ticket | `.claudeskills/run.sh fetch PROJ-123` |
| `query` | Query tickets with JQL | `.claudeskills/run.sh query "project = PROJ"` |
| `bulk` | Fetch multiple tickets | `.claudeskills/run.sh bulk PROJ-123 PROJ-124` |
| `list-fields` | List custom fields | `.claudeskills/run.sh list-fields` |
| `download-images` | Download images | `.claudeskills/run.sh download-images` |

### Common Use Cases

**Fetch a specific ticket:**
```bash
.claudeskills/run.sh fetch PROJ-123
```

**Get all in-progress tickets:**
```bash
.claudeskills/run.sh query "project = MYPROJECT AND status = 'In Progress'"
```

**Export multiple tickets:**
```bash
.claudeskills/run.sh bulk PROJ-100 PROJ-101 PROJ-102
```

**Download all images:**
```bash
.claudeskills/run.sh download-images
```

## Using with Claude

When Claude Code is active in this directory, you can use natural language:

- "Test my JIRA connection"
- "Fetch ticket PROJ-123 from JIRA"
- "Get all bugs assigned to me"
- "List available JIRA custom fields"
- "Download images from the markdown files"

## Documentation Structure

```
.claudeskills/
├── INDEX.md            ← You are here - Documentation index
├── SETUP.md            ← Installation and configuration
├── USAGE.md            ← Detailed usage guide with examples
├── README.md           ← Skill overview
├── manifest.json       ← Machine-readable skill definition
├── skill.yaml          ← Human-readable skill definition
└── run.sh              ← Skill entry point (executable)
```

## Key Features

- **Single Ticket Fetch**: Fetch individual JIRA tickets by key
- **JQL Queries**: Query multiple tickets using JIRA Query Language
- **Bulk Operations**: Fetch many tickets at once with progress tracking
- **Image Downloads**: Download JIRA attachments and update markdown references
- **Custom Fields**: Automatically maps custom field IDs to friendly names
- **Configurable Output**: Customize markdown format and content
- **Error Handling**: Robust error messages and logging

## System Requirements

- **Python**: 3.8 or higher
- **Package Manager**: uv (recommended) or pip
- **JIRA Access**: Cloud or Server instance with API access
- **Credentials**: JIRA API token

## Output Structure

Generated files are organized as:

```
./output/
  ├── PROJ-123.md        ← Ticket markdown files
  ├── PROJ-124.md
  ├── PROJ-125.md
  └── images/            ← Downloaded images
      ├── screenshot-1.png
      └── diagram-2.jpg

./logs/
  └── jira_to_markdown.log  ← Logs for debugging
```

## Configuration Files

- **`.env`** - JIRA credentials (required)
- **`config/config.yaml`** - Tool configuration (optional)
- **`.claudeskills/manifest.json`** - Skill metadata
- **`.claudeskills/skill.yaml`** - Skill commands

## Troubleshooting Quick Tips

**Connection issues?**
```bash
# Verify credentials
cat .env

# Test connection with verbose output
source .venv/bin/activate
jira-to-md test-connection -v
```

**Permission errors?**
```bash
# Make run.sh executable
chmod +x .claudeskills/run.sh
```

**Missing dependencies?**
```bash
# Reinstall dependencies
uv sync --reinstall
```

See [SETUP.md#troubleshooting](SETUP.md#troubleshooting) for detailed troubleshooting.

## Getting Help

1. **Setup Issues**: See [SETUP.md](SETUP.md#troubleshooting)
2. **Usage Questions**: See [USAGE.md](USAGE.md)
3. **Feature Details**: See [README.md](README.md)
4. **Development**: See [../CLAUDE.md](../CLAUDE.md)
5. **Logs**: Check `logs/jira_to_markdown.log`

## Useful Links

- [Atlassian API Token](https://id.atlassian.com/manage-profile/security/api-tokens) - Create JIRA API tokens
- [JQL Documentation](https://www.atlassian.com/software/jira/guides/jql) - JIRA Query Language guide
- [JIRA REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/) - Official API docs
- [uv Documentation](https://github.com/astral-sh/uv) - uv package manager

## Examples by Scenario

### For Bug Tracking
```bash
# Get all open bugs
.claudeskills/run.sh query "type = Bug AND status = Open"

# Get critical bugs
.claudeskills/run.sh query "type = Bug AND priority = Highest"
```

### For Sprint Planning
```bash
# Get current sprint tickets
.claudeskills/run.sh query "sprint = 'Sprint 42' ORDER BY priority DESC"

# Get all story points
.claudeskills/run.sh query "project = PROJ AND 'Story Points' is not empty"
```

### For Documentation
```bash
# Export entire epic
.claudeskills/run.sh query "'Epic Link' = PROJ-100"

# Export with images
.claudeskills/run.sh fetch PROJ-123 --download-images
```

### For Reporting
```bash
# Get tickets by date range
.claudeskills/run.sh query "created >= -7d ORDER BY created DESC"

# Get completed tickets
.claudeskills/run.sh query "status = Done AND updated >= -14d"
```

## Next Steps

1. **New Users**: Start with [SETUP.md](SETUP.md)
2. **Learning**: Read [USAGE.md](USAGE.md) for examples
3. **Advanced**: Review [configuration options](USAGE.md#configuration)
4. **Developers**: See [../CLAUDE.md](../CLAUDE.md)

## Contributing

Contributions are welcome! See the main [README.md](../README.md) for contribution guidelines.

## License

MIT License - See LICENSE file for details

---

*Last updated: 2026-01-29*
*Version: 0.1.0*
