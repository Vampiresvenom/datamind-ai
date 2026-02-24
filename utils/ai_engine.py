import anthropic, json, re
import pandas as pd
import numpy as np


def _claude(api_key, prompt, max_tokens=3000):
    client = anthropic.Anthropic(api_key=api_key)
    r = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    text = r.content[0].text.strip()
    return re.sub(r'```[a-z]*\n?', '', text).strip()


def build_data_summary(df: pd.DataFrame) -> str:
    lines = [f"Shape: {df.shape[0]} rows x {df.shape[1]} columns\nColumns:"]
    for col in df.columns:
        dtype = str(df[col].dtype)
        nulls = int(df[col].isnull().sum())
        unique = int(df[col].nunique())
        if df[col].dtype in [np.float64, np.int64, np.float32, np.int32]:
            info = f"min={df[col].min():.1f}, max={df[col].max():.1f}, mean={df[col].mean():.1f}"
        else:
            samples = str(df[col].dropna().unique()[:4].tolist())
            info = f"samples={samples}"
        lines.append(f"  {col} | {dtype} | {nulls} nulls | {unique} unique | {info}")
    return "\n".join(lines)


def analyze_with_claude(api_key, filename, data_summary):
    prompt = f"""You are an expert BI analyst. Analyze this dataset. Respond ONLY with valid JSON, no markdown.

File: {filename}
{data_summary}

Return exactly:
{{
  "data_description": "2-3 sentence summary",
  "domain": "Sales|Finance|HR|Inventory|Marketing|Operations|Other",
  "date_column": "exact column name or null",
  "numeric_columns": ["col1","col2"],
  "category_columns": ["col1","col2"],
  "kpis": ["KPI 1: name — description","KPI 2","KPI 3","KPI 4","KPI 5"],
  "charts": ["Chart type: what to show","...x4"],
  "quality_issues": ["issue1","issue2"],
  "insights": ["insight1","insight2","insight3"]
}}"""
    text = _claude(api_key, prompt, max_tokens=2000)
    try:
        return json.loads(text)
    except:
        return {
            "data_description": "Dataset processed successfully.",
            "domain": "General",
            "date_column": None,
            "numeric_columns": list(df.select_dtypes(include=[np.number]).columns)[:4] if 'df' in dir() else [],
            "category_columns": [],
            "kpis": ["Row Count", "Column Count"],
            "charts": ["Bar Chart: Category Distribution"],
            "quality_issues": [],
            "insights": ["Data has been analysed and cleaned."]
        }


def generate_dax(api_key, filename, df, ai_analysis):
    import re as _re
    table = _re.sub(r'[^a-zA-Z0-9_]', '_', filename.replace('.xlsx','').replace('.csv',''))

    cols_info = {}
    for col in df.columns:
        cols_info[col] = {
            "type": str(df[col].dtype),
            "sample": [str(v) for v in df[col].dropna().unique()[:3].tolist()]
        }

    prompt = f"""You are a Power BI DAX expert. Write production-ready DAX measures. Respond ONLY with valid JSON.

Table: '{table}'
Domain: {ai_analysis.get('domain','General')}
Columns: {json.dumps(cols_info)}
Date column: {ai_analysis.get('date_column','none')}
Numeric columns: {ai_analysis.get('numeric_columns',[])}
Category columns: {ai_analysis.get('category_columns',[])}

Generate 10-12 measures including: totals, averages, count, % of total, YTD/MTD (if date exists),
MoM Growth (if date), Running Total (if date), Ranking (RANKX), Max, Min, conditional flag.

JSON only:
{{"Measure Name": "DAX formula", ...}}"""

    text = _claude(api_key, prompt, max_tokens=3000)
    try:
        return json.loads(text), table
    except:
        return {"Row Count": f"Row Count = COUNTROWS('{table}')"}, table


def generate_power_query(api_key, filename, df_raw, df_clean, cleaning_actions):
    col_types = {}
    for col in df_clean.columns:
        dtype = str(df_clean[col].dtype)
        col_types[col] = "type number" if ('int' in dtype or 'float' in dtype) else \
                         "type datetime" if 'datetime' in dtype else "type text"

    prompt = f"""Write complete Power Query M code. Return ONLY the M code, no markdown.

Source: {filename}
Original columns: {list(df_raw.columns)}
Final columns & types: {json.dumps(col_types)}
Cleaning done: {json.dumps(cleaning_actions)}

Write let...in M script that: loads Excel, promotes headers, removes duplicates,
removes empty rows, trims text, sets correct types, replaces empty strings with null.
Each step must have a comment. User will update the file path."""

    text = _claude(api_key, prompt, max_tokens=2500)
    # Ensure it's valid M code
    if not text.strip().startswith('let'):
        # Build fallback
        type_pairs = ", ".join([f'{{"{c}", {t}}}' for c, t in col_types.items()])
        return f"""let
    // Step 1: Load source Excel file (update path below)
    Source = Excel.Workbook(File.Contents("C:\\\\YourPath\\\\{filename}"), null, true),
    Sheet = Source{{0}}[Data],
    // Step 2: Promote first row as headers
    Headers = Table.PromoteHeaders(Sheet, [PromoteAllScalars=true]),
    // Step 3: Remove duplicate rows
    NoDuplicates = Table.Distinct(Headers),
    // Step 4: Remove fully empty rows
    NoEmpties = Table.SelectRows(NoDuplicates, each not List.IsEmpty(
        List.RemoveMatchingItems(Record.FieldValues(_), {{null, ""}}))),
    // Step 5: Trim whitespace from text columns
    Trimmed = Table.TransformColumns(NoEmpties, {{}}, Text.Trim),
    // Step 6: Set correct data types
    TypedTable = Table.TransformColumnTypes(Trimmed, {{{type_pairs}}}),
    // Step 7: Final output
    Final = TypedTable
in
    Final"""
    return text
