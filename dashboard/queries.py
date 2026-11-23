import pandas as pd
import streamlit as st

from dashboard.connection import get_snowflake_connection


# --------------------------------------------------
# EXECUTE SQL QUERY
# --------------------------------------------------

def execute_query(query, params=None):

    connection = get_snowflake_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(query, params)

        results = cursor.fetchall()

        columns = [column[0] for column in cursor.description]

        return results, columns

    finally:

        cursor.close()


# --------------------------------------------------
# GET ANALYTICS MART COUNTS
# --------------------------------------------------

@st.cache_data(ttl=300)

def get_mart_table_counts():

    tables = [
        "MART_TOP_INVESTOR_RECOMMENDATIONS",
        "MART_INVESTOR_PERFORMANCE",
        "MART_STARTUP_MATCHING_PERFORMANCE"
    ]

    counts = {}

    for table in tables:

        query = f"""
            SELECT COUNT(*)
            FROM VC_DEAL_FLOW_DB.DBT_DEV.{table}
        """

        results, _ = execute_query(query)

        counts[table] = results[0][0]

    return counts


# --------------------------------------------------
# EXECUTIVE OVERVIEW METRICS
# --------------------------------------------------

@st.cache_data(ttl=300)
def get_executive_metrics():

    query = """
        SELECT
            COUNT(DISTINCT COMPANY_ID) AS TOTAL_STARTUPS,
            COUNT(*) AS TOTAL_RECOMMENDATIONS,
            COUNT(DISTINCT INVESTOR_SLUG) AS UNIQUE_INVESTORS,
            ROUND(AVG(COMPATIBILITY_SCORE), 2) AS AVG_COMPATIBILITY,
            ROUND(AVG(EVIDENCE_COVERAGE) * 100, 2) AS AVG_EVIDENCE_COVERAGE
        FROM VC_DEAL_FLOW_DB.DBT_DEV.MART_TOP_INVESTOR_RECOMMENDATIONS
    """

    results, columns = execute_query(query)

    return pd.DataFrame(results, columns=columns)


# --------------------------------------------------
# TOP 10 RECOMMENDED INVESTORS
# --------------------------------------------------

@st.cache_data(ttl=300)
def get_top_investors():

    query = """
        SELECT
            INVESTOR_NAME,
            TOTAL_RECOMMENDATIONS,
            AVG_COMPATIBILITY_SCORE,
            AVG_RECOMMENDATION_RANK
        FROM VC_DEAL_FLOW_DB.DBT_DEV.MART_INVESTOR_PERFORMANCE
        ORDER BY TOTAL_RECOMMENDATIONS DESC
        LIMIT 10
    """

    results, columns = execute_query(query)

    return pd.DataFrame(results, columns=columns)

    # --------------------------------------------------
# STARTUP EXPLORER
# --------------------------------------------------

@st.cache_data(ttl=300)
def get_startup_list():

    query = """
        SELECT DISTINCT
            COMPANY_ID,
            COMPANY_NAME,
            STARTUP_INDUSTRY,
            STARTUP_COUNTRY,
            STARTUP_STAGE
        FROM VC_DEAL_FLOW_DB.DBT_DEV.MART_TOP_INVESTOR_RECOMMENDATIONS
        ORDER BY COMPANY_NAME
    """

    results, columns = execute_query(query)

    return pd.DataFrame(results, columns=columns)


# --------------------------------------------------
# GET RECOMMENDATIONS FOR SELECTED STARTUP
# --------------------------------------------------

@st.cache_data(ttl=300)
def get_startup_recommendations(company_id):

    query = """
        SELECT
            RECOMMENDATION_RANK,
            INVESTOR_NAME,
            INVESTOR_TYPE,
            INVESTOR_HQ_COUNTRY,
            COMPATIBILITY_SCORE,
            COMPATIBILITY_BAND,
            EVIDENCE_COVERAGE,
            SEMANTIC_SCORE,
            INDUSTRY_SCORE,
            GEOGRAPHY_SCORE,
            STAGE_SCORE,
            TECHNOLOGY_SCORE,
            ACTIVITY_SCORE,
            BUSINESS_MODEL_SCORE
        FROM VC_DEAL_FLOW_DB.DBT_DEV.MART_TOP_INVESTOR_RECOMMENDATIONS
        WHERE COMPANY_ID = %s
        ORDER BY RECOMMENDATION_RANK
    """

    results, columns = execute_query(query, (company_id,))

    return pd.DataFrame(results, columns=columns)


