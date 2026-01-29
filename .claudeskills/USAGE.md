# Using the JIRA to Markdown Claude Skill

This guide shows how to use the JIRA to Markdown skill within Claude Code.

## Quick Start

Once the skill is set up, you can use it from Claude by referencing the skill commands:

```bash
# Test connection
.claudeskills/run.sh test-connection

# Fetch a single ticket
.claudeskills/run.sh fetch PROJ-123

# Query tickets
.claudeskills/run.sh query "project = MYPROJECT"

# Bulk fetch
.claudeskills/run.sh bulk PROJ-123 PROJ-124 PROJ-125

# List fields
.claudeskills/run.sh list-fields

# Download images
.claudeskills/run.sh download-images --dry-run
```

## Using from Claude Code

When working with Claude Code in this directory, you can ask Claude to:

### Example Requests

**Test the JIRA connection:**
```
"Test my JIRA connection"
"Can you verify the JIRA credentials are working?"
```

**Fetch specific tickets:**
```
"Fetch JIRA ticket PROJ-123 and convert it to markdown"
"Get tickets PROJ-123, PROJ-124, and PROJ-125 as markdown files"
```

**Query for tickets:**
```
"Get all tickets in project MYPROJECT that are in progress"
"Fetch all bugs assigned to me from JIRA"
"Query JIRA for tickets created last week"
```

**Bulk operations:**
```
"Convert these ticket keys to markdown: PROJ-100, PROJ-101, PROJ-102"
"Fetch all tickets listed in tickets.txt"
```

**List custom fields:**
```
"What custom fields are available in JIRA?"
"Show me all JIRA custom fields"
```

**Download images:**
```
"Download all images from the markdown files"
"Run a dry run of image downloads to see what would be downloaded"
```

## Command Reference

### test-connection

Test connection to JIRA instance.

```bash
.claudeskills/run.sh test-connection
```

### fetch

Fetch a single JIRA ticket.

```bash
.claudeskills/run.sh fetch <TICKET-KEY> [OPTIONS]

Options:
  --output, -o DIR       Output directory
  --overwrite            Overwrite existing files
  --download-images      Download images after conversion
```

**Examples:**
```bash
# Basic fetch
.claudeskills/run.sh fetch PROJ-123

# Fetch with custom output directory
.claudeskills/run.sh fetch PROJ-123 --output /path/to/output

# Fetch and download images
.claudeskills/run.sh fetch PROJ-123 --download-images

# Overwrite existing file
.claudeskills/run.sh fetch PROJ-123 --overwrite
```

### query

Fetch tickets using JQL query.

```bash
.claudeskills/run.sh query "<JQL-QUERY>" [OPTIONS]

Options:
  --max-results, -n NUM  Maximum number of results
  --output, -o DIR       Output directory
  --overwrite            Overwrite existing files
  --download-images      Download images after conversion
```

**Examples:**
```bash
# Query by project
.claudeskills/run.sh query "project = MYPROJECT"

# Query with filters
.claudeskills/run.sh query "project = MYPROJECT AND status = 'In Progress'"

# Limit results
.claudeskills/run.sh query "project = MYPROJECT" --max-results 50

# Complex query
.claudeskills/run.sh query "assignee = currentUser() AND status != Done ORDER BY created DESC"
```

### bulk

Fetch multiple specific tickets.

```bash
.claudeskills/run.sh bulk <TICKET-KEYS...> [OPTIONS]
.claudeskills/run.sh bulk --file <FILE> [OPTIONS]

Options:
  --file, -f FILE        Read ticket keys from file (one per line)
  --output, -o DIR       Output directory
  --overwrite            Overwrite existing files
  --download-images      Download images after conversion
```

**Examples:**
```bash
# Bulk fetch by keys
.claudeskills/run.sh bulk PROJ-123 PROJ-124 PROJ-125

# Bulk fetch from file
.claudeskills/run.sh bulk --file tickets.txt

# Both keys and file
.claudeskills/run.sh bulk PROJ-100 PROJ-101 --file more_tickets.txt

# With overwrite
.claudeskills/run.sh bulk PROJ-123 PROJ-124 --overwrite
```

### list-fields

List all custom fields available in JIRA.

```bash
.claudeskills/run.sh list-fields
```

This shows all custom fields with their IDs and names, useful for configuration.

### download-images

Download images from markdown files and update references to use local paths.

```bash
.claudeskills/run.sh download-images [OPTIONS]

Options:
  --directory, -d DIR    Directory containing markdown files
  --images-dir, -i DIR   Directory to save images
  --dry-run              Show what would be downloaded without downloading
```

**Examples:**
```bash
# Download images from default output directory
.claudeskills/run.sh download-images

# Dry run to see what would be downloaded
.claudeskills/run.sh download-images --dry-run

# Specify directories
.claudeskills/run.sh download-images --directory ./output --images-dir ./output/img

# Preview and then execute
.claudeskills/run.sh download-images --dry-run
.claudeskills/run.sh download-images
```

## Output Structure

### Markdown Files

Generated markdown files are saved to `./output/` (configurable) with the following structure:

