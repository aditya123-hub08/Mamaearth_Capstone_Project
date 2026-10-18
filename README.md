# Mamaearth Returns & Growth Intelligence Pipeline

A data analytics capstone project that combines SQL, Python, data cleaning, exploratory data analysis (EDA), visualization, and Generative AI to identify product-return risks and revenue trends for Mamaearth.

**Repository:** [Mamaearth Capstone Project](https://github.com/aditya123-hub08/Mamaearth_Capstone_Project)

## 1. Project Overview

This project builds a reproducible analytics pipeline to examine order data, calculate revenue, analyze product returns across payment methods and city tiers, detect quantity outliers, and generate business insights using a GenAI-powered narrative.

The project is organized into three parts:

- **Part 1 — SQL Analytics:** Database schema, seed data, and analytical reports.
- **Part 2 — Python Analytics:** Data cleaning, EDA, outlier detection, return-rate analysis, and visualizations.
- **Part 3 — GenAI Insight Narrator:** Structured findings, business narrative generation, error handling, and an offline fallback.

## 2. Project Objectives

- Calculate order revenue after discounts.
- Identify and reconcile duplicate order records.
- Compare return rates across payment methods.
- Identify high-risk customer segments by payment method and city tier.
- Detect quantity outliers using the Interquartile Range (IQR) method.
- Analyze monthly revenue trends before and after correcting for outliers.
- Generate a business-oriented Situation–Complication–Resolution (SCR) narrative using verified analytical results.
- Make the entire workflow reproducible without depending on a paid API or continuous network access.

## 3. Repository Structure

```text
Mamaearth_Capstone_Project/
│
├── README.md
│
├── sql/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── reports.sql
│
├── data/
│   ├── customers.csv
│   ├── products.csv
│   └── orders.csv
│
├── analysis/
│   ├── clean_and_eda.py
│   └── visualize.py
│
├── visualizations/
│   ├── return_rate_by_payment.png
│   └── monthly_revenue_trend.png
│
└── narrator/
    ├── findings.json
    └── generate_narrative.py
```

## 4. Prerequisites

Install or configure the following tools:

- MySQL Server and MySQL Workbench
- Python 3
- Git and GitHub
- A Gemini API key for online narrative generation (optional; the offline fallback should work without one)

Install the Python dependencies used by the analytics and narrator scripts:

```bash
python3 -m pip install pandas matplotlib google-genai
```

Run the commands below from the root directory of the repository.

## 5. Step-by-Step Execution Guide

### Step 1 — Set up the SQL database

Open MySQL Workbench and connect to your local MySQL Server.

Execute the SQL files in the following order:

1. Open `sql/schema.sql` and execute it to create the required database tables and schema.
2. Open `sql/seed_data.sql` and execute it to populate the tables with the supplied data.
3. Open `sql/reports.sql` and execute it to run the analytical queries.

Verify that the tables have been populated and that the SQL reports return results before proceeding to Python analysis.

**Execution order:** `schema.sql` → `seed_data.sql` → `reports.sql`

### Step 2 — Run data cleaning and exploratory data analysis

From the repository root, run:

```bash
python3 analysis/clean_and_eda.py
```

This script performs the data preparation and analytical checks required by the project, including:

- Loading and merging the relevant datasets.
- Checking data quality and handling duplicate records.
- Calculating revenue after discounts.
- Detecting quantity outliers using the IQR method.
- Comparing return rates across payment methods.
- Performing segmented analysis by payment method and city tier.
- Examining correlations among rating, return status, discount percentage, and quantity.
- Analyzing monthly revenue with and without the identified outlier orders.

The cleaning and EDA script also exports the verified findings required by the visualization and narration stages, including `narrator/findings.json`.

### Step 3 — Generate the visualizations

After the cleaning and EDA script completes successfully, run:

```bash
python3 analysis/visualize.py
```

The script should generate and save the following charts in the `visualizations/` directory:

**1. `return_rate_by_payment.png`**

A descending bar chart comparing return rates across payment methods. Each bar should display its corresponding return rate, and the title should communicate the main finding.

**2. `monthly_revenue_trend.png`**

A line chart showing the outlier-corrected monthly revenue trend. The chart should include axis labels and identify the actual peak month.

Both visualizations must be regenerated from the analytical outputs rather than edited manually.

### Step 4 — Generate the GenAI-powered business narrative

The narrator converts the verified numerical findings into a structured business narrative using the Situation–Complication–Resolution (SCR) framework.

The relevant files are:

- `narrator/findings.json` — structured numerical findings exported by the analytics pipeline.
- `narrator/generate_narrative.py` — the narrative-generation function, Gemini API integration, error handling, and offline fallback.

#### Option A: Run with a Gemini API key

Configure your Gemini API key as an environment variable in the terminal:

```bash
export GEMINI_API_KEY="your_gemini_api_key"
```

Replace the placeholder with your own valid API key. Never commit the key to GitHub.

Run the narrator:

```bash
python3 narrator/generate_narrative.py
```

The script should read the findings, construct the required SCR narrative, and use the Gemini API to generate the business report.

#### Option B: Run without an API key

If no Gemini API key is configured, run the same command:

```bash
python3 narrator/generate_narrative.py
```

The program should use `generate_scr_narrative_offline(findings)` to generate the same three-section narrative structure directly from the verified findings.

The offline fallback must not make a network request or require an API key. It should preserve the required numerical values and return a structured result consistent with the online path.

If the online request fails, the program should handle the error gracefully and use the fallback when implemented by the pipeline.

## 6. Key Analytical Findings

The following are the expected reference values specified in the project brief. They should be reproducible from the supplied data and analytical scripts.

| Metric | Expected result |
|---|---:|
| Raw revenue total | ₹99,860.20 |
| Cleaned revenue total | ₹97,358.30 |
| Duplicate-related reconciliation difference | ₹2,501.90 |
| CARD return rate | 14.7% |
| COD return rate | 44.4% |
| UPI return rate | 18.9% |
| Highest-risk segment | COD + Tier-2 cities |
| Highest-risk segment return rate | 54.5% |
| Outlier-inflated peak month | January 2026 |
| Corrected peak month | March 2026 |
| Corrected peak-month revenue | ₹20,318.90 |

The revenue reconciliation difference is ₹2,501.90, attributable to the five duplicate order rows identified in the project brief. It must be reconciled against the removed rows' order values rather than attributed to an unexplained cleaning adjustment.

The two quantity outliers identified by the project brief are:

- Order `000111` — quantity 25
- Order `000098` — quantity 30

These orders must be flagged rather than deleted from the dataset. The corrected monthly revenue analysis excludes their contribution for the outlier-adjusted comparison.

The expected return-rate results suggest that COD orders have a higher return rate than CARD and UPI orders. The segmented analysis further identifies COD orders in Tier-2 cities as the highest-risk segment.

These figures are validation targets from the project specification; the scripts and underlying data remain the source of the reported results.

## 7. Data Integrity and Reproducibility

The pipeline is designed to preserve the relationship between the source data, cleaned data, analytical results, visualizations, and generated narrative.

The following checks are important:

- The cleaned dataset should contain 175 rows.
- The cleaned revenue calculation should use quantity, price, and discount percentage.
- Duplicate reconciliation should explicitly account for the identified duplicate rows.
- Quantity outliers should be flagged with a Boolean `is_outlier` column rather than removed.
- Return rates should be calculated by payment method and by payment-method/city-tier segment.
- Monthly revenue should be calculated both before and after excluding the two flagged outlier orders from the comparison.
- The narrative must use the same verified figures as `findings.json`.
- The online and offline narrative paths must preserve the required numerical values and SCR structure.

The scripts should be rerunnable end-to-end without manually editing intermediate outputs.

## 8. GenAI Design and Reliability

The narrator follows a structured approach to business insight generation:

1. **Input:** Read the verified findings from `narrator/findings.json`.
2. **Instruction:** Provide a system instruction specifying the analyst role, SCR structure, and numerical accuracy requirements.
3. **Generation:** Use the Gemini API when available.
4. **Error handling:** Return a structured result rather than exposing an unhandled exception.
5. **Fallback:** Generate a deterministic, template-based SCR narrative when the API is unavailable.
6. **Validation:** Check that the generated narrative contains the required numerical findings.

The narrator is intended to explain verified analytical results, not invent statistics or independently change the calculated findings.

## 9. Complete Pipeline

Run the components in this order:

```text
MySQL Database Setup
        |
        v
schema.sql
        |
        v
seed_data.sql
        |
        v
reports.sql
        |
        v
clean_and_eda.py
        |
        v
findings.json
        |
        v
visualize.py
        |
        v
generate_narrative.py
        |
        v
Business Insights (SCR Narrative)
```

### Commands for the Python stages

```bash
python3 analysis/clean_and_eda.py
python3 analysis/visualize.py
python3 narrator/generate_narrative.py
```

The SQL stages must be executed in MySQL Workbench before the Python stages. The Python pipeline should regenerate the analytical outputs from the project data and save the two chart files in `visualizations/`.

## 10. Expected Deliverables

- SQL schema, seed data, and analytical reports.
- Cleaned and analyzed order data.
- Verified numerical findings in `narrator/findings.json`.
- `return_rate_by_payment.png`.
- `monthly_revenue_trend.png`.
- A three-section Situation–Complication–Resolution business narrative.
- A working Gemini API integration with error handling.
- A deterministic offline narrative fallback.
- A README that enables a new user to reproduce the workflow from start to finish.

## 11. Conclusion

The Mamaearth Returns & Growth Intelligence Pipeline demonstrates how SQL-based reporting, Python analytics, data visualization, and Generative AI can work together in a reproducible business intelligence workflow.

By combining data-quality checks with return-rate segmentation and outlier-corrected revenue trends, the project identifies potential operational risks and converts the verified findings into an actionable business narrative. Its offline fallback also ensures that the core reporting workflow does not depend entirely on external API availability.

---

**Project:** Mamaearth Returns & Growth Intelligence Pipeline  
**Repository:** [GitHub — Mamaearth Capstone Project](https://github.com/aditya123-hub08/Mamaearth_Capstone_Project)
