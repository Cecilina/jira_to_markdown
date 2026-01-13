"""
Command-line interface for JIRA to Markdown converter.
"""

import sys
import os
import click
import logging
from pathlib import Path

from .config import Config, ConfigurationError
from .logger import setup_logger
from .jira_client import JiraClient, JiraConnectionError, JiraAuthenticationError, TicketNotFoundError
from .ticket_fetcher import TicketFetcher
from .markdown_converter import MarkdownConverter
from .file_writer import FileWriter, FileWriteError


# Global context for sharing configuration
class Context:
    def __init__(self):
        self.config = None
        self.logger = None
        self.verbose = False


@click.group()
@click.option('--config', type=click.Path(exists=True), default=None,
              help='Path to configuration file (default: config/config.yaml)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--jira-url', help='JIRA instance URL (overrides config)')
@click.option('--username', help='JIRA username (overrides config)')
@click.option('--api-token', help='JIRA API token (overrides config)')
@click.pass_context
def cli(ctx, config, verbose, jira_url, username, api_token):
    """
    JIRA to Markdown Converter

    Convert JIRA tickets to Markdown files using the JIRA REST API.
    """
    ctx.obj = Context()
    ctx.obj.verbose = verbose

    # Load configuration
    try:
        # Try default config file if not specified
        if config is None:
            default_config = 'config/config.yaml'
            if os.path.exists(default_config):
                config = default_config

        ctx.obj.config = Config(config_file=config)

        # Override with command-line options
        if jira_url:
            ctx.obj.config.set('jira.url', jira_url)
        if username:
            ctx.obj.config.set('jira.username', username)
        if api_token:
            ctx.obj.config.set('jira.api_token', api_token)

        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO
        file_log_level = getattr(logging, ctx.obj.config.log_level.upper(), logging.INFO)
        console_log_level = log_level

        ctx.obj.logger = setup_logger(
            'jira_to_markdown',
            log_file=ctx.obj.config.log_file,
            file_level=file_log_level,
            console_level=console_log_level,
            console_enabled=ctx.obj.config.log_console
        )

    except ConfigurationError as e:
        click.echo(f"Configuration error: {e}", err=True)
        click.echo("\nPlease ensure you have:")
        click.echo("1. Created a .env file with JIRA credentials (see .env.example)")
        click.echo("2. Set JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN environment variables")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def test_connection(ctx):
    """
    Test connection to JIRA.

    Verifies that the credentials and JIRA URL are correct.
    """
    config = ctx.obj.config
    logger = ctx.obj.logger

    try:
        click.echo("Testing JIRA connection...")

        client = JiraClient(
            url=config.jira_url,
            username=config.jira_username,
            api_token=config.jira_api_token,
            verify_ssl=config.jira_verify_ssl
        )

        client.connect()
        client.test_connection()

        click.echo(click.style("✓ Connection successful!", fg='green'))
        click.echo(f"Connected to: {config.jira_url}")

    except JiraAuthenticationError as e:
        click.echo(click.style(f"✗ Authentication failed: {e}", fg='red'), err=True)
        sys.exit(1)
    except JiraConnectionError as e:
        click.echo(click.style(f"✗ Connection failed: {e}", fg='red'), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.argument('ticket_key')
@click.option('--output', '-o', help='Output directory (overrides config)')
@click.option('--overwrite', is_flag=True, help='Overwrite existing files')
@click.pass_context
def fetch(ctx, ticket_key, output, overwrite):
    """
    Fetch a single JIRA ticket and convert to Markdown.

    TICKET_KEY: The JIRA ticket key (e.g., PROJ-123)
    """
    config = ctx.obj.config
    logger = ctx.obj.logger

    try:
        # Override output directory if specified
        output_dir = output or config.output_directory
        if overwrite:
            config.set('output.overwrite', True)

        click.echo(f"Fetching ticket {ticket_key}...")

        # Initialize components
        client = JiraClient(
            url=config.jira_url,
            username=config.jira_username,
            api_token=config.jira_api_token,
            verify_ssl=config.jira_verify_ssl
        )
        client.connect()

        fetcher = TicketFetcher(client)
        converter = MarkdownConverter(config)
        writer = FileWriter(output_dir, overwrite=config.output_overwrite)

        # Fetch and convert
        ticket_data = fetcher.fetch_single(ticket_key)
        markdown = converter.convert(ticket_data)

        # Write to file
        filepath = writer.write_ticket(ticket_key, markdown, ticket_data)

        click.echo(click.style(f"✓ Successfully written to {filepath}", fg='green'))

    except TicketNotFoundError as e:
        click.echo(click.style(f"✗ {e}", fg='red'), err=True)
        sys.exit(1)
    except (JiraConnectionError, JiraAuthenticationError) as e:
        click.echo(click.style(f"✗ JIRA error: {e}", fg='red'), err=True)
        sys.exit(1)
    except FileWriteError as e:
        click.echo(click.style(f"✗ File write error: {e}", fg='red'), err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        click.echo(click.style(f"✗ Error: {e}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.argument('jql_query')
@click.option('--max-results', '-n', type=int, help='Maximum number of results (default: unlimited)')
@click.option('--output', '-o', help='Output directory (overrides config)')
@click.option('--overwrite', is_flag=True, help='Overwrite existing files')
@click.pass_context
def query(ctx, jql_query, max_results, output, overwrite):
    """
    Fetch tickets using JQL query and convert to Markdown.

    JQL_QUERY: JIRA Query Language string (e.g., "project = PROJ")
    """
    config = ctx.obj.config
    logger = ctx.obj.logger

    try:
        # Override output directory if specified
        output_dir = output or config.output_directory
        if overwrite:
            config.set('output.overwrite', True)

        click.echo(f"Searching with JQL: {jql_query}")

        # Initialize components
        client = JiraClient(
            url=config.jira_url,
            username=config.jira_username,
            api_token=config.jira_api_token,
            verify_ssl=config.jira_verify_ssl
        )
        client.connect()

        fetcher = TicketFetcher(client)
        converter = MarkdownConverter(config)
        writer = FileWriter(output_dir, overwrite=config.output_overwrite)

        # Fetch tickets
        tickets = fetcher.fetch_by_jql(jql_query, max_results=max_results)

        if not tickets:
            click.echo("No tickets found matching the query.")
            return

        click.echo(f"Found {len(tickets)} ticket(s). Converting to Markdown...")

        # Process with progress bar
        with click.progressbar(tickets, label='Processing tickets') as bar:
            success_count = 0
            for ticket_data in bar:
                try:
                    markdown = converter.convert(ticket_data)
                    writer.write_ticket(ticket_data['key'], markdown, ticket_data)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to process {ticket_data.get('key', 'unknown')}: {e}")

        click.echo(click.style(f"✓ Successfully processed {success_count}/{len(tickets)} tickets", fg='green'))
        click.echo(f"Output directory: {output_dir}")

    except (JiraConnectionError, JiraAuthenticationError) as e:
        click.echo(click.style(f"✗ JIRA error: {e}", fg='red'), err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        click.echo(click.style(f"✗ Error: {e}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.argument('ticket_keys', nargs=-1)
@click.option('--file', '-f', type=click.Path(exists=True), help='Read ticket keys from file (one per line)')
@click.option('--output', '-o', help='Output directory (overrides config)')
@click.option('--overwrite', is_flag=True, help='Overwrite existing files')
@click.pass_context
def bulk(ctx, ticket_keys, file, output, overwrite):
    """
    Fetch multiple specific tickets and convert to Markdown.

    TICKET_KEYS: One or more ticket keys (e.g., PROJ-123 PROJ-124)

    Use --file to read ticket keys from a file instead.
    """
    config = ctx.obj.config
    logger = ctx.obj.logger

    try:
        # Get ticket keys from file or arguments
        keys = list(ticket_keys)

        if file:
            with open(file, 'r') as f:
                file_keys = [line.strip() for line in f if line.strip()]
                keys.extend(file_keys)

        if not keys:
            click.echo("Error: No ticket keys provided.", err=True)
            click.echo("Use: jira-to-md bulk PROJ-123 PROJ-124")
            click.echo("Or:  jira-to-md bulk --file tickets.txt")
            sys.exit(1)

        # Remove duplicates while preserving order
        keys = list(dict.fromkeys(keys))

        # Override output directory if specified
        output_dir = output or config.output_directory
        if overwrite:
            config.set('output.overwrite', True)

        click.echo(f"Fetching {len(keys)} ticket(s)...")

        # Initialize components
        client = JiraClient(
            url=config.jira_url,
            username=config.jira_username,
            api_token=config.jira_api_token,
            verify_ssl=config.jira_verify_ssl
        )
        client.connect()

        fetcher = TicketFetcher(client)
        converter = MarkdownConverter(config)
        writer = FileWriter(output_dir, overwrite=config.output_overwrite)

        # Process with progress bar
        with click.progressbar(keys, label='Processing tickets') as bar:
            success_count = 0
            for key in bar:
                try:
                    ticket_data = fetcher.fetch_single(key)
                    markdown = converter.convert(ticket_data)
                    writer.write_ticket(key, markdown, ticket_data)
                    success_count += 1
                except TicketNotFoundError:
                    logger.error(f"Ticket {key} not found")
                except Exception as e:
                    logger.error(f"Failed to process {key}: {e}")

        click.echo(click.style(f"✓ Successfully processed {success_count}/{len(keys)} tickets", fg='green'))
        click.echo(f"Output directory: {output_dir}")

    except (JiraConnectionError, JiraAuthenticationError) as e:
        click.echo(click.style(f"✗ JIRA error: {e}", fg='red'), err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        click.echo(click.style(f"✗ Error: {e}", fg='red'), err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def list_fields(ctx):
    """
    List all custom fields available in JIRA.

    This helps you identify which custom fields are available
    for your JIRA instance.
    """
    config = ctx.obj.config
    logger = ctx.obj.logger

    try:
        click.echo("Fetching custom fields from JIRA...")

        client = JiraClient(
            url=config.jira_url,
            username=config.jira_username,
            api_token=config.jira_api_token,
            verify_ssl=config.jira_verify_ssl
        )
        client.connect()

        custom_fields = client.get_custom_fields()

        if not custom_fields:
            click.echo("No custom fields found.")
            return

        click.echo(f"\nFound {len(custom_fields)} custom fields:\n")

        # Display in a formatted table
        for field_id, field_name in sorted(custom_fields.items(), key=lambda x: x[1]):
            click.echo(f"  {field_id:20s} → {field_name}")

    except (JiraConnectionError, JiraAuthenticationError) as e:
        click.echo(click.style(f"✗ JIRA error: {e}", fg='red'), err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        click.echo(click.style(f"✗ Error: {e}", fg='red'), err=True)
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
