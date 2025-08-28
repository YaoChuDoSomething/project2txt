"""Tests for the txt2llm.utils module."""

import pytest
from pathlib import Path

from txt2llm import utils


@pytest.mark.parametrize(
    "file_name, expected_lang",
    [
        ("main.py", "python"),
        ("config.yaml", "yaml"),
        ("README.md", "markdown"),
        ("script.sh", "shell"),
        ("data.json", "json"),
        ("file.txt", "text"),
        ("unknown.xyz", ""),  # Unrecognized extension
        ("no_extension", ""),  # No extension
    ],
)
def test_get_markdown_lang(file_name: str, expected_lang: str):
    """Tests the get_markdown_lang function."""
    file_path = Path(file_name)
    assert utils.get_markdown_lang(file_path) == expected_lang


def test_is_binary_file_text(tmp_path: Path):
    """Tests is_binary_file with a text file."""
    text_file = tmp_path / "test.txt"
    text_file.write_text("This is a plain text file.")
    assert not utils.is_binary_file(text_file)


def test_is_binary_file_binary(tmp_path: Path):
    """Tests is_binary_file with a binary file (containing null bytes)."""
    binary_file = tmp_path / "test.bin"
    binary_file.write_bytes(b"\x00\xDE\xAD\xBE\xEF")
    assert utils.is_binary_file(binary_file)


def test_is_binary_file_empty(tmp_path: Path):
    """Tests is_binary_file with an empty file."""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")
    assert not utils.is_binary_file(empty_file)


def test_is_binary_file_non_existent():
    """Tests is_binary_file with a non-existent file."""
    non_existent_file = Path("non_existent_file.bin")
    assert not utils.is_binary_file(non_existent_file)
