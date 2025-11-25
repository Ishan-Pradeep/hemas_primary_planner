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

# Format numbers for display ONLY
def format_numbers(df):
    numeric_cols = df.select_dtypes(include=['float', 'int']).columns
    df[numeric_cols] = df[numeric_cols].applymap(lambda x: f"{x:,.0f}")
    return df


# Distributor summary
dist_summary = distributor_summary(df_products)

st.subheader("📋 Distributor Summary (Formatted View)")
display_summary = dist_summary.copy()
display_summary = format_numbers(display_summary)
st.dataframe(display_summary, use_container_width=True)

st.markdown("### ✏️ Adjust Distributor-Level Targets")
edited_targets = {}

for _, row in dist_summary.iterrows():
    dist = row["distributor_id"]
    name = row["distributor_name"]
    default_val = float(row["total_primary_base"])
    
    edited_val = st.number_input(
        f"📦 {dist} — {name}",
        min_value=0.0,
        value=round(default_val, 0),
        step=100.0,
        key=f"target_{dist}"
    )
    edited_targets[dist] = float(edited_val)


# Sidebar for product-level allocation
st.sidebar.header("📈 Product-Level Allocation")
selected_dist = st.sidebar.selectbox(
    "Select Distributor", 
    sorted(df_products["distributor_id"].astype(str).unique())
)

st.sidebar.write("Base Primary:", 
    f"{float(dist_summary.loc[dist_summary['distributor_id'] == selected_dist, 'total_primary_base'].iloc[0]):,.0f}")
st.sidebar.write("Updated Target:", f"{edited_targets.get(selected_dist):,.0f}")

if st.sidebar.button("🔄 Recalculate Product Targets"):
    df_dist = df_products[df_products["distributor_id"] == selected_dist].copy()
    target = edited_targets.get(selected_dist)
    result = allocate_primary_for_distributor(df_dist, distributor_target=target)

    st.subheader(f"📊 Product Allocation for Distributor {selected_dist}")
    display_result = format_numbers(result.copy())
    
    st.dataframe(display_result, use_container_width=True)

    excel_file = f"primary_{selected_dist}.xlsx"
    export_excel(result, selected_dist, excel_file)
    with open(excel_file, "rb") as f:
        st.download_button(
            label="⬇️ Download Excel",
            data=f,
            file_name=excel_file
        )

if st.button("⬇️ Download Full Original Table (All Distributors)"):
    export_excel(df_products, "ALL", "primary_all_base.xlsx")
    with open("primary_all_base.xlsx", "rb") as f:
        st.download_button("Download Full Table", f, "primary_all_base.xlsx")
