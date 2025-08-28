"""Configuration module for the txt2llm project.

This module defines the configuration settings for the project, including
paths, ignored directories, and included file extensions.
"""

import dataclasses
from pathlib import Path


@dataclasses.dataclass(frozen=True)
class ProjectConfig:
    """Stores project configuration settings.

    Attributes:
        project_root: The absolute path to the project's root directory.
        output_path: The absolute path for the output file.
        ignored_dirs: A set of directory names to ignore during file search.
        include_exts: A set of file extensions to include during file search.
    """
    project_root: Path
    output_path: Path
    ignored_dirs: set[str]
    include_exts: set[str]
