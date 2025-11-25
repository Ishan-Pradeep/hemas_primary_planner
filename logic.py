import pandas as pd

def calculate_primary(df, primary_target):
    # Base SHP values
    TARGET_SHP = 1.2
    MIN_SHP = 1.0
    SHP_DOWN_STEP = 0.05
    SHP_UP_STEP = 0.05

    # Base stock target
    df["base_target_stock"] = df["rd_avg"] * TARGET_SHP
    df["base_primary"] = df["base_target_stock"] - df["current_stock"] + df["rd_remaining"]

    base_total = df["base_primary"].sum()

    # Speed (movement rate)
    df["speed"] = df["rd_avg"] / df["rd_avg"].sum()

    # Weight (sales value importance)
    df["weight"] = (df["rd_3m_value"] + df["rd_this_value"]) / \
                    (df["rd_3m_value"] + df["rd_this_value"]).sum()

    # ---------------------
    # Case 1 — Reduce primary to match target
    # ---------------------
    if primary_target < base_total:
        df["rank"] = df["speed"].rank(ascending=True)

        df["adj_shp"] = df.apply(
            lambda r: max(MIN_SHP, TARGET_SHP - (r["rank"] - 1) * SHP_DOWN_STEP),
            axis=1
        )

    # ---------------------
    # Case 2 — Increase primary above normal
    # ---------------------
    else:
        df["rank"] = df["weight"].rank(ascending=False)

        df["adj_shp"] = df.apply(
            lambda r: TARGET_SHP + (r["rank"] - 1) * SHP_UP_STEP,
            axis=1
        )

    # Final primary allocation
    df["adj_target_stock"] = df["adj_shp"] * df["rd_avg"]
    df["adj_primary"] = df["adj_target_stock"] - df["current_stock"] + df["rd_remaining"]

    return df
