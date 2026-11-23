import streamlit as st

from dashboard.queries import get_executive_metrics
from dashboard.styling import (
    apply_dashboard_theme,
    render_dashboard_header,
    render_dashboard_footer,
)

st.set_page_config(
    page_title="VC Deal Flow Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_dashboard_theme()

with st.sidebar:
    st.markdown("## Deal Flow")
    st.caption("Investor intelligence workspace")
    st.divider()
    workspace_audience = st.selectbox(
        "Workspace focus",
        ["Founder / business", "Investor"],
        help="Choose the workflow you want to prioritize on this landing page.",
    )
    st.divider()
    st.markdown("**DATA STACK**")
    st.caption("Python · Snowflake · dbt · Streamlit · Prefect")
    st.divider()
    st.caption("Model context: 2026")

render_dashboard_header(
    title="VC Deal Flow Intelligence",
    subtitle="A decision workspace for discovering startups and identifying thesis-aligned investors.",
)

st.markdown(
    """
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
      <div>
        <div class="section-label">Decision workspace</div>
        <h2 style="margin:0;">Workspace overview</h2>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    metrics = get_executive_metrics()
    if not metrics.empty:
        row = metrics.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Startups analysed", f"{int(row['TOTAL_STARTUPS']):,}")
        c2.metric(
            "Recommendation records",
            f"{int(row['TOTAL_RECOMMENDATIONS']):,}",
            help="Rows in the recommendation mart; not confirmed investor interest or completed deals.",
        )
        c3.metric("Investors represented", f"{int(row['UNIQUE_INVESTORS']):,}")
        c4.metric(
            "Average compatibility",
            f"{float(row['AVG_COMPATIBILITY']):.1f}%",
            help="Estimated alignment across available matching dimensions.",
        )
    else:
        st.warning("Executive metrics are unavailable because the recommendation mart returned no data.")
except Exception as error:
    st.error("Executive metrics could not be loaded from Snowflake.")
    st.caption(str(error))

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

if workspace_audience == "Founder / business":
    st.subheader("Find relevant investors")
    st.caption("Start with your company profile, then review ranked matches and the evidence behind each score.")
    primary_page = "pages/2_Startup_Explorer.py"
    primary_label = "Open Startup Explorer"
    secondary_title = "Research investors"
    secondary_body = "Compare investor activity, compatibility and evidence coverage across the directory."
else:
    st.subheader("Explore the matching universe")
    st.caption("Review startup-to-investor alignment and investigate investor-level recommendation patterns.")
    primary_page = "pages/2_Startup_Explorer.py"
    primary_label = "Explore startup matches"
    secondary_title = "Investor landscape"
    secondary_body = "Screen investor profiles by type and headquarters, then compare their modeled matches."

primary, secondary = st.columns([1.2, 1])
with primary:
    st.markdown(
        """
        <div class="product-card">
            <div class="card-icon">01</div>
            <h3>Startup Explorer</h3>
            <p>Review company profiles, ranked investor recommendations, match quality and score drivers.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(primary_page, label=primary_label)
with secondary:
    st.markdown(
        f"""
        <div class="product-card">
            <div class="card-icon">02</div>
            <h3>{secondary_title}</h3>
            <p>{secondary_body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/3_Investor_Explorer.py", label="Open Investor Explorer")

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

left, right = st.columns([2, 1])
with left:
    st.info(
        "The system estimates investor-startup alignment. It does not represent verified investor interest "
        "or investment probability."
    )
with right:
    st.page_link("pages/3_Matching_Methodology.py", label="Review scoring methodology")

render_dashboard_footer()