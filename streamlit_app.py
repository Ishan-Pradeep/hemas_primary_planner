# streamlit_app.py
import streamlit as st
import pandas as pd
from rd_loader import load_merged_data
from logic import distributor_summary, allocate_primary_for_distributor
from excel_export import export_excel

st.set_page_config(page_title="Hemas Primary Planner", layout="wide")
st.title("Hemas Distributor Primary Allocation Tool")

@st.cache_data
def load_data():
    return load_merged_data()

df_products = load_data()
dist_summary = distributor_summary(df_products)

st.subheader("Distributor-level summary and targets")
display_df = dist_summary.rename(columns={
    "distributor_id": "Distributor Code",
    "distributor_name": "Distributor Name",
    "total_rd_avg": "Total RD Avg",
    "total_primary_base": "Total Primary (base)",
    "end_shp_base": "End SHP (base)"
})
st.dataframe(display_df, use_container_width=True)

# Editable target per distributor
edited_targets = {}
for _, row in dist_summary.iterrows():
    dist = row["distributor_id"]
    val = st.number_input(f"{dist} — {row['distributor_name']}", min_value=0.0,
                          value=float(row["total_primary_base"]), step=1.0, key=f"target_{dist}")
    edited_targets[dist] = val

# Distributor selection for product-level allocation
selected_dist = st.sidebar.selectbox("Select Distributor", sorted(df_products["distributor_id"].unique()))

if st.sidebar.button("Recalculate product targets"):
    df_dist_products = df_products[df_products["distributor_id"] == selected_dist].copy()
    target = edited_targets[selected_dist]
    result = allocate_primary_for_distributor(df_dist_products, distributor_target=target)

    result_display = result.rename(columns={
        "3m_avg": "3 Months Avg",
        "rd_upto_now": "RD Upto Now",
        "balance_rd": "Balance RD",
        "current_stock": "Current Stock",
        "primary_alloc": "Primary Plan (allocated)",
        "estimated_end_stock": "Estimated End Stock",
        "final_shp": "SHP"
    })
    st.subheader(f"Product-level allocation for Distributor {selected_dist}")
    st.dataframe(result_display[[
        "product_id", "product_name", "Current Stock", "3 Months Avg", "RD Upto Now",
        "Balance RD", "Primary Plan (allocated)", "Estimated End Stock", "SHP"
    ]], use_container_width=True)

    # Excel download
    excel_file = f"primary_{selected_dist}.xlsx"
    export_excel(result, selected_dist, excel_file)
    with open(excel_file, "rb") as f:
        st.download_button("Download Distributor Excel", f, file_name=excel_file,
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Download full base table
if st.button("Download full base product table"):
    export_excel(df_products, "ALL", "primary_all_base.xlsx")
    with open("primary_all_base.xlsx", "rb") as f:
        st.download_button("Download Full Table", f, "primary_all_base.xlsx")
