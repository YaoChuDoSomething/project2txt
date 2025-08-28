#!/usr/bin/env bash
# pyproject2txt.sh
# 概覽專案，輸出目錄樹 + 指定副檔名檔案清單 + 各檔案內容到單一文字檔
# 用法：
#   bash pyproject2txt.sh --path /path/to/project [--output /path/to/output.txt]
# 需求：
#   - 可選：tree、iconv、file、realpath（若無會有 fallback）
#   - 會忽略目錄：.git、__pycache__、.venv
set -Eeuo pipefail

# -------- Args parsing --------
PROJ=""
OUTPUT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --path)
      PROJ="${2:-}"; shift 2 ;;
    --output)
      OUTPUT="${2:-}"; shift 2 ;;
    -h|--help)
      echo "Usage: bash $0 --path <PROJECT_ROOT> [--output <OUTPUT_TXT>]"
      exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "${PROJ}" ]]; then
  echo "Error: --path is required." >&2
  exit 1
fi

# 允許相對路徑；轉為絕對
to_abs() {
  local p="$1"
  if [[ -d "$p" ]]; then
    (cd "$p" && pwd)
  else
    local dir
    dir="$(cd "$(dirname "$p")" && pwd)"
    echo "$dir/$(basename "$p")"
  fi
}
PROJ="$(to_abs "$PROJ")"
if [[ ! -d "$PROJ" ]]; then
  echo "Error: path not found or not a directory: $PROJ" >&2
  exit 1
fi

# 動態輸出檔名
ts="$(date +"%Y%m%d-%H%M%S")"
proj_base="$(basename "$PROJ")"
if [[ -z "${OUTPUT}" ]]; then
  OUTPUT="$(pwd)/${proj_base}_overview_${ts}.txt"
fi

# -------- Helpers --------
have_cmd() { command -v "$1" >/dev/null 2>&1; }

# 相對路徑（realpath 不在時用 python3；再不行做最簡 fallback）
relpath() {
  local base="$1" target="$2"
  if have_cmd realpath; then
    realpath --relative-to="$base" "$target"
  elif have_cmd python3; then
    python3 - "$base" "$target" <<'PY'
import os,sys
print(os.path.relpath(sys.argv[2], sys.argv[1]))
PY
  else
    # 最簡 fallback（可能不處理符號連結/大小寫差異）
    local prefix="${base%/}/"
    printf '%s\n' "${target#${prefix}}"
  fi
}

# 目錄樹輸出（有 tree 用 tree；否則用 find/awk fallback）
print_tree() {
  local root="$1"
  if have_cmd tree; then
    # -a 顯示隱藏檔、 -I 忽略模式、--noreport 不印統計
    tree -a --noreport -I '.git|__pycache__|.venv' "$root"
  else
    # fallback：以「縮排 + - name」呈現層級
    # 1) 列出所有檔案/目錄且排除忽略資料夾
    # 2) 轉成相對於 root 的路徑
    # 3) 依路徑深度縮排
    find "$root" \( -name ".git" -o -name "__pycache__" -o -name ".venv" \) -prune -o -print \
    | sed -e "s|^$root|.|" \
    | LC_ALL=C sort \
    | awk -F'/' '
      BEGIN{print "."}
      NR>1{
        depth=NF-1
        indent=""
        for(i=1;i<depth;i++) indent=indent"  "
        print indent"- "$NF
      }'
  fi
}

is_text_file() {
  local f="$1"
  if command -v file >/dev/null 2>&1; then
    file -b --mime-type "$f" | grep -q '^text/' && return 0
  fi
  grep -Iq . "$f" 2>/dev/null && return 0
  return 1
}

detect_encoding() {
  command -v file >/dev/null 2>&1 && file -b --mime-encoding "$1" || echo "utf-8"
}

cat_as_utf8() {
  local f="$1" enc
  enc="$(detect_encoding "$f")"
  case "$enc" in
    utf-8|us-ascii) cat "$f" ;;
    *)
      if command -v iconv >/dev/null 2>&1; then
        iconv -f "$enc" -t utf-8 "$f" 2>/dev/null || cat "$f"
      else
        cat "$f"
      fi
      ;;
  esac
}

lang_for_ext() {
  # 讓內容區塊用對應語言的 Markdown fenced code
  local f="$1"
  case "${f##*.}" in
    py)   echo "python" ;;
    yaml) echo "yaml" ;;
    yml)  echo "yaml" ;;
    md)   echo "markdown" ;;
    toml) echo "toml" ;;
    txt)  echo "text" ;;
    *)    echo "" ;;
  esac
}

# -------- 準備檔案清單（符合副檔名、排序、相對路徑） --------
# 使用 find 搭配 prune 忽略目錄
mapfile -d '' FILES < <(
  find "$PROJ" \
    \( -name ".git" -o -name "__pycache__" -o -name ".venv" \) -prune -o \
    -type f \
    \( -iname "*.py" -o -iname "*.yaml" -o -iname "*.yml" -o -iname "*.md" -o -iname "*.txt" -o -iname "*.toml" \) \
    -print0
)

# 轉相對路徑並排序
rel_list=()
for f in "${FILES[@]:-}"; do
  [[ -z "$f" ]] && continue
  rel_list+=( "$(relpath "$PROJ" "$f")" )
done
# 排序
IFS=$'\n' read -r -d '' -a rel_sorted < <(printf "%s\n" "${rel_list[@]:-}" | LC_ALL=C sort -u && printf '\0')

# -------- 輸出 --------
{
  echo "# Project Overview"
  echo "- Project path : $PROJ"
  echo "- Project name : $proj_base"
  echo "- Generated at : $(date -Iseconds)"
  echo "- Output file  : $OUTPUT"
  echo "- Ignore dirs  : .git, __pycache__, .venv"
  echo "- File filter  : *.py, *.yaml, *.yml, *.md, *.txt, *.toml"
  echo

  echo "## 1) Directory Tree"
  echo '```text'
  print_tree "$PROJ"
  echo '```'
  echo

  echo "## 2) Selected Files (relative paths, sorted)"
  echo "(count: ${#rel_sorted[@]})"
  echo '```text'
  for rp in "${rel_sorted[@]:-}"; do
    echo "$rp"
  done
  echo '```'
  echo

  echo "## 3) File Contents (UTF-8; skip binaries)"
  for rp in "${rel_sorted[@]:-}"; do
    abs="$PROJ/$rp"
    if [[ ! -f "$abs" ]]; then
      echo
      echo "===== BEGIN FILE: $rp ====="
      echo "[WARN] File not found at generation time."
      echo "===== END FILE: $rp ====="
      continue
    fi
    if ! is_text_file "$abs"; then
      echo
      echo "===== BEGIN FILE: $rp ====="
      echo "[SKIP] Binary or non-text file detected."
      echo "===== END FILE: $rp ====="
      continue
    fi
    lang="$(lang_for_ext "$abs")"
    echo
    echo "===== BEGIN FILE: $rp ====="
    if [[ -n "$lang" ]]; then
      printf '```%s\n' "$lang"
      cat "$abs"
      printf '```\n'
    else
      printf '```%s\n'
      cat "$abs"
      printf '```\n'
    fi
    echo "===== END FILE: $rp ====="
  done

} > "$OUTPUT"

echo "✅ Done. Output written to:"
echo "   $OUTPUT"

