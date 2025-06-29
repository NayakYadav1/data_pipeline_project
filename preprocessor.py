import pandas as pd
import re

def detect_name_column(df):
    name_patterns = ['name', 'full_name', 'fullname', 'user name', 'username']
    for col in df.columns:
        if any(pat in col.lower().replace("_", " ") for pat in name_patterns):
            return col
    return None

def split_name_column(df, name_col):
    # Split into first, middle, last (handles 1, 2, or 3+ parts)
    names = df[name_col].astype(str).str.strip().str.split(r'\s+', n=2, expand=True)
    df['first_name'] = names[0].fillna('-')
    if names.shape[1] > 1:
        df['middle_name'] = names[1].fillna('-')
    else:
        df['middle_name'] = '-'
    if names.shape[1] > 2:
        df['last_name'] = names[2].fillna('-')
    elif names.shape[1] > 1:
        df['last_name'] = names[1].fillna('-')
    else:
        df['last_name'] = '-'
    return df

def smart_fillna(df):
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(df[col].mean())
        else:
            mode = df[col].mode()
            df[col] = df[col].fillna(mode[0] if not mode.empty else "Unknown")
    return df

def validate_column(df, col, pattern):
    if col in df.columns:
        invalid_mask = ~df[col].astype(str).str.match(pattern)
        return invalid_mask
    return pd.Series([False]*len(df))

def preprocess(df):
    warnings = []
    # Smart name detection and splitting
    name_col = detect_name_column(df)
    if name_col:
        df = split_name_column(df, name_col)
        df.drop(columns=[name_col], inplace=True)
    else:
        warnings.append("No name column detected; skipping name split.")

    # Fill nulls smartly
    df = smart_fillna(df)

    # Validate common fields
    invalids = {}
    if 'email' in [c.lower() for c in df.columns]:
        email_col = [c for c in df.columns if c.lower() == 'email'][0]
        invalid_mask = validate_column(df, email_col, r"^[\w\.-]+@[\w\.-]+\.\w+$")
        if invalid_mask.any():
            warnings.append(f"Invalid emails found in column '{email_col}'.")
            df.loc[invalid_mask, email_col] = "Invalid"
    if 'phone' in [c.lower() for c in df.columns]:
        phone_col = [c for c in df.columns if 'phone' in c.lower()][0]
        invalid_mask = validate_column(df, phone_col, r"^\+?\d{7,15}$")
        if invalid_mask.any():
            warnings.append(f"Invalid phone numbers found in column '{phone_col}'.")
            df.loc[invalid_mask, phone_col] = "Invalid"
    # Try to standardize date columns
    for col in df.columns:
        if 'date' in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
                df[col] = df[col].fillna("Unknown")
            except Exception:
                warnings.append(f"Could not standardize date column '{col}'.")
    return df, warnings