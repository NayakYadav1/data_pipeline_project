import pandas as pd
import re
import os

def parse_config(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    config = {}

    match = re.search(r'filename:\s*(\w+)', content)
    if match:
        config['filename'] = match.group(1)
    else:
        raise ValueError("❌ 'filename:' not found or incorrect in config!")

    match = re.search(r'task:\s*([\w,\s]+)', content)
    config['tasks'] = [t.strip().lower() for t in match.group(1).split(',')] if match else []

    match = re.search(r'cols:\s*([^\n\r]+)', content)
    config['cols'] = [col.strip() for col in match.group(1).split(',')] if match else []

    match = re.search(r'filter:\s*(.+)', content)
    config['filter'] = match.group(1).strip() if match else ""

    return config


def split_name_column(df):
    if 'name' in df.columns:
        print("👥 Splitting 'name' into first, middle, last and removing 'name'...")
        name_split = df['name'].str.split(' ', expand=True)
        df['first_name'] = name_split[0]
        if name_split.shape[1] == 2:
            df['middle_name'] = ''
            df['last_name'] = name_split[1]
        elif name_split.shape[1] >= 3:
            df['middle_name'] = name_split[1]
            df['last_name'] = name_split[2]
        else:
            df['middle_name'] = ''
            df['last_name'] = ''
        df.drop(columns=['name'], inplace=True)
    return df


def convert_dates(df):
    print("📅 Checking for date columns to standardize...")
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
                df[col] = df[col].dt.strftime('%Y-%m-%d')
                print(f"✅ Standardized column '{col}' to date format.")
            except Exception:
                continue
    return df


def process_file(file_path):
    config = parse_config(file_path)
    file_to_load = f"input_files/{config['filename']}.csv"
    print(f"📂 Processing file: {file_to_load}")

    try:
        df = pd.read_csv(file_to_load)
    except FileNotFoundError:
        print(f"❌ File not found: {file_to_load}")
        return

    # Clean
    if 'clean' in config['tasks']:
        print("🧹 Cleaning: Removing nulls and duplicates...")
        df.drop_duplicates(inplace=True)
        df.dropna(inplace=True)

    # Split name before filtering (so we can use first_name/last_name if needed)
    df = split_name_column(df)

    # Filter
    if 'filter' in config['tasks'] and config['filter']:
        print(f"🔍 Applying filter: {config['filter']}")
        try:
            df = df.query(config['filter'])
        except Exception as e:
            print(f"❌ Filter error: {e}")
            return

    # Select columns (only if mentioned in config)
    if 'selectcol' in config['tasks'] and config['cols']:
        print(f"🧾 Selecting columns: {config['cols']}")
        missing = [col for col in config['cols'] if col not in df.columns]
        if missing:
            print(f"❌ Missing columns in data: {missing}")
            return
        df = df[config['cols']]

    # Convert any dates
    df = convert_dates(df)

    # Save
    output_path = f"data/cleaned_{config['filename']}.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Saved cleaned data to: {output_path}")