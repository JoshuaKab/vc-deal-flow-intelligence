import streamlit as st


# ==================================================
# DASHBOARD THEME
# ==================================================

def apply_dashboard_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
        :root {
            --ink: #172033;
            --muted: #667085;
            --blue: #3157d5;
            --blue-dark: #243f9e;
            --line: #e7eaf0;
            --surface: #ffffff;
            --canvas: #f6f7f9;
        }
        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
        .stApp { background: var(--canvas); }
        .block-container { padding-top: 1.25rem; padding-bottom: 3rem; max-width: 1480px; }
        [data-testid="stSidebar"] {
            background: #111827;
            border-right: 1px solid #263244;
        }
        [data-testid="stSidebar"] * { color: #f8fafc; }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #abb5c5; }
        [data-testid="stSidebar"] hr { border-color: #303b4d; }
        [data-testid="stSidebarNav"] { padding-top: 0.5rem; }
        [data-testid="stSidebarNav"] a {
            border-radius: 8px;
            padding: 0.55rem 0.75rem;
            margin: 0.12rem 0;
            color: #cbd5e1 !important;
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: #263756;
            color: #ffffff !important;
        }
        h1, h2, h3 { color: var(--ink); font-family: 'Manrope', sans-serif; }
        h1 { font-size: 2.05rem !important; letter-spacing: -0.04em; }
        h2 { font-size: 1.35rem !important; letter-spacing: -0.02em; }
        h3 { font-size: 1.08rem !important; }
        p, .stCaption { color: var(--muted); }
        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 18px 20px;
            box-shadow: 0 4px 14px rgba(23,32,51,0.035);
        }
        [data-testid="stMetricLabel"] { color: #758195; font-size: 0.78rem; font-weight: 600; }
        [data-testid="stMetricValue"] { color: var(--ink); font-family: 'Manrope', sans-serif; font-weight: 800; }
        [data-testid="stMetricDelta"] { font-weight: 600; }
        [data-testid="stDataFrame"], [data-testid="stTable"] {
            border: 1px solid var(--line);
            border-radius: 10px;
            overflow: hidden;
        }
        .stButton > button, .stDownloadButton > button {
            background: var(--blue);
            color: #fff;
            border: 1px solid var(--blue);
            border-radius: 7px;
            font-weight: 600;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            background: var(--blue-dark);
            color: #fff;
            border-color: var(--blue-dark);
        }
        [data-testid="stTextInput"] input,
        [data-testid="stSelectbox"] > div,
        [data-testid="stMultiSelect"] > div {
            border-radius: 7px;
        }
        hr { border-color: var(--line); }
        .dashboard-header {
            background: linear-gradient(125deg, #172033 0%, #243f9e 100%);
            padding: 27px 30px 25px 30px;
            border-radius: 12px;
            margin: 0.1rem 0 1.35rem 0;
            box-shadow: 0 12px 26px rgba(23,32,51,0.10);
        }
        .dashboard-header h1 { color: #fff; font-size: 1.8rem !important; margin: 0 0 7px 0; }
        .dashboard-header p { color: #d8e1fb; margin: 0; font-size: 0.96rem; }
        .section-label {
            color: var(--blue);
            font-size: 0.69rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1.55px;
            margin: 0.15rem 0 0.2rem 0;
        }
        .product-card {
            background: #fff;
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 22px;
            min-height: 150px;
            box-shadow: 0 4px 14px rgba(23,32,51,0.035);
        }
        .product-card h3 { margin: 8px 0 8px 0; }
        .product-card p { margin: 0; line-height: 1.55; }
        .card-icon {
            display: inline-flex;
            width: 34px;
            height: 34px;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            background: #edf2ff;
            color: var(--blue);
            font-size: 1.05rem;
        }
        .recommendation-card {
            background: #fff;
            border: 1px solid var(--line);
            border-left: 4px solid var(--blue);
            border-radius: 9px;
            padding: 15px 17px;
            margin-bottom: 10px;
        }
        .recommendation-card strong { color: var(--ink); }
        .dashboard-footer {
            text-align: center;
            color: #98a2b3;
            font-size: 0.78rem;
            padding: 24px 0 8px 0;
            border-top: 1px solid var(--line);
            margin-top: 36px;
        }
        [data-testid="stAlert"] { border-radius: 8px; }
        </style>
        """,
        unsafe_allow_html=True
    )


# ==================================================
# DASHBOARD HEADER
# ==================================================

# ==================================================
# DASHBOARD HEADER
# ==================================================

import textwrap


def render_dashboard_header(title, subtitle):

    header_html = textwrap.dedent(f"""
        <div class="dashboard-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
    """)

    st.markdown(
        header_html,
        unsafe_allow_html=True
    )


# ==================================================
# SECTION HEADER
# ==================================================

def render_section_header(
    title,
    description=None
):

    st.markdown(
        f"""
        <div class="section-label">
            ANALYTICS
        </div>

        <h3>{title}</h3>
        """,
        unsafe_allow_html=True
    )

    if description:

        st.caption(description)


# ==================================================
# DASHBOARD FOOTER
# ==================================================

def render_dashboard_footer():

    footer_html = """
    <div class="dashboard-footer">
    <div>
        VC Deal Flow Intelligence |
        AI-Powered Investor Discovery
    </div>

    <div style="margin-top: 18px;">
        Built with Python, Streamlit,
        Snowflake, dbt and Prefect.
    </div>
    </div>
"""

    st.markdown(
        footer_html,
        unsafe_allow_html=True
    )