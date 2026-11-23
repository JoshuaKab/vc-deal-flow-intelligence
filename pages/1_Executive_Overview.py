import plotly.express as px
import streamlit as st

from dashboard.connection import test_snowflake_connection
from dashboard.queries import (
    get_executive_metrics,
    get_mart_table_counts,
    get_top_investors,
)
from dashboard.styling import (
    apply_dashboard_theme,
    render_dashboard_header,
    render_section_header,
    render_dashboard_footer,
)

st.set_page_config(
    page_title="Executive Overview | VC Deal Flow Intelligence",
    page_icon="◆",
    layout="wide",
)
apply_dashboard_theme()

render_dashboard_header(
    title="Executive Overview",
    subtitle="Portfolio-scale matching activity, investor concentration and platform health.",
)

render_section_header("Platform status", "Live warehouse and analytics mart availability.")
try:
    connection = test_snowflake_connection()
    mart_counts = get_mart_table_counts()
    status_ok = True
except Exception as error:
    status_ok = False
    connection = None
    mart_counts = None

if status_ok:
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Warehouse", connection["warehouse"])
    s2.metric("Database", connection["database"])
    s3.metric("Analytics marts", "3 accessible")
    s4.metric(
        "Recommendation rows",
        f"{mart_counts['MART_TOP_INVESTOR_RECOMMENDATIONS']:,}",
    )
else:
    st.error("The Snowflake connection or analytics marts are unavailable.")
    st.caption(str(error))

st.divider()

render_section_header("Executive metrics", "Key coverage and matching indicators.")
try:
    metrics_df = get_executive_metrics()
    top_investors = get_top_investors()
except Exception as error:
    st.error("Executive analytics could not be loaded.")
    st.exception(error)
    render_dashboard_footer()
    st.stop()

if metrics_df.empty:
    st.warning("No executive metrics are available.")
else:
    metrics = metrics_df.iloc[0]
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Startups", f"{int(metrics['TOTAL_STARTUPS']):,}")
    m2.metric("Recommendations", f"{int(metrics['TOTAL_RECOMMENDATIONS']):,}")
    m3.metric("Unique investors", f"{int(metrics['UNIQUE_INVESTORS']):,}")
    m4.metric("Avg. compatibility", f"{float(metrics['AVG_COMPATIBILITY']):.1f}%")
    m5.metric("Evidence coverage", f"{float(metrics['AVG_EVIDENCE_COVERAGE']):.1f}%")

st.divider()

render_section_header("Investor concentration", "Investors appearing most often in the top-10 recommendations.")
if top_investors.empty:
    st.warning("No investor-ranking data is available.")
else:
    chart_col, table_col = st.columns([1.4, 1])

    with chart_col:
        chart_data = top_investors.sort_values("TOTAL_RECOMMENDATIONS", ascending=True)
        fig = px.bar(
            chart_data,
            x="TOTAL_RECOMMENDATIONS",
            y="INVESTOR_NAME",
            orientation="h",
            text="TOTAL_RECOMMENDATIONS",
            color="TOTAL_RECOMMENDATIONS",
            color_continuous_scale=["#dbe4ff", "#3157d5"],
            labels={
                "TOTAL_RECOMMENDATIONS": "Recommendations",
                "INVESTOR_NAME": "Investor",
            },
        )
        fig.update_layout(
            height=430,
            template="plotly_white",
            coloraxis_showscale=False,
            margin=dict(l=10, r=20, t=20, b=30),
            xaxis=dict(title="Recommendation volume"),
            yaxis=dict(title=None),
        )
        st.plotly_chart(fig, use_container_width=True)

    with table_col:
        display = top_investors.rename(
            columns={
                "INVESTOR_NAME": "Investor",
                "TOTAL_RECOMMENDATIONS": "Recommendations",
                "AVG_COMPATIBILITY_SCORE": "Avg. compatibility %",
                "AVG_RECOMMENDATION_RANK": "Avg. rank",
            }
        )
        st.dataframe(display, use_container_width=True, hide_index=True)

st.info(
    "Recommendation frequency reflects model output volume, not completed investments or confirmed investor interest."
)

render_dashboard_footer()
