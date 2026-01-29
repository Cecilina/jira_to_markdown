"""Tests for markdown converter."""

from datetime import datetime
import pytest
from jira_to_markdown.markdown_converter import MarkdownConverter


class MockConfig:
    """Mock config for testing."""

    def __init__(self):
        self._config = {
            'markdown': {
                'include_metadata_table': True,
                'include_comments': True,
                'include_attachments': True,
                'include_subtasks': True,
                'include_links': True,
                'date_format': '%Y-%m-%d %H:%M:%S',
                'convert_markup': True
            },
            'jira': {
                'url': 'https://test.atlassian.net'
            }
        }

    def get(self, key, default=None):
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value

    @property
    def jira_url(self):
        return 'https://test.atlassian.net'


@pytest.fixture
def converter():
    """Create a markdown converter with mock config."""
    config = MockConfig()
    return MarkdownConverter(config)


@pytest.fixture
def sample_ticket_data():
    """Sample ticket data for testing."""
    return {
        'key': 'TEST-123',
        'summary': 'Test Issue',
        'description': 'This is a *bold* test with _italic_ text.',
        'status': 'In Progress',
        'issue_type': 'Bug',
        'priority': 'High',
        'assignee': {'name': 'John Doe', 'email': 'john@example.com'},
        'reporter': {'name': 'Jane Smith', 'email': 'jane@example.com'},
        'created': datetime(2024, 1, 13, 10, 30, 0),
        'updated': datetime(2024, 1, 14, 15, 45, 0),
        'resolved': None,
        'due_date': None,
        'labels': ['bug', 'critical'],
        'components': ['Backend'],
        'fix_versions': [],
        'affects_versions': [],
        'resolution': None,
        'parent': None,
        'subtasks': ['TEST-124', 'TEST-125'],
        'comments': [
            {
                'author': {'name': 'John Doe'},
                'body': 'This is a comment',
                'created': datetime(2024, 1, 13, 11, 0, 0)
            }
        ],
        'attachments': [
            {
                'filename': 'test.png',
                'size': 1024,
                'url': 'https://example.com/test.png'
            }
        ],
        'links': [],
        'custom_fields': {
            'Story Points': 5,
            'Sprint': 'Sprint 42'
        },
        'url': 'https://test.atlassian.net/browse/TEST-123'
    }


def test_convert_basic(converter, sample_ticket_data):
    """Test basic markdown conversion."""
    markdown = converter.convert(sample_ticket_data)

    assert '# [TEST-123] Test Issue' in markdown
    assert '## Metadata' in markdown
    assert 'In Progress' in markdown
    assert 'Bug' in markdown
    assert 'John Doe' in markdown


def test_convert_jira_markup_bold(converter):
    """Test JIRA bold markup conversion."""
    text = 'This is *bold* text'
    result = converter._convert_jira_markup(text)
    assert '**bold**' in result


def test_convert_jira_markup_italic(converter):
    """Test JIRA italic markup conversion."""
    text = 'This is _italic_ text'
    result = converter._convert_jira_markup(text)
    assert '*italic*' in result


def test_convert_jira_markup_monospace(converter):
    """Test JIRA monospace markup conversion."""
    text = 'This is {{monospace}} text'
    result = converter._convert_jira_markup(text)
    assert '`monospace`' in result


def test_convert_jira_markup_code_block(converter):
    """Test JIRA code block markup conversion."""
    text = '{code}print("hello"){code}'
    result = converter._convert_jira_markup(text)
    assert '```' in result
    assert 'print("hello")' in result


def test_convert_jira_markup_link(converter):
    """Test JIRA link markup conversion."""
    text = '[Example|https://example.com]'
    result = converter._convert_jira_markup(text)
    assert '[Example](https://example.com)' in result


def test_render_metadata_table(converter, sample_ticket_data):
    """Test metadata table rendering."""
    table = converter._render_metadata_table(sample_ticket_data)

    assert '## Metadata' in table
    assert 'TEST-123' in table
    assert 'In Progress' in table
    assert 'High' in table
    assert 'John Doe' in table
    assert 'bug, critical' in table


def test_render_comments(converter, sample_ticket_data):
    """Test comments rendering."""
    comments = converter._render_comments(sample_ticket_data['comments'])

    assert '## Comments' in comments
    assert 'John Doe' in comments
    assert 'This is a comment' in comments


def test_render_custom_fields(converter, sample_ticket_data):
    """Test custom fields rendering."""
    fields = converter._render_custom_fields(sample_ticket_data['custom_fields'])

    assert '## Custom Fields' in fields
    assert 'Story Points' in fields
    assert '5' in fields
    assert 'Sprint' in fields
    assert 'Sprint 42' in fields


def test_format_size(converter):
    """Test file size formatting."""
    assert converter._format_size(500) == '500.0 B'
    assert converter._format_size(1024) == '1.0 KB'
    assert converter._format_size(1024 * 1024) == '1.0 MB'
    assert converter._format_size(1024 * 1024 * 1024) == '1.0 GB'
