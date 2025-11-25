import streamlit as st
import pandas as pd
from rd_loader import load_merged_data
from logic import calculate_primary
from excel_export import export_excel

st.set_page_config(page_title="Hemas Primary Planner", layout="wide")

st.title("Hemas Distributor Primary Allocation Tool")

# Load merged data (3-month RD + this month + stock)
@st.cache_data
def load_data():
    return load_merged_data()

df = load_data()

# Distributor selection
dist_list = sorted(df["distributor_id"].unique())
selected_dist = st.selectbox("Select Distributor", dist_list)

# Filter for distributor
df_dist = df[df["distributor_id"] == selected_dist].copy()

# Show distributor data
st.subheader(f"Distributor {selected_dist} - Current Data")
st.dataframe(df_dist[[
    "product_id", "product_name", "current_stock",
    "rd_3m_value", "rd_this_value", "rd_avg", "rd_remaining"
]])

# Input for target primary
target_primary = st.number_input(
    "Enter Target Primary Value",
    min_value=0.0,
    value=float(df_dist["rd_avg"].sum())
)

# Button to calculate
if st.button("Calculate Primary Allocation"):
    result = calculate_primary(df_dist, target_primary)
    
    st.subheader("Suggested Primary Allocation")
    st.dataframe(result[[
        "product_id", "product_name", "current_stock",
        "rd_avg", "rd_upto_now", "adj_shp", "adj_primary"
    ]])

    # Excel download
    excel_file = f"primary_{selected_dist}.xlsx"
    export_excel(result, selected_dist, excel_file)

    st.success(f"Excel generated: {excel_file}")
    st.download_button(
        label="Download Excel",
        data=open(excel_file, "rb"),
        file_name=excel_file,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
