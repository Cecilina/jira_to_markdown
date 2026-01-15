"""
Image downloader for JIRA attachments and external URLs.
"""

import os
import re
import logging
import tempfile
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, NamedTuple
from urllib.parse import urlparse

import requests


class ImageInfo(NamedTuple):
    """Information about an image found in markdown."""
    alt_text: str
    url: str
    full_match: str
    is_jira: bool


class DownloadResult(NamedTuple):
    """Result of an image download attempt."""
    success: bool
    local_path: Optional[str]
    error: Optional[str]


class ImageDownloader:
    """Downloads images from markdown files and updates paths."""

    IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico'}
    MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB

    def __init__(
        self,
        output_dir: str,
        images_dir: str,
        jira_url: str,
        jira_username: str = None,
        jira_api_token: str = None,
        verify_ssl: bool = True
    ):
        """
        Initialize image downloader.

        Args:
            output_dir: Directory containing markdown files
            images_dir: Directory where images will be saved
            jira_url: Base JIRA URL for identifying JIRA attachments
            jira_username: JIRA username for authentication
            jira_api_token: JIRA API token for authentication
            verify_ssl: Whether to verify SSL certificates
        """
        self.output_dir = Path(output_dir)
        self.images_dir = Path(images_dir)
        self.jira_url = jira_url.rstrip('/') if jira_url else ''
        self.jira_domain = urlparse(jira_url).netloc if jira_url else ''
        self.jira_username = jira_username
        self.jira_api_token = jira_api_token
        self.verify_ssl = verify_ssl
        self.logger = logging.getLogger(__name__)
        self._downloaded_files: Dict[str, str] = {}

    def process_directory(self) -> Dict[str, Dict]:
        """
        Process all markdown files in the output directory.

        Returns:
            Dictionary mapping filenames to processing results
        """
        self._ensure_directory(self.images_dir)

        results = {}
        md_files = list(self.output_dir.glob('*.md'))

        self.logger.info(f"Found {len(md_files)} markdown files to process")

        for md_file in md_files:
            result = self.process_file(md_file)
            results[md_file.name] = result

        return results

    def process_file(self, filepath: Path) -> Dict:
        """
        Process a single markdown file.

        Args:
            filepath: Path to the markdown file

        Returns:
            Dictionary with processing results
        """
        ticket_key = self._extract_ticket_key(filepath)

        self.logger.debug(f"Processing {filepath.name} (ticket: {ticket_key})")

        result = {
            'ticket_key': ticket_key,
            'images_found': 0,
            'images_downloaded': 0,
            'images_skipped': 0,
            'images_failed': 0,
            'errors': []
        }

        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            result['errors'].append(f"Failed to read file: {e}")
            return result

        images = self._find_images(content)
        result['images_found'] = len([img for img in images if img.url.startswith(('http://', 'https://'))])

        if not images:
            self.logger.debug(f"No images found in {filepath.name}")
            return result

        updated_content = content
        for img in images:
            if not img.url.startswith(('http://', 'https://')):
                result['images_skipped'] += 1
                continue

            local_filename = self._generate_filename(ticket_key, img.url, img.alt_text)
            local_path = self.images_dir / local_filename

            if img.url in self._downloaded_files:
                existing_path = self._downloaded_files[img.url]
                relative_path = self._get_relative_path(filepath.parent, Path(existing_path))
                updated_content = updated_content.replace(
                    img.full_match,
                    f'![{img.alt_text}]({relative_path})',
                    1
                )
                result['images_downloaded'] += 1
                continue

            download_result = self._download_image(img.url, local_path, img.is_jira)

            if download_result.success:
                self._downloaded_files[img.url] = str(local_path)
                relative_path = self._get_relative_path(filepath.parent, local_path)
                updated_content = updated_content.replace(
                    img.full_match,
                    f'![{img.alt_text}]({relative_path})',
                    1
                )
                result['images_downloaded'] += 1
                self.logger.info(f"Downloaded: {local_filename}")
            else:
                result['images_failed'] += 1
                result['errors'].append(f"{img.url}: {download_result.error}")
                self.logger.warning(f"Failed to download {img.url}: {download_result.error}")

        if updated_content != content:
            self._write_atomic(filepath, updated_content)
            self.logger.info(f"Updated {filepath.name}")

        return result

    def _find_images(self, content: str) -> List[ImageInfo]:
        """Find all image references in markdown content."""
        images = []

        for match in self.IMAGE_PATTERN.finditer(content):
            alt_text = match.group(1)
            url = match.group(2)
            full_match = match.group(0)
            is_jira = self._is_jira_url(url)

            images.append(ImageInfo(
                alt_text=alt_text,
                url=url,
                full_match=full_match,
                is_jira=is_jira
            ))

        return images

    def _is_jira_url(self, url: str) -> bool:
        """Check if URL points to JIRA attachment."""
        if not self.jira_domain:
            return False
        parsed = urlparse(url)
        return (
            parsed.netloc == self.jira_domain or
            ('/rest/api/' in url and '/attachment/' in url)
        )

    def _extract_ticket_key(self, filepath: Path) -> str:
        """
        Extract ticket key from filename.

        Handles formats like:
        - PROJ-123.md
        - PROJ-123 Some Title.md
        """
        filename = filepath.stem
        match = re.match(r'^([A-Z]+-\d+)', filename)
        if match:
            return match.group(1)
        return filename

    def _generate_filename(self, ticket_key: str, url: str, alt_text: str) -> str:
        """
        Generate unique local filename for downloaded image.

        Format: {ticket-key}-{original-filename}
        """
        parsed = urlparse(url)
        path = parsed.path
        original_name = Path(path).name if path else ''

        if not original_name or not self._has_image_extension(original_name):
            if alt_text and self._has_image_extension(alt_text):
                original_name = alt_text
            else:
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                original_name = f"image-{url_hash}.png"

        original_name = self._sanitize_filename(original_name)
        final_name = f"{ticket_key}-{original_name}"

        base_name, ext = os.path.splitext(final_name)
        counter = 1
        while (self.images_dir / final_name).exists():
            final_name = f"{base_name}-{counter}{ext}"
            counter += 1

        return final_name

    def _has_image_extension(self, filename: str) -> bool:
        """Check if filename has a valid image extension."""
        ext = Path(filename).suffix.lower()
        return ext in self.IMAGE_EXTENSIONS

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = filename.strip('. ')

        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200 - len(ext)] + ext

        return filename or 'image.png'

    def _download_image(self, url: str, local_path: Path, is_jira: bool) -> DownloadResult:
        """
        Download image from URL to local path.

        Args:
            url: Image URL
            local_path: Where to save the image
            is_jira: Whether this is a JIRA URL (requires auth)

        Returns:
            DownloadResult with success status
        """
        try:
            headers = {'User-Agent': 'jira-to-markdown/1.0'}
            auth = None

            if is_jira and self.jira_username and self.jira_api_token:
                auth = (self.jira_username, self.jira_api_token)

            response = requests.get(
                url,
                auth=auth,
                headers=headers,
                stream=True,
                timeout=30,
                verify=self.verify_ssl
            )
            response.raise_for_status()

            self._ensure_directory(local_path.parent)

            temp_fd, temp_path = tempfile.mkstemp(
                dir=local_path.parent,
                prefix=f'.{local_path.name}.',
                suffix='.tmp'
            )

            try:
                downloaded_size = 0
                with os.fdopen(temp_fd, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        downloaded_size += len(chunk)
                        if downloaded_size > self.MAX_IMAGE_SIZE:
                            raise Exception(f"Image exceeds maximum size of {self.MAX_IMAGE_SIZE} bytes")
                        f.write(chunk)

                os.replace(temp_path, local_path)

            except Exception as e:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
                raise e

            return DownloadResult(success=True, local_path=str(local_path), error=None)

        except requests.exceptions.HTTPError as e:
            return DownloadResult(success=False, local_path=None, error=f"HTTP {e.response.status_code}")
        except requests.exceptions.ConnectionError:
            return DownloadResult(success=False, local_path=None, error="Connection failed")
        except requests.exceptions.Timeout:
            return DownloadResult(success=False, local_path=None, error="Request timed out")
        except Exception as e:
            return DownloadResult(success=False, local_path=None, error=str(e))

    def _get_relative_path(self, from_dir: Path, to_file: Path) -> str:
        """Calculate relative path from markdown file to image."""
        try:
            return os.path.relpath(to_file, from_dir)
        except ValueError:
            return str(to_file)

    def _ensure_directory(self, path: Path):
        """Create directory if it doesn't exist."""
        path.mkdir(parents=True, exist_ok=True)

    def _write_atomic(self, filepath: Path, content: str):
        """Write file content atomically."""
        temp_fd, temp_path = tempfile.mkstemp(
            dir=filepath.parent,
            prefix=f'.{filepath.name}.',
            suffix='.tmp'
        )

        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(content)
            os.replace(temp_path, filepath)
        except Exception as e:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise e
