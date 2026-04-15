# theme.py

from __future__ import annotations

import streamlit as st


def apply_theme():
    """
    Institutional minimalist theme for the BIST Quant Terminal.

    Design principles:
    - serious and professional
    - low-saturation palette
    - compact KPI layout
    - clean spacing
    - restrained visual hierarchy
    - no overly bright / playful colors
    """

    st.markdown(
        """
        <style>
        :root {
            --bg-main: #0f1722;
            --bg-surface: #151f2d;
            --bg-surface-2: #1a2535;
            --bg-soft: #202c3f;

            --border-soft: rgba(255,255,255,0.06);
            --border-mid: rgba(255,255,255,0.10);

            --text-main: #e8edf5;
            --text-soft: #a8b4c4;
            --text-muted: #7f8b9c;

            --accent: #7f9bb8;
            --accent-strong: #93aeca;

            --success: #6f8f7b;
            --warning: #b89a68;
            --danger: #b27a7a;

            --shadow-soft: 0 6px 16px rgba(0,0,0,0.18);
            --shadow-mid: 0 10px 24px rgba(0,0,0,0.22);

            --radius-lg: 16px;
            --radius-md: 12px;
            --radius-sm: 10px;
        }

        html, body, [class*="css"] {
            font-family: "Inter", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
        }

        .stApp {
            background: linear-gradient(180deg, #0e1520 0%, #111a27 100%);
            color: var(--text-main);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #121b28 0%, #162130 100%);
            border-right: 1px solid var(--border-soft);
        }

        /* Main hero */
        .hero-box {
            background: linear-gradient(180deg, #162131 0%, #1a2636 100%);
            border: 1px solid var(--border-mid);
            border-radius: var(--radius-lg);
            padding: 18px 20px 16px 20px;
            margin-bottom: 14px;
            box-shadow: var(--shadow-mid);
        }

        .main-title {
            font-size: 1.72rem;
            font-weight: 750;
            color: var(--text-main);
            line-height: 1.2;
            letter-spacing: 0.01em;
            margin-bottom: 4px;
        }

        .sub-title {
            font-size: 0.93rem;
            color: var(--text-soft);
            line-height: 1.5;
            margin-bottom: 0;
        }

        .section-title {
            font-size: 0.96rem;
            font-weight: 700;
            color: var(--text-main);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 8px;
        }

        .small-note {
            font-size: 0.78rem;
            color: var(--text-muted);
            line-height: 1.45;
        }

        /* Compact institutional KPI shell */
        .kpi-shell {
            background: linear-gradient(180deg, #182334 0%, #1b2738 100%);
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-md);
            padding: 10px 12px;
            min-height: 86px;
            box-shadow: var(--shadow-soft);
        }

        .kpi-label {
            font-size: 0.64rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 4px;
        }

        .kpi-value {
            font-size: 1.00rem;
            font-weight: 750;
            color: var(--text-main);
            line-height: 1.18;
            margin-bottom: 3px;
        }

        .kpi-foot {
            font-size: 0.72rem;
            color: var(--text-soft);
            line-height: 1.35;
        }

        .panel-shell {
            background: linear-gradient(180deg, #161f2d 0%, #1a2434 100%);
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-md);
            padding: 12px 14px;
            margin-bottom: 12px;
            box-shadow: var(--shadow-soft);
        }

        .badge-pill {
            display: inline-block;
            background: rgba(127, 155, 184, 0.12);
            color: #d7e1ee;
            border: 1px solid rgba(147, 174, 202, 0.18);
            border-radius: 999px;
            padding: 0.20rem 0.58rem;
            font-size: 0.70rem;
            font-weight: 650;
            margin-right: 6px;
            margin-bottom: 6px;
        }

        /* Streamlit metric widgets toned down */
        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, #172130 0%, #1a2535 100%);
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-md);
            padding: 8px 10px;
            box-shadow: none;
        }

        div[data-testid="stMetricLabel"] {
            font-size: 0.64rem !important;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: var(--text-muted) !important;
            font-weight: 700 !important;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.00rem !important;
            font-weight: 750 !important;
            color: var(--text-main) !important;
        }

        div[data-testid="stMetricDelta"] {
            font-size: 0.72rem !important;
        }

        /* Tabs */
        button[data-baseweb="tab"] {
            background: transparent !important;
            color: var(--text-soft) !important;
            border-radius: 10px 10px 0 0 !important;
            font-size: 0.83rem !important;
            font-weight: 650 !important;
            padding: 10px 14px !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--text-main) !important;
            background: rgba(255,255,255,0.03) !important;
            border-bottom: 2px solid var(--accent) !important;
        }

        /* Inputs */
        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stNumberInput > div > div,
        .stDateInput > div > div {
            background-color: #182232 !important;
            border: 1px solid var(--border-soft) !important;
            border-radius: 10px !important;
            color: var(--text-main) !important;
        }

        /* Dataframe container */
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border-soft);
            border-radius: 12px;
            overflow: hidden;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(180deg, #223145 0%, #1c293a 100%);
            color: var(--text-main);
            border: 1px solid var(--border-mid);
            border-radius: 10px;
            font-weight: 650;
            font-size: 0.84rem;
            padding: 0.52rem 0.95rem;
        }

        .stButton > button:hover {
            border-color: rgba(147, 174, 202, 0.28);
            color: #ffffff;
        }

        /* Alerts toned down */
        div[data-baseweb="notification"] {
            border-radius: 12px !important;
            border: 1px solid var(--border-soft) !important;
        }

        /* Reduce visual clutter around block containers */
        div.block-container {
            padding-top: 1.2rem;
            padding-bottom: 1.4rem;
            max-width: 1500px;
        }

        /* Headings */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-main);
            letter-spacing: 0.01em;
        }

        /* Horizontal rule feel */
        .soft-divider {
            border: none;
            height: 1px;
            background: linear-gradient(
                to right,
                transparent,
                rgba(255,255,255,0.10),
                transparent
            );
            margin: 8px 0 12px 0;
        }

        /* Hide noisy default menu elements less aggressively if needed */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, subtitle: str):
    """
    Optional reusable hero renderer.
    """
    st.markdown(
        f"""
        <div class="hero-box">
            <div class="main-title">{title}</div>
            <div class="sub-title">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, foot: str = ""):
    """
    Optional compact KPI renderer.
    """
    st.markdown(
        f"""
        <div class="kpi-shell">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_panel_title(title: str, note: str | None = None):
    """
    Optional section title block.
    """
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
