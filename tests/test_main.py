"""Tests for the txt2llm.main module."""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from txt2llm.main import main
from txt2llm.config import ProjectConfig
from txt2llm.core import TextProjectBuilder

@pytest.fixture
def mock_project_root(tmp_path: Path) -> Path:
    """Creates a mock project directory for testing."""
    (tmp_path / "my_test_project").mkdir()
    (tmp_path / "my_test_project" / "file.txt").write_text("content")
    return tmp_path / "my_test_project"

@pytest.fixture
def mock_datetime_now():
    """Mocks datetime.now() to return a fixed datetime and its strftime method."""
    with patch("txt2llm.main.datetime") as mock_dt:
        mock_now_return_value = MagicMock(spec=datetime)
        mock_now_return_value.strftime.return_value = "20230101_103000"
        mock_dt.now.return_value = mock_now_return_value
        yield

@pytest.fixture
def mock_sys_exit():
    """Mocks sys.exit to prevent actual exit during tests."""
    with patch("sys.exit") as mock_exit:
        yield mock_exit

@pytest.fixture
def mock_text_project_builder():
    """Mocks TextProjectBuilder and its generate_report method."""
    with patch("txt2llm.main.TextProjectBuilder") as MockBuilder:
        mock_instance = MockBuilder.return_value
        mock_instance.generate_report.return_value = "Mock Report Content"
        yield MockBuilder

@pytest.fixture
def mock_project_config():
    """Mocks ProjectConfig to capture arguments and mock its instance."""
    with patch("txt2llm.main.ProjectConfig") as MockConfig:
        yield MockConfig

@pytest.fixture
def mock_path_mkdir():
    """Mocks Path.mkdir to prevent actual directory creation."""
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        yield mock_mkdir

@pytest.fixture
def mock_path_write_text():
    """Mocks Path.write_text to capture content and prevent actual file writing."""
    with patch("pathlib.Path.write_text") as mock_write:
        yield mock_write

def test_default_output_path_generation(
    mock_project_root: Path,
    mock_datetime_now,
    mock_sys_exit,
    mock_text_project_builder,
    mock_project_config,
    mock_path_mkdir,
    mock_path_write_text,
):
    """
    Tests that the default output path is correctly generated
    when --output is not provided.
    """
    test_args = ["--path", str(mock_project_root)]
    with patch.object(sys, "argv", ["main.py"] + test_args):
        with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
            mock_args = MagicMock()
            mock_args.path = mock_project_root
            mock_args.output = None
            mock_parse_args.return_value = mock_args

            main()

            # Determine the txt2llm project root based on the test file's location.
            current_file_path = Path(__file__).resolve()
            # tests/ -> txt2llm/ (project root)
            txt2llm_project_root = current_file_path.parents[2]

            target_project_name = mock_project_root.name # "my_test_project"
            expected_output_dir = txt2llm_project_root / "output" / target_project_name
            expected_output_filename = f"{target_project_name}_overview_20230101_103000.txt"
            expected_output_path = expected_output_dir / expected_output_filename

            # Verify ProjectConfig was called with the correct output_path
            mock_project_config.assert_called_once()
            config_call_args = mock_project_config.call_args[1]
            assert config_call_args["output_path"] == expected_output_path

            # Verify mkdir was called for the output directory
            mock_path_mkdir.assert_called_once_with(parents=True, exist_ok=True)

            # Verify TextProjectBuilder was instantiated and generate_report called
            mock_text_project_builder.assert_called_once_with(mock_project_config.return_value)
            mock_text_project_builder.return_value.generate_report.assert_called_once()

            # Verify write_text was called with the correct path and content
            mock_path_write_text.assert_called_once_with(
                "Mock Report Content", encoding="utf-8"
            )
            

def test_explicit_output_path(
    mock_project_root: Path,
    mock_sys_exit,
    mock_text_project_builder,
    mock_project_config,
    mock_path_mkdir,
    mock_path_write_text,
):
    """
    Tests that the explicit output path is used when --output is provided.
    """
    explicit_output = mock_project_root.parent / "custom_report.txt"
    test_args = ["--path", str(mock_project_root), "--output", str(explicit_output)]
    with patch.object(sys, "argv", ["main.py"] + test_args):
        with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
            mock_args = MagicMock()
            mock_args.path = mock_project_root
            mock_args.output = explicit_output
            mock_parse_args.return_value = mock_args

            main()

            # Verify ProjectConfig was called with the explicit output_path
            mock_project_config.assert_called_once()
            config_call_args = mock_project_config.call_args[1]
            assert config_call_args["output_path"] == explicit_output

            # Verify mkdir was NOT called for the default output path
            mock_path_mkdir.assert_not_called()

            # Verify TextProjectBuilder was instantiated and generate_report called
            mock_text_project_builder.assert_called_once_with(mock_project_config.return_value)
            mock_text_project_builder.return_value.generate_report.assert_called_once()

            # Verify write_text was called with the correct path and content
            mock_path_write_text.assert_called_once_with(
                "Mock Report Content", encoding="utf-8"
            )
            

def test_invalid_project_path(
    tmp_path: Path,
    mock_sys_exit,
):
    """Tests that main exits if the provided project path is not a directory."""
    invalid_path = tmp_path / "non_existent_dir"
    test_args = ["--path", str(invalid_path)]
    with patch.object(sys, "argv", ["main.py"] + test_args):
        with patch("argparse.ArgumentParser.parse_args") as mock_parse_args, patch("txt2llm.main.ProjectConfig") as MockProjectConfig, patch("txt2llm.main.TextProjectBuilder") as MockTextProjectBuilder, patch("pathlib.Path.mkdir") as mock_mkdir, patch("pathlib.Path.write_text") as mock_write_text:

            mock_args = MagicMock()
            mock_args.path = invalid_path
            mock_args.output = None
            mock_parse_args.return_value = mock_args

            main()
            mock_sys_exit.assert_called_once_with(1)

            # Verify that ProjectConfig, TextProjectBuilder, mkdir, and write_text were NOT called
            MockProjectConfig.assert_not_called()
            MockTextProjectBuilder.assert_not_called()
            mock_mkdir.assert_not_called()
            mock_write_text.assert_not_called()
