import streamlit as st
import requests
import pandas as pd

st.title("Universal Data Uploader & Cleaner")

uploaded_file = st.file_uploader("Upload CSV, Excel, JSON, or XML", type=["csv", "xlsx", "json", "xml"])

if uploaded_file:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    with st.spinner("Processing..."):
        resp = requests.post("http://localhost:8000/upload", files=files)
    if resp.status_code == 200:
        data = resp.json()
        if "error" in data:
            st.error(data["error"])
        else:
            st.success(data["message"])
            st.dataframe(pd.DataFrame(data["preview"]))
            if data["warnings"]:
                st.warning("Warnings:")
                for w in data["warnings"]:
                    st.write(f"- {w}")
            st.download_button("Download Cleaned Preview", pd.DataFrame(data["preview"]).to_csv(index=False), file_name="cleaned_preview.csv")
    else:
        st.error("Server error. Please check backend logs.")