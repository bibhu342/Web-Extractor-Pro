import streamlit as st
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="Web-Extractor-Pro Demo", layout="wide")
st.title("Web-Extractor-Pro — Demo")
st.markdown("Preview cleaned CSV produced by the CLI. Use this lightweight demo for clients.")

sample_path = Path("data/cleaned/quotes.csv")

uploaded = st.file_uploader("Upload cleaned CSV (optional)", type=["csv"])
if uploaded is not None:
    df = pd.read_csv(uploaded)
    st.success(f"Loaded {len(df)} rows from uploaded file.")
    st.dataframe(df)
else:
    if sample_path.exists():
        st.markdown("**Sample output from CLI:**")
        df = pd.read_csv(sample_path)
        st.dataframe(df)
        st.download_button("Download sample CSV", data=df.to_csv(index=False), file_name="quotes_sample.csv")
    else:
        st.info("No sample CSV found. Run the CLI first: `python scripts/web_extractor.py --urls data/raw_urls.txt --output data/cleaned/quotes.csv`")
