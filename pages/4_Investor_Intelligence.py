import streamlit as st
import plotly.express as px

from dashboard.queries import get_top_investors

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
    page_title="Investor Intelligence | VC Deal Flow Intelligence",
    page_icon="🏦",
    layout="wide"
)

apply_dashboard_theme()


# ==================================================
# PAGE HEADER
# ==================================================

render_dashboard_header(
    title="Investor Intelligence",
    subtitle=(
        "Explore investor performance, recommendation "
        "frequency and startup-investor compatibility."
    )
)


# ==================================================
# LOAD INVESTOR DATA
# ==================================================

render_section_header(
    "Investor Performance",
    "Analysis of investors appearing in the recommendation engine."
)

try:

    investors_df = get_top_investors()

    if investors_df.empty:

        st.warning("No investor performance records found.")

    else:

        # ==========================================
        # KPI METRICS
        # ==========================================

        total_recommendations = int(
            investors_df["TOTAL_RECOMMENDATIONS"].sum()
        )

        average_compatibility = (
            investors_df["AVG_COMPATIBILITY_SCORE"].mean()
        )

        average_rank = (
            investors_df["AVG_RECOMMENDATION_RANK"].mean()
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Top 10 Recommendation Volume",
                f"{total_recommendations:,}"
            )

        with col2:
            st.metric(
                "Average Compatibility",
                f"{average_compatibility:.2f}%"
            )

        with col3:
            st.metric(
                "Average Recommendation Rank",
                f"{average_rank:.2f}"
            )


        # ==========================================
        # INVESTOR RANKINGS
        # ==========================================

        st.divider()

        render_section_header(
            "Top 10 Investors",
            "Investors ranked by the number of startup recommendations."
        )

        display_df = investors_df.copy()

        display_df = display_df.rename(
            columns={
                "INVESTOR_NAME": "Investor",
                "TOTAL_RECOMMENDATIONS": "Recommendations",
                "AVG_COMPATIBILITY_SCORE": "Average Compatibility (%)",
                "AVG_RECOMMENDATION_RANK": "Average Rank"
            }
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


        # ==========================================
        # RECOMMENDATION VOLUME CHART
        # ==========================================

        st.divider()

        render_section_header(
            "Investor Recommendation Volume",
            "Number of startup recommendations received by each investor."
        )

        fig = px.bar(
            investors_df.sort_values(
                "TOTAL_RECOMMENDATIONS",
                ascending=True
            ),
            x="TOTAL_RECOMMENDATIONS",
            y="INVESTOR_NAME",
            orientation="h",
            text="TOTAL_RECOMMENDATIONS",
            labels={
                "TOTAL_RECOMMENDATIONS": "Total Recommendations",
                "INVESTOR_NAME": "Investor"
            },
            title="Top 10 Investors by Recommendation Volume"
        )

        fig.update_layout(
            height=500,
            xaxis_title="Total Recommendations",
            yaxis_title="Investor",
            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


        # ==========================================
        # COMPATIBILITY COMPARISON
        # ==========================================

        st.divider()

        render_section_header(
            "Investor Compatibility Comparison",
            "Average compatibility scores across the top 10 investors."
        )

        fig2 = px.bar(
            investors_df.sort_values(
                "AVG_COMPATIBILITY_SCORE",
                ascending=False
            ),
            x="INVESTOR_NAME",
            y="AVG_COMPATIBILITY_SCORE",
            text_auto=".2f",
            labels={
                "INVESTOR_NAME": "Investor",
                "AVG_COMPATIBILITY_SCORE": "Average Compatibility (%)"
            },
            title="Average Investor Compatibility"
        )

        fig2.update_layout(
            height=450,
            xaxis_title="Investor",
            yaxis_title="Average Compatibility (%)",
            showlegend=False
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )


        # ==========================================
        # MODEL INTERPRETATION
        # ==========================================

        st.info(
            "Recommendation volume measures how frequently an investor "
            "appears in the platform's top-10 startup recommendations. "
            "It does not represent confirmed investor interest, "
            "completed investments or funding amounts."
        )


except Exception as error:

    st.error("Unable to load Investor Intelligence.")

    st.exception(error)


# ==================================================
# FOOTER
# ==================================================

render_dashboard_footer()