import streamlit as st
import pandas as pd

from dashboard.queries import (
    get_mart_table_counts,
    get_data_quality_metrics
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
    page_title="Data Quality | VC Deal Flow Intelligence",
    page_icon="🛡️",
    layout="wide"
)

apply_dashboard_theme()


# ==================================================
# PAGE HEADER
# ==================================================

render_dashboard_header(
    title="Data Quality & Monitoring",
    subtitle=(
        "Monitor analytics data integrity, "
        "recommendation quality and database health."
    )
)


# ==================================================
# LOAD DATA
# ==================================================

try:

    mart_counts = get_mart_table_counts()

    quality_df = get_data_quality_metrics()

    total_issues = int(
        quality_df["ISSUE_COUNT"].sum()
    )

    passed_checks = int(
        (quality_df["ISSUE_COUNT"] == 0).sum()
    )

    total_checks = len(quality_df)


    # ==================================================
    # OVERALL QUALITY STATUS
    # ==================================================

    render_section_header(
        "Overall Data Quality Status",
        "Summary of the recommendation dataset validation."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Quality Checks",
            total_checks
        )

    with col2:
        st.metric(
            "Checks Passed",
            passed_checks
        )

    with col3:
        st.metric(
            "Total Quality Issues",
            total_issues
        )

    if total_issues == 0:

        st.success(
            "All data quality checks passed successfully. "
            "No issues were detected in the tested conditions."
        )

    else:

        st.warning(
            f"{total_issues:,} data quality issues detected. "
            "Review the validation results below."
        )


    # ==================================================
    # INDIVIDUAL QUALITY CHECKS
    # ==================================================

    st.divider()

    render_section_header(
        "Data Quality Checks",
        "Detailed results from the recommendation dataset."
    )

    for start in range(0, total_checks, 3):

        cols = st.columns(3)

        for index, col in enumerate(cols):

            row_index = start + index

            if row_index >= total_checks:
                break

            row = quality_df.iloc[row_index]

            check_name = row["CHECK_NAME"]

            issue_count = int(row["ISSUE_COUNT"])

            with col:

                st.metric(
                    label=check_name,
                    value=issue_count,
                    delta=(
                        "Passed" if issue_count == 0
                        else "Issues detected"
                    ),
                    delta_color=(
                        "normal" if issue_count == 0
                        else "inverse"
                    )
                )


    # ==================================================
    # QUALITY RESULTS TABLE
    # ==================================================

    st.divider()

    render_section_header(
        "Validation Results",
        "Complete data quality validation report."
    )

    display_df = quality_df.copy()

    display_df["STATUS"] = display_df[
        "ISSUE_COUNT"
    ].apply(
        lambda value: (
            "PASS" if value == 0 else "REVIEW REQUIRED"
        )
    )

    display_df = display_df.rename(
        columns={
            "CHECK_NAME": "Quality Check",
            "ISSUE_COUNT": "Issues Found",
            "STATUS": "Validation Status"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


    # ==================================================
    # ANALYTICS MART MONITORING
    # ==================================================

    st.divider()

    render_section_header(
        "Analytics Mart Monitoring",
        "Record counts from the three Snowflake analytics marts."
    )

    mart_labels = {
        "MART_TOP_INVESTOR_RECOMMENDATIONS":
            "Top Investor Recommendations",

        "MART_INVESTOR_PERFORMANCE":
            "Investor Performance",

        "MART_STARTUP_MATCHING_PERFORMANCE":
            "Startup Matching Performance"
    }

    mart_cols = st.columns(3)

    for index, (table, count) in enumerate(
        mart_counts.items()
    ):

        with mart_cols[index % 3]:

            st.metric(
                label=mart_labels.get(table, table),
                value=f"{count:,}"
            )


    # ==================================================
    # MONITORING SCOPE
    # ==================================================

    st.divider()

    render_section_header(
        "Monitoring Scope",
        "Understanding what this dashboard currently validates."
    )

    st.markdown(
        """
        **Data quality monitoring**

        - Missing startup identifiers.
        - Missing investor identifiers.
        - Missing compatibility scores.
        - Invalid compatibility scores.
        - Missing evidence coverage.
        - Duplicate startup-investor pairs.

        **Database monitoring**

        - Record counts across three analytics marts.
        - Snowflake analytics data availability.
        """
    )

    st.info(
        "These checks validate specific conditions in the "
        "top-10 investor recommendations mart. They do not "
        "measure all aspects of data accuracy or pipeline health. "
        "Prefect execution monitoring is not connected to this page."
    )


except Exception as error:

    st.error(
        "Unable to load Data Quality Monitoring."
    )

    st.exception(error)


# ==================================================
# FOOTER
# ==================================================

render_dashboard_footer()