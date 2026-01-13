"""
Ticket retrieval and data extraction logic.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dateutil import parser as date_parser


class TicketFetcher:
    """Handles fetching and extracting ticket data from JIRA."""

    def __init__(self, jira_client):
        """
        Initialize ticket fetcher.

        Args:
            jira_client: JiraClient instance
        """
        self.jira_client = jira_client
        self.logger = logging.getLogger(__name__)
        self._custom_field_mapping = None

    def _get_custom_field_mapping(self) -> Dict[str, str]:
        """Get or fetch custom field mapping."""
        if self._custom_field_mapping is None:
            self._custom_field_mapping = self.jira_client.get_custom_fields()
        return self._custom_field_mapping

    def fetch_single(self, ticket_key: str) -> Dict[str, Any]:
        """
        Fetch a single ticket by key.

        Args:
            ticket_key: Ticket key (e.g., 'PROJ-123')

        Returns:
            Dictionary containing ticket data
        """
        self.logger.info(f"Fetching ticket {ticket_key}")
        issue = self.jira_client.get_issue(ticket_key)
        return self._extract_ticket_data(issue)

    def fetch_by_jql(self, jql: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch tickets using JQL query.

        Args:
            jql: JQL query string
            max_results: Maximum number of results (None for all)

        Returns:
            List of ticket data dictionaries
        """
        self.logger.info(f"Fetching tickets with JQL: {jql}")

        if max_results:
            issues = self.jira_client.search_issues(jql, max_results=max_results)
        else:
            issues = self.jira_client.search_all_issues(jql)

        return [self._extract_ticket_data(issue) for issue in issues]

    def fetch_bulk(self, ticket_keys: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch multiple specific tickets.

        Args:
            ticket_keys: List of ticket keys

        Returns:
            List of ticket data dictionaries
        """
        self.logger.info(f"Fetching {len(ticket_keys)} tickets")
        tickets = []

        for key in ticket_keys:
            try:
                ticket = self.fetch_single(key)
                tickets.append(ticket)
            except Exception as e:
                self.logger.error(f"Failed to fetch {key}: {e}")
                continue

        return tickets

    def _extract_ticket_data(self, issue) -> Dict[str, Any]:
        """
        Extract all relevant data from a JIRA issue object.

        Args:
            issue: JIRA issue object

        Returns:
            Dictionary containing structured ticket data
        """
        fields = issue.fields

        # Basic fields
        data = {
            'key': issue.key,
            'summary': fields.summary or '',
            'description': fields.description or '',
            'status': str(fields.status) if fields.status else '',
            'issue_type': str(fields.issuetype) if fields.issuetype else '',
            'priority': str(fields.priority) if fields.priority else '',
        }

        # People
        data['assignee'] = self._extract_user(fields.assignee)
        data['reporter'] = self._extract_user(fields.reporter)
        data['creator'] = self._extract_user(fields.creator)

        # Dates
        data['created'] = self._parse_date(fields.created)
        data['updated'] = self._parse_date(fields.updated)
        data['resolved'] = self._parse_date(getattr(fields, 'resolutiondate', None))
        data['due_date'] = self._parse_date(fields.duedate)

        # Lists
        data['labels'] = fields.labels or []
        data['components'] = [str(c) for c in fields.components] if fields.components else []
        data['fix_versions'] = [str(v) for v in fields.fixVersions] if fields.fixVersions else []
        data['affects_versions'] = [str(v) for v in getattr(fields, 'versions', [])] if hasattr(fields, 'versions') else []

        # Resolution
        data['resolution'] = str(fields.resolution) if fields.resolution else None

        # Parent/subtasks
        data['parent'] = getattr(fields, 'parent', None)
        if data['parent']:
            data['parent'] = data['parent'].key

        data['subtasks'] = []
        if hasattr(fields, 'subtasks') and fields.subtasks:
            data['subtasks'] = [subtask.key for subtask in fields.subtasks]

        # Comments
        data['comments'] = self._extract_comments(issue)

        # Attachments
        data['attachments'] = self._extract_attachments(fields)

        # Issue links
        data['links'] = self._extract_links(fields)

        # Custom fields
        data['custom_fields'] = self._extract_custom_fields(issue)

        # JIRA URL
        data['url'] = f"{self.jira_client.url}/browse/{issue.key}"

        return data

    def _extract_user(self, user) -> Optional[Dict[str, str]]:
        """Extract user information."""
        if not user:
            return None

        return {
            'name': getattr(user, 'displayName', None) or getattr(user, 'name', 'Unknown'),
            'email': getattr(user, 'emailAddress', None) or ''
        }

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None

        try:
            return date_parser.parse(date_str)
        except Exception as e:
            self.logger.warning(f"Failed to parse date '{date_str}': {e}")
            return None

    def _extract_comments(self, issue) -> List[Dict[str, Any]]:
        """Extract comments from issue."""
        comments = []

        try:
            for comment in issue.fields.comment.comments:
                comments.append({
                    'author': self._extract_user(comment.author),
                    'body': comment.body or '',
                    'created': self._parse_date(comment.created),
                    'updated': self._parse_date(comment.updated)
                })
        except Exception as e:
            self.logger.warning(f"Failed to extract comments: {e}")

        return comments

    def _extract_attachments(self, fields) -> List[Dict[str, Any]]:
        """Extract attachment information."""
        attachments = []

        try:
            if hasattr(fields, 'attachment') and fields.attachment:
                for attachment in fields.attachment:
                    attachments.append({
                        'filename': attachment.filename,
                        'size': attachment.size,
                        'mime_type': getattr(attachment, 'mimeType', ''),
                        'url': attachment.content,
                        'created': self._parse_date(attachment.created)
                    })
        except Exception as e:
            self.logger.warning(f"Failed to extract attachments: {e}")

        return attachments

    def _extract_links(self, fields) -> List[Dict[str, str]]:
        """Extract issue links."""
        links = []

        try:
            if hasattr(fields, 'issuelinks') and fields.issuelinks:
                for link in fields.issuelinks:
                    link_data = {
                        'type': str(link.type) if hasattr(link, 'type') else ''
                    }

                    # Check if it's an outward or inward link
                    if hasattr(link, 'outwardIssue'):
                        link_data['direction'] = 'outward'
                        link_data['key'] = link.outwardIssue.key
                        link_data['summary'] = link.outwardIssue.fields.summary
                    elif hasattr(link, 'inwardIssue'):
                        link_data['direction'] = 'inward'
                        link_data['key'] = link.inwardIssue.key
                        link_data['summary'] = link.inwardIssue.fields.summary

                    links.append(link_data)
        except Exception as e:
            self.logger.warning(f"Failed to extract links: {e}")

        return links

    def _extract_custom_fields(self, issue) -> Dict[str, Any]:
        """Extract custom fields with friendly names."""
        custom_fields = {}
        mapping = self._get_custom_field_mapping()

        try:
            for field_id, field_name in mapping.items():
                if hasattr(issue.fields, field_id):
                    value = getattr(issue.fields, field_id)
                    if value is not None:
                        # Convert complex objects to strings
                        if isinstance(value, (list, tuple)):
                            value = [str(v) for v in value]
                        elif not isinstance(value, (str, int, float, bool)):
                            value = str(value)

                        custom_fields[field_name] = value
        except Exception as e:
            self.logger.warning(f"Failed to extract custom fields: {e}")

        return custom_fields
