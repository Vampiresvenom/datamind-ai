import pandas as pd
import numpy as np
import re


def clean_dataframe(df: pd.DataFrame):
    df_c = df.copy()
    actions = []

    # Clean column names
    old = list(df_c.columns)
    df_c.columns = [_clean_col(c) for c in df_c.columns]
    renamed = [(o, n) for o, n in zip(old, df_c.columns) if o != n]
    if renamed:
        actions.append(f"Renamed {len(renamed)} column(s) — removed special characters & spaces")

    # Remove fully empty
    before = len(df_c)
    df_c.dropna(how='all', inplace=True)
    df_c.dropna(axis=1, how='all', inplace=True)
    removed_empty = before - len(df_c)
    if removed_empty > 0:
        actions.append(f"Removed {removed_empty} fully empty row(s)")

    # Remove duplicates
    dups = df_c.duplicated().sum()
    if dups > 0:
        df_c.drop_duplicates(inplace=True)
        actions.append(f"Removed {dups} duplicate row(s)")

    # Trim whitespace
    for col in df_c.select_dtypes(include='object').columns:
        df_c[col] = df_c[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
        df_c[col] = df_c[col].replace('', np.nan)
    actions.append("Trimmed whitespace from all text columns")

    # Convert text → numeric
    converted_num = []
    for col in df_c.select_dtypes(include='object').columns:
        sample = df_c[col].dropna().head(20)
        if len(sample) > 0 and sample.apply(_is_num).mean() > 0.8:
            try:
                df_c[col] = pd.to_numeric(
                    df_c[col].astype(str).str.replace(',','').str.replace('$','').str.replace('%','').str.strip(),
                    errors='coerce'
                )
                converted_num.append(col)
            except:
                pass
    if converted_num:
        actions.append(f"Converted {len(converted_num)} column(s) from text to numeric: {', '.join(converted_num)}")

    # Parse date columns
    converted_dt = []
    for col in df_c.select_dtypes(include='object').columns:
        if any(k in col.lower() for k in ['date','time','year','month','day','dt','created','updated']):
            try:
                result = pd.to_datetime(df_c[col], infer_datetime_format=True, errors='coerce')
                if result.notna().mean() > 0.7:
                    df_c[col] = result
                    converted_dt.append(col)
            except:
                pass
    if converted_dt:
        actions.append(f"Parsed date column(s): {', '.join(converted_dt)}")

    # Fill numeric nulls with median
    filled = []
    for col in df_c.select_dtypes(include=[np.number]).columns:
        nulls = df_c[col].isnull().sum()
        if nulls > 0:
            df_c[col] = df_c[col].fillna(df_c[col].median())
            filled.append(f"{col} ({nulls})")
    if filled:
        actions.append(f"Filled missing numeric values with median in: {', '.join(filled)}")

    df_c.reset_index(drop=True, inplace=True)
    return df_c, actions


def _clean_col(name):
    name = str(name).strip()
    name = re.sub(r'[^a-zA-Z0-9\s_]', '', name)
    name = re.sub(r'\s+', '_', name).strip('_')
    if name and name[0].isdigit():
        name = 'Col_' + name
    return name or 'Column'


def _is_num(s):
    try:
        float(str(s).replace(',','').replace('$','').replace('%','').strip())
        return True
    except:
        return False


def build_data_summary(df: pd.DataFrame) -> str:
    import numpy as np
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