```
./output/
  ├── PROJ-123.md
  ├── PROJ-124.md
  ├── PROJ-125.md
  └── images/
      ├── screenshot-1.png
      ├── diagram-2.jpg
      └── ...
```

### Markdown Format

Each markdown file includes:

- **Title**: Ticket key and summary
- **Metadata Table**: Key, Type, Status, Priority, Reporter, Assignee, Created, Updated
- **Description**: Converted from JIRA markup to Markdown
- **Comments**: All comments with author and timestamp
- **Attachments**: List of files with download links
- **Subtasks**: Related subtasks
- **Linked Issues**: Related tickets with relationship types
- **Custom Fields**: Configured custom fields

### Logs

Logs are saved to `./logs/jira_to_markdown.log` for troubleshooting.

## JQL Query Examples

JIRA Query Language (JQL) is powerful for filtering tickets:

```jql
# By project
project = MYPROJECT

# By status
project = MYPROJECT AND status = "In Progress"

# By assignee
assignee = currentUser()

# By date range
created >= -7d

# By priority
priority in (High, Highest)

# By multiple conditions
project = MYPROJECT AND status != Done AND assignee = currentUser()

# Ordering
project = MYPROJECT ORDER BY created DESC

# Text search
project = MYPROJECT AND text ~ "authentication"

# By custom field (after listing fields)
"Story Points" > 5
```

For more JQL examples, see: https://www.atlassian.com/software/jira/guides/jql

## Configuration

### Environment Variables (.env)

Required in `.env` file:

```env
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your.email@example.com
JIRA_API_TOKEN=your_api_token_here
```

### Configuration File (config/config.yaml)

Optional configuration for output formatting:

```yaml
output:
  directory: ./output
  overwrite: false
  filename_format: "{key}.md"

markdown:
  include_metadata: true
  include_description: true
  include_comments: true
  include_attachments: true
  include_subtasks: true
  include_links: true
  date_format: "%Y-%m-%d %H:%M:%S"

images:
  download: false
  directory: ./output/images
```

## Troubleshooting

### Skill Not Found

If Claude cannot find the skill:
1. Ensure you're in the project directory
2. Verify `.claudeskills/` directory exists
3. Check that `run.sh` is executable: `chmod +x .claudeskills/run.sh`

### Authentication Errors

If you get authentication errors:
1. Verify `.env` file exists and has correct credentials
2. Test connection: `.claudeskills/run.sh test-connection`
3. Generate a new API token if needed
4. Ensure JIRA_URL includes `https://`

### Virtual Environment Not Found

If the script complains about missing virtual environment:
1. Install dependencies: `uv sync`
2. Verify `.venv` directory exists

### No Tickets Found

If queries return no tickets:
1. Test your JQL query in JIRA web interface first
2. Check permissions - you can only fetch tickets you have access to
3. Verify project key is correct (case-sensitive)

### Import Errors

If you get Python import errors:
1. Reinstall dependencies: `uv sync`
2. Activate virtual environment manually: `source .venv/bin/activate`
3. Check Python version: `python --version` (must be 3.8+)

## Tips and Best Practices

### 1. Test Connection First

Always test your connection before bulk operations:
```bash
.claudeskills/run.sh test-connection
```

### 2. Use Dry Run for Images

Preview image downloads before executing:
```bash
.claudeskills/run.sh download-images --dry-run
```

### 3. Start with Small Queries

When using JQL, start with `--max-results` to avoid overwhelming output:
```bash
.claudeskills/run.sh query "project = LARGE" --max-results 10
```

### 4. List Custom Fields

Find available custom fields before querying:
```bash
.claudeskills/run.sh list-fields
```

### 5. Use File for Bulk Operations

For many tickets, use a file:
```bash
echo "PROJ-123" > tickets.txt
echo "PROJ-124" >> tickets.txt
echo "PROJ-125" >> tickets.txt
.claudeskills/run.sh bulk --file tickets.txt
```

### 6. Organize Output

Use custom output directories for different projects:
```bash
.claudeskills/run.sh query "project = PROJ1" --output ./docs/proj1
.claudeskills/run.sh query "project = PROJ2" --output ./docs/proj2
```

## Integration with Claude Code

When Claude is helping you work on a project that uses JIRA:

1. **Documentation**: Ask Claude to fetch relevant tickets for context
2. **Status Updates**: Query for your assigned tickets
3. **Planning**: Fetch epic and story tickets for sprint planning
4. **Bug Triage**: Query for open bugs to review
5. **Reporting**: Bulk fetch tickets for documentation

Claude can automatically suggest using this skill when you mention JIRA tickets or need to fetch issue details.

## Next Steps

- Read the main [README.md](../README.md) for project details
- Check [CLAUDE.md](../CLAUDE.md) for developer guidance
- Review [config/config.yaml](../config/config.yaml) for customization options
- Explore JQL documentation for advanced queries

## Support

For issues:
1. Check logs in `./logs/jira_to_markdown.log`
2. Enable verbose mode: Add `-v` flag to commands
3. Review the GitHub repository issues
4. Consult JIRA API documentation
