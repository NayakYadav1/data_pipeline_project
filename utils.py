import pandas as pd
import sqlite3
import os

def split_name_column(df):
    if 'name' in df.columns:
        print("👥 Splitting 'name' into first, middle, last and removing 'name'...")
        split = df['name'].astype(str).str.strip().str.split(' ', expand=True)
        df['first_name'] = split[0]
        df['middle_name'] = split[1] if split.shape[1] > 2 else ''
        df['last_name'] = split[2] if split.shape[1] > 2 else split[1] if split.shape[1] > 1 else ''
        df.drop(columns=['name'], inplace=True)
    else:
        print("⚠️ 'name' column not found. Skipping split.")
    return df

def convert_dates(df):
    print("📅 Converting date-like columns...")
    for col in df.columns:
        if df[col].dtype == 'object':
            parsed = pd.to_datetime(df[col], format="mixed", errors='coerce')  # Use mixed format
            if parsed.notna().sum() > 0:
                df[col] = parsed.dt.strftime('%Y-%m-%d')
                print(f"✅ Converted '{col}' to date format.")
    return df

def save_to_db(df, table_name):
    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect("db/processed_data.db")
    df.to_sql(table_name, conn, if_exists="append", index=False)
    conn.close()
    print(f"🗃️ Saved data to DB table: {table_name}")
