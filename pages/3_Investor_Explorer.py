import streamlit as st
import plotly.express as px

from dashboard.queries import get_investor_list

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
    page_title="Investor Explorer | VC Deal Flow Intelligence",
    page_icon="🏦",
    layout="wide"
)

apply_dashboard_theme()


# ==================================================
# PAGE HEADER
# ==================================================

render_dashboard_header(
    title="Investor Explorer",
    subtitle=(
        "Explore investor profiles, recommendation activity "
        "and historical matching performance."
    )
)


# ==================================================
# LOAD INVESTOR DATA
# ==================================================

render_section_header(
    "Investor Intelligence",
    "Explore investors ranked by their recommendation activity."
)


try:

    investors_df = get_investor_list()

    if investors_df.empty:

        st.warning("No investor records found.")

    else:

        # ==========================================
        # SEARCH AND FILTERS
        # ==========================================

        st.subheader("Search and Filter Investors")

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:

            search = st.text_input(
                "Search investor by name",
                placeholder="Enter investor name..."
            )

        with col2:

            investor_types = sorted(
                investors_df["INVESTOR_TYPE"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_type = st.selectbox(
                "Filter by investor type",
                ["All"] + investor_types
            )

        with col3:
            countries = sorted(
                investors_df["INVESTOR_HQ_COUNTRY"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
            selected_country = st.selectbox(
                "Filter by HQ country",
                ["All"] + countries
            )


        # ==========================================
        # APPLY FILTERS
        # ==========================================

        filtered_df = investors_df.copy()

        if search:

            filtered_df = filtered_df[
                filtered_df["INVESTOR_NAME"]
                .str.contains(search, case=False, na=False)
            ]

        if selected_type != "All":

            filtered_df = filtered_df[
                filtered_df["INVESTOR_TYPE"] == selected_type
            ]

        if selected_country != "All":
            filtered_df = filtered_df[
                filtered_df["INVESTOR_HQ_COUNTRY"].astype(str) == selected_country
            ]


        # ==========================================
        # CHECK FILTER RESULTS
        # ==========================================

        if filtered_df.empty:

            st.warning(
                "No investors match your search or selected filters."
            )

        else:

            # ======================================
            # PERFORMANCE METRICS
            # ======================================

            st.divider()

            render_section_header(
                "Investor Performance",
                "Key performance indicators for the selected investors."
            )

            recommendation_total = filtered_df["TOTAL_RECOMMENDATIONS"].sum()
            if recommendation_total:
                weighted_compatibility = (
                    filtered_df["AVG_COMPATIBILITY_SCORE"]
                    * filtered_df["TOTAL_RECOMMENDATIONS"]
                ).sum() / recommendation_total
                weighted_evidence = (
                    filtered_df["AVG_EVIDENCE_COVERAGE"]
                    * filtered_df["TOTAL_RECOMMENDATIONS"]
                ).sum() / recommendation_total
            else:
                weighted_compatibility = None
                weighted_evidence = None

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Investors",
                    f"{len(filtered_df):,}"
                )

            with col2:

                st.metric(
                    "Recommendation records",
                    f"{recommendation_total:,}",
                    help="Modeled recommendation rows, not confirmed interest or completed deals.",
                )

            with col3:

                st.metric(
                    "Weighted compatibility",
                    f"{weighted_compatibility:.2f}%" if weighted_compatibility is not None else "—",
                    help="Investor compatibility averages weighted by recommendation volume.",
                )

            with col4:

                st.metric(
                    "Weighted evidence coverage",
                    f"{weighted_evidence:.1f}%" if weighted_evidence is not None else "—",
                    help="Evidence coverage weighted by recommendation volume.",
                )


            # ======================================
            # INVESTOR RECOMMENDATION CHART
            # ======================================

            st.divider()

            render_section_header(
                "Investor Recommendation Activity",
                "The 15 investors appearing most frequently in startup recommendations."
            )

            chart_df = (
                filtered_df
                .nlargest(15, "TOTAL_RECOMMENDATIONS")
                .sort_values(
                    "TOTAL_RECOMMENDATIONS",
                    ascending=True
                )
            )

            fig = px.bar(
                chart_df,
                x="TOTAL_RECOMMENDATIONS",
                y="INVESTOR_NAME",
                orientation="h",
                color="TOTAL_RECOMMENDATIONS",
                color_continuous_scale="Blues",
                labels={
                    "TOTAL_RECOMMENDATIONS": "Total Recommendations",
                    "INVESTOR_NAME": "Investor"
                },
                title="Top 15 Investors by Recommendation Volume"
            )

            fig.update_layout(
                height=600,
                template="plotly_white",
                showlegend=False,
                coloraxis_showscale=False,
                margin=dict(
                    l=20,
                    r=20,
                    t=60,
                    b=20
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.divider()

            render_section_header(
                "Compatibility and evidence",
                "Compare average modeled fit with the evidence coverage behind each investor's recommendations.",
            )

            scatter_data = filtered_df.dropna(
                subset=["AVG_COMPATIBILITY_SCORE", "AVG_EVIDENCE_COVERAGE"]
            )
            if scatter_data.empty:
                st.info("Compatibility and evidence data are unavailable for the current filters.")
            else:
                fig = px.scatter(
                    scatter_data,
                    x="AVG_COMPATIBILITY_SCORE",
                    y="AVG_EVIDENCE_COVERAGE",
                    size="TOTAL_RECOMMENDATIONS",
                    color="INVESTOR_TYPE",
                    hover_name="INVESTOR_NAME",
                    hover_data={
                        "INVESTOR_HQ_COUNTRY": True,
                        "TOTAL_RECOMMENDATIONS": ":,",
                        "AVG_COMPATIBILITY_SCORE": ":.1f",
                        "AVG_EVIDENCE_COVERAGE": ":.1f",
                    },
                    size_max=28,
                    labels={
                        "AVG_COMPATIBILITY_SCORE": "Average compatibility (%)",
                        "AVG_EVIDENCE_COVERAGE": "Average evidence coverage (%)",
                        "TOTAL_RECOMMENDATIONS": "Recommendation records",
                        "INVESTOR_TYPE": "Investor type",
                    },
                )
                fig.add_vline(x=80, line_dash="dash", line_color="#98a2b3")
                fig.add_hline(y=70, line_dash="dash", line_color="#98a2b3")
                fig.update_layout(
                    height=520,
                    template="plotly_white",
                    xaxis=dict(range=[0, 105]),
                    yaxis=dict(range=[0, 105]),
                    legend_title_text="",
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption(
                    "Bubble size reflects recommendation volume. Reference lines are screening guides, not validated confidence thresholds."
                )


            # ======================================
            # INVESTOR PERFORMANCE TABLE
            # ======================================

            st.divider()

            render_section_header(
                "Investor Performance Rankings",
                "Historical investor recommendation performance."
            )

            display_df = filtered_df[
                [
                    "INVESTOR_NAME",
                    "INVESTOR_TYPE",
                    "INVESTOR_HQ_COUNTRY",
                    "TOTAL_RECOMMENDATIONS",
                    "UNIQUE_STARTUPS_RECOMMENDED",
                    "FIRST_PLACE_RANKINGS",
                    "AVG_COMPATIBILITY_SCORE",
                    "AVG_RECOMMENDATION_RANK",
                    "AVG_EVIDENCE_COVERAGE",
                    "BEST_COMPATIBILITY_SCORE"
                ]
            ].copy()

            display_df = display_df.rename(
                columns={
                    "INVESTOR_NAME": "Investor",
                    "INVESTOR_TYPE": "Investor Type",
                    "INVESTOR_HQ_COUNTRY": "HQ Country",
                    "TOTAL_RECOMMENDATIONS": "Recommendations",
                    "UNIQUE_STARTUPS_RECOMMENDED": "Unique Startups",
                    "FIRST_PLACE_RANKINGS": "First-place Rankings",
                    "AVG_COMPATIBILITY_SCORE": "Average Compatibility (%)",
                    "AVG_RECOMMENDATION_RANK": "Average Rank",
                    "AVG_EVIDENCE_COVERAGE": "Evidence Coverage (%)",
                    "BEST_COMPATIBILITY_SCORE": "Best Compatibility (%)"
                }
            )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )


            # ======================================
            # DATA INTERPRETATION
            # ======================================

            st.info(
                "Investor performance reflects historical recommendations "
                "generated by the matching engine. It does not establish "
                "verified investor interest, investment mandates or "
                "investment probabilities."
            )


except Exception as error:

    st.error("Unable to load investor information.")

    st.exception(error)


# ==================================================
# FOOTER
# ==================================================

render_dashboard_footer()