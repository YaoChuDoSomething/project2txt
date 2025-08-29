# ROADMAP.md

## Current Status

- **步驟 1: 專案初始化** (Project Initialization): **完成**
  - `pyproject.toml` 已設定。
  - `src/txt2llm/` 和 `tests/` 的基本檔案結構已建立。
- **步驟 2: 命令列介面 (CLI)**: **完成**
  - `main.py` 已包含 `argparse` 設置、參數解析、預設輸出檔名生成和初步的配置日誌。
- **步驟 3: 檔案探索器 (`_find_files`)**: **完成**
  - `_find_files` 方法已在 `core.py` 中實現並通過測試。
- **步驟 4: 目錄樹產生器 (`_generate_tree`)**: **完成**
  - `_generate_tree` 方法已在 `core.py` 中實現並通過測試。
- **步驟 5: 檔案內容處理 (`_read_file_content` & `utils.py`)**: **完成**
  - `_read_file_content` 方法已在 `core.py` 中實現。
  - `is_binary_file` 和 `get_markdown_lang` 函式已在 `utils.py` 中實現並通過測試。
- **步驟 6: 整合與報告生成 (`generate_report`)**: **完成**
  - `generate_report` 方法已在 `core.py` 中實現並通過整合測試。

## Enhancements

- **任務 1: 優化預設輸出路徑** (Refine Default Output Path): **完成**
  - **目標**: 變更預設輸出行為。當使用者未指定 `--output` 時，報告應生成於 `txt2llm` 專案根目錄下的 `output/<target_project_name>/` 資料夾內。
  - **理由**: 避免在使用者當前工作目錄產生雜亂檔案，集中管理所有生成的報告。
  - **影響範圍**: `src/txt2llm/main.py`, `tests/test_main.py` (新增)。


---

好的，這是一份將 `txt2llm.sh` Bash 腳本轉換為 Python 專案的詳細分析與開發計畫。

### 1. Bash 腳本解讀與功能拆解

這個 Bash 腳本的核心目標是「專案概覽」，它掃描指定的專案目錄，並將目錄結構、指定類型的檔案清單以及這些檔案的內容，全部匯出到一個純文字檔案中，方便使用者快速理解整個專案的樣貌。

腳本的主要功能可以拆解如下：

| 元件/物件 | 功能描述 | 對應的 Bash 程式碼 |
| :--- | :--- | :--- |
| **CLI 介面 (Argument Parser)** | - 解析 `--path` (專案路徑，必要) 和 `--output` (輸出檔案，可選) 參數。<br>- 提供 `-h`/`--help` 說明。 | `while [[ $# -gt 0 ]]` 迴圈 |
| **組態設定 (Configuration)** | - 定義要忽略的目錄 (`.git`, `__pycache__`, `.venv`)。<br>- 定義要包含的檔案副檔名 (`.py`, `.yaml`, etc.)。 | 硬編碼在 `find` 指令與註解中 |
| **路徑管理器 (Path Manager)** | - 將輸入路徑轉換為絕對路徑。<br>- 如果未提供輸出路徑，則動態生成一個（包含專案名稱和時間戳）。<br>- 計算檔案的相對路徑。 | `to_abs`, `relpath` 函式, `OUTPUT` 變數的動態生成 |
| **檔案探索器 (File Finder)** | - 遍歷專案目錄，根據組態過濾檔案（忽略特定目錄、篩選副檔名）。<br>- 產出一個排序過的檔案路徑清單。 | `find` 指令搭配 `-prune`, `mapfile`, `rel_sorted` 陣列的處理 |
| **內容產生器 (Content Generators)** | - **目錄樹產生器**: 生成專案的目錄結構樹狀圖。優先使用 `tree` 指令，若不存在則用 `find/awk` 替代。<br>- **檔案內容讀取器**: 讀取單一檔案內容。它會偵測檔案是否為文字檔，並嘗試將其轉為 UTF-8 編碼。 | `print_tree`, `is_text_file`, `detect_encoding`, `cat_as_utf8` |
| **報告產生器 (Report Generator)** | - 彙整所有內容，組合成最終的報告。<br>- 報告包含：標頭資訊、目錄樹、檔案清單、各檔案內容。<br>- 為檔案內容加上 Markdown 的程式碼區塊 (fenced code blocks)，並標示語言。 | 主體的 `echo` 區塊，以及 `lang_for_ext` 函式 |
| **系統工具檢查器 (Tool Checker)** | - 檢查系統指令是否存在 (`tree`, `file`, `iconv`, `realpath`)，並提供備援方案。 | `have_cmd` 函式 |

---

### 2. Python 專案架構設計

我們將採用物件導向的設計，將核心邏輯封裝在一個類別中，並讓 CLI 介面與核心邏輯分離。

#### 建議的類別/方法設計

