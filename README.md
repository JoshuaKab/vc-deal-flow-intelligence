# VC Deal Flow Intelligence & Thesis Scoring Engine

An end-to-end data science and analytics platform that helps analyse startup-investor alignment through semantic matching, structured investment criteria and explainable multi-factor scoring.

The project combines machine learning, natural language processing, data engineering and interactive analytics to generate ranked investor recommendations for startups.

## Project Overview

The platform evaluates startup-investor compatibility using a multi-factor scoring engine. It analyses startup profiles and investor investment characteristics to identify potential alignment.

The resulting recommendations are presented through an interactive Streamlit dashboard powered by Snowflake analytics marts.

**Important:** Compatibility scores represent estimated thesis alignment. They are not investment probabilities, confirmed investor interest or verified investment mandates.

## Key Features

- **Startup Explorer:** Explore startup profiles and their top-ranked investor recommendations.
- **Investor Intelligence:** Analyse investor recommendation frequency and matching performance.
- **Semantic Matching:** Use sentence-transformer embeddings to measure textual similarity between startup and investor profiles.
- **Explainable Scoring:** Evaluate compatibility across seven dimensions.
- **Matching Analytics:** Explore compatibility distributions and evidence coverage.
- **Data Quality Monitoring:** Monitor missing identifiers, invalid scores and duplicate startup-investor pairs.
- **Executive Overview:** View key platform metrics and analytics.
- **Pipeline Orchestration:** Automate dbt builds and tests using Prefect.
- **Cloud Data Warehouse:** Store and transform startup, investor and recommendation data using Snowflake.

## Scoring Methodology

The matching engine evaluates seven dimensions:

| Scoring Dimension | Weight |
|---|---:|
| Semantic Similarity | 25% |
| Industry Alignment | 20% |
| Geographic Alignment | 15% |
| Investment Stage | 15% |
| Technology Alignment | 10% |
| Investor Activity | 10% |
| Business Model Alignment | 5% |
| **Total** | **100%** |

The final compatibility score uses the available scoring dimensions and renormalises their weights when evidence is missing.

Evidence coverage measures the availability of scoring evidence. It does not measure data accuracy.

## Project Dataset

The analytical platform contains:

| Dataset | Records |
|---|---:|
| Startup Profiles | 5,384 |
| Investor Profiles | 8,827 |
| Investor Recommendations | 107,680 |

The recommendation dataset contains the top 20 recommendations for each startup.

The Streamlit dashboard presents the top 10 recommendations per startup.

## Technology Stack

**Programming and Analytics**
- Python
- pandas
- NumPy
- Plotly

**Machine Learning and NLP**
- Sentence Transformers
- all-MiniLM-L6-v2
- Cosine Similarity

**Data Engineering**
- Snowflake
- dbt Fusion
- Prefect

**Dashboard**
- Streamlit

**AI Integration**
- OpenAI API (optional AI-generated decision briefs)

**Version Control and Deployment**
- Git
- GitHub
- Streamlit Community Cloud (planned deployment)

## Dashboard Pages

1. Executive Overview
2. Startup Explorer
3. Matching Methodology
4. Investor Intelligence
5. Matching Analytics
6. Data Quality & Pipeline Monitoring

## Project Architecture

```text
Startup & Investor Data
          |
          v
Data Cleaning & Feature Engineering
          |
          v
NLP Embeddings & Semantic Matching
          |
          v
Explainable Multi-Factor Scoring
          |
          v
Snowflake Data Warehouse
          |
          v
dbt Transformations & Analytics Marts
          |
          v
Prefect Pipeline Orchestration
          |
          v
Streamlit Analytics Dashboard
```

## Run Locally

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd vc_deal_flow_dbt_8
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Snowflake credentials

Create a file named:

```text
.streamlit/secrets.toml
```

Add your Snowflake connection settings:

```toml
[snowflake]
account = "YOUR_ACCOUNT"
user = "YOUR_USERNAME"
password = "YOUR_PASSWORD"
warehouse = "YOUR_WAREHOUSE"
database = "VC_DEAL_FLOW_DB"
schema = "DBT_DEV"
role = "YOUR_READ_ONLY_ROLE"
```

Never commit this file or expose your credentials publicly.

### 5. Launch the dashboard

```bash
python -m streamlit run app.py
```

## Security

- Snowflake credentials are stored outside the source code.
- Streamlit secrets are excluded through `.gitignore`.
- Public deployment should use a restricted, read-only Snowflake account.
- API keys must be configured through secure environment variables or hosting secrets.

## Project Status

The following components have been implemented:

- Data preparation and exploratory analysis
- Feature engineering
- NLP embeddings
- Semantic matching
- Explainable multi-factor scoring
- Snowflake integration
- dbt staging, intermediate and analytics models
- dbt testing and documentation
- Prefect pipeline orchestration
- Multi-page Streamlit dashboard

GitHub publication and public dashboard deployment are the next project milestones.

## Disclaimer

This platform is an analytical decision-support tool. Its recommendations are based on available startup and investor profile data and historical investment characteristics.

The system does not guarantee investment outcomes, verify investor mandates or establish confirmed investor interest.