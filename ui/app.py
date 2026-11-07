"""Streamlit UI for StreamSearch."""

import os
import requests
import streamlit as st

API_URL = os.environ.get("SS_API_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(page_title="StreamSearch", page_icon="🎥", layout="wide")
st.title("🎥 StreamSearch")
st.caption("Real-time multimodal video search. Query video content with natural language.")

with st.sidebar:
    st.header("Settings")
    limit = st.slider("Max results", 1, 50, 10)
    video_id = st.text_input("Filter by video_id (optional)").strip() or None
    col1, col2 = st.columns(2)
    with col1:
        min_t = st.number_input("Min timestamp (s)", min_value=0.0, value=0.0)
    with col2:
        max_t = st.number_input("Max timestamp (s)", min_value=0.0, value=0.0)
    st.divider()
    if st.button("Health check"):
        try:
            r = requests.get(f"{API_URL}/health/ready", timeout=5)
            st.json(r.json())
        except Exception as exc:
            st.error(str(exc))

query = st.text_input("Search query", placeholder="e.g. a person wearing a red shirt")

if st.button("Search", type="primary") and query.strip():
    payload = {
        "query": query.strip(),
        "limit": limit,
        "video_id": video_id,
        "min_timestamp": min_t if min_t > 0 else None,
        "max_timestamp": max_t if max_t > 0 else None,
    }
    payload = {k: v for k, v in payload.items() if v is not None}

    with st.spinner("Searching…"):
        try:
            r = requests.post(f"{API_URL}/search", json=payload, timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as exc:
            st.error(f"Search failed: {exc}")
            st.stop()

    st.subheader(f"{data['count']} result(s) for \"{query}\"")
    if data.get("cached"):
        st.info("Served from cache")

    if not data["results"]:
        st.warning("No matching frames found.")
    else:
        for i, hit in enumerate(data["results"], start=1):
            st.markdown(
                f"**{i}. Score {hit['score']:.4f}** — "
                f"timestamp `{hit['timestamp_sec']}s` — video `{hit['video_path']}`"
            )
            st.divider()
