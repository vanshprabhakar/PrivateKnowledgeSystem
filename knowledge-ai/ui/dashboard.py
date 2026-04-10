from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestrator.pipeline import RAGPipeline


@st.cache_resource
def load_pipeline(config_path: str) -> RAGPipeline:
    return RAGPipeline(config_path=config_path)


def main() -> None:
    st.set_page_config(page_title="Knowledge AI Dashboard", page_icon="🧠", layout="wide")
    st.title("🧠 Multi-KB RAG Dashboard")
    st.caption("Local testing UI for ingestion and querying across configured knowledge bases.")

    with st.sidebar:
        st.header("Configuration")
        config_path = st.text_input("Config path", value="config/config.yaml")
        pipeline = load_pipeline(config_path)

        kb_names = pipeline.config.all_kb_names()
        selected_kbs = st.multiselect("Knowledge bases", options=kb_names, default=kb_names)

        source_filter_text = st.text_input("Source filter (comma-separated)", value="")
        source_filter = [x.strip() for x in source_filter_text.split(",") if x.strip()]

        top_k = st.slider("Top K", min_value=1, max_value=20, value=pipeline.config.settings.top_k)

        st.divider()
        st.subheader("Ingestion")
        ingest_kb = st.selectbox("Ingest specific KB", options=kb_names)
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Ingest selected KB", use_container_width=True):
                result = pipeline.ingest_kb(ingest_kb)
                st.success(f"Ingestion complete: {result}")
        with col_b:
            if st.button("Ingest all KBs", use_container_width=True):
                result = pipeline.ingest_all()
                st.success(f"Ingestion complete: {result}")

    st.subheader("Ask a question")
    query = st.text_area("Question", placeholder="How does payroll integration work?", height=100)

    if st.button("Run query", type="primary", use_container_width=True):
        if not query.strip():
            st.warning("Please enter a question.")
            return
        if not selected_kbs:
            st.warning("Please select at least one knowledge base.")
            return

        with st.spinner("Retrieving and generating answer..."):
            response = pipeline.query(
                query=query,
                kb_names=selected_kbs,
                source_filter=source_filter or None,
                top_k=top_k,
            )

        st.markdown("### Answer")
        st.write(response["answer"])

        st.markdown("### Retrieved Context")
        for idx, result in enumerate(response["results"], start=1):
            metadata = result.get("metadata", {})
            with st.expander(
                f"#{idx} | KB: {metadata.get('kb')} | Source: {metadata.get('source')} | Title: {metadata.get('title')}",
                expanded=(idx == 1),
            ):
                st.write(result.get("content", ""))
                st.caption(f"URL: {metadata.get('url', '')}")
                st.caption(f"Type: {metadata.get('type', '')} | Distance: {result.get('distance')}")


if __name__ == "__main__":
    main()
