import pandas as pd
import re
import os
from utils import split_name_column, convert_dates, save_to_db

def parse_config(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    config = {}

    match = re.search(r'filename:\s*(\w+)', content)
    if match:
        config['filename'] = match.group(1)
    else:
        raise ValueError("❌ 'filename:' not found!")

    match = re.search(r'task:\s*([\w,\s]+)', content)
    config['tasks'] = [t.strip().lower() for t in match.group(1).split(',')] if match else []

    match = re.search(r'cols:\s*([^\n\r]+)', content)
    config['cols'] = [col.strip() for col in match.group(1).split(',')] if match else []

    match = re.search(r'filter:\s*(.+)', content)
    config['filter'] = match.group(1).strip() if match else ""

    return config


def process_file(file_path):
    config = parse_config(file_path)
    filename_base = config['filename']
    base_path = f"input_files/{filename_base}"
    full_path = None

    for ext in ['.csv', '.xlsx', '.json']:
        test_path = base_path + ext
        if os.path.exists(test_path):
            full_path = test_path
            break

    if not full_path:
        print("❌ No matching file found with .csv/.xlsx/.json.")
        return

    try:
        print(f"📂 Reading file: {full_path}")
        if full_path.endswith('.csv'):
            df = pd.read_csv(full_path)
        elif full_path.endswith('.xlsx'):
            df = pd.read_excel(full_path)
        elif full_path.endswith('.json'):
            df = pd.read_json(full_path)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return

    if 'clean' in config['tasks']:
        print("🧹 Cleaning: Removing duplicates...")
        df.drop_duplicates(inplace=True)

    df = split_name_column(df)

    if 'filter' in config['tasks'] and config['filter']:

        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='ignore')

        print(f"🔍 Applying filter: {config['filter']}")
        try:
            df = df.query(config['filter'])
        except Exception as e:
            print(f"❌ Invalid filter: {e}")
            return

    if 'selectcol' in config['tasks'] and config['cols']:
        print(f"🧾 Selecting columns: {config['cols']}")
        missing = [col for col in config['cols'] if col not in df.columns]
        if missing:
            print(f"❌ Missing columns in data: {missing}")
            return
        df = df[config['cols']]

    df = convert_dates(df)

    save_to_db(df, filename_base)

    os.makedirs("data", exist_ok=True)
    output_path = f"data/cleaned_{filename_base}.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Saved to: {output_path}")
