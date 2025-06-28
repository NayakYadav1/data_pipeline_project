import pandas as pd
import re
import os

def parse_config(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    config = {}
    config['filename'] = re.search(r'filename:\s*(\w+)', content).group(1)
    config['tasks'] = re.search(r'task:\s*([\w,\s]+)', content).group(1).split(',')
    config['tasks'] = [t.strip() for t in config['tasks']]
    config['cols'] = re.findall(r'cols:\s*([\w,\s]+)', content)
    config['filter'] = re.findall(r'filter:\s*(.+)', content)

    return config

def process_file(file_path):
    config = parse_config(file_path)
    file_to_load = f"input_files/{config['filename']}.csv"

    print(f"Processing file: {file_to_load}")
    df = pd.read_csv(file_to_load)

    if 'clean' in config['tasks']:
        df.drop_duplicates(inplace=True)
        df.dropna(inplace=True)

    if 'selectcol' in config['tasks'] and config['cols']:
        cols = [col.strip() for col in config['cols'][0].split(',')]
        df = df[cols]

    if 'filter' in config['tasks'] and config['filter']:
        try:
            df = df.query(config['filter'][0])
        except Exception as e:
            print("Error in filter query:", e)

    output_path = f"data/cleaned_{config['filename']}.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned data to {output_path}")