@st.cache_data(ttl=300)
def get_investor_list():

    #import pandas as pd

    query = """
        SELECT
            INVESTOR_SLUG,
            INVESTOR_NAME,
            INVESTOR_TYPE,
            INVESTOR_HQ_COUNTRY,
            TOTAL_RECOMMENDATIONS,
            UNIQUE_STARTUPS_MATCHED AS UNIQUE_STARTUPS_RECOMMENDED,
            FIRST_PLACE_RANKINGS,
            AVG_COMPATIBILITY_SCORE,
            AVG_RECOMMENDATION_RANK,
            AVG_EVIDENCE_COVERAGE_PCT AS AVG_EVIDENCE_COVERAGE,
            BEST_COMPATIBILITY_SCORE

        FROM VC_DEAL_FLOW_DB.DBT_DEV.MART_INVESTOR_PERFORMANCE

        ORDER BY TOTAL_RECOMMENDATIONS DESC
    """

    results, columns = execute_query(query)

    return pd.DataFrame(results, columns=columns)

@st.cache_data(ttl=300)
def get_matching_analytics():

    query = """
        WITH SCORE_BUCKETS AS (
            SELECT
                CASE
                    WHEN COMPATIBILITY_SCORE < 60 THEN 1
                    WHEN COMPATIBILITY_SCORE < 70 THEN 2
                    WHEN COMPATIBILITY_SCORE < 80 THEN 3
                    WHEN COMPATIBILITY_SCORE < 90 THEN 4
                    ELSE 5
                END AS BUCKET_ID,
                COMPATIBILITY_SCORE,
                EVIDENCE_COVERAGE
            FROM VC_DEAL_FLOW_DB.DBT_DEV.MART_TOP_INVESTOR_RECOMMENDATIONS
        )
        SELECT
            CASE BUCKET_ID
                WHEN 1 THEN 'Below 60%'
                WHEN 2 THEN '60% - 69.99%'
                WHEN 3 THEN '70% - 79.99%'
                WHEN 4 THEN '80% - 89.99%'
                ELSE '90% - 100%'
            END AS COMPATIBILITY_RANGE,
            COUNT(*) AS TOTAL_MATCHES,
            ROUND(AVG(COMPATIBILITY_SCORE), 2) AS AVG_COMPATIBILITY,
            ROUND(AVG(EVIDENCE_COVERAGE) * 100, 2) AS AVG_EVIDENCE_COVERAGE
        FROM SCORE_BUCKETS
        GROUP BY BUCKET_ID
        ORDER BY BUCKET_ID
    """

    results, columns = execute_query(query)

    return pd.DataFrame(results, columns=columns)


def get_data_quality_metrics():

    query = """
        SELECT
            'Missing Startup IDs' AS CHECK_NAME,
            COALESCE(COUNT_IF(COMPANY_ID IS NULL), 0) AS ISSUE_COUNT
        FROM VC_DEAL_FLOW_DB.DBT_DEV.MART_TOP_INVESTOR_RECOMMENDATIONS

        UNION ALL

        SELECT
            'Missing Investor Identifiers',
            COALESCE(COUNT_IF(INVESTOR_SLUG IS NULL), 0)
        FROM VC_DEAL_FLOW_DB.DBT_DEV.MART_TOP_INVESTOR_RECOMMENDATIONS

        UNION ALL

        SELECT
            'Missing Compatibility Scores',
            COALESCE(COUNT_IF(COMPATIBILITY_SCORE IS NULL), 0)
        FROM VC_DEAL_FLOW_DB.DBT_DEV.MART_TOP_INVESTOR_RECOMMENDATIONS

        UNION ALL

        SELECT
            'Invalid Compatibility Scores',
            COALESCE(COUNT_IF(
                COMPATIBILITY_SCORE < 0
                OR COMPATIBILITY_SCORE > 100
            ), 0)
        FROM VC_DEAL_FLOW_DB.DBT_DEV.MART_TOP_INVESTOR_RECOMMENDATIONS

        UNION ALL

        SELECT
            'Missing Evidence Coverage',
            COALESCE(COUNT_IF(EVIDENCE_COVERAGE IS NULL), 0)
        FROM VC_DEAL_FLOW_DB.DBT_DEV.MART_TOP_INVESTOR_RECOMMENDATIONS

        UNION ALL

        SELECT
            'Duplicate Startup-Investor Pairs',
            COUNT(*)
        FROM (
            SELECT COMPANY_ID, INVESTOR_SLUG
            FROM VC_DEAL_FLOW_DB.DBT_DEV.MART_TOP_INVESTOR_RECOMMENDATIONS
            GROUP BY COMPANY_ID, INVESTOR_SLUG
            HAVING COUNT(*) > 1
        )
    """

    results, columns = execute_query(query)

    return pd.DataFrame(results, columns=columns)