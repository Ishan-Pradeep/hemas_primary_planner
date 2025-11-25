import pandas as pd

def export_excel(df, distributor, filename):
    """
    Exports the primary allocation DataFrame to Excel.
    """
    df.to_excel(filename, index=False)
