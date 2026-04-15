# theme.py

from __future__ import annotations

import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            --bg-main: #f5f7fa;
            --bg-surface: #ffffff;
            --bg-surface-2: #f8fafc;

            --border-soft: rgba(15, 23, 42, 0.08);
            --border-mid: rgba(15, 23, 42, 0.14);

            --text-main: #0f172a;
            --text-soft: #475569;
            --text-muted: #64748b;

            --accent: #3b556e;
            --accent-soft: #6b8197;

            --success: #4f6f5d;
            --warning: #8a6b3f;
            --danger: #8b5e5e;

            --shadow-soft: 0 4px 14px rgba(15, 23, 42, 0.05);
            --shadow-mid: 0 10px 22px rgba(15, 23, 42, 0.06);

            --radius-lg: 16px;
            --radius-md: 12px;
            --radius-sm: 10px;
        }

        html, body, [class*="css"] {
            font-family: "Inter", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
        }

        .stApp {
            background: linear-gradient(180deg, #f7f9fc 0%, #f3f6fa 100%);
            color: var(--text-main);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #eef2f7 0%, #e9eef5 100%);
            border-right: 1px solid var(--border-soft);
        }

        .hero-box {
            background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
            border: 1px solid var(--border-mid);
            border-radius: var(--radius-lg);
            padding: 18px 20px 16px 20px;
            margin-bottom: 14px;
            box-shadow: var(--shadow-mid);
        }

        .main-title {
            font-size: 1.68rem;
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
            font-size: 0.79rem;
            color: var(--text-muted);
            line-height: 1.45;
        }

        .kpi-shell {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
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
            background: linear-gradient(180deg, #ffffff 0%, #fbfcfe 100%);
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-md);
            padding: 12px 14px;
            margin-bottom: 12px;
            box-shadow: var(--shadow-soft);
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-md);
            padding: 8px 10px;
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
            background: rgba(15, 23, 42, 0.03) !important;
            border-bottom: 2px solid var(--accent) !important;
        }

        .stButton > button {
            background: linear-gradient(180deg, #eef2f7 0%, #e8edf3 100%);
            color: var(--text-main);
            border: 1px solid var(--border-mid);
            border-radius: 10px;
            font-weight: 650;
            font-size: 0.84rem;
            padding: 0.52rem 0.95rem;
        }

        .stButton > button:hover {
            border-color: rgba(59, 85, 110, 0.28);
            color: #0f172a;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border-soft);
            border-radius: 12px;
            overflow: hidden;
            background: white;
        }

        div.block-container {
            padding-top: 1.2rem;
            padding-bottom: 1.4rem;
            max-width: 1500px;
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--text-main);
            letter-spacing: 0.01em;
        }

        .soft-divider {
            border: none;
            height: 1px;
            background: linear-gradient(
                to right,
                transparent,
                rgba(15, 23, 42, 0.10),
                transparent
            );
            margin: 8px 0 12px 0;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, subtitle: str):
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
