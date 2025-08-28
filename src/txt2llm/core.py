"""Core module for the txt2llm project.

This module contains the main logic for finding files, generating a directory
tree, reading file contents, and assembling the final report.
"""

import logging
from pathlib import Path

from .config import ProjectConfig
from . import utils


class TextProjectBuilder:
    """Builds a consolidated text representation of a project.

    This class orchestrates the process of scanning a project directory,
    filtering files, and generating a comprehensive text report.

    Attributes:
        config: The project configuration object.
    """

    def __init__(self, config: ProjectConfig):
        """Initializes the TextProjectBuilder with a project configuration.

        Args:
            config: A ProjectConfig object containing all necessary settings.
        """
        self.config = config

    def _find_files(self) -> list[Path]:
        """Finds and filters files based on the project configuration.

        This method recursively scans the project root directory and returns a
        sorted list of file paths that match the inclusion criteria and are

        Returns:
            A sorted list of Path objects, relative to the project root.
        """
        logging.info("Starting file search...")
        found_files = []
        for path in self.config.project_root.rglob("*"):
            if not path.is_file():
                continue

            # Check if any part of the path is in the ignored directories
            if any(
                part in self.config.ignored_dirs
                for part in path.relative_to(self.config.project_root).parts
            ):
                continue

            # Check if the file extension is in the inclusion list
            if path.suffix in self.config.include_exts:
                found_files.append(path)

        # Sort the files and make them relative to the project root
        sorted_files = sorted(
            [
                f.relative_to(self.config.project_root)
                for f in found_files
            ]
        )
        logging.info(f"Found {len(sorted_files)} matching files.")
        return sorted_files

    def _generate_tree(self) -> str:
        """Generates a string representation of the directory tree.

        This method walks the directory structure, ignoring specified
        directories, and builds a visual tree using prefix characters.

        Returns:
            A string representing the directory tree.
        """
        logging.info("Generating directory tree...")
        tree_lines = []

        def recurse_tree(directory: Path, prefix: str = ""):
            # Get directory contents, filter ignored, and sort
            try:
                contents = sorted(
                    [
                        p
                        for p in directory.iterdir()
                        if p.name not in self.config.ignored_dirs
                    ],
                    key=lambda p: (p.is_file(), p.name.lower()),
                )
            except OSError as e:
                logging.warning(f"Could not read directory {directory}: {e}")
                return

            pointers = ["├── "] * (len(contents) - 1) + ["└── "]
            for pointer, path in zip(pointers, contents):
                display_name = f"{path.name}/" if path.is_dir() else path.name
                tree_lines.append(f"{prefix}{pointer}{display_name}")
                if path.is_dir():
                    extension = "│   " if pointer == "├── " else "    "
                    recurse_tree(path, prefix=prefix + extension)

        tree_lines.append(f"{self.config.project_root.name}/")
        recurse_tree(self.config.project_root)
        tree_str = "\n".join(tree_lines)
        logging.info("Directory tree generation complete.")
        return tree_str

    def _read_file_content(
        self,
        file_path: Path
    ) -> tuple[str, str | None]:
        """Reads the content of a file.

        Args:
            file_path: The relative path of the file to read.

        Returns:
            A tuple containing the file content as a string and an
            optional warning message (e.g., for binary files).
        """
        full_path = self.config.project_root / file_path
        if utils.is_binary_file(full_path):
            return "", "[SKIP] Binary file"

        try:
            with open(
                full_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:
                return f.read(), None
        except IOError as e:
            logging.warning(f"Could not read file {full_path}: {e}")
            return "", f"[SKIP] Could not read file: {e}"

    def _build_header(self) -> str:
        """Builds the header section of the report.

        Returns:
            A string containing the formatted report header.
        """
        header_lines = [
            f"# Project Overview: {self.config.project_root.name}",
            "",
            "---",
            "",
            "## Configuration",
            f"- Project Root: `{self.config.project_root}`",
            f"- Output Path: `{self.config.output_path}`",
            f"- Ignored Directories: `{', '.join(sorted(list(self.config.ignored_dirs)))}`",
            f"- Included Extensions: `{', '.join(sorted(list(self.config.include_exts)))}`",
            "",
            "---",
            "",
        ]
        return "\n".join(header_lines)

    def generate_report(self) -> str:
        """Generates the full project overview report.

        This method orchestrates the collection of project information,
        including the directory tree, file list, and file contents, into
        a single Markdown-formatted string.

        Returns:
            A string containing the complete project overview report.
        """
        logging.info("Starting report generation...")
        report_parts = []

        # 1. Add Header
        report_parts.append(self._build_header())

        # 2. Add Directory Tree
        report_parts.append("## Directory Tree")
        report_parts.append("")
        report_parts.append("```")
        report_parts.append(self._generate_tree())
        report_parts.append("```")
        report_parts.append("")

        # 3. Add File Contents
        report_parts.append("## File Contents")
        report_parts.append("")
        found_files = self._find_files()
        if not found_files:
            report_parts.append("No files found matching the criteria.")
        else:
            for file_path in found_files:
                report_parts.append(f"### `{file_path}`")
                report_parts.append("")
                content, warning = self._read_file_content(file_path)
                if warning:
                    report_parts.append(f"```text\n{warning}\n```")
                else:
                    lang = utils.get_markdown_lang(file_path)
                    report_parts.append(f"```{lang}")
                    report_parts.append(content)
                    report_parts.append("```")
                report_parts.append("") # Add an extra newline for separation

        final_report = "\n".join(report_parts)
        logging.info("Report generation complete.")
        return final_report