| 類別/模組 | 方法/屬性 | 職責 | 注意事項 |
| :--- | :--- | :--- | :--- |
| **`txt2llm/config.py`** | `ProjectConfig` (dataclass) | - `ignored_dirs: set[str]`<br>- `include_exts: set[str]`<br>- `project_root: Path`<br>- `output_path: Path` | 使用 `pathlib.Path` 處理路徑。設定應為不可變物件，適合用 `dataclasses.dataclass(frozen=True)`。 |
| **`txt2llm/core.py`** | `TextProjectBuilder` (class) | 負責執行整個專案概覽的流程。 | |
| | `__init__(self, config: ProjectConfig)` | 初始化，接收組態物件。 | 依賴注入 (Dependency Injection)，方便測試。 |
| | `_find_files(self) -> list[Path]` | 找出所有符合條件的檔案，回傳排序過的**相對路徑**列表。 | 使用 `pathlib.Path.rglob` 搭配篩選邏輯，比 `os.walk` 更現代化。 |
| | `_generate_tree(self) -> str` | 產生目錄樹字串。 | 這是轉換的難點。需自行實作 `os.walk` 或 `pathlib` 遍歷，並手動產生縮排與前綴。不建議依賴外部 `tree` 指令。 |
| | `_read_file_content(self, file_path: Path) -> tuple[str, str | None]` | 讀取檔案內容。回傳 `(內容, 警告訊息)`。例如，若為二進位檔，內容為空，警告訊息為 `"[SKIP] Binary file"`。 | - 用 `try-except UnicodeDecodeError` 判斷是否為文字檔。<br>- 使用 `open(..., encoding='utf-8', errors='ignore')` 確保穩定性。 |
| | `generate_report(self) -> str` | 組合所有元件（標頭、樹、檔案清單、內容）成最終報告字串。 | 將報告的各個區塊生成邏輯拆分成小的 private a 方法，如 `_build_header()`。 |
| **`txt2llm/utils.py`** | `get_markdown_lang(file_path: Path) -> str` | 根據副檔名回傳 Markdown 語言標籤。 | 純函式，容易單元測試。可以設計成一個 `dict` mapping。 |
| | `is_binary_file(file_path: Path) -> bool` | 判斷是否為二進位檔案。 | 實作細節：可以讀取檔案開頭數 KB，檢查是否包含大量 NULL 字元 (`\x00`) 或非 ASCII 字元。 |
| **`txt2llm/main.py`** (或 `cli.py`) | `main()` | - 使用 `argparse` 解析命令列參數。<br>- 建立 `ProjectConfig` 物件。<br>- 實例化 `TextProjectBuilder` 並呼叫 `generate_report`。<br>- 將報告寫入檔案或印到 stdout。 | CLI 邏輯與核心商業邏輯分離。使用 `logging` 模組取代 `print` 來顯示進度或錯誤訊息。 |

---

### 3. 開發詳細步驟與檢核方式

#### 步驟 1: 專案初始化
1.  **建立專案結構**:
    ```
    txt2llm/
    ├── pyproject.toml
    ├── src/
    │   └── txt2llm/
    │       ├── __init__.py
    │       ├── config.py
    │       ├── core.py
    │       ├── main.py
    │       └── utils.py
    └── tests/
        ├── __init__.py
        ├── test_core.py
        └── test_utils.py
    ```
2.  **設定 `pyproject.toml`**: 使用 uv 等現代化工具來管理依賴與專案設定。
3.  **檢核方式**: 能夠成功建立虛擬環境並安裝 `pytest`。

#### 步驟 2: 命令列介面 (CLI)
1.  **開發 `main.py`**: 使用 `argparse` 模組建立 CLI。定義 `--path` 和 `--output` 參數。
2.  **邏輯**: `main` 函式應能解析參數，處理預設輸出檔名（包含時間戳），並印出解析後的設定。
3.  **檢核/測試**:
    - 手動執行 `python -m txt2llm.main --path . --help` 應顯示說明。
    - 執行 `python -m txt2llm.main --path /some/path` 能正確印出解析的路徑。

#### 步驟 3: 檔案探索器 (`_find_files`)
1.  **開發 `core.py`**: 在 `TextProjectBuilder` 中實作 `_find_files` 方法。
2.  **邏輯**:
    - 使用 `self.config.project_root.rglob('*')` 遍歷所有檔案。
    - 過濾掉在 `self.config.ignored_dirs` 中的路徑。
    - 過濾掉不符合 `self.config.include_exts` 的檔案。
    - 將結果（相對路徑）排序後回傳。
