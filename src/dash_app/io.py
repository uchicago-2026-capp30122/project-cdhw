import json
import pandas as pd

def load_df(path: str, id_col: str):
    df = pd.read_csv(path, dtype = {id_col: str})
    return df

def load_geojson(path: str):
    with open(path, "r") as f:
        return json.load(f)

def infer_featureidkey(geojson: dict, id_prop: str):
    # returns "properties.<id_prop>"
    return f"properties.{id_prop}"