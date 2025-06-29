import streamlit as st
import pandas as pd
import os
from file_parser import read_file
from preprocessor import preprocess

st.title("🧹 Universal Data Cleaner")

uploaded_file = st.file_uploader("Upload CSV, Excel, JSON, or XML", type=["csv", "xlsx", "json", "xml"])

if uploaded_file:
    df = read_file(uploaded_file)
    if df is None or df.empty:
        st.error("❌ Could not read file or file is empty.")
    else:
        cleaned_df, warnings = preprocess(df)
        cleaned_df.reset_index(drop=True, inplace=True)
        cleaned_df.index = cleaned_df.index + 1
        cleaned_df.insert(0, 'S.No', cleaned_df.index)

        st.subheader("Preview of Cleaned Data")
        st.dataframe(cleaned_df)

        st.download_button("Download Cleaned CSV", cleaned_df.to_csv(index=False), file_name="cleaned_data.csv")

        if warnings:
            st.warning("Warnings:")
            for w in warnings:
                st.write(f"- {w}")