"""Utilities module for the txt2llm project.

This module provides helper functions for file operations, such as
determining if a file is binary and getting the appropriate Markdown
language identifier for a given file extension.
"""

from pathlib import Path

_MARKDOWN_LANG_MAP = {
    ".py": "python",
    ".java": "java",
    ".js": "javascript",
    ".ts": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".md": "markdown",
    ".txt": "text",
    ".rst": "rst",
    ".sh": "shell",
    ".bat": "batch",
}


def get_markdown_lang(file_path: Path) -> str:
    """Gets the Markdown language identifier for a file.

    Args:
        file_path: The path to the file.

    Returns:
        The Markdown language identifier (e.g., 'python') or an empty
        string if the extension is not recognized.
    """
    return _MARKDOWN_LANG_MAP.get(file_path.suffix, "")


def is_binary_file(file_path: Path) -> bool:
    """Checks if a file is likely binary.

    This function reads the first few kilobytes of a file and checks for a
    significant number of null bytes, which is a common indicator of a
    binary file.

    Args:
        file_path: The path to the file.

    Returns:
        True if the file is likely binary, False otherwise.
    """
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(4096)  # Read first 4KB
        return b"\x00" in chunk
    except IOError:
        return False  # Could not read the file
