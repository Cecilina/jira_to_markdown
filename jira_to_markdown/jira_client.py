"""
JIRA API client wrapper with authentication and error handling.
"""

from jira import JIRA
from jira.exceptions import JIRAError
import logging
from typing import List, Optional, Dict


class JiraConnectionError(Exception):
    """Raised when JIRA connection fails."""
    pass


class JiraAuthenticationError(Exception):
    """Raised when JIRA authentication fails."""
    pass


class TicketNotFoundError(Exception):
    """Raised when a ticket is not found."""
    pass


class JiraClient:
    """Wrapper around JIRA Python library with enhanced error handling."""

    def __init__(self, url: str, username: str, api_token: str, verify_ssl: bool = True):
        """
        Initialize JIRA client.

        Args:
            url: JIRA instance URL
            username: JIRA username (email)
            api_token: JIRA API token
            verify_ssl: Whether to verify SSL certificates
        """
        self.url = url
        self.username = username
        self.api_token = api_token
        self.verify_ssl = verify_ssl
        self.logger = logging.getLogger(__name__)
        self._jira = None
        self._custom_fields = None

    def connect(self) -> bool:
        """
        Establish connection to JIRA.

        Returns:
            True if connection successful

        Raises:
            JiraConnectionError: If connection fails
            JiraAuthenticationError: If authentication fails
        """
        try:
            self.logger.info(f"Connecting to JIRA at {self.url}")

            # Create JIRA client with basic auth
            options = {
                'server': self.url,
                'verify': self.verify_ssl
            }

            self._jira = JIRA(
                options=options,
                basic_auth=(self.username, self.api_token)
            )

            # Test connection by getting server info
            server_info = self._jira.server_info()
            self.logger.info(f"Connected to JIRA version {server_info.get('version', 'unknown')}")

            return True

        except JIRAError as e:
            if e.status_code == 401:
                raise JiraAuthenticationError(
                    "Authentication failed. Please check your username and API token."
                )
            else:
                raise JiraConnectionError(f"Failed to connect to JIRA: {e.text}")
        except Exception as e:
            raise JiraConnectionError(f"Failed to connect to JIRA: {str(e)}")

    def test_connection(self) -> bool:
        """
        Test JIRA connection and credentials.

        Returns:
            True if connection test passes

        Raises:
            JiraConnectionError: If connection test fails
        """
        if not self._jira:
            return self.connect()

        try:
            # Try to get current user info
            self._jira.myself()
            self.logger.info("Connection test successful")
            return True
        except JIRAError as e:
            raise JiraConnectionError(f"Connection test failed: {e.text}")

    def get_issue(self, key: str, fields: str = '*all') -> Optional[object]:
        """
        Fetch a single JIRA issue by key.

        Args:
            key: Issue key (e.g., 'PROJ-123')
            fields: Fields to include ('*all' for all fields)

        Returns:
            JIRA issue object

        Raises:
            TicketNotFoundError: If ticket doesn't exist
            JiraConnectionError: If connection fails
        """
        if not self._jira:
            self.connect()

        try:
            self.logger.debug(f"Fetching issue {key}")
            issue = self._jira.issue(key, fields=fields)
            return issue
        except JIRAError as e:
            if e.status_code == 404:
                raise TicketNotFoundError(f"Ticket {key} not found")
            else:
                raise JiraConnectionError(f"Failed to fetch ticket {key}: {e.text}")

    def search_issues(self, jql: str, max_results: int = 100,
                      fields: str = '*all', start_at: int = 0) -> List[object]:
        """
        Search for issues using JQL.

        Args:
            jql: JQL query string
            max_results: Maximum number of results
            fields: Fields to include
            start_at: Starting index for pagination (ignored for Jira Cloud)

        Returns:
            List of JIRA issue objects

        Raises:
            JiraConnectionError: If search fails
        """
        if not self._jira:
            self.connect()

        try:
            self.logger.debug(f"Searching issues with JQL: {jql}")
            # Use enhanced_search_issues for Jira Cloud (search_issues is deprecated)
            if hasattr(self._jira, 'enhanced_search_issues'):
                issues = self._jira.enhanced_search_issues(
                    jql,
                    maxResults=max_results,
                    fields=fields
                )
            else:
                # Fallback for older jira-python versions or Jira Server
                issues = self._jira.search_issues(
                    jql,
                    maxResults=max_results,
                    startAt=start_at,
                    fields=fields
                )
            self.logger.info(f"Found {len(issues)} issues")
            return issues
        except JIRAError as e:
            raise JiraConnectionError(f"Failed to search issues: {e.text}")

    def search_all_issues(self, jql: str, fields: str = '*all',
                         batch_size: int = 50) -> List[object]:
        """
        Search for all issues matching JQL with pagination.

        Args:
            jql: JQL query string
            fields: Fields to include
            batch_size: Number of results per request (used for Jira Server only)

        Returns:
            List of all matching JIRA issue objects

        Raises:
            JiraConnectionError: If search fails
        """
        if not self._jira:
            self.connect()

        try:
            self.logger.debug(f"Searching all issues with JQL: {jql}")
            # Use enhanced_search_issues for Jira Cloud - it auto-paginates when maxResults=0
            if hasattr(self._jira, 'enhanced_search_issues'):
                issues = list(self._jira.enhanced_search_issues(
                    jql,
                    maxResults=0,  # 0 means fetch all with auto-pagination
                    fields=fields
                ))
                self.logger.info(f"Retrieved {len(issues)} issues total")
                return issues
            else:
                # Fallback for older jira-python versions or Jira Server
                all_issues = []
                start_at = 0

                while True:
                    issues = self._jira.search_issues(
                        jql,
                        maxResults=batch_size,
                        startAt=start_at,
                        fields=fields
                    )

                    if not issues:
                        break

                    all_issues.extend(issues)
                    start_at += len(issues)

                    if len(issues) < batch_size:
                        break

                self.logger.info(f"Retrieved {len(all_issues)} issues total")
                return all_issues
        except JIRAError as e:
            raise JiraConnectionError(f"Failed to search issues: {e.text}")

    def get_custom_fields(self) -> Dict[str, str]:
        """
        Get mapping of custom field IDs to field names.

        Returns:
            Dictionary mapping field IDs to names

        Raises:
            JiraConnectionError: If fetching fields fails
        """
        if self._custom_fields is not None:
            return self._custom_fields

        if not self._jira:
            self.connect()

        try:
            self.logger.debug("Fetching custom field mappings")
            fields = self._jira.fields()

            # Create mapping of custom field IDs to names
            self._custom_fields = {}
            for field in fields:
                if field.get('custom'):
                    field_id = field['id']
                    field_name = field['name']
                    self._custom_fields[field_id] = field_name

            self.logger.info(f"Found {len(self._custom_fields)} custom fields")
            return self._custom_fields

        except JIRAError as e:
            raise JiraConnectionError(f"Failed to fetch custom fields: {e.text}")

    def get_comments(self, issue_key: str) -> List[object]:
        """
        Get all comments for an issue.

        Args:
            issue_key: Issue key

        Returns:
            List of comment objects

        Raises:
            JiraConnectionError: If fetching comments fails
        """
        if not self._jira:
            self.connect()

        try:
            comments = self._jira.comments(issue_key)
            return comments
        except JIRAError as e:
            self.logger.warning(f"Failed to fetch comments for {issue_key}: {e.text}")
            return []

    def disconnect(self):
        """Close JIRA connection."""
        if self._jira:
            self._jira.close()
            self._jira = None
            self.logger.info("Disconnected from JIRA")
