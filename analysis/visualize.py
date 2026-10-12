
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PART 2 — TASK 11: CREATE THE REQUIRED VISUALIZATIONS
# ============================================================

# Locate the repository folders
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VISUAL_DIR = BASE_DIR / "visualizations"

# Create the visualizations folder if it does not exist
VISUAL_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# STEP 1: LOAD THE ORIGINAL CSV FILES
# ============================================================

customers = pd.read_csv(DATA_DIR / "customers.csv")
products = pd.read_csv(DATA_DIR / "products.csv")
orders = pd.read_csv(DATA_DIR / "orders.csv")

print("Customers shape:", customers.shape)
print("Products shape:", products.shape)
print("Orders shape:", orders.shape)


# ============================================================
# STEP 2: CLEAN THE ORDERS DATA
# Use the same cleaning rules as clean_and_eda.py
# ============================================================

# Standardize payment methods
orders["payment_method"] = (
    orders["payment_method"]
    .str.strip()
    .str.upper()
)

# Remove duplicate orders using the natural key
duplicate_key = [
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "discount_pct",
    "payment_method",
    "rating",
    "returned"
]

orders_clean = orders.drop_duplicates(
    subset=duplicate_key,
    keep="first"
).copy()

# Fill missing discounts with zero
orders_clean["discount_pct"] = (
    orders_clean["discount_pct"].fillna(0)
)

# Fill missing ratings with the median
orders_clean["rating"] = (
    orders_clean["rating"].fillna(
        orders_clean["rating"].median()
    )
)

print("Cleaned orders shape:", orders_clean.shape)


# ============================================================
# STEP 3: CALCULATE RETURN RATE BY PAYMENT METHOD
# ============================================================

return_analysis = orders_clean.groupby("payment_method").agg(
    total_orders=("order_id", "count"),
    returned_orders=("returned", "sum")
)

return_analysis["return_rate_pct"] = (
    return_analysis["returned_orders"]
    / return_analysis["total_orders"]
    * 100
)

# Sort from highest to lowest return rate
return_chart = return_analysis.sort_values(
    "return_rate_pct",
    ascending=False
)

print("\nReturn rate by payment method:")
print(return_chart.round(1))


# ============================================================
# VISUALIZATION 1: RETURN RATE BY PAYMENT METHOD
# ============================================================

fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(
    return_chart.index,
    return_chart["return_rate_pct"]
)

# Add percentage labels above the bars
ax.bar_label(
    bars,
    labels=[
        f"{value:.1f}%"
        for value in return_chart["return_rate_pct"]
    ],
    padding=4
)

highest_method = return_chart.index[0]
highest_rate = return_chart["return_rate_pct"].iloc[0]

ax.set_title(
    f"{highest_method} Has the Highest Return Rate "
    f"at {highest_rate:.1f}%"
)
ax.set_xlabel("Payment Method")
ax.set_ylabel("Return Rate (%)")

ax.set_ylim(
    0,
    return_chart["return_rate_pct"].max() * 1.20
)

ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.set_axisbelow(True)

fig.tight_layout()

fig.savefig(
    VISUAL_DIR / "return_rate_by_payment.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close(fig)


# ============================================================
# STEP 4: CALCULATE MONTHLY REVENUE
# Exclude quantity outliers for the corrected comparison
# ============================================================

# Identify quantity outliers using the IQR method
q1 = orders_clean["quantity"].quantile(0.25)
q3 = orders_clean["quantity"].quantile(0.75)
iqr = q3 - q1

lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr

outlier_mask = (
    (orders_clean["quantity"] < lower_bound)
    | (orders_clean["quantity"] > upper_bound)
)

outlier_ids = orders_clean.loc[
    outlier_mask, "order_id"
].tolist()

print("\nQuantity outlier order IDs:", outlier_ids)

# Convert order dates into datetime format
orders_clean["order_date"] = pd.to_datetime(
    orders_clean["order_date"]
)

# Merge product prices into the cleaned orders
revenue_data = orders_clean.merge(
    products[["product_id", "price"]],
    on="product_id",
    how="left",
    validate="many_to_one"
)

# Calculate order value using the same revenue formula
revenue_data["order_value"] = (
    revenue_data["quantity"]
    * revenue_data["price"]
    * (1 - revenue_data["discount_pct"] / 100)
)

# Exclude quantity outliers only for this comparison
revenue_corrected = revenue_data.loc[
    ~revenue_data["order_id"].isin(outlier_ids)
].copy()

# Group corrected revenue by month
revenue_corrected["year_month"] = (
    revenue_corrected["order_date"].dt.to_period("M")
)

monthly_revenue_corrected = (
    revenue_corrected
    .groupby("year_month")["order_value"]
    .sum()
    .sort_index()
)

# Identify the actual peak month after excluding outliers
peak_month = monthly_revenue_corrected.idxmax()
peak_revenue = monthly_revenue_corrected.max()

print("\nMonthly revenue excluding quantity outliers:")
print(monthly_revenue_corrected.round(2))

print("\nActual peak month:", peak_month)
print(f"Peak-month revenue: Rs. {peak_revenue:,.2f}")


# ============================================================
# VISUALIZATION 2: OUTLIER-CORRECTED MONTHLY REVENUE
# ============================================================

fig, ax = plt.subplots(figsize=(9, 5))

# Convert monthly periods into strings for the x-axis
month_labels = [
    str(month)
    for month in monthly_revenue_corrected.index
]

revenue_values = monthly_revenue_corrected.values

ax.plot(
    month_labels,
    revenue_values,
    marker="o",
    linewidth=2,
    markersize=6
)

# Label each monthly revenue value
for month, revenue in zip(month_labels, revenue_values):
    ax.annotate(
        f"₹{revenue:,.0f}",
        xy=(month, revenue),
        xytext=(0, 9),
        textcoords="offset points",
        ha="center",
        fontsize=8
    )

# Highlight the actual peak month in the title
ax.set_title(
    f"Monthly Revenue Excluding Quantity Outliers "
    f"— Peak: {peak_month}"
)
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (₹)")

ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.set_axisbelow(True)

plt.setp(
    ax.get_xticklabels(),
    rotation=45,
    ha="right"
)

fig.tight_layout()

fig.savefig(
    VISUAL_DIR / "monthly_revenue_trend.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close(fig)


# ============================================================
# COMPLETION MESSAGE
# ============================================================

print("\nBoth visualization files have been saved.")

print(
    "Return-rate chart:",
    VISUAL_DIR / "return_rate_by_payment.png"
)

print(
    "Monthly revenue chart:",
    VISUAL_DIR / "monthly_revenue_trend.png"
)