3.  **檢核/測試 (`tests/test_core.py`)**:
    - 建立一個假的專案目錄結構（使用 `py.path.local` 或 `pathlib`）。
    - 結構應包含：`.py` 檔、`.txt` 檔、其他副檔名檔案、一個 `.git` 目錄、一個 `__pycache__` 目錄。
    - **測試腳本**: 斷言 `_find_files` 的回傳列表：
        - (a) 包含了所有應包含的檔案。
        - (b) 不包含被忽略目錄下的任何檔案。
        - (c) 不包含副檔名不符的檔案。
        - (d) 回傳的路徑是相對於專案根目錄的。
        - (e) 列表是排序過的。

#### 步驟 4: 目錄樹產生器 (`_generate_tree`)
1.  **開發 `core.py`**: 實作 `_generate_tree` 方法。這是最複雜的純演算法部分。
2.  **邏輯**:
    - 使用 `os.walk` 或遞迴函式來遍歷目錄。
    - 對每一層的目錄和檔案進行排序，確保輸出順序穩定。
    - 根據目錄深度計算並產生前綴字串 (e.g., `│   `, `├── `, `└── `)。
3.  **檢核/測試 (`tests/test_core.py`)**:
    - 使用與上一步相同的假專案結構。
    - **測試腳本**:
        - 斷言 `_generate_tree` 產生的字串與一個預先寫好的「標準答案」字串完全相符。這稱為**黃金測試 (Golden Testing)**。

#### 步驟 5: 檔案內容處理 (`_read_file_content` & `utils.py`)
1.  **開發 `utils.py`**: 實作 `is_binary_file` 和 `get_markdown_lang`。
2.  **開發 `core.py`**: 實作 `_read_file_content`。呼叫 `utils` 中的輔助函式。
3.  **檢核/測試 (`tests/test_utils.py` and `tests/test_core.py`)**:
    - **測試腳本 (`test_utils.py`)**:
        - 對 `get_markdown_lang`：提供不同檔名，斷言其回傳正確的語言標籤 (e.g., `main.py` -> `python`)。
        - 對 `is_binary_file`：建立一個臨時的純文字檔和一個二進位檔（例如 `b'\x00\xDE\xAD\xBE\xEF'`），斷言函式回傳 `False` 和 `True`。
    - **測試腳本 (`test_core.py`)**:
        - 測試 `_read_file_content` 讀取文字檔時，回傳正確的內容和 `None` 警告。
        - 測試讀取二進位檔時，回傳空字串和對應的警告訊息。

#### 步驟 6: 整合與報告生成 (`generate_report`)
1.  **開發 `core.py`**: 實作 `generate_report`。
2.  **邏輯**:
    - 依序呼叫 `_build_header`, `_generate_tree`, `_find_files` 等方法。
    - 迴圈處理檔案列表，對每個檔案呼叫 `_read_file_content`。
    - 使用 f-string 或樣板引擎將所有部分組合成一個巨大的字串。
3.  **檢核/測試 (`tests/test_core.py`)**:
    - 這是**整合測試**。
    - **測試腳本**:
        - 針對測試用的假專案結構，呼叫 `generate_report`。
        - 將產出的完整報告字串與一個預先準備好的「黃金標準報告.txt」進行比對，斷言兩者完全相同。

#### 步驟 7: 完成 `main.py` 與收尾
1.  **開發 `main.py`**: 將 CLI 解析的參數傳遞給 `TextProjectBuilder`，呼叫 `generate_report`，並將結果寫入檔案。
2.  **加入日誌**: 使用 `logging` 模組在開始和結束時輸出資訊性訊息（"正在分析專案..."、"報告已生成於..."）。
3.  **手動測試**: 找一個真實的小型專案，執行打包好的 CLI 工具，檢查輸出是否符合預期。
4.  **文件**: 撰寫 `README.md`，說明如何安裝與使用。

這個計畫將 Bash 腳本的邏輯分解為獨立、可測試的 Python 元件，確保了程式碼的品質、可維護性和擴展性。每個步驟都有明確的產出和驗證方法，有助於順利完成轉換工作。

## Known Issues

- **Issue 1: Incorrect Default Output Directory**
  - **Description**: The current default output directory is `../output/`, which is relative to the execution location. It should be an absolute path within the project, specifically `/wk2/yaochu/DLAMP_model/txt2llm/output/`.
  - **Impact**: Inconsistent output location, potential for files to be created outside the project directory.
  - **Affected Files**: `src/txt2llm/main.py`, `src/txt2llm/config.py` (if output path is configured there), `tests/test_main.py`.

- **Issue 2: Project Overview Output Directory Not Skipped**
  - **Description**: The directory used for storing project overview reports (e.g., `output/txt2llm/`) is currently scanned or processed by the tool itself, leading to self-referential issues or unnecessary processing.
  - **Impact**: Inefficient processing, potential for infinite loops or incorrect report generation if the tool tries to process its own output.
  - **Affected Files**: `src/txt2llm/core.py` (`_find_files` method), `src/txt2llm/config.py` (for ignore patterns), `tests/test_core.py`.