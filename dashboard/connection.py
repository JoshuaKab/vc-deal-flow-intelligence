import streamlit as st
import snowflake.connector


@st.cache_resource
def get_snowflake_connection():
    """
    Establish and cache a connection to Snowflake.
    """

    connection = snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"],
        role=st.secrets["snowflake"]["role"],
        login_timeout=30
    )

    return connection


def test_snowflake_connection():
    """
    Test the Snowflake connection and return account details.
    """

    connection = get_snowflake_connection()

    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                CURRENT_ACCOUNT(),
                CURRENT_DATABASE(),
                CURRENT_SCHEMA(),
                CURRENT_WAREHOUSE(),
                CURRENT_ROLE()
        """)

        result = cursor.fetchone()

        return {
            "account": result[0],
            "database": result[1],
            "schema": result[2],
            "warehouse": result[3],
            "role": result[4]
        }

    finally:
        cursor.close()