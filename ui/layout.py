# ui/layout.py

from __future__ import annotations

import streamlit as st
from theme import render_kpi_card


def render_section_header(title: str, note: str | None = None):
    note_html = f'<div class="small-note">{note}</div>' if note else ""
    st.markdown(
        f"""
        <div class="panel-shell">
            <div class="section-title">{title}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_row(kpi_map: dict[str, tuple[str, str]]):
    items = list(kpi_map.items())
    cols = st.columns(len(items))

    for col, (label, (value, foot)) in zip(cols, items):
        with col:
            render_kpi_card(label, value, foot)
