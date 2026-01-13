"""
Markdown conversion logic for JIRA tickets.
"""

import re
import logging
from typing import Dict, Any, List
from datetime import datetime


class MarkdownConverter:
    """Converts JIRA ticket data to Markdown format."""

    def __init__(self, config):
        """
        Initialize markdown converter.

        Args:
            config: Config instance
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

    def convert(self, ticket_data: Dict[str, Any]) -> str:
        """
        Convert ticket data to markdown string.

        Args:
            ticket_data: Dictionary containing ticket data

        Returns:
            Markdown formatted string
        """
        sections = []

        # Title
        sections.append(self._render_title(ticket_data))
        sections.append("")

        # Metadata table
        if self.config.get('markdown.include_metadata_table', True):
            sections.append(self._render_metadata_table(ticket_data))
            sections.append("")

        # Description
        if ticket_data.get('description'):
            sections.append("## Description\n")
            sections.append(self._render_description(ticket_data['description']))
            sections.append("")

        # Comments
        if (self.config.get('markdown.include_comments', True) and
            ticket_data.get('comments')):
            sections.append(self._render_comments(ticket_data['comments']))
            sections.append("")

        # Custom fields
        if ticket_data.get('custom_fields'):
            sections.append(self._render_custom_fields(ticket_data['custom_fields']))
            sections.append("")

        # Attachments
        if (self.config.get('markdown.include_attachments', True) and
            ticket_data.get('attachments')):
            sections.append(self._render_attachments(ticket_data['attachments']))
            sections.append("")

        # Subtasks
        if (self.config.get('markdown.include_subtasks', True) and
            ticket_data.get('subtasks')):
            sections.append(self._render_subtasks(ticket_data['subtasks']))
            sections.append("")

        # Links
        if (self.config.get('markdown.include_links', True) and
            (ticket_data.get('links') or ticket_data.get('parent'))):
            sections.append(self._render_links(ticket_data))
            sections.append("")

        # Footer
        sections.append(self._render_footer())

        return "\n".join(sections)

    def _render_title(self, ticket_data: Dict[str, Any]) -> str:
        """Render the title."""
        key = ticket_data['key']
        summary = ticket_data['summary']
        return f"# [{key}] {summary}"

    def _render_metadata_table(self, ticket_data: Dict[str, Any]) -> str:
        """Render metadata as a table."""
        lines = ["## Metadata\n", "| Field | Value |", "|-------|-------|"]

        # Key fields
        metadata = [
            ("Key", ticket_data['key']),
            ("Status", ticket_data.get('status', '-')),
            ("Type", ticket_data.get('issue_type', '-')),
            ("Priority", ticket_data.get('priority', '-')),
        ]

        # People
        assignee = ticket_data.get('assignee')
        if assignee:
            metadata.append(("Assignee", assignee['name']))
        else:
            metadata.append(("Assignee", "Unassigned"))

        reporter = ticket_data.get('reporter')
        if reporter:
            metadata.append(("Reporter", reporter['name']))

        # Dates
        date_format = self.config.get('markdown.date_format', '%Y-%m-%d %H:%M:%S')

        if ticket_data.get('created'):
            metadata.append(("Created", self._format_date(ticket_data['created'], date_format)))
        if ticket_data.get('updated'):
            metadata.append(("Updated", self._format_date(ticket_data['updated'], date_format)))
        if ticket_data.get('resolved'):
            metadata.append(("Resolved", self._format_date(ticket_data['resolved'], date_format)))
        if ticket_data.get('due_date'):
            metadata.append(("Due Date", self._format_date(ticket_data['due_date'], date_format)))

        # Resolution
        if ticket_data.get('resolution'):
            metadata.append(("Resolution", ticket_data['resolution']))

        # Labels
        if ticket_data.get('labels'):
            metadata.append(("Labels", ", ".join(ticket_data['labels'])))

        # Components
        if ticket_data.get('components'):
            metadata.append(("Components", ", ".join(ticket_data['components'])))

        # Versions
        if ticket_data.get('fix_versions'):
            metadata.append(("Fix Versions", ", ".join(ticket_data['fix_versions'])))
        if ticket_data.get('affects_versions'):
            metadata.append(("Affects Versions", ", ".join(ticket_data['affects_versions'])))

        # Add to table
        for field, value in metadata:
            # Escape pipe characters in values
            value_str = str(value).replace('|', '\\|')
            lines.append(f"| **{field}** | {value_str} |")

        return "\n".join(lines)

    def _render_description(self, description: str) -> str:
        """Render description with JIRA markup conversion."""
        if not description:
            return "_No description provided._"

        if self.config.get('markdown.convert_markup', True):
            description = self._convert_jira_markup(description)

        return description

    def _render_comments(self, comments: List[Dict[str, Any]]) -> str:
        """Render comments section."""
        lines = ["## Comments\n"]

        date_format = self.config.get('markdown.date_format', '%Y-%m-%d %H:%M:%S')

        for comment in comments:
            author = comment.get('author', {})
            author_name = author.get('name', 'Unknown') if author else 'Unknown'
            created = comment.get('created')
            created_str = self._format_date(created, date_format) if created else 'Unknown'

            lines.append(f"### {author_name} - {created_str}\n")

            body = comment.get('body', '')
            if self.config.get('markdown.convert_markup', True):
                body = self._convert_jira_markup(body)

            lines.append(body)
            lines.append("")

        return "\n".join(lines)

    def _render_custom_fields(self, custom_fields: Dict[str, Any]) -> str:
        """Render custom fields."""
        lines = ["## Custom Fields\n"]

        for field_name, value in sorted(custom_fields.items()):
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value)
            else:
                value_str = str(value)

            lines.append(f"- **{field_name}**: {value_str}")

        return "\n".join(lines)

    def _render_attachments(self, attachments: List[Dict[str, Any]]) -> str:
        """Render attachments section."""
        lines = ["## Attachments\n"]

        for attachment in attachments:
            filename = attachment['filename']
            size = self._format_size(attachment['size'])
            url = attachment['url']
            lines.append(f"- [{filename}]({url}) ({size})")

        return "\n".join(lines)

    def _render_subtasks(self, subtasks: List[str]) -> str:
        """Render subtasks section."""
        lines = ["## Subtasks\n"]

        for subtask_key in subtasks:
            lines.append(f"- [ ] {subtask_key}")

        return "\n".join(lines)

    def _render_links(self, ticket_data: Dict[str, Any]) -> str:
        """Render links section."""
        lines = ["## Links\n"]

        # Parent issue
        if ticket_data.get('parent'):
            parent_key = ticket_data['parent']
            parent_url = f"{self.config.jira_url}/browse/{parent_key}"
            lines.append(f"- **Parent Issue**: [{parent_key}]({parent_url})")

        # Issue links
        if ticket_data.get('links'):
            for link in ticket_data['links']:
                link_type = link.get('type', 'Related')
                link_key = link.get('key', '')
                link_summary = link.get('summary', '')
                direction = link.get('direction', '')

                if link_key:
                    link_url = f"{self.config.jira_url}/browse/{link_key}"
                    lines.append(f"- **{link_type}** ({direction}): [{link_key}]({link_url}) - {link_summary}")

        # View in JIRA
        jira_url = ticket_data.get('url', '')
        if jira_url:
            lines.append(f"\n- **View in JIRA**: [{ticket_data['key']}]({jira_url})")

        return "\n".join(lines)

    def _render_footer(self) -> str:
        """Render footer."""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"---\n*Generated on {now} by JIRA to Markdown Converter*"

    def _convert_jira_markup(self, text: str) -> str:
        """
        Convert JIRA markup to Markdown.

        Args:
            text: Text with JIRA markup

        Returns:
            Text with Markdown formatting
        """
        if not text:
            return ""

        # Code blocks (must be first to avoid affecting other conversions)
        text = re.sub(r'\{code:?([^}]*)\}(.*?)\{code\}',
                     lambda m: f"```{m.group(1).strip()}\n{m.group(2)}\n```",
                     text, flags=re.DOTALL)

        # Noformat blocks
        text = re.sub(r'\{noformat\}(.*?)\{noformat\}',
                     r'```\n\1\n```', text, flags=re.DOTALL)

        # Quote blocks
        text = re.sub(r'\{quote\}(.*?)\{quote\}',
                     lambda m: '\n'.join(f'> {line}' for line in m.group(1).strip().split('\n')),
                     text, flags=re.DOTALL)

        # Headers (h1-h6)
        for i in range(1, 7):
            text = re.sub(f'^h{i}\\. (.+)$', '#' * i + r' \1', text, flags=re.MULTILINE)

        # Bold
        text = re.sub(r'\*(\S.*?)\*', r'**\1**', text)

        # Italic
        text = re.sub(r'_(\S.*?)_', r'*\1*', text)

        # Strikethrough
        text = re.sub(r'-(\S.*?)-', r'~~\1~~', text)

        # Monospace
        text = re.sub(r'\{\{(.*?)\}\}', r'`\1`', text)

        # Underline (no direct Markdown equivalent, use emphasis)
        text = re.sub(r'\+(\S.*?)\+', r'*\1*', text)

        # Links [text|url]
        text = re.sub(r'\[([^|\]]+)\|([^\]]+)\]', r'[\1](\2)', text)

        # Bulleted lists (convert - to *)
        text = re.sub(r'^- ', r'* ', text, flags=re.MULTILINE)

        # Numbered lists are already compatible

        # Mentions (@username) - keep as is or link if needed
        # text = re.sub(r'\[~([^\]]+)\]', r'@\1', text)

        return text

    def _format_date(self, date_obj: datetime, date_format: str) -> str:
        """Format datetime object as string."""
        if isinstance(date_obj, datetime):
            return date_obj.strftime(date_format)
        return str(date_obj)

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
