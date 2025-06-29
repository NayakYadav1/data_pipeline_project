import pandas as pd
import xml.etree.ElementTree as ET
import json
from io import BytesIO, StringIO

def parse_csv(file):
    return pd.read_csv(file)

def parse_excel(file):
    return pd.read_excel(file)

def parse_json(file):
    try:
        return pd.read_json(file)
    except Exception:
        file.seek(0)
        data = json.load(file)
        return pd.json_normalize(data)

def parse_xml(file):
    file.seek(0)
    tree = ET.parse(file)
    root = tree.getroot()
    all_rows = []
    for child in root:
        row = {}
        for elem in child:
            row[elem.tag] = elem.text
        all_rows.append(row)
    return pd.DataFrame(all_rows)

def detect_and_parse(file, filename):
    ext = filename.lower().split('.')[-1]
    if ext == 'csv':
        return parse_csv(file)
    elif ext in ['xls', 'xlsx']:
        return parse_excel(file)
    elif ext == 'json':
        return parse_json(file)
    elif ext == 'xml':
        return parse_xml(file)
    else:
        raise ValueError("Unsupported file format")