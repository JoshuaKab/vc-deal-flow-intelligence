import streamlit as st

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
    page_title="Matching Methodology | VC Deal Flow Intelligence",
    page_icon="🎯",
    layout="wide"
)

apply_dashboard_theme()


# ==================================================
# PAGE HEADER
# ==================================================

render_dashboard_header(
    title="Investment Matching Methodology",
    subtitle=(
        "Understanding the explainable multi-factor "
        "startup-investor compatibility engine."
    )
)


# ==================================================
# INTRODUCTION
# ==================================================

render_section_header(
    "How the Matching Engine Works",
    "A structured approach to evaluating startup-investor alignment."
)

st.write(
    """
    The matching engine evaluates startup-investor compatibility
    using seven analytical dimensions.

    Each dimension contributes a weighted score to the final
    compatibility calculation. Missing evidence is excluded
    and the remaining weights are renormalised.
    """
)


# ==================================================
# SCORING DIMENSIONS
# ==================================================

render_section_header(
    "Scoring Dimensions",
    "The seven dimensions used to evaluate compatibility."
)

scoring_data = {
    "Dimension": [
        "Semantic Similarity",
        "Industry Alignment",
        "Geographic Alignment",
        "Investment Stage",
        "Technology Alignment",
        "Investor Activity",
        "Business Model Alignment"
    ],
    "Weight": [
        "25%",
        "20%",
        "15%",
        "15%",
        "10%",
        "10%",
        "5%"
    ],
    "Purpose": [
        "Measures similarity between startup and investor investment profiles.",
        "Evaluates alignment between startup industries and investor sector interests.",
        "Evaluates alignment with investor preferred investment countries.",
        "Evaluates alignment between startup development stage and historical investor activity.",
        "Measures alignment between startup technologies and investor sectors.",
        "Considers the investor's historical investment activity.",
        "Evaluates potential alignment between startup business models and investor sectors."
    ]
}

st.dataframe(
    scoring_data,
    use_container_width=True,
    hide_index=True
)


# ==================================================
# SCORING FORMULA
# ==================================================

st.divider()

render_section_header(
    "Compatibility Score",
    "How the final compatibility score is calculated."
)

st.latex(
    r"""
    C =
    \frac{\sum_{i=1}^{n} w_i s_i}
    {\sum_{i=1}^{n} w_i}
    \times 100
    """
)

st.markdown(
    """
    Where:

    - **C** = Final compatibility score.
    - **wᵢ** = Weight assigned to a scoring dimension.
    - **sᵢ** = Normalised score for that dimension.
    - **n** = Number of scoring dimensions with available evidence.
    """
)


# ==================================================
# EVIDENCE COVERAGE
# ==================================================

render_section_header(
    "Evidence Coverage",
    "Understanding the availability of information behind each score."
)

st.write(
    """
    Evidence coverage measures how much of the scoring framework
    has usable information for a particular startup-investor pair.

    A higher evidence coverage means more scoring dimensions
    contributed to the compatibility calculation.
    """
)

st.info(
    "Evidence coverage measures information availability, "
    "not data accuracy or recommendation confidence."
)


# ==================================================
# INTERPRETATION
# ==================================================

render_section_header(
    "Important Model Considerations",
    "How to interpret the recommendations responsibly."
)

st.markdown(
    """
    - Compatibility scores represent estimated alignment, not investment probability.
    - Recommendations do not confirm investor interest or willingness to invest.
    - Historical investment activity is used as an analytical proxy.
    - Missing information is not automatically treated as a negative match.
    - Investor headquarters are not treated as preferred investment geography.
    - The matching engine prioritises equity investors: VC, PE and CVC.
    """
)


# ==================================================
# FOOTER
# ==================================================

render_dashboard_footer()