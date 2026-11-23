import os

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.ai_insights import AIInsightsError, generate_ai_decision_brief
from dashboard.queries import get_startup_list, get_startup_recommendations
from dashboard.styling import (
    apply_dashboard_theme,
    render_dashboard_header,
    render_section_header,
    render_dashboard_footer,
)

st.set_page_config(
    page_title="Startup Explorer | VC Deal Flow Intelligence",
    page_icon="◆",
    layout="wide",
)
apply_dashboard_theme()

render_dashboard_header(
    title="Startup Explorer",
    subtitle="Screen a company and identify the investors most aligned with its profile.",
)

try:
    startups = get_startup_list()
except Exception as error:
    st.error("Startup records could not be loaded.")
    st.exception(error)
    render_dashboard_footer()
    st.stop()

if startups.empty:
    st.warning("No startup records are available.")
    render_dashboard_footer()
    st.stop()

render_section_header("Company search", "Search or filter the startup universe.")

search_col, stage_col, country_col = st.columns([2, 1, 1])
with search_col:
    search = st.text_input("Search by company name", placeholder="Company name")
with stage_col:
    stages = ["All"] + sorted(startups["STARTUP_STAGE"].dropna().astype(str).unique().tolist())
    selected_stage = st.selectbox("Development stage", stages)
with country_col:
    countries = ["All"] + sorted(startups["STARTUP_COUNTRY"].dropna().astype(str).unique().tolist())
    selected_country = st.selectbox("Country", countries)

filtered = startups.copy()
if search:
    filtered = filtered[
        filtered["COMPANY_NAME"].fillna("").str.contains(search, case=False, regex=False)
    ]
if selected_stage != "All":
    filtered = filtered[filtered["STARTUP_STAGE"].astype(str) == selected_stage]
if selected_country != "All":
    filtered = filtered[filtered["STARTUP_COUNTRY"].astype(str) == selected_country]

if filtered.empty:
    st.warning("No startups match the current filters.")
    render_dashboard_footer()
    st.stop()

selected_name = st.selectbox(
    "Select startup",
    filtered["COMPANY_NAME"].tolist(),
)
selected = filtered[filtered["COMPANY_NAME"] == selected_name].iloc[0]
company_id = selected["COMPANY_ID"]

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

render_section_header("Startup profile", "Available company and investment characteristics.")

p1, p2, p3, p4 = st.columns(4)
p1.metric("Company", str(selected["COMPANY_NAME"]))
p2.metric("Industry", str(selected["STARTUP_INDUSTRY"]))
p3.metric("Country", str(selected["STARTUP_COUNTRY"]))
p4.metric("Stage", str(selected["STARTUP_STAGE"]))

recommendations = get_startup_recommendations(company_id)
if recommendations.empty:
    st.warning("No investor recommendations are available for this startup.")
    render_dashboard_footer()
    st.stop()

st.divider()
render_section_header(
    "Top investor recommendations",
    "Filter ranked matches by estimated fit and the amount of evidence available.",
)

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    minimum_compatibility = st.slider(
        "Minimum compatibility score",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
        format="%d%%",
    )
with filter_col2:
    minimum_evidence = st.slider(
        "Minimum evidence coverage",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
        format="%d%%",
    )

recommendations = recommendations[
    (recommendations["COMPATIBILITY_SCORE"] >= minimum_compatibility)
    & (recommendations["EVIDENCE_COVERAGE"] * 100 >= minimum_evidence)
].copy()

if recommendations.empty:
    st.warning("No recommendations meet both selected thresholds.")
    render_dashboard_footer()
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Matches shown", f"{len(recommendations):,}")
k2.metric("Median compatibility", f"{recommendations['COMPATIBILITY_SCORE'].median():.1f}%")
k3.metric(
    "Average evidence coverage",
    f"{recommendations['EVIDENCE_COVERAGE'].mean() * 100:.1f}%",
)
high_support = recommendations[
    (recommendations["COMPATIBILITY_SCORE"] >= 80)
    & (recommendations["EVIDENCE_COVERAGE"] >= 0.70)
]
k4.metric(
    "High fit + evidence",
    f"{len(high_support):,} ({len(high_support) / len(recommendations) * 100:.0f}%)",
    help="Matches with compatibility at least 80% and evidence coverage at least 70%.",
)

ranking_tab, quality_tab, evidence_tab = st.tabs(
    ["Recommendation ranking", "Match quality", "Score drivers"]
)

