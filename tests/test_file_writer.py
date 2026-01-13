"""Tests for file writer."""

import pytest
import os
import tempfile
import shutil
from jira_to_markdown.file_writer import FileWriter, FileWriteError


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


@pytest.fixture
def writer(temp_dir):
    """Create a file writer with temp directory."""
    return FileWriter(temp_dir, overwrite=False)


def test_write_ticket(writer, temp_dir):
    """Test writing a single ticket."""
    content = "# Test Content\n\nThis is a test."
    filepath = writer.write_ticket('TEST-123', content)

    assert os.path.exists(filepath)
    assert filepath.endswith('TEST-123.md')

    with open(filepath, 'r') as f:
        assert f.read() == content


def test_write_ticket_no_overwrite(writer, temp_dir):
    """Test that existing files are not overwritten by default."""
    content1 = "First content"
    content2 = "Second content"

    # Write first time
    filepath1 = writer.write_ticket('TEST-123', content1)

    # Try to write again with different content
    filepath2 = writer.write_ticket('TEST-123', content2)

    # File should still have first content
    with open(filepath1, 'r') as f:
        assert f.read() == content1


def test_write_ticket_with_overwrite(temp_dir):
    """Test overwriting existing files."""
    writer = FileWriter(temp_dir, overwrite=True)

    content1 = "First content"
    content2 = "Second content"

    # Write first time
    writer.write_ticket('TEST-123', content1)

    # Write again with overwrite enabled
    filepath = writer.write_ticket('TEST-123', content2)

    # File should have second content
    with open(filepath, 'r') as f:
        assert f.read() == content2


def test_sanitize_filename(writer):
    """Test filename sanitization."""
    # Test illegal characters
    assert writer._sanitize_filename('test<file>.md') == 'test_file_.md'
    assert writer._sanitize_filename('test:file.md') == 'test_file.md'
    assert writer._sanitize_filename('test/file.md') == 'test_file.md'
    assert writer._sanitize_filename('test|file.md') == 'test_file.md'

    # Test leading/trailing spaces and dots
    assert writer._sanitize_filename('  test.md  ') == 'test.md'
    assert writer._sanitize_filename('.test.md') == 'test.md'


def test_file_exists(writer, temp_dir):
    """Test checking if file exists."""
    assert not writer.file_exists('TEST-123')

    writer.write_ticket('TEST-123', 'content')

    assert writer.file_exists('TEST-123')


def test_get_existing_files(writer, temp_dir):
    """Test getting list of existing files."""
    assert len(writer.get_existing_files()) == 0

    writer.write_ticket('TEST-123', 'content 1')
    writer.write_ticket('TEST-124', 'content 2')

    files = writer.get_existing_files()
    assert len(files) == 2
    assert 'TEST-123.md' in files
    assert 'TEST-124.md' in files


def test_ensure_directory_creation(temp_dir):
    """Test that nested directories are created."""
    nested_dir = os.path.join(temp_dir, 'nested', 'deep', 'path')
    writer = FileWriter(nested_dir)

    assert os.path.exists(nested_dir)


def test_atomic_write(writer, temp_dir):
    """Test atomic write functionality."""
    content = "Test content"
    filepath = os.path.join(temp_dir, 'atomic_test.md')

    writer._write_atomic(filepath, content)

    assert os.path.exists(filepath)
    with open(filepath, 'r') as f:
        assert f.read() == content

    # Ensure no temp files are left
    temp_files = [f for f in os.listdir(temp_dir) if f.startswith('.') and f.endswith('.tmp')]
    assert len(temp_files) == 0
