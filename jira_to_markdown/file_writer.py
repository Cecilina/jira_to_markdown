"""
File output management with safety checks.
"""

import os
import re
import logging
from typing import Dict
import tempfile


class FileWriteError(Exception):
    """Raised when file writing fails."""
    pass


class FileWriter:
    """Handles writing markdown files to disk."""

    def __init__(self, output_dir: str, overwrite: bool = False, filename_format: str = "{key}.md"):
        """
        Initialize file writer.

        Args:
            output_dir: Directory where files will be written
            overwrite: Whether to overwrite existing files
            filename_format: Format string for filenames (e.g., "{key}.md")
        """
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.filename_format = filename_format
        self.logger = logging.getLogger(__name__)

        # Ensure output directory exists
        self._ensure_directory(self.output_dir)

    def write_ticket(self, ticket_key: str, markdown_content: str, ticket_data: Dict = None) -> str:
        """
        Write a single ticket to a markdown file.

        Args:
            ticket_key: Ticket key (e.g., 'PROJ-123')
            markdown_content: Markdown content to write
            ticket_data: Full ticket data (for filename formatting)

        Returns:
            Path to the written file

        Raises:
            FileWriteError: If writing fails
        """
        # Generate filename
        filename = self._generate_filename(ticket_key, ticket_data)
        filepath = os.path.join(self.output_dir, filename)

        # Check if file exists and overwrite is disabled
        if not self.overwrite and os.path.exists(filepath):
            self.logger.warning(f"File {filepath} already exists, skipping (use --overwrite to replace)")
            return filepath

        # Write file atomically
        try:
            self._write_atomic(filepath, markdown_content)
            self.logger.info(f"Written {filepath}")
            return filepath
        except Exception as e:
            raise FileWriteError(f"Failed to write {filepath}: {e}")

    def write_multiple(self, tickets_data: Dict[str, tuple]) -> list:
        """
        Write multiple tickets to markdown files.

        Args:
            tickets_data: Dictionary mapping ticket_key to (markdown_content, ticket_data)

        Returns:
            List of written file paths
        """
        written_files = []

        for ticket_key, (markdown_content, ticket_data) in tickets_data.items():
            try:
                filepath = self.write_ticket(ticket_key, markdown_content, ticket_data)
                written_files.append(filepath)
            except FileWriteError as e:
                self.logger.error(f"Failed to write {ticket_key}: {e}")
                continue

        return written_files

    def _generate_filename(self, ticket_key: str, ticket_data: Dict = None) -> str:
        """
        Generate filename from format string.

        Args:
            ticket_key: Ticket key
            ticket_data: Full ticket data for additional fields

        Returns:
            Sanitized filename
        """
        # Prepare variables for formatting
        variables = {'key': ticket_key}

        if ticket_data:
            # Add other useful fields
            variables['summary'] = ticket_data.get('summary', '')
            if ticket_data.get('created'):
                variables['created'] = ticket_data['created'].strftime('%Y%m%d')
            if ticket_data.get('updated'):
                variables['updated'] = ticket_data['updated'].strftime('%Y%m%d')

        try:
            filename = self.filename_format.format(**variables)
        except KeyError as e:
            self.logger.warning(f"Invalid filename format variable: {e}, using default")
            filename = f"{ticket_key}.md"

        # Sanitize filename
        filename = self._sanitize_filename(filename)

        return filename

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename by removing or replacing illegal characters.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove or replace illegal characters for most filesystems
        # Illegal: < > : " / \ | ? *
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')

        # Limit length (most filesystems support 255 chars)
        if len(filename) > 255:
            # Keep extension
            name, ext = os.path.splitext(filename)
            max_name_len = 255 - len(ext)
            filename = name[:max_name_len] + ext

        # Ensure filename is not empty
        if not filename:
            filename = "unnamed.md"

        return filename

    def _ensure_directory(self, path: str):
        """
        Create directory if it doesn't exist.

        Args:
            path: Directory path

        Raises:
            FileWriteError: If directory creation fails
        """
        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                self.logger.info(f"Created directory: {path}")
        except Exception as e:
            raise FileWriteError(f"Failed to create directory {path}: {e}")

    def _write_atomic(self, filepath: str, content: str):
        """
        Write file atomically using a temporary file.

        This ensures that the file is either fully written or not at all,
        preventing partial writes in case of errors.

        Args:
            filepath: Target file path
            content: Content to write

        Raises:
            Exception: If writing fails
        """
        # Get directory and filename
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)

        # Write to temporary file in the same directory
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=directory,
            prefix=f'.{filename}.',
            suffix='.tmp',
            delete=False
        ) as temp_file:
            temp_path = temp_file.name
            temp_file.write(content)

        try:
            # Atomic rename (or as atomic as possible on the platform)
            os.replace(temp_path, filepath)
        except Exception as e:
            # Clean up temp file if rename fails
            try:
                os.remove(temp_path)
            except:
                pass
            raise e

    def get_existing_files(self) -> list:
        """
        Get list of existing markdown files in output directory.

        Returns:
            List of filenames
        """
        if not os.path.exists(self.output_dir):
            return []

        files = []
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.md'):
                files.append(filename)

        return files

    def file_exists(self, ticket_key: str) -> bool:
        """
        Check if a file for the given ticket key already exists.

        Args:
            ticket_key: Ticket key

        Returns:
            True if file exists
        """
        filename = self._generate_filename(ticket_key)
        filepath = os.path.join(self.output_dir, filename)
        return os.path.exists(filepath)
