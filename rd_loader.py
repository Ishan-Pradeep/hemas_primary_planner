import pandas as pd

# -----------------------
# LOAD 3-MONTH RD DATA
# -----------------------
def load_rd_3m():
    df = pd.read_excel("RDdata.xlsx")

    df.rename(columns={
        "DBCode": "distributor_id",
        "DbName": "distributor_name",
        "Icode": "product_id",
        "Iname": "product_name",
        "value": "rd_3m_value"
    }, inplace=True)

    df_grouped = df.groupby(
        ["distributor_id", "distributor_name", "product_id", "product_name"],
        as_index=False
    )["rd_3m_value"].sum()

    return df_grouped


# -----------------------
# LOAD THIS MONTH RD
# -----------------------
def load_rd_this_month():
    df = pd.read_excel("RDthis.xlsx")

    df.rename(columns={
        "DBCode": "distributor_id",
        "DbName": "distributor_name",
        "Icode": "product_id",
        "Iname": "product_name",
        "value": "rd_this_value"
    }, inplace=True)

    df_grouped = df.groupby(
        ["distributor_id", "distributor_name", "product_id", "product_name"],
        as_index=False
    )["rd_this_value"].sum()

    return df_grouped


# -----------------------
# LOAD CURRENT STOCK
# -----------------------
def load_stock_data():
    df = pd.read_excel("CurrentDBS.xlsx")

    df.rename(columns={
        "DistributorID": "distributor_id",
        "ProductCode": "product_id",
        "StockValue": "current_stock"
    }, inplace=True)

    df_grouped = df.groupby(
        ["distributor_id", "product_id"],
        as_index=False
    )["current_stock"].sum()

    return df_grouped


# -----------------------
# MERGE EVERYTHING
# -----------------------
def load_merged_data():
    rd3 = load_rd_3m()
    rdthis = load_rd_this_month()
    stock = load_stock_data()

    # Merge RD data
    df = pd.merge(
        rd3,
        rdthis,
        on=["distributor_id", "product_id"],
        how="outer",
        suffixes=("_3m", "_this")
    )

    # Restore names when missing
    df["distributor_name"] = df["distributor_name_3m"].fillna(df["distributor_name_this"])
    df["product_name"] = df["product_name_3m"].fillna(df["product_name_this"])

    df.drop(columns=[
        col for col in df.columns
        if col.endswith("_3m") or col.endswith("_this")
    ], inplace=True)

    # Fill missing RD values
    df["rd_3m_value"] = df["rd_3m_value"].fillna(0)
    df["rd_this_value"] = df["rd_this_value"].fillna(0)

    # Load stock
    df = pd.merge(
        df,
        stock,
        on=["distributor_id", "product_id"],
        how="left"
    )
    df["current_stock"].fillna(0, inplace=True)

    # Compute RD average and remaining
    df["rd_avg"] = df["rd_3m_value"] / 3
    df["rd_upto_now"] = df["rd_this_value"]

    return df
