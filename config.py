import yaml

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def update_config(new_columns, path="config.yaml"):
    config = load_config(path)
    config['columns'].extend([col for col in new_columns if col not in config['columns']])
    with open(path, "w") as f:
        yaml.safe_dump(config, f)