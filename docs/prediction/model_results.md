# Prediction model results

Auto-generated when you run **Prediction** in the web UI or CLI. Rows within each model are ordered by predicted value (highest first).

- **Generated at:** 2026-07-26T23:55:03
- **Run id:** 2
- **Status:** completed
- **Training window (months):** 24
- **Horizons:** 3
- **Models:** baseline, prophet, sarima, arima, rf, hgb
- **Elapsed (seconds):** 744.239

## Time per model

| Model | Seconds |
|-------|---------|
| `baseline` | 0.089 |
| `prophet` | 730.561 |
| `sarima` | 3.011 |
| `arima` | 1.448 |
| `rf` | 4.702 |
| `hgb` | 4.39 |

## Training shortlist (historical top-K, not model ranking)

- **Roles used as forecast targets:** Data Analyst, Data Engineer, Data Scientist, ML Engineer, Analytics Engineer, AI Engineer, BI Developer, MLOps Engineer, Research Scientist, Product Analyst, Backend Engineer, Platform Engineer, Data Platform Engineer, NLP Engineer, Computer Vision Engineer
- **Skills used as forecast targets:** Python, SQL, Spark, Airflow, dbt, Tableau, Power BI, AWS, GCP, Azure, Kubernetes, TensorFlow, Docker, PyTorch, scikit-learn

## Model: `arima`

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| salary_role | NLP Engineer | 3 | 2026-10-01 | 5684 |
| salary_role | AI Engineer | 3 | 2026-10-01 | 5672 |
| salary_role | Computer Vision Engineer | 3 | 2026-10-01 | 5543 |
| salary_role | ML Engineer | 3 | 2026-10-01 | 5447 |
| salary_role | MLOps Engineer | 3 | 2026-10-01 | 5373 |
| salary_role | Data Platform Engineer | 3 | 2026-10-01 | 5320 |
| salary_role | Data Scientist | 3 | 2026-10-01 | 5200 |
| salary_role | Research Scientist | 3 | 2026-10-01 | 5164 |
| salary_role | Platform Engineer | 3 | 2026-10-01 | 5018 |
| salary_role | Backend Engineer | 3 | 2026-10-01 | 4839 |
| salary_role | Data Engineer | 3 | 2026-10-01 | 4773 |
| salary_role | Analytics Engineer | 3 | 2026-10-01 | 4393 |
| salary_role | BI Developer | 3 | 2026-10-01 | 4107 |
| salary_role | Product Analyst | 3 | 2026-10-01 | 4061 |
| salary_role | Data Analyst | 3 | 2026-10-01 | 3862 |
| skill | Spark | 3 | 2026-10-01 | 125.33 |
| skill | dbt | 3 | 2026-10-01 | 118.56 |
| skill | AWS | 3 | 2026-10-01 | 114.76 |
| skill | Power BI | 3 | 2026-10-01 | 114.21 |
| skill | Tableau | 3 | 2026-10-01 | 111.80 |
| skill | SQL | 3 | 2026-10-01 | 111.20 |
| skill | Python | 3 | 2026-10-01 | 111.19 |
| skill | GCP | 3 | 2026-10-01 | 111.03 |
| skill | Airflow | 3 | 2026-10-01 | 102.60 |
| skill | Docker | 3 | 2026-10-01 | 98.95 |
| skill | Azure | 3 | 2026-10-01 | 98.49 |
| skill | Kubernetes | 3 | 2026-10-01 | 96.96 |
| skill | scikit-learn | 3 | 2026-10-01 | 95.00 |
| skill | TensorFlow | 3 | 2026-10-01 | 80.38 |
| skill | PyTorch | 3 | 2026-10-01 | 59.87 |
| role | Data Analyst | 3 | 2026-10-01 | 37.58 |
| role | Data Engineer | 3 | 2026-10-01 | 32.58 |
| role | Data Scientist | 3 | 2026-10-01 | 30.69 |
| role | ML Engineer | 3 | 2026-10-01 | 25.36 |
| role | Analytics Engineer | 3 | 2026-10-01 | 22.27 |
| role | AI Engineer | 3 | 2026-10-01 | 20.39 |
| role | BI Developer | 3 | 2026-10-01 | 19.31 |
| role | MLOps Engineer | 3 | 2026-10-01 | 15.02 |
| role | Research Scientist | 3 | 2026-10-01 | 13.59 |
| role | Product Analyst | 3 | 2026-10-01 | 12.42 |
| role | Backend Engineer | 3 | 2026-10-01 | 11.34 |
| role | Platform Engineer | 3 | 2026-10-01 | 10.26 |
| role | Data Platform Engineer | 3 | 2026-10-01 | 9.86 |
| role | NLP Engineer | 3 | 2026-10-01 | 8.55 |
| role | Computer Vision Engineer | 3 | 2026-10-01 | 6.74 |

