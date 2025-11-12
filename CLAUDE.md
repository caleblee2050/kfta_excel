# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Excel Unifier (강원교총 엑셀통합 에이전트) - A smart tool that automatically analyzes and unifies Excel files with inconsistent formats. Built for Gangwon Teachers' Association (KFTA) to consolidate personnel data from multiple sources with varying column names and formats.

## Key Commands

### Development & Testing
```bash
# Run CLI with basic mode
./run.sh file1.xlsx file2.xlsx -o output.xlsx -k 이름 학교

# Run CLI with AI mode (requires GEMINI_API_KEY in .env)
./run.sh file1.xlsx file2.xlsx -o output.xlsx --ai -k 이름 학교

# Generate test examples
venv/bin/python example_generator.py

# Test with generated examples
./run.sh examples/*.xlsx -o examples/unified_result.xlsx -k 이름 학교

# Run web dashboard (recommended)
./start_app.sh
# Opens at http://localhost:8501
```

### Manual Python Execution
```bash
# Create venv if needed
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# Run CLI directly
venv/bin/python excel_unifier.py file1.xlsx file2.xlsx -o output.xlsx

# Run web app directly
venv/bin/streamlit run app.py

# Test AI matcher
venv/bin/python ai_matcher.py
```

## Architecture

### Core Components

**ExcelUnifier (excel_unifier.py)** - Main unification engine with 3-tier hybrid matching system:

1. **Keyword Dictionary Matching (Tier 1)** - Fast, exact matching using predefined keyword mappings
   - KFTA standard columns prioritized (현재교육청, 현재본청, 대응, etc.)
   - General mappings as fallback (이름→성명, 학교→대학교)
   - Located in `analyze_columns()` method's `keyword_mappings` dict

2. **AI Semantic Matching (Tier 2)** - Context-aware matching via Gemini API
   - Handles synonyms: "이름" ↔ "성명" (95% similarity)
   - Multilingual: "email" ↔ "이메일" (100%)
   - Abbreviations: "HP" ↔ "휴대폰" (98%)
   - Activated with `use_ai=True` flag

3. **Levenshtein Distance (Tier 3)** - Character-based fuzzy matching
   - Default threshold: 85%
   - Fallback when AI fails or is disabled
   - Uses fuzzywuzzy library

**KFTAParser (kfta_parser.py)** - Position-based field parser for KFTA standard format:
- Extracts data based on fixed column positions (not column names)
- Maps Gangwon regions to education offices (GANGWON_REGIONS dict)
- Transforms raw data into 12-column KFTA standard format
- Key method: `parse_row_to_kfta()` - converts row data by position indices

**GeminiMatcher (ai_matcher.py)** - AI-powered semantic similarity analyzer:
- Uses `gemini-2.5-flash` model
- LRU cache to prevent duplicate API calls
- Returns structured JSON: {similarity, is_similar, reason, mapping}
- Handles multilingual, synonym, and abbreviation matching

**Streamlit Web App (app.py)** - User-friendly web dashboard with 4 tabs:
1. File Upload - Multi-file drag & drop with preview
2. Data Analysis - Column mapping and unification execution
3. Results - Preview and download (Excel/CSV)
4. Statistics - Charts and data analysis

### Data Flow

1. **File Loading** (`load_excel_files`)
   - Supports .xlsx, .xls, .csv
   - Reads all sheets from Excel files
   - Stores as list of dicts: {path, sheet, data, columns}

2. **Column Analysis** (`analyze_columns`)
   - Applies 3-tier matching system
   - Groups similar columns
   - Returns column_mappings: {unified_name: [original_names]}

3. **Data Unification** (`unify_dataframes`)
   - Two modes: standard mapping vs KFTA parsing
   - KFTA mode: Uses KFTAParser for position-based extraction
   - Standard mode: Applies column_mappings to rename and merge
   - Optional: Smart duplicate removal via `_remove_duplicates_smart()`

4. **Output Formatting** (controlled by `output_format` parameter)
   - `'auto'`: Auto-detects format from input columns
   - `'standard'`: Keeps all columns from input files
   - `'kfta'`: Forces 12-column KFTA standard format via `_apply_kfta_format()`

### KFTA Standard Format

12-column standard output (when `output_format='kfta'`):
```
현재교육청, 현재본청, 대응, 발령교육청, 발령본청, 과목, 직위, 직종분류, 분류명, 취급코드, 시군구분, 교호기호등
```

Position-based parsing (KFTAParser):
- Field 3 (index 2) → 대응 (name)
- Field 5 (index 4) → 직위 (position)
- Field 6 (index 5) → 발령본청 + 발령교육청 (extracted from region name)
- Field 8 (index 7) → 현재본청 (conditional)
- Field 9 (index 8) → Reference for 현재교육청/현재본청

## Important Patterns

### AI Mode Configuration

AI mode requires GEMINI_API_KEY in environment:
```bash
# .env file
GEMINI_API_KEY=your_api_key_here
```

ExcelUnifier initialization:
```python
# Basic mode (keyword + Levenshtein)
unifier = ExcelUnifier(similarity_threshold=85)

# AI mode (all 3 tiers)
unifier = ExcelUnifier(use_ai=True, similarity_threshold=85)
```

Web app reads from sidebar checkbox + .env file automatically.

### Adding New Column Mappings

To add new column name variations, edit `keyword_mappings` dict in `excel_unifier.py:114-137`:
```python
keyword_mappings = {
    '통합컬럼명': ['원본명1', '원본명2', '별칭'],
    # KFTA columns should come first (higher priority)
    # General columns come after
}
```

Order matters: More specific patterns should be placed before general ones.

### Extending KFTA Parser

To modify field position mappings, edit `parse_row_to_kfta()` in `kfta_parser.py:92-166`:
- Uses 0-based indexing: `row.iloc[index]`
- Field extraction logic is position-dependent
- Region extraction uses `GANGWON_REGIONS` dict for mapping

## Key Files

- `excel_unifier.py` - Main engine (ExcelUnifier class)
- `kfta_parser.py` - Position-based KFTA parser
- `ai_matcher.py` - Gemini AI semantic matcher
- `app.py` - Streamlit web dashboard
- `example_generator.py` - Test data generator
- `run.sh` - CLI wrapper with venv auto-setup
- `start_app.sh` - Web app launcher

## Environment

- Python 3.7+
- Virtual environment auto-created by run.sh/start_app.sh
- Dependencies: pandas, openpyxl, fuzzywuzzy, streamlit, plotly, google-generativeai
- Optional: GEMINI_API_KEY for AI mode

## Common Pitfalls

1. **Column mapping not working**: Check if column name exists in `keyword_mappings`. KFTA columns have higher priority than general columns.

2. **KFTA format not applied**: Ensure `output_format='kfta'` is passed to `unify_dataframes()`. Auto mode only applies KFTA format if KFTA columns are detected.

3. **Position-based parsing issues**: KFTAParser expects specific field positions. If input format changes, update index numbers in `parse_row_to_kfta()`.

4. **AI mode not working**: Verify GEMINI_API_KEY in .env file. Check if `use_ai=True` is set. AI failures automatically fall back to Levenshtein matching.

5. **Duplicate removal not working**: Key columns must exist in unified output. Normalization happens on `_normalized` temp columns which are case-insensitive and stripped of whitespace.
