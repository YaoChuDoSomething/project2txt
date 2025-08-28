"""Main module for the txt2llm command-line interface.

This module parses command-line arguments, sets up the project
configuration, and orchestrates the process of generating the project
overview report.
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from .config import ProjectConfig
from .core import TextProjectBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)


def main():
    """Parses CLI arguments and generates the project report."""
    parser = argparse.ArgumentParser(
        description="""
A developer utility that consolidates an entire project's text-based
files into a single output file, optimized for context-rich interactions
with Large Language Models (LLMs).
"""
    )
    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="The path to the project directory.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="""
The path for the output file. If not provided, a default name is
generated in the project's parent directory.
""",
    )
    args = parser.parse_args()

    project_path = args.path.resolve()
    if not project_path.is_dir():
        logging.error(f"Error: Path '{project_path}' is not a valid directory.")
        sys.exit(1)
    else:
        logging.info(f"Starting project overview generation for: {project_path}")
        # Only proceed with output path and config if project_path is valid
        if args.output:
            output_path = args.output.resolve()
        else:
            # Determine the txt2llm project root (e.g., /wk2/yaochu/DLAMP_model/txt2llm/)
            # main.py is in src/txt2llm/, so go up three levels from main.py's location
            txt2llm_project_root = Path(__file__).resolve().parents[3]

            # Construct the output directory: <txt2llm_project_root>/output/<target_project_name>/
            target_project_name = project_path.name
            output_dir = txt2llm_project_root / "output" / target_project_name
            output_dir.mkdir(parents=True, exist_ok=True)  # Create directories if they don't exist

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{target_project_name}_overview_{timestamp}.txt"
            output_path = output_dir / output_filename

        # Default configuration values from the roadmap
        ignored_dirs = {".git", "__pycache__", ".venv"}
        include_exts = {
            # Code
            ".py", ".java", ".js", ".ts", ".go", ".rs", ".c", ".h", ".cpp",
            # Config
            ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg",
            # Docs
            ".md", ".txt", ".rst",
            # Shell/Scripts
            ".sh", ".bat",
        }

        config = ProjectConfig(
            project_root=project_path,
            output_path=output_path,
            ignored_dirs=ignored_dirs,
            include_exts=include_exts,
        )

        logging.info(f"Project path: {config.project_root}")
        logging.info(f"Output file: {config.output_path}")
        logging.info(f"Ignored directories: {config.ignored_dirs}")
        logging.info(f"Included extensions: {config.include_exts}")

        builder = TextProjectBuilder(config)
        
        try:
            report_content = builder.generate_report()
            output_path.write_text(report_content, encoding="utf-8")
            logging.info(f"Project overview report successfully generated at: {output_path}")
        except Exception as e:
            logging.error(f"An error occurred during report generation: {e}")
            sys.exit(1)
        finally:
            logging.info("Project overview generation finished.")


if __name__ == "__main__":
    main()
