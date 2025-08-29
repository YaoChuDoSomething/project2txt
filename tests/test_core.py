"Tests for the txt2llm.core module."

import pytest
from pathlib import Path

from txt2llm.config import ProjectConfig
from txt2llm.core import TextProjectBuilder


@pytest.fixture
def mock_project_root(tmp_path: Path) -> Path:
    """Creates a mock project directory structure for testing."""
    # Root directory
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "module_a").mkdir()
    (tmp_path / "src" / "module_b").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / ".git").mkdir()  # Ignored directory
    (tmp_path / "__pycache__").mkdir()  # Ignored directory
    (tmp_path / ".venv").mkdir()  # Ignored directory
    (tmp_path / "temp").mkdir()  # Not ignored by default
    (tmp_path / "output").mkdir() # Ignored by new config
    (tmp_path / "output" / "report.txt").write_text("report content") # File in ignored dir

    # Files
    (tmp_path / "README.md").write_text("Project README")
    (tmp_path / "src" / "main.py").write_text("print('Hello')")
    (tmp_path / "src" / "module_a" / "component.py").write_text("class Component: pass")
    (tmp_path / "src" / "module_b" / "helper.js").write_text("function helper() {}")
    (tmp_path / "docs" / "guide.md").write_text("User Guide")
    (tmp_path / "config.yaml").write_text("setting: value")
    (tmp_path / "test.txt").write_text("A simple text file")
    (tmp_path / "src" / "binary.bin").write_bytes(b"\x00\x01\x02")  # Binary file
    (tmp_path / ".git" / "config").write_text("[core]")  # File in ignored dir
    (tmp_path / "src" / "temp_file.log").write_text("log entry") # Not in include_exts

    return tmp_path


@pytest.fixture
def mock_config(mock_project_root: Path) -> ProjectConfig:
    """Creates a mock ProjectConfig for testing."""
    return ProjectConfig(
        project_root=mock_project_root,
        output_path=mock_project_root / "output.txt",
        ignored_dirs={'.git', '__pycache__', '.venv', 'output'},
        include_exts={'.py', '.md', '.js', '.yaml', '.txt'},
    )


def test_find_files(mock_config: ProjectConfig):
    """Tests the _find_files method."""
    builder = TextProjectBuilder(mock_config)
    found_files = builder._find_files()

    expected_files = sorted([
        Path("README.md"),
        Path("config.yaml"),
        Path("docs/guide.md"),
        Path("src/main.py"),
        Path("src/module_a/component.py"),
        Path("src/module_b/helper.js"),
        Path("test.txt"),
    ])

    assert len(found_files) == len(expected_files)
    assert all(f in found_files for f in expected_files)
    assert found_files == expected_files  # Check order


def test_generate_tree(mock_config: ProjectConfig):
    """Tests the _generate_tree method."""
    builder = TextProjectBuilder(mock_config)
    generated_tree = builder._generate_tree()

    # Golden answer for the mock project structure
    expected_tree = f"""{mock_config.project_root.name}/\n├── docs/\n│   └── guide.md\n├── src/\n│   ├── module_a/\n│   │   └── component.py\n│   ├── module_b/\n│   │   └── helper.js\n│   ├── binary.bin\n│   ├── main.py\n│   └── temp_file.log\n├── temp/\n├── config.yaml\n├── README.md\n└── test.txt"""

    # Normalize paths for comparison (replace mock_project_root.name with a placeholder)
    # The actual tree generation uses path.name, so this is fine.
    # The important part is the structure and file names.
    assert generated_tree == expected_tree


def test_read_file_content_text(mock_config: ProjectConfig):
    """Tests _read_file_content with a text file."""
    builder = TextProjectBuilder(mock_config)
    file_path = Path("README.md")
    content, warning = builder._read_file_content(file_path)
    assert content == "Project README"
    assert warning is None


def test_read_file_content_binary(mock_config: ProjectConfig):
    """Tests _read_file_content with a binary file."""
    builder = TextProjectBuilder(mock_config)
    file_path = Path("src/binary.bin")
    content, warning = builder._read_file_content(file_path)
    assert content == ""
    assert warning == "[SKIP] Binary file"


def test_read_file_content_non_existent(mock_config: ProjectConfig):
    """Tests _read_file_content with a non-existent file."""
    builder = TextProjectBuilder(mock_config)
    file_path = Path("non_existent.txt")
    content, warning = builder._read_file_content(file_path)
    assert content == ""
    assert "Could not read file" in warning

def test_generate_report(mock_config: ProjectConfig):
    """Tests the generate_report method (integration test)."""
    builder = TextProjectBuilder(mock_config)
    generated_report = builder.generate_report()

    # Manually construct the expected golden report based on mock_project_root and logic
    expected_report_parts = [
        f"# Project Overview: {mock_config.project_root.name}",
        "",
        "---",
        "",
        "## Configuration",
        f"- Project Root: `{mock_config.project_root}`",
        f"- Output Path: `{mock_config.output_path}`",
        f"- Ignored Directories: `.git, .venv, __pycache__, output`", # Sorted
        f"- Included Extensions: `.js, .md, .py, .txt, .yaml`", # Sorted
        "",
        "---",
        "",
        "## Directory Tree",
        "",
        "```",
        f"{mock_config.project_root.name}/",
        "├── docs/",
        "│   └── guide.md",
        "├── src/",
        "│   ├── module_a/",
        "│   │   └── component.py",
        "│   ├── module_b/",
        "│   │   └── helper.js",
        "│   ├── binary.bin",
        "│   ├── main.py",
        "│   └── temp_file.log",
        "├── temp/",
        "├── config.yaml",
        "├── README.md",
        "└── test.txt",
        "```",
        "",
        "## File Contents",
        "",
        "### `README.md`",
        "",
        "```markdown",
        "Project README",
        "```",
        "",
        "### `config.yaml`",
        "",
        "```yaml",
        "setting: value",
        "```",
        "",
        "### `docs/guide.md`",
        "",
        "```markdown",
        "User Guide",
        "```",
        "",
        "### `src/main.py`",
        "",
        "```python",
        "print('Hello')",
        "```",
        "",
        "### `src/module_a/component.py`",
        "",
        "```python",
        "class Component: pass",
        "```",
        "",
        "### `src/module_b/helper.js`",
        "",
        "```javascript",
        "function helper() {}",
        "```",
        "",
        "### `test.txt`",
        "",
        "```text",
        "A simple text file",
        "```",
        "",
    ]
    expected_report = "\n".join(expected_report_parts)

    assert generated_report == expected_report