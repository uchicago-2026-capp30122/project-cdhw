import json
import pandas as pd

def load_rideshare_json(path):
    with open(path) as f:
        return json.load(f)

def load_census_csv(path):
    return pd.read_csv(path)