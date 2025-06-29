import pandas as pd
import sqlite3
import tempfile

def parse_sqlite(file):
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name

    # Connect to SQLite and list tables
    conn = sqlite3.connect(tmp_path)
    tables = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type='table';", conn
    )['name'].tolist()
    if not tables:
        conn.close()
        raise ValueError("No tables found in SQLite database.")

    # For simplicity, read the first table
    df = pd.read_sql_query(f"SELECT * FROM {tables[0]}", conn)
    conn.close()
    return df

def detect_and_parse(file, filename):
    ext = filename.lower().split('.')[-1]
    if ext == 'csv':
        return pd.read_csv(file)
    elif ext in ['xls', 'xlsx']:
        return pd.read_excel(file)
    elif ext == 'json':
        try:
            return pd.read_json(file)
        except Exception:
            file.seek(0)
            import json
            data = json.load(file)
            return pd.json_normalize(data)
    elif ext == 'xml':
        # ... your XML logic ...
        pass
    elif ext == 'db':
        return parse_sqlite(file)
    else:
        raise ValueError("Unsupported file format")