import pandas as pd
import sqlite3
import os

def split_name_column(df):
    if 'name' in df.columns:
        split_names = df['name'].str.split(' ', n=2, expand=True)
        df['first_name'] = split_names[0].fillna('-')
        # If only two parts, middle will be NaN
        df['middle_name'] = split_names[1].where(split_names[2].notna(), '-').fillna('-')
        df['last_name'] = split_names[2].fillna('-')
        # If only two parts, move second part to last_name
        mask_two_parts = split_names[2].isna() & split_names[1].notna()
        df.loc[mask_two_parts, 'last_name'] = split_names[1][mask_two_parts]
        df.loc[mask_two_parts, 'middle_name'] = '-'
        df = df.drop(columns=['name'])
    else:
        df['first_name'] = '-'
        df['middle_name'] = '-'
        df['last_name'] = '-'
    return df

def convert_dates(df):
    if 'date_of_birth' in df.columns:
        df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce').dt.strftime('%Y-%m-%d')
        df['date_of_birth'] = df['date_of_birth'].fillna('-')
    return df

def save_to_db(df, table_name):
    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect("db/processed_data.db")
    df.to_sql(table_name, conn, if_exists="append", index=False)
    conn.close()
    print(f"🗃️ Saved data to DB table: {table_name}")
