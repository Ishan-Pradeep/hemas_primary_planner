# excel_export.py
import pandas as pd

def export_excel(df, distributor, filename):
    df = df.copy()
    num_cols = df.select_dtypes(include=['float', 'int']).columns
    df[num_cols] = df[num_cols].round(0).astype(int)
    df.to_excel(filename, index=False)