with ranking_tab:
    left, right = st.columns([1.55, 1])
    with left:
        display = recommendations[
            [
                "RECOMMENDATION_RANK",
                "INVESTOR_NAME",
                "INVESTOR_TYPE",
                "INVESTOR_HQ_COUNTRY",
                "COMPATIBILITY_SCORE",
                "COMPATIBILITY_BAND",
                "EVIDENCE_COVERAGE",
            ]
        ].copy()
        display["EVIDENCE_COVERAGE"] = display["EVIDENCE_COVERAGE"] * 100
        display = display.rename(
            columns={
                "RECOMMENDATION_RANK": "Rank",
                "INVESTOR_NAME": "Investor",
                "INVESTOR_TYPE": "Type",
                "INVESTOR_HQ_COUNTRY": "HQ",
                "COMPATIBILITY_SCORE": "Compatibility %",
                "COMPATIBILITY_BAND": "Band",
                "EVIDENCE_COVERAGE": "Evidence %",
            }
        )
        st.dataframe(display, use_container_width=True, hide_index=True)

    with right:
        chart = recommendations.sort_values("COMPATIBILITY_SCORE", ascending=True)
        fig = px.bar(
            chart,
            x="COMPATIBILITY_SCORE",
            y="INVESTOR_NAME",
            orientation="h",
            text="COMPATIBILITY_SCORE",
            color="COMPATIBILITY_SCORE",
            color_continuous_scale=["#dbe4ff", "#3157d5"],
            labels={
                "COMPATIBILITY_SCORE": "Compatibility",
                "INVESTOR_NAME": "Investor",
            },
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig.update_layout(
            height=430,
            template="plotly_white",
            coloraxis_showscale=False,
            margin=dict(l=10, r=30, t=20, b=30),
            xaxis=dict(range=[0, 105], title="Compatibility score"),
            yaxis=dict(title=None),
        )
        st.plotly_chart(fig, use_container_width=True)

with quality_tab:
    scatter_data = recommendations.copy()
    scatter_data["EVIDENCE_COVERAGE_PCT"] = scatter_data["EVIDENCE_COVERAGE"] * 100
    fig = px.scatter(
        scatter_data,
        x="EVIDENCE_COVERAGE_PCT",
        y="COMPATIBILITY_SCORE",
        color="COMPATIBILITY_BAND",
        hover_name="INVESTOR_NAME",
        hover_data={
            "INVESTOR_TYPE": True,
            "INVESTOR_HQ_COUNTRY": True,
            "EVIDENCE_COVERAGE_PCT": ":.1f",
            "COMPATIBILITY_SCORE": ":.1f",
        },
        labels={
            "EVIDENCE_COVERAGE_PCT": "Evidence coverage (%)",
            "COMPATIBILITY_SCORE": "Compatibility score (%)",
            "COMPATIBILITY_BAND": "Compatibility band",
        },
        color_discrete_sequence=["#3157d5", "#5b7be5", "#9aa9c5", "#d0d7e5"],
    )
    fig.add_vline(
        x=70,
        line_dash="dash",
        line_color="#98a2b3",
        annotation_text="70% evidence",
    )
    fig.add_hline(
        y=80,
        line_dash="dash",
        line_color="#98a2b3",
        annotation_text="80% compatibility",
    )
    fig.update_layout(
        height=500,
        template="plotly_white",
        xaxis=dict(range=[0, 105]),
        yaxis=dict(range=[0, 105]),
        legend_title_text="",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "The reference lines are screening guides, not validated confidence or investment-probability thresholds."
    )

with evidence_tab:
    score_columns = [
        "INVESTOR_NAME",
        "SEMANTIC_SCORE",
        "INDUSTRY_SCORE",
        "GEOGRAPHY_SCORE",
        "STAGE_SCORE",
        "TECHNOLOGY_SCORE",
        "ACTIVITY_SCORE",
        "BUSINESS_MODEL_SCORE",
    ]
    score_detail = recommendations[score_columns].rename(
        columns={
            "INVESTOR_NAME": "Investor",
            "SEMANTIC_SCORE": "Semantic",
            "INDUSTRY_SCORE": "Industry",
            "GEOGRAPHY_SCORE": "Geography",
            "STAGE_SCORE": "Stage",
            "TECHNOLOGY_SCORE": "Technology",
            "ACTIVITY_SCORE": "Activity",
            "BUSINESS_MODEL_SCORE": "Business model",
        }
    )
    st.dataframe(score_detail, use_container_width=True, hide_index=True)

    heatmap_columns = [
        "SEMANTIC_SCORE",
        "INDUSTRY_SCORE",
        "GEOGRAPHY_SCORE",
        "STAGE_SCORE",
        "TECHNOLOGY_SCORE",
        "ACTIVITY_SCORE",
        "BUSINESS_MODEL_SCORE",
    ]
    heatmap_data = recommendations.nsmallest(10, "RECOMMENDATION_RANK")[
        ["INVESTOR_NAME", *heatmap_columns]
    ].copy()
    heatmap_data[heatmap_columns] = heatmap_data[heatmap_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )
    heatmap_data = heatmap_data.rename(
        columns={
            "SEMANTIC_SCORE": "Semantic",
            "INDUSTRY_SCORE": "Industry",
            "GEOGRAPHY_SCORE": "Geography",
            "STAGE_SCORE": "Stage",
            "TECHNOLOGY_SCORE": "Technology",
            "ACTIVITY_SCORE": "Activity",
            "BUSINESS_MODEL_SCORE": "Business model",
        }
    )
    heatmap = px.imshow(
        heatmap_data.set_index("INVESTOR_NAME"),
        text_auto=".0f",
        aspect="auto",
        color_continuous_scale=["#f1f5fb", "#3157d5"],
        zmin=0,
        zmax=100,
        labels={"x": "Scoring dimension", "y": "Investor", "color": "Score"},
    )
    heatmap.update_layout(
        height=max(350, len(heatmap_data) * 42),
        template="plotly_white",
        margin=dict(l=10, r=10, t=25, b=35),
    )
    st.plotly_chart(heatmap, use_container_width=True)

    radar_source = recommendations.iloc[0]
    radar_df = pd.DataFrame(
        {
            "Dimension": [
                "Semantic",
                "Industry",
                "Geography",
                "Stage",
                "Technology",
                "Activity",
                "Business model",
            ],
            "Score": [
                radar_source["SEMANTIC_SCORE"],
                radar_source["INDUSTRY_SCORE"],
                radar_source["GEOGRAPHY_SCORE"],
                radar_source["STAGE_SCORE"],
                radar_source["TECHNOLOGY_SCORE"],
                radar_source["ACTIVITY_SCORE"],
                radar_source["BUSINESS_MODEL_SCORE"],
            ],
        }
    )
    fig = px.line_polar(
        radar_df,
        r="Score",
        theta="Dimension",
        line_close=True,
    )
    fig.update_traces(fill="toself", line_color="#3157d5")
    fig.update_layout(
        height=470,
        template="plotly_white",
        title=f"Score profile: {radar_source['INVESTOR_NAME']}",
        polar=dict(radialaxis=dict(range=[0, 100], showticklabels=True)),
    )
    st.plotly_chart(fig, use_container_width=True)

with st.expander("AI decision brief (OpenAI)", expanded=False):
    st.write(
        "Generate cautious, evidence-based suggestions for prioritizing investor "
        "outreach and deciding what to verify next."
    )
    st.caption(
        "With your confirmation, the app sends the startup's industry, country and "
        "stage plus up to five anonymized match records (investor type, HQ country, "
        "scores and evidence coverage) to OpenAI. Company and investor names and "
        "IDs are not sent."
    )
    with st.form("ai_decision_brief_form"):
        consent = st.checkbox(
            "I agree to send these selected fields to OpenAI for this brief."
        )
        generate_brief = st.form_submit_button("Generate AI decision brief")

    if generate_brief:
        if not consent:
            st.warning("Confirm the data-sharing notice before requesting a brief.")
        else:
            openai_settings = st.secrets.get("openai", {})
            api_key = os.environ.get("OPENAI_API_KEY") or openai_settings.get(
                "api_key",
                "",
            )
            model = os.environ.get("OPENAI_MODEL") or openai_settings.get(
                "model",
                "gpt-4o-mini",
            )
            if not api_key:
                st.error(
                    "OpenAI is not configured. Set OPENAI_API_KEY or add "
                    "[openai].api_key to Streamlit secrets."
                )
            else:
                with st.spinner("Generating a decision brief..."):
                    try:
                        brief = generate_ai_decision_brief(
                            {
                                "STARTUP_INDUSTRY": selected["STARTUP_INDUSTRY"],
                                "STARTUP_COUNTRY": selected["STARTUP_COUNTRY"],
                                "STARTUP_STAGE": selected["STARTUP_STAGE"],
                            },
                            recommendations.to_dict(orient="records"),
                            api_key=api_key,
                            model=model,
                        )
                    except AIInsightsError as error:
                        st.error(str(error))
                    else:
                        st.markdown(brief)
                        st.caption(
                            "AI-generated decision support, not investment advice. "
                            "Verify all claims and use human judgment."
                        )

st.info(
    "Compatibility estimates thesis alignment; it is not a forecast of investment or confirmed investor interest."
)

render_dashboard_footer()
