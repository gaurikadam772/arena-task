# E-commerce Sales Analysis - Report

Period analysed: **03 Jan 2026 to 29 Jun 2026** (97 orders, 11 products, 4 categories).

## 1. Headline numbers

| Metric | Value |
|---|---|
| Total revenue | $40,161 |
| Orders | 97 |
| Units sold | 364 |
| Average order value | $414 |
| Median order value | $210 |
| Largest order | $2,519 |

## 2. Data preparation

The raw file had 100 rows. After cleaning, 97 rows remain (1 duplicate, 2 missing/invalid and 0 non-positive rows removed). Revenue was calculated as quantity x unit price.

## 3. Findings

### Revenue is driven by a few categories

![Bar chart of revenue by category](../visualizations/category_revenue_bar.png)

Electronics brings in 58.0% of revenue ($23,311) from only 21.6% of orders, with an average order of $1,110. Stationery is the smallest category at 2.1% of revenue even though it makes up 21.6% of orders. Order count alone is therefore a poor guide to where the money comes from.

| Category | Revenue | Share | Orders | Avg order |
|---|---|---|---|---|
| Electronics | $23,311 | 58.0% | 21 | $1,110 |
| Furniture | $9,153 | 22.8% | 28 | $327 |
| Clothing | $6,853 | 17.1% | 27 | $254 |
| Stationery | $845 | 2.1% | 21 | $40 |

**Three products account for most of the revenue.** The top three products (Smartphone, Laptop, Standing Desk) generate 61.8% of total revenue across 11 products. Smartphone alone contributes 25.3%. Stock, pricing and marketing decisions for these items have an outsized effect on results.

| Product | Category | Revenue | Share | Units |
|---|---|---|---|---|
| Smartphone | Electronics | $10,143 | 25.3% | 17 |
| Laptop | Electronics | $9,384 | 23.4% | 11 |
| Standing Desk | Furniture | $5,286 | 13.2% | 16 |
| Sneakers | Clothing | $4,222 | 10.5% | 57 |
| Headphones | Electronics | $3,783 | 9.4% | 42 |

### Monthly revenue is uneven

![Line chart of monthly revenue](../visualizations/monthly_revenue_line.png)

January was the strongest month ($13,490) and June the weakest ($3,940). Revenue moved from $13,490 in January to $3,940 in June, and month-to-month variation is large (coefficient of variation 53%). With only about 16 orders per month, a handful of high-value sales can swing a month, so single-month changes should be read cautiously rather than as a firm trend.

### A small share of orders produces a large share of revenue

![Histogram of order values](../visualizations/order_value_histogram.png)

The average order is $414 but the median is only $210 (2.0x lower), so the distribution is right-skewed (skew 2.3). Orders of $500 or more are 24.7% of orders (24 orders) but 68.2% of revenue. The median is the better description of a typical order.

**Cheaper items are bought in larger quantities.** Unit price and units per order show a moderate negative relationship (Spearman rho = -0.51). Orders for items priced below the median unit price ($83) average 5.2 units, versus 2.3 units for items priced at or above it. This is a correlation in this sample, not proof of cause.

### Biggest category-month result: Electronics in January

![Heatmap of revenue by category and month](../visualizations/category_month_heatmap.png)

The single biggest category-month cell is Electronics in January ($9,059), about 3.2x that category's average in its other months. Electronics is the top category in 6 of 6 months and Stationery is last in 6 of 6. Much of the early-year strength in the line chart therefore comes from one category in one month rather than from broad growth.

## 4. Recommendations

1. Protect the core: keep Smartphone, Laptop, Standing Desk well stocked and competitively priced, because they carry 62% of revenue.
2. Grow Stationery through bundling or cross-selling with larger orders; it has many orders but contributes little revenue.
3. Track revenue with a rolling 3-month average and report order counts beside revenue, so one large order does not look like a trend.
4. Collect more history (a full year or more) before judging seasonality.

## 5. Limitations

- The sample is small (under 100 orders over six months), so percentages can shift noticeably with a few extra orders.
- There is no order or customer id, so identical rows were treated as duplicates and customer-level analysis (repeat buyers, lifetime value) is not possible.
- The dataset in `data/` is a synthetic practice file with deliberate quality issues; conclusions describe this data, not a real business.
