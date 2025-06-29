import pandas as pd
import re

def split_name_column(df, config):
    rule = config.get('name_split', {})
    src = rule.get('source', 'name')
    targets = rule.get('target', ['first_name', 'middle_name', 'last_name'])
    if src in df.columns:
        split_names = df[src].str.split(' ', n=2, expand=True)
        df[targets[0]] = split_names[0].fillna('-')
        if split_names.shape[1] == 2:
            df[targets[1]] = '-'
            df[targets[2]] = split_names[1].fillna('-')
        elif split_names.shape[1] == 3:
            df[targets[1]] = split_names[1].fillna('-')
            df[targets[2]] = split_names[2].fillna('-')
        else:
            df[targets[1]] = '-'
            df[targets[2]] = '-'
        df = df.drop(columns=[src])
    return df

def handle_nulls(df, config):
    null_cfg = config.get('null_handling', {})
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if null_cfg.get('numeric', 'mean') == 'mean':
                df[col] = df[col].fillna(df[col].mean())
            elif null_cfg.get('numeric') == 'median':
                df[col] = df[col].fillna(df[col].median())
        else:
            mode = df[col].mode()[0] if not df[col].mode().empty else null_cfg.get('text_placeholder', 'Unknown')
            df[col] = df[col].fillna(mode)
    return df

def type_conversion(df, config):
    fmt_cfg = config.get('formatting', {})
    for col, fmt in fmt_cfg.items():
        if col in df.columns:
            if fmt == 'email' or fmt == 'phone':
                continue
            if 'date' in fmt:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime(fmt)
    return df

def validate_columns(df, config):
    val_cfg = config.get('validation', {})
    for col, pattern in val_cfg.items():
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x if pd.isna(x) or re.match(pattern, str(x)) else 'Invalid')
    return df

def preprocess(df, config):
    df = split_name_column(df, config)
    df = handle_nulls(df, config)
    df = type_conversion(df, config)
    df = validate_columns(df, config)
    return df