# rd_loader.py
import pandas as pd

# -----------------------
# LOAD 3-MONTH RD DATA
# -----------------------
def load_rd_3m(path="RDdata.xlsx"):
    df = pd.read_excel(path)
    df["DBCode"] = df["DBCode"].astype(str)
    df["Icode"] = df["Icode"].astype(str)

    df = df.rename(columns={
        "DBCode": "distributor_id",
        "DbName": "distributor_name",
        "Icode": "product_id",
        "Iname": "product_name",
        "value": "rd_3m_value"
    })

    return df.groupby(
        ["distributor_id", "distributor_name", "product_id", "product_name"], 
        as_index=False
    )["rd_3m_value"].sum()


# -----------------------
# LOAD THIS MONTH RD
# -----------------------
def load_rd_this_month(path="RDthis.xlsx"):
    df = pd.read_excel(path)
    df["DBCode"] = df["DBCode"].astype(str)
    df["Icode"] = df["Icode"].astype(str)

    df = df.rename(columns={
        "DBCode": "distributor_id",
        "DbName": "distributor_name",
        "Icode": "product_id",
        "Iname": "product_name",
        "value": "rd_this_value"
    })

    return df.groupby(
        ["distributor_id", "distributor_name", "product_id", "product_name"], 
        as_index=False
    )["rd_this_value"].sum()


# -----------------------
# LOAD CURRENT STOCK
# -----------------------
def load_stock_data(path="CurrentDBS.xlsx"):
    df = pd.read_excel(path)
    df["DistributorID"] = df["DistributorID"].astype(str)
    df["ProductCode"] = df["ProductCode"].astype(str)

    df = df.rename(columns={
        "DistributorID": "distributor_id",
        "ProductCode": "product_id",
        "StockValue": "current_stock"
    })

    return df.groupby(["distributor_id", "product_id"], as_index=False)["current_stock"].sum()


# -----------------------
# MERGE EVERYTHING AND CALCULATE UPDATED METRICS
# -----------------------
def load_merged_data(rd3_path="RDdata.xlsx", rdthis_path="RDthis.xlsx", stock_path="CurrentDBS.xlsx"):
    rd3 = load_rd_3m(rd3_path)
    rdthis = load_rd_this_month(rdthis_path)
    stock = load_stock_data(stock_path)

    df = pd.merge(rd3, rdthis, on=["distributor_id", "product_id"], how="outer", suffixes=("_3m", "_this"))

    df["distributor_name"] = df["distributor_name_3m"].fillna(df["distributor_name_this"])
    df["product_name"] = df["product_name_3m"].fillna(df["product_name_this"])
    df = df.drop(columns=[c for c in df.columns if c.endswith("_3m") or c.endswith("_this")])

    df["rd_3m_value"] = df.get("rd_3m_value", 0).fillna(0)
    df["rd_this_value"] = df.get("rd_this_value", 0).fillna(0)

    df = pd.merge(df, stock, on=["distributor_id", "product_id"], how="left")
    df["current_stock"] = df["current_stock"].fillna(0)

    df["rd_avg"] = df["rd_3m_value"] / 3
    df["rd_upto_now"] = df["rd_this_value"]
    df["balance_rd"] = df["rd_avg"] - df["rd_upto_now"]

    # ⭐ UPDATED FORMULA:
    df["primary_base"] = (df["rd_avg"] * 1.2) - df["current_stock"] + df["balance_rd"]
    df["primary_base"] = df["primary_base"].clip(lower=0)

    df["est_end_stock_base"] = df["current_stock"] + df["primary_base"] - df["balance_rd"]

    return df.rename(columns={
        "rd_avg": "3m_avg",
        "primary_base": "primary_plan_base",
        "est_end_stock_base": "estimated_end_stock_base"
    })
