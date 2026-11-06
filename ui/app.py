"""StreamSearch UI (Streamlit)."""

import streamlit as st

st.set_page_config(page_title="StreamSearch", page_icon="🔍")

st.title("StreamSearch")
st.write("Search video streams by text or image query.")

query = st.text_input("Search query", placeholder="e.g. a person walking in a park")
limit = st.slider("Results", min_value=1, max_value=50, value=10)

if st.button("Search") and query:
    st.info("Search against the StreamSearch API")
    st.write(f"Query: {query}")
    st.write(f"Limit: {limit}")
