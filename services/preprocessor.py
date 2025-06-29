import pandas as pd
import re

def detect_name_column(df):
    name_patterns = ['name', 'full_name', 'fullname', 'user name', 'username']
    for col in df.columns:
        if any(pat in col.lower().replace("_", " ") for pat in name_patterns):
            return col
    return None

def split_name_column(df, name_col):
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
        if col.lower() == "age":
            # Fill missing ages with mode and convert to int
            df[col] = pd.to_numeric(df[col], errors='coerce')
            mode = df[col].mode()
            fill_value = int(mode[0]) if not mode.empty else 0
            df[col] = df[col].fillna(fill_value).astype(int)
        elif pd.api.types.is_numeric_dtype(df[col]):
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
    name_col = detect_name_column(df)
    if name_col:
        df = split_name_column(df, name_col)
        df.drop(columns=[name_col], inplace=True)
    else:
        warnings.append("No name column detected; skipping name split.")

    df = smart_fillna(df)

    # Validate emails
    email_col = next((c for c in df.columns if 'email' in c.lower()), None)
    if email_col:
        invalid_mask = validate_column(df, email_col, r"^[\w\.-]+@[\w\.-]+\.\w+$")
        if invalid_mask.any():
            warnings.append(f"Invalid emails found in column '{email_col}'.")
            df.loc[invalid_mask, email_col] = "Invalid"

    # Validate phone
    phone_col = next((c for c in df.columns if 'phone' in c.lower()), None)
    if phone_col:
        invalid_mask = validate_column(df, phone_col, r"^\+?\d{7,15}$")
        if invalid_mask.any():
            warnings.append(f"Invalid phone numbers found in column '{phone_col}'.")
            df.loc[invalid_mask, phone_col] = "Invalid"

    # Standardize date columns
    for col in df.columns:
        if 'date' in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
                df[col] = df[col].fillna("Unknown")
            except Exception:
                warnings.append(f"Could not standardize date column '{col}'.")
    return df, warnings