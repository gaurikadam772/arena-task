
import pandas as pd

# ==========================================
# PROJECT: SALES DATA ANALYSIS
# ==========================================

# STEP 1: LOAD DATASET
df = pd.read_csv("sales_data.csv")

print("========== ORIGINAL DATA ==========")
print(df.head())

# STEP 2: EXPLORE DATA
print("\nDataset Shape:", df.shape)
print("\nColumn Names:", df.columns.tolist())
print("\nData Types:\n", df.dtypes)
print("\nDataset Information:")
df.info()

# STEP 3: HANDLE MISSING VALUES

print("\nMissing Values Before Cleaning:")
print(df.isnull().sum())

# Remove duplicate records
df = df.drop_duplicates()

# Fill missing product names
df["Product"] = df["Product"].fillna("Unknown")

# Fill missing numerical values
df["Quantity"] = df["Quantity"].fillna(0)
df["Price"] = df["Price"].fillna(0)

# STEP 4: VALIDATE AND CLEAN DATA

# Convert numeric columns safely
df["Quantity"] = pd.to_numeric(
    df["Quantity"], errors="coerce"
)
df["Price"] = pd.to_numeric(
    df["Price"], errors="coerce"
)

# Remove records with invalid values
df = df.dropna(subset=["Quantity", "Price"])

df = df[
    (df["Quantity"] >= 0) &
    (df["Price"] >= 0)
]

# Recalculate sales revenue
df["Total_Sales"] = df["Quantity"] * df["Price"]

print("\nMissing Values After Cleaning:")
print(df.isnull().sum())

# STEP 5: SALES ANALYSIS

# Total revenue
total_revenue = df["Total_Sales"].sum()

# Total quantity sold
total_quantity = df["Quantity"].sum()

# Total unique orders
total_orders = df["Order_ID"].nunique()

# Average order value
average_order_value = (
    total_revenue / total_orders if total_orders else 0
)

# Product-wise revenue
product_sales = df.groupby(
    "Product"
)["Total_Sales"].sum()

# Product-wise quantity
quantity_sales = df.groupby(
    "Product"
)["Quantity"].sum()

# Best product by revenue
best_product = (
    product_sales.idxmax() if not product_sales.empty else "N/A"
)

# Most sold product by quantity
most_sold_product = (
    quantity_sales.idxmax() if not quantity_sales.empty else "N/A"
)

# STEP 6: DISPLAY RESULTS

print("\n========== SALES REPORT ==========")

print(f"Total Revenue: ₹{total_revenue:,.2f}")
print(f"Total Quantity Sold: {total_quantity:,.0f}")
print(f"Total Orders: {total_orders}")
print(f"Average Order Value: ₹{average_order_value:,.2f}")

print(f"Best-Selling Product by Revenue: {best_product}")
print(f"Most Sold Product by Quantity: {most_sold_product}")

print("\n========== PRODUCT-WISE SALES ==========")
print(product_sales)

# STEP 7: SAVE CLEANED DATA

df.to_csv("cleaned_sales_data.csv", index=False)

# STEP 8: GENERATE REPORT

report = f"""
# SALES DATA ANALYSIS REPORT

## Overall Performance

- Total Revenue: ₹{total_revenue:,.2f}
- Total Quantity Sold: {total_quantity:,.0f}
- Total Orders: {total_orders}
- Average Order Value: ₹{average_order_value:,.2f}

## Product Insights

- Best-Selling Product by Revenue: {best_product}
- Most Sold Product by Quantity: {most_sold_product}

## Product-Wise Revenue

{product_sales.to_string()}

## Conclusion

The analysis identifies the highest-revenue
product and the product with the highest
quantity sold.

This report provides an overview of
business sales performance.
"""

with open("analysis_report.md", "w", encoding="utf-8") as file:
    file.write(report)

print("\nReport generated successfully!")
print("Files saved: cleaned_sales_data.csv and analysis_report.md")