## Model: `baseline`

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| baseline_skill | SQL | 0 | — | 118 |
| baseline_skill | Spark | 0 | — | 110 |
| baseline_skill | Airflow | 0 | — | 107 |
| baseline_skill | dbt | 0 | — | 106 |
| baseline_skill | Python | 0 | — | 103 |
| baseline_skill | AWS | 0 | — | 95 |
| baseline_skill | GCP | 0 | — | 95 |
| baseline_skill | Tableau | 0 | — | 90 |
| baseline_skill | Azure | 0 | — | 87 |
| baseline_skill | Power BI | 0 | — | 87 |
| baseline_skill | Docker | 0 | — | 81 |
| baseline_skill | Kubernetes | 0 | — | 80 |
| baseline_skill | TensorFlow | 0 | — | 74 |
| baseline_skill | PyTorch | 0 | — | 71 |
| baseline_skill | scikit-learn | 0 | — | 69 |
| baseline_role | Data Engineer | 0 | — | 30 |
| baseline_role | Data Scientist | 0 | — | 29 |
| baseline_role | Data Analyst | 0 | — | 26 |
| baseline_role | Backend Engineer | 0 | — | 20 |
| baseline_role | ML Engineer | 0 | — | 17 |
| baseline_role | BI Developer | 0 | — | 16 |
| baseline_role | AI Engineer | 0 | — | 14 |
| baseline_role | Analytics Engineer | 0 | — | 13 |
| baseline_role | Research Scientist | 0 | — | 12 |
| baseline_role | MLOps Engineer | 0 | — | 9 |
| baseline_role | NLP Engineer | 0 | — | 8 |
| baseline_role | Platform Engineer | 0 | — | 8 |
| baseline_role | Data Platform Engineer | 0 | — | 7 |
| baseline_role | Product Analyst | 0 | — | 7 |
| baseline_role | Computer Vision Engineer | 0 | — | 4 |

## Model: `hgb`

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| salary_role | AI Engineer | 3 | 2026-10-01 | 5547 |
| salary_role | Computer Vision Engineer | 3 | 2026-10-01 | 5475 |
| salary_role | NLP Engineer | 3 | 2026-10-01 | 5409 |
| salary_role | ML Engineer | 3 | 2026-10-01 | 5259 |
| salary_role | MLOps Engineer | 3 | 2026-10-01 | 5213 |
| salary_role | Data Platform Engineer | 3 | 2026-10-01 | 5126 |
| salary_role | Research Scientist | 3 | 2026-10-01 | 5086 |
| salary_role | Data Scientist | 3 | 2026-10-01 | 4992 |
| salary_role | Platform Engineer | 3 | 2026-10-01 | 4833 |
| salary_role | Backend Engineer | 3 | 2026-10-01 | 4763 |
| salary_role | Data Engineer | 3 | 2026-10-01 | 4665 |
| salary_role | Analytics Engineer | 3 | 2026-10-01 | 4435 |
| salary_role | BI Developer | 3 | 2026-10-01 | 3971 |
| salary_role | Product Analyst | 3 | 2026-10-01 | 3900 |
| salary_role | Data Analyst | 3 | 2026-10-01 | 3750 |
| skill | Python | 3 | 2026-10-01 | 135.83 |
| skill | SQL | 3 | 2026-10-01 | 133.94 |
| skill | Spark | 3 | 2026-10-01 | 129.44 |
| skill | dbt | 3 | 2026-10-01 | 129.22 |
| skill | Airflow | 3 | 2026-10-01 | 127.78 |
| skill | Tableau | 3 | 2026-10-01 | 121.17 |
| skill | Power BI | 3 | 2026-10-01 | 118.17 |
| skill | AWS | 3 | 2026-10-01 | 117 |
| skill | GCP | 3 | 2026-10-01 | 115.06 |
| skill | Azure | 3 | 2026-10-01 | 112.50 |
| skill | Kubernetes | 3 | 2026-10-01 | 109.83 |
| skill | TensorFlow | 3 | 2026-10-01 | 106.11 |
| skill | Docker | 3 | 2026-10-01 | 103.67 |
| skill | PyTorch | 3 | 2026-10-01 | 101.06 |
| skill | scikit-learn | 3 | 2026-10-01 | 97.06 |
| role | Data Analyst | 3 | 2026-10-01 | 35.17 |
| role | Data Engineer | 3 | 2026-10-01 | 33.56 |
| role | Data Scientist | 3 | 2026-10-01 | 31.17 |
| role | ML Engineer | 3 | 2026-10-01 | 25.50 |
| role | Analytics Engineer | 3 | 2026-10-01 | 24.50 |
| role | AI Engineer | 3 | 2026-10-01 | 21.11 |
| role | BI Developer | 3 | 2026-10-01 | 20.06 |
| role | MLOps Engineer | 3 | 2026-10-01 | 14.94 |
| role | Product Analyst | 3 | 2026-10-01 | 13.72 |
| role | Research Scientist | 3 | 2026-10-01 | 13.22 |
| role | Backend Engineer | 3 | 2026-10-01 | 11.39 |
| role | Platform Engineer | 3 | 2026-10-01 | 10.28 |
| role | Data Platform Engineer | 3 | 2026-10-01 | 9.83 |
| role | NLP Engineer | 3 | 2026-10-01 | 8.83 |
| role | Computer Vision Engineer | 3 | 2026-10-01 | 8.17 |

## Model: `prophet`

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| salary_role | Platform Engineer | 3 | 2026-10-01 | 6022 |
| salary_role | AI Engineer | 3 | 2026-10-01 | 5757 |
| salary_role | MLOps Engineer | 3 | 2026-10-01 | 5739 |
| salary_role | Computer Vision Engineer | 3 | 2026-10-01 | 5723 |
| salary_role | NLP Engineer | 3 | 2026-10-01 | 5594 |
| salary_role | ML Engineer | 3 | 2026-10-01 | 5370 |
| salary_role | Data Platform Engineer | 3 | 2026-10-01 | 5346 |
| salary_role | Research Scientist | 3 | 2026-10-01 | 5107 |
| salary_role | Data Scientist | 3 | 2026-10-01 | 4961 |
| salary_role | Data Engineer | 3 | 2026-10-01 | 4886 |
| salary_role | Backend Engineer | 3 | 2026-10-01 | 4474 |
| salary_role | BI Developer | 3 | 2026-10-01 | 4202 |
| salary_role | Analytics Engineer | 3 | 2026-10-01 | 4181 |
| salary_role | Data Analyst | 3 | 2026-10-01 | 3967 |
| salary_role | Product Analyst | 3 | 2026-10-01 | 3901 |
| skill | SQL | 3 | 2026-10-01 | 119.07 |
| skill | Airflow | 3 | 2026-10-01 | 117.16 |
| skill | GCP | 3 | 2026-10-01 | 107.60 |
| skill | TensorFlow | 3 | 2026-10-01 | 104.03 |
| skill | Azure | 3 | 2026-10-01 | 102.83 |
| skill | Power BI | 3 | 2026-10-01 | 102.82 |
| skill | Tableau | 3 | 2026-10-01 | 93.31 |
| skill | dbt | 3 | 2026-10-01 | 90.55 |
| skill | Python | 3 | 2026-10-01 | 86.27 |
| skill | scikit-learn | 3 | 2026-10-01 | 85.25 |
| skill | Spark | 3 | 2026-10-01 | 81.71 |
| skill | PyTorch | 3 | 2026-10-01 | 79.20 |
| skill | Kubernetes | 3 | 2026-10-01 | 76.33 |
| skill | Docker | 3 | 2026-10-01 | 75.06 |
| skill | AWS | 3 | 2026-10-01 | 63.36 |
| role | ML Engineer | 3 | 2026-10-01 | 33.33 |
| role | Data Scientist | 3 | 2026-10-01 | 32.65 |
| role | Analytics Engineer | 3 | 2026-10-01 | 28.44 |
| role | Data Analyst | 3 | 2026-10-01 | 24.27 |
| role | AI Engineer | 3 | 2026-10-01 | 16.29 |
| role | BI Developer | 3 | 2026-10-01 | 13.50 |
| role | Data Platform Engineer | 3 | 2026-10-01 | 13.27 |
| role | MLOps Engineer | 3 | 2026-10-01 | 10.65 |
| role | NLP Engineer | 3 | 2026-10-01 | 10.63 |
| role | Data Engineer | 3 | 2026-10-01 | 9.40 |
| role | Platform Engineer | 3 | 2026-10-01 | 8.05 |
| role | Research Scientist | 3 | 2026-10-01 | 6.29 |
| role | Product Analyst | 3 | 2026-10-01 | 4.94 |
| role | Backend Engineer | 3 | 2026-10-01 | 0 |
| role | Computer Vision Engineer | 3 | 2026-10-01 | 0 |

## Model: `rf`

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| salary_role | NLP Engineer | 3 | 2026-10-01 | 5718 |
| salary_role | AI Engineer | 3 | 2026-10-01 | 5670 |
| salary_role | Computer Vision Engineer | 3 | 2026-10-01 | 5633 |
| salary_role | ML Engineer | 3 | 2026-10-01 | 5435 |
| salary_role | MLOps Engineer | 3 | 2026-10-01 | 5397 |
| salary_role | Research Scientist | 3 | 2026-10-01 | 5181 |
| salary_role | Data Platform Engineer | 3 | 2026-10-01 | 5150 |
| salary_role | Data Scientist | 3 | 2026-10-01 | 5148 |
| salary_role | Backend Engineer | 3 | 2026-10-01 | 4840 |
| salary_role | Platform Engineer | 3 | 2026-10-01 | 4817 |
| salary_role | Data Engineer | 3 | 2026-10-01 | 4775 |
| salary_role | Analytics Engineer | 3 | 2026-10-01 | 4460 |
| salary_role | BI Developer | 3 | 2026-10-01 | 4081 |
| salary_role | Product Analyst | 3 | 2026-10-01 | 4061 |
| salary_role | Data Analyst | 3 | 2026-10-01 | 3775 |
| skill | Python | 3 | 2026-10-01 | 113.06 |
| skill | Tableau | 3 | 2026-10-01 | 110.55 |
| skill | dbt | 3 | 2026-10-01 | 109.50 |
| skill | Spark | 3 | 2026-10-01 | 109.33 |
| skill | Power BI | 3 | 2026-10-01 | 108.10 |
| skill | SQL | 3 | 2026-10-01 | 105.53 |
| skill | Airflow | 3 | 2026-10-01 | 102.91 |
| skill | GCP | 3 | 2026-10-01 | 101.38 |
| skill | AWS | 3 | 2026-10-01 | 98.62 |
| skill | TensorFlow | 3 | 2026-10-01 | 95.92 |
| skill | Azure | 3 | 2026-10-01 | 95.62 |
| skill | Docker | 3 | 2026-10-01 | 90.94 |
| skill | PyTorch | 3 | 2026-10-01 | 84.81 |
| skill | Kubernetes | 3 | 2026-10-01 | 82.64 |
| skill | scikit-learn | 3 | 2026-10-01 | 77.88 |
| role | Data Scientist | 3 | 2026-10-01 | 31.52 |
| role | Data Analyst | 3 | 2026-10-01 | 29.73 |
| role | Data Engineer | 3 | 2026-10-01 | 25.20 |
| role | Analytics Engineer | 3 | 2026-10-01 | 24.32 |
| role | BI Developer | 3 | 2026-10-01 | 20.90 |
| role | AI Engineer | 3 | 2026-10-01 | 19.42 |
| role | ML Engineer | 3 | 2026-10-01 | 18.39 |
| role | Research Scientist | 3 | 2026-10-01 | 14.29 |
| role | MLOps Engineer | 3 | 2026-10-01 | 13.11 |
| role | Backend Engineer | 3 | 2026-10-01 | 12.85 |
| role | Platform Engineer | 3 | 2026-10-01 | 11.14 |
| role | Product Analyst | 3 | 2026-10-01 | 9.40 |
| role | Data Platform Engineer | 3 | 2026-10-01 | 9.19 |
| role | Computer Vision Engineer | 3 | 2026-10-01 | 7.20 |
| role | NLP Engineer | 3 | 2026-10-01 | 6.34 |

## Model: `sarima`

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| salary_role | AI Engineer | 3 | 2026-10-01 | 5629 |
| salary_role | NLP Engineer | 3 | 2026-10-01 | 5627 |
| salary_role | Computer Vision Engineer | 3 | 2026-10-01 | 5504 |
| salary_role | MLOps Engineer | 3 | 2026-10-01 | 5415 |
| salary_role | ML Engineer | 3 | 2026-10-01 | 5408 |
| salary_role | Data Platform Engineer | 3 | 2026-10-01 | 5346 |
| salary_role | Platform Engineer | 3 | 2026-10-01 | 5198 |
| salary_role | Data Scientist | 3 | 2026-10-01 | 5195 |
| salary_role | Research Scientist | 3 | 2026-10-01 | 5143 |
| salary_role | Backend Engineer | 3 | 2026-10-01 | 4833 |
| salary_role | Data Engineer | 3 | 2026-10-01 | 4807 |
| salary_role | Analytics Engineer | 3 | 2026-10-01 | 4387 |
| salary_role | BI Developer | 3 | 2026-10-01 | 4095 |
| salary_role | Product Analyst | 3 | 2026-10-01 | 4062 |
| salary_role | Data Analyst | 3 | 2026-10-01 | 3885 |
| skill | dbt | 3 | 2026-10-01 | 125.87 |
| skill | Spark | 3 | 2026-10-01 | 115.90 |
| skill | AWS | 3 | 2026-10-01 | 113.83 |
| skill | Power BI | 3 | 2026-10-01 | 109.63 |
| skill | SQL | 3 | 2026-10-01 | 108.13 |
| skill | Tableau | 3 | 2026-10-01 | 99.67 |
| skill | Airflow | 3 | 2026-10-01 | 99.32 |
| skill | Kubernetes | 3 | 2026-10-01 | 98.14 |
| skill | Azure | 3 | 2026-10-01 | 98.06 |
| skill | GCP | 3 | 2026-10-01 | 93.95 |
| skill | Docker | 3 | 2026-10-01 | 93.67 |
| skill | scikit-learn | 3 | 2026-10-01 | 79.94 |
| skill | Python | 3 | 2026-10-01 | 69.75 |
| skill | TensorFlow | 3 | 2026-10-01 | 64.80 |
| skill | PyTorch | 3 | 2026-10-01 | 64.03 |
| role | Data Analyst | 3 | 2026-10-01 | 35.28 |
| role | Data Scientist | 3 | 2026-10-01 | 30.25 |
| role | ML Engineer | 3 | 2026-10-01 | 27.98 |
| role | Backend Engineer | 3 | 2026-10-01 | 19.82 |
| role | Analytics Engineer | 3 | 2026-10-01 | 19.81 |
| role | BI Developer | 3 | 2026-10-01 | 19.49 |
| role | AI Engineer | 3 | 2026-10-01 | 19.46 |
| role | Data Engineer | 3 | 2026-10-01 | 18.39 |
| role | Research Scientist | 3 | 2026-10-01 | 12.71 |
| role | Product Analyst | 3 | 2026-10-01 | 12.41 |
| role | MLOps Engineer | 3 | 2026-10-01 | 12.08 |
| role | Data Platform Engineer | 3 | 2026-10-01 | 10.78 |
| role | NLP Engineer | 3 | 2026-10-01 | 9.87 |
| role | Platform Engineer | 3 | 2026-10-01 | 9.37 |
| role | Computer Vision Engineer | 3 | 2026-10-01 | 8.52 |
