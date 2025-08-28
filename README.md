# txt2llm: Project to LLM Context Generator

Package your entire codebase into a single, LLM-friendly file. This tool scans a project directory and aggregates all source code, configuration, and text files into one comprehensive context file, streamlining the process of prompting Large Language Models.

## Purpose

`txt2llm` is designed to simplify feeding entire software projects into Large Language Models. It recursively scans a specified project directory, gathering all relevant text files (such as source code, markdown, and configuration files) and consolidates their contents into a single, well-structured text file. This eliminates the need to upload numerous files individually, providing the LLM with a complete and holistic view of the project's architecture and logic.

## Features

-   **Recursive Project Scanning**: Automatically discovers files within a given project directory.
-   **Configurable File Inclusion/Exclusion**: Ignores common development artifacts (`.git`, `__pycache__`, `.venv`) and focuses on specified file types.
-   **Structured Output**: Generates a report that includes:
    -   Project overview header.
    -   A clear directory tree.
    -   A list of included files.
    -   The content of each included file, formatted with Markdown fenced code blocks and language highlighting.
-   **Flexible Output Path**: Allows users to specify an output file or uses a sensible default.

## Installation

### Prerequisites

-   Python 3.11+
-   `uv` (recommended for dependency management) or `pip`

### Steps

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-repo/txt2llm.git
    cd txt2llm
    ```

2.  **Set up a virtual environment and install dependencies**:

    **Using `uv` (recommended):**
    ```bash
    uv python install ">3.10, <=3.11"
    uv python pin ">3.10, <=3.11"
    uv venv
    source .venv/bin/activate # On Windows: .venv\Scripts\activate
    uv pip install -e .
    ```

    **Using `pip`:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate # On Windows: .venv\Scripts\activate
    pip install -e .
    ```

## Usage

The `txt2llm` tool is executed via the command line.

```bash
python -m txt2llm.main --path <PROJECT_DIRECTORY> [--output <OUTPUT_FILE_PATH>]
```

### Arguments

-   `--path <PROJECT_DIRECTORY>` (Required): The absolute or relative path to the project directory you want to analyze.
-   `--output <OUTPUT_FILE_PATH>` (Optional): The absolute or relative path where the generated report file will be saved.

### Output Behavior

-   **Default Output Path**: If `--output` is not specified, the report will be generated in a structured directory within the `txt2llm` project's root:
    `txt2llm_project_root/output/<target_project_name>/<target_project_name>_overview_<timestamp>.txt`
-   **Explicit Output Path**: If `--output` is provided, the report will be saved to the specified path.

### Examples

1.  **Generate a report for the current directory with default output:**
    ```bash
    python -m txt2llm.main --path .
    ```
    (The report will be saved in `txt2llm/output/current_directory_name/current_directory_name_overview_YYYYMMDD_HHMMSS.txt`)

2.  **Generate a report for a specific project and save it to a custom location:**
    ```bash
    python -m txt2llm.main --path /path/to/my/awesome_project --output /tmp/awesome_project_report.txt
    ```

3.  **Generate a report for a project relative to the current working directory:**
    ```bash
    python -m txt2llm.main --path ../another_project
    ```

### Configuration (Default)

The tool is configured to ignore common development directories and include a broad set of text-based file extensions by default.

**Ignored Directories**:
-   `.git`
-   `__pycache__`
-   `.venv`

**Included Extensions**:
-   **Code**: `.py`, `.java`, `.js`, `.ts`, `.go`, `.rs`, `.c`, `.h`, `.cpp`
-   **Config**: `.yaml`, `.yml`, `.json`, `.toml`, `.ini`, `.cfg`
-   **Docs**: `.md`, `.txt`, `.rst`
-   **Shell/Scripts**: `.sh`, `.bat`

## Logging

The tool provides informative logging messages to `stdout` indicating the progress, configuration details, and any errors encountered during the report generation process.

---