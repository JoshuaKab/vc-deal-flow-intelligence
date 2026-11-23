import streamlit as st
import plotly.express as px

from dashboard.queries import (
    get_executive_metrics,
    get_matching_analytics
)

from dashboard.styling import (
    apply_dashboard_theme,
    render_dashboard_header,
    render_section_header,
    render_dashboard_footer
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Matching Analytics | VC Deal Flow Intelligence",
    page_icon="📈",
    layout="wide"
)

apply_dashboard_theme()


# ==================================================
# PAGE HEADER
# ==================================================

render_dashboard_header(
    title="Matching Analytics",
    subtitle=(
        "Performance monitoring and analytical insights "
        "from the startup-investor matching engine."
    )
)


# ==================================================
# LOAD ANALYTICS DATA
# ==================================================

try:

    metrics_df = get_executive_metrics()
    matching_df = get_matching_analytics()

    if metrics_df.empty or matching_df.empty:

        st.warning("Matching analytics data is unavailable.")

    else:

        # ==========================================
        # OVERALL MATCHING PERFORMANCE
        # ==========================================

        render_section_header(
            "Overall Matching Performance",
            "Key performance indicators from the recommendation engine."
        )

        metrics = metrics_df.iloc[0]

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Startups",
                f"{int(metrics['TOTAL_STARTUPS']):,}"
            )

        with col2:
            st.metric(
                "Recommendations",
                f"{int(metrics['TOTAL_RECOMMENDATIONS']):,}"
            )

        with col3:
            st.metric(
                "Unique Investors",
                f"{int(metrics['UNIQUE_INVESTORS']):,}"
            )

        with col4:
            st.metric(
                "Average Compatibility",
                f"{metrics['AVG_COMPATIBILITY']:.2f}%"
            )

        with col5:
            st.metric(
                "Evidence Coverage",
                f"{metrics['AVG_EVIDENCE_COVERAGE']:.2f}%"
            )


        # ==========================================
        # COMPATIBILITY DISTRIBUTION
        # ==========================================

        st.divider()

        render_section_header(
            "Compatibility Score Distribution",
            "Distribution of recommendations across compatibility ranges."
        )

        chart_df = matching_df.copy()

        fig = px.bar(
            chart_df,
            x="COMPATIBILITY_RANGE",
            y="TOTAL_MATCHES",
            text="TOTAL_MATCHES",
            labels={
                "COMPATIBILITY_RANGE": "Compatibility Range",
                "TOTAL_MATCHES": "Number of Matches"
            },
            title="Investor Compatibility Distribution"
        )

        fig.update_layout(
            height=450,
            xaxis_title="Compatibility Range",
            yaxis_title="Number of Matches",
            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


        # ==========================================
        # DISTRIBUTION TABLE
        # ==========================================

        st.subheader("Compatibility Distribution Details")

        st.dataframe(
            chart_df,
            use_container_width=True,
            hide_index=True
        )


        # ==========================================
        # EVIDENCE COVERAGE ANALYSIS
        # ==========================================

        st.divider()

        render_section_header(
            "Evidence Coverage Analysis",
            "Average evidence availability across compatibility ranges."
        )

        fig2 = px.bar(
            chart_df,
            x="COMPATIBILITY_RANGE",
            y="AVG_EVIDENCE_COVERAGE",
            text_auto=".2f",
            labels={
                "COMPATIBILITY_RANGE": "Compatibility Range",
                "AVG_EVIDENCE_COVERAGE": "Average Evidence Coverage (%)"
            },
            title="Evidence Coverage by Compatibility Range"
        )

        fig2.update_layout(
            height=450,
            xaxis_title="Compatibility Range",
            yaxis_title="Evidence Coverage (%)",
            showlegend=False
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )


        # ==========================================
        # ANALYTICAL INTERPRETATION
        # ==========================================

        st.divider()

        render_section_header(
            "Analytical Interpretation",
            "Understanding the matching engine's results."
        )

        st.markdown(
            """
            **Compatibility distribution**

            Shows how recommendations are distributed across
            different estimated compatibility score ranges.

            **Evidence coverage**

            Indicates the availability of information used
            by the matching engine. Higher coverage means
            more scoring dimensions contributed to the result.
            """
        )

        st.info(
            "Compatibility scores are estimated alignment scores, "
            "not investment probabilities. Evidence coverage measures "
            "information availability, not data accuracy."
        )

except Exception as error:
    st.error("Matching analytics could not be loaded.")
    st.exception(error)


render_dashboard_footer()