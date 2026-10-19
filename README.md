# Mamaearth Returns & Growth Intelligence Pipeline

## 1. Project Overview

The **Mamaearth Returns & Growth Intelligence Pipeline** is a data analytics capstone project that combines SQL-based analysis, Python data cleaning, exploratory data analysis (EDA), visualization, and AI-assisted business reporting.

The project analyzes customer, product, and order data to identify revenue trends, return-rate patterns, payment-method risks, duplicate transactions, and the effect of quantity outliers on monthly revenue.

The final stage generates a concise **Situation–Complication–Resolution (SCR)** business narrative using the Gemini API, with a deterministic offline fallback and numeric accuracy checks to ensure that the key findings are retained.

### Project Objectives

- Analyze sales, customer, product, and order data using SQL.
- Clean and validate order data using Python.
- Investigate missing values, duplicate orders, payment-method return rates, and quantity outliers.
- Compare revenue before and after data cleaning.
- Visualize return rates and monthly revenue trends.
- Export verified analytical findings to a structured JSON file.
- Generate an AI-assisted business narrative with an offline alternative.
- Validate that the generated narrative contains the required figures.

## 2. Repository Structure

```text
Mamaearth_Capstone_Project/
├── README.md
├── .gitignore
├── sql/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── reports.sql
├── data/
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   └── cleaned_data.csv
├── analysis/
│   ├── clean_and_eda.py
│   └── visualize.py
├── visualizations/
│   ├── return_rate_by_payment.png
│   └── monthly_revenue_trend.png
└── narrator/
    ├── findings.json
    ├── generate_narrative.py
    └── sample_output.txt
```

The `.gitignore` file excludes Python cache files, local environment files, and macOS metadata. The `sample_output.txt` file contains a saved example of the narrative-generation and validation results.

## 3. Prerequisites

Install the following before running the project:

- Python 3.10 or later
- A SQL database compatible with the SQL syntax in the project scripts
- A Python package manager such as `pip`
- A Gemini API key for online narrative generation (optional if using offline mode)

The project was developed using Python and SQL. File paths should be interpreted relative to the repository root unless a command specifies otherwise.

## 4. SQL Analysis — Part 1

The SQL scripts establish the database structure, load the supplied data, and execute analytical queries.

### Step 1: Create the database tables

Open your SQL client, select or create the database you intend to use, and execute:

```sql
SOURCE sql/schema.sql;
```

This creates the tables required for the project. If your SQL client does not support the `SOURCE` command, open `sql/schema.sql` and execute its contents in the client.

### Step 2: Load the seed data

Execute:

```sql
SOURCE sql/seed_data.sql;
```

This loads the sample customer, product, and order records into the database.

If `SOURCE` is unavailable in your SQL client, open `sql/seed_data.sql` and execute the script using the client's SQL editor.

### Step 3: Run the analytical reports

Execute:

```sql
SOURCE sql/reports.sql;
```

The reports examine order and revenue totals, missing ratings, customers without orders, customer spending, product-category performance, and return patterns across relevant groups.

**Execution order:** `schema.sql` → `seed_data.sql` → `reports.sql`.

Run the schema and seed scripts against a fresh or appropriately reset database when reproducing the analysis to avoid duplicate inserts.

## 5. Python Data Cleaning and EDA — Part 2

The Python analysis script processes the supplied CSV files, standardizes values, removes duplicate orders, handles missing values, investigates outliers, and calculates the metrics used in the final report.

From the repository root, run:

```bash
python3 analysis/clean_and_eda.py
```

The analysis covers:

1. Loading and inspecting the customer, product, and order datasets.
2. Standardizing payment-method labels.
3. Identifying and removing duplicate order records using the project's order key.
4. Handling missing discount and rating values according to the cleaning procedure.
5. Comparing raw revenue with cleaned revenue.
6. Identifying quantity outliers using the Interquartile Range (IQR) method.
7. Comparing return rates across payment methods.
8. Examining return rates by payment method and city tier.
9. Investigating relationships between numeric variables.
10. Comparing monthly revenue before and after excluding identified quantity outliers.

Outliers are flagged for sensitivity analysis rather than automatically removed from the underlying cleaned dataset. Their effect on monthly revenue is evaluated separately.

### Verified analytical findings

The analysis identified the following key results:

| Metric | Result |
|---|---:|
| Raw revenue | ₹99,860.20 |
| Cleaned revenue | ₹97,358.30 |
| Duplicate-driven revenue difference | ₹2,501.90 |
| COD return rate | 44.4% |
| UPI return rate | 18.9% |
| Card return rate | 14.7% |
| Highest-risk segment: COD, Tier 2 | 54.5% return rate |
| True peak month after outlier correction | March 2026 |
| Corrected March revenue | ₹20,318.90 |
| Apparent January 2026 revenue before outlier correction | ₹29,582.10 |
| Corrected January 2026 revenue | ₹11,637.10 |

These results motivate further investigation of COD returns, particularly for Tier-2 city orders, and careful treatment of outliers when reporting monthly performance.

## 6. Visualizations

After the analysis has produced the required cleaned data and metrics, generate the charts by running:

```bash
python3 analysis/visualize.py
```

The visualizations are saved in the `visualizations/` directory.

- **`return_rate_by_payment.png`** compares return rates for COD, UPI, and card payments.
- **`monthly_revenue_trend.png`** presents the monthly revenue trend after the project's quantity-outlier correction.

The charts help communicate the principal operational risks and the distinction between apparent and corrected monthly revenue.

## 7. Exporting Verified Findings

The narrator uses `narrator/findings.json` as its structured input.

The Task 5 findings-export step in `analysis/clean_and_eda.py` must write this JSON file from the calculated Part 2 results, rather than relying on manually re-entered figures. This keeps the narrative input consistent with the analysis.

The exported findings include:

- Raw and cleaned revenue.
- The duplicate-reconciliation difference.
- Return rates by payment method.
- The highest-risk payment-method and city-tier segment.
- The corrected peak month and its revenue.
- The month whose apparent revenue peak was inflated by quantity outliers.

The JSON file is consumed by the narrative generator in the next stage.

**Reproducibility note:** Run the analysis and findings-export step before generating the narrative whenever the source data or cleaning logic changes.

## 8. AI-Assisted Business Narrative — Part 3

The narrative generator is located at:

```text
narrator/generate_narrative.py
```

It reads `narrator/findings.json` and generates a concise business report with exactly three sections:

1. **Situation** — summarizes the principal financial and operational results.
2. **Complication** — explains the key return-rate and revenue-reporting risks.
3. **Resolution** — recommends practical next steps grounded in the findings.

The script includes parameter controls, error handling, section validation, numeric accuracy checks, and a deterministic offline fallback.

### 8.1 Install the required Python dependencies

Install the packages used by the relevant scripts:

```bash
python3 -m pip install pandas matplotlib google-genai python-dotenv
```

If the project environment already has these packages installed, this step can be skipped. The optional `python-dotenv` dependency supports loading a local `.env` file.

### 8.2 Configure the Gemini API key

Online narrative generation requires a valid Gemini API key.

Set the key as an environment variable before running the script. For example, in macOS Terminal:

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Replace the placeholder with your own key. Do not commit the key to GitHub, put it in the README, or include it in the saved output.

Alternatively, the script can load a local `.env` file if `python-dotenv` is installed and the script is configured to read that file. The `.env` file must remain excluded from version control.

### 8.3 Run the online narrative generator

From the repository root, execute:

```bash
python3 narrator/generate_narrative.py
```

When a valid API key, model access, and available quota are present, the script attempts to generate the narrative using Gemini.

The generator uses controlled parameters and handles API errors. If the API request fails, or the generated response fails the required validation checks, the script can switch to the deterministic offline narrative, depending on the selected execution path and validation logic.

A successful API request is not guaranteed: service availability, model access, and usage quotas can affect online execution.

### 8.4 Run the offline fallback

The offline fallback generates the SCR report directly from `findings.json` using a deterministic template. It does not require a Gemini API key, an API request, or an internet connection.

Run:

```bash
python3 narrator/generate_narrative.py --offline
```

The offline mode should produce the same required three-section structure and preserve the required figures from the findings file.

Use this mode to reproduce the report when API access is unavailable.

### 8.5 Numeric accuracy validation

The narrative generator checks that the report includes the five required numeric findings:

1. Cleaned revenue: `97358.30` or `97,358.30`.
2. COD return rate: `44.4`.
3. Highest-risk segment return rate: `54.5`.
4. Duplicate-reconciliation difference: `2501.90` or `2,501.90`.
5. March 2026 true peak revenue: `20318.90` or `20,318.90`, with March identified as the true peak month.

The checker normalizes commas where appropriate and reports individual PASS or FAIL results. It also checks the required SCR section structure.

The actual narrative must be validated before it is accepted. If the API output fails validation, the offline fallback should be generated and validated instead of adding a separate numerical summary to make an invalid narrative pass.

The saved `narrator/sample_output.txt` provides evidence of the narrative-generation run and the corresponding validation results. Its source label must accurately indicate whether the saved narrative came from Gemini or the offline fallback.

## 9. Expected Outputs

After running the project in the documented order, the repository should contain:

- SQL schema, seed data, and analytical report scripts.
- Source customer, product, and order CSV files.
- Cleaned data and Python analysis outputs.
- `visualizations/return_rate_by_payment.png`.
- `visualizations/monthly_revenue_trend.png`.
- `narrator/findings.json`, exported from the analytical results.
- `narrator/generate_narrative.py`, containing online generation, validation, and offline fallback logic.
- `narrator/sample_output.txt`, containing the saved narrative and validation evidence.

The online path requires a valid key and available API quota. The offline path remains available for reproducible narrative generation without API access.

## 10. End-to-End Execution Order

To reproduce the pipeline from start to finish:

1. Execute `sql/schema.sql`.
2. Execute `sql/seed_data.sql`.
3. Execute `sql/reports.sql`.
4. Run `python3 analysis/clean_and_eda.py`.
5. Confirm that the analysis produces the expected cleaned data and exports `narrator/findings.json`.
6. Run `python3 analysis/visualize.py`.
7. Configure `GEMINI_API_KEY` if online narrative generation is required.
8. Run `python3 narrator/generate_narrative.py` for the online-capable path.
9. If API access is unavailable, run `python3 narrator/generate_narrative.py --offline`.
10. Verify the SCR section check and numeric accuracy check.
11. Review `narrator/sample_output.txt` and confirm that its source label matches the narrative actually saved.

Following this order keeps the SQL analysis, Python calculations, exported findings, visualizations, and final business narrative connected in a reproducible workflow.

## 11. Conclusion

This project demonstrates an end-to-end analytics workflow that combines SQL querying, Python-based data preparation, exploratory analysis, visualization, structured findings export, and AI-assisted reporting.

The principal findings highlight the importance of duplicate reconciliation, payment-method return-rate analysis, and outlier-aware revenue reporting. The validated narrative layer translates these findings into actionable business questions while retaining an offline fallback for reproducibility when online model access is unavailable.
