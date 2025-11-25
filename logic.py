# logic.py
import pandas as pd
import numpy as np

def distributor_summary(df_products):
    agg = df_products.groupby(["distributor_id", "distributor_name"], as_index=False).agg({
        "3m_avg": "sum",
        "primary_plan_base": "sum"
    }).rename(columns={
        "3m_avg": "total_rd_avg",
        "primary_plan_base": "total_primary_base"
    })

    agg["end_shp_base"] = agg.apply(
        lambda r: (r["total_primary_base"] / r["total_rd_avg"]) if r["total_rd_avg"] > 0 else np.nan,
        axis=1
    )

    agg["target_primary"] = agg["total_primary_base"].copy()
    return agg


def allocate_primary_for_distributor(df_products_for_dist, distributor_target=None):
    df = df_products_for_dist.copy().reset_index(drop=True)

    df["primary_alloc"] = df["primary_plan_base"].astype(float)
    base_total = df["primary_alloc"].sum()

    if distributor_target is None:
        distributor_target = base_total

    distributor_target = float(distributor_target)
    delta = distributor_target - base_total

    if abs(delta) < 1e-8:
        df["estimated_end_stock"] = df["current_stock"] + df["primary_alloc"] - df["balance_rd"]
        df["final_shp"] = (df["current_stock"] + df["primary_alloc"] - df["balance_rd"]) / df["3m_avg"]
        df["final_shp"] = df["final_shp"].round(1)
        return df

    # Increase allocation: fast movers first
    if delta > 0:
        total_rd = df["3m_avg"].sum()
        df = df.sort_values("3m_avg", ascending=False).reset_index(drop=True)
        if total_rd <= 0:
            df["add"] = delta / len(df)
        else:
            df["share"] = df["3m_avg"] / total_rd
            df["add"] = df["share"] * delta
        df["primary_alloc"] += df["add"]

    # Reduce allocation: slow movers first
    else:
        to_remove = -delta
        df = df.sort_values("3m_avg", ascending=True).reset_index(drop=True)
        for idx, row in df.iterrows():
            available = row["primary_alloc"]
            remove = min(available, to_remove)
            df.at[idx, "primary_alloc"] = available - remove
            to_remove -= remove
            if to_remove <= 0:
                break

    df["primary_alloc"] = df["primary_alloc"].clip(lower=0)
    df["estimated_end_stock"] = df["current_stock"] + df["primary_alloc"] - df["balance_rd"]
    df["final_shp"] = (df["current_stock"] + df["primary_alloc"] - df["balance_rd"]) / df["3m_avg"]
    df["final_shp"] = df["final_shp"].round(1)

    df = df.sort_values("3m_avg", ascending=False).reset_index(drop=True)
    return df
