import pandas as pd
import xml.etree.ElementTree as ET
import json
import io

def read_file(uploaded_file):
    filename = uploaded_file.name.lower()
    try:
        if filename.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif filename.endswith('.xlsx'):
            return pd.read_excel(uploaded_file)
        elif filename.endswith('.json'):
            # Try reading as JSON records or array
            try:
                return pd.read_json(uploaded_file)
            except Exception:
                uploaded_file.seek(0)
                data = json.load(uploaded_file)
                return pd.json_normalize(data)
        elif filename.endswith('.xml'):
            uploaded_file.seek(0)
            tree = ET.parse(uploaded_file)
            root = tree.getroot()
            all_rows = []
            for child in root:
                row = {}
                for elem in child:
                    row[elem.tag] = elem.text
                all_rows.append(row)
            return pd.DataFrame(all_rows)
        else:
            return None
    except Exception as e:
        return None