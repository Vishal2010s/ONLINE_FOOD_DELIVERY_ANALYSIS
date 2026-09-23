# Online Food Delivery Analysis

**From noisy order data to business insights with Python, MySQL, Streamlit, and Plotly.**

## Project overview

This project explores online food delivery operations through data profiling, preprocessing, exploratory data analysis (EDA), feature engineering, SQL analytics, and an interactive dashboard. It connects customer ordering patterns with revenue, restaurant performance, delivery efficiency, and cancellations.

The project documentation and supplied profiling report describe **100,000 orders and 25 original features**. The Streamlit application presents **7 KPIs and 15 business analyses**, with filters for city, cuisine, month, and payment mode.

## Problem statement

Food delivery data contains missing customer details, inconsistent dates, incomplete financial fields, and unusual delivery times. These issues complicate comparisons across customers, restaurants, cities, and cuisines. The project investigates how this data can be prepared and summarized to support operational and commercial decisions.

## Objectives

- Profile the dataset and identify missing values, data-type issues, and outliers.
- Apply column-specific imputation and business-rule-based preprocessing.
- Explore customer segments, order patterns, revenue, discounts, and delivery performance.
- Create interpretable features for segmentation and time-based analysis.
- Store processed records in MySQL and answer business questions using SQL.
- Communicate results through interactive charts, KPI cards, and analytical tables.

## Dataset

| Attribute | Description |
|---|---|
| Original size | 100,000 records × 25 features, supported by `report.html` and the project document |
| Unit of analysis | An online food delivery order |
| Customer information | Customer identifiers, age, gender, city, and area |
| Order information | Order identifiers, date, time, value, status, and payment mode |
| Restaurant information | Restaurant identifiers, names, cuisine, and ratings |
| Delivery information | Distance, delivery time, delivery rating, and cancellation reason |
| Financial information | Order value, discount, final amount, and profit margin |


## Technology stack

| Technology | Role demonstrated |
|---|---|
| Python | Data processing, conditional logic, iteration, and feature creation |
| Pandas | CSV loading, filtering, grouping, imputation, date handling, and aggregation |
| NumPy | Imported numerical support library |
| YData Profiling | Automated dataset profiling and HTML reporting |
| scikit-learn `LabelEncoder` | Categorical encoding for exploratory correlation analysis |
| MySQL | Storage and analytical querying of processed records |
| SQLAlchemy and PyMySQL | Python–MySQL connection and DataFrame upload |
| Streamlit | Dashboard layout, filters, KPI cards, and query selection |
| Plotly Express and Graph Objects | Interactive charts, heatmaps, and combined bar/line views |
| Matplotlib | Imported in the processing script; also used in notebook examples |
| Jupyter Notebook | Supporting EDA learning material and examples |

The implemented dashboard is Streamlit-based. Power BI appears in the project brief, but no Power BI report is included.

## Data cleaning and preprocessing

`Masteranalysis_file.py` contains the food-delivery preprocessing workflow:

- Copies the raw DataFrame before transformation.
- Converts selected fields to categorical and numeric types.
- Parses mixed date formats and extracts date components.
- Encodes categorical/object fields in a separate DataFrame for correlation exploration.
- Detects numerical outliers and constructs annotated Plotly boxplots.
- Applies missing-value strategies appropriate to individual columns.
- Clips selected values and creates derived analytical fields.
- Exports processed data to CSV and uploads it to MySQL.

### Missing-value imputation

| Field or group | Implemented approach |
|---|---|
| `Customer_Age`, `Delivery_Rating` | Median imputation |
| `Distance_km` | Mean imputation, followed by rounding to two decimals |
| `Discount_Applied` | Mode within delivered/cancelled order groups |
| `Final_Amount` | Conditional arithmetic and median fallback, followed by a zero lower bound |
| `Order_Value` | Conditional arithmetic using available financial fields; see implementation notes below |
| Gender, city, area, cuisine, payment mode, peak-hour flag | Sampling observed non-null values with replacement |
| `Order_Date`, `Order_Time` | Forward-fill |
| `Delivery_Time_Min` | Fixed distance-band values for delivered orders; 20 minutes for missing values on cancelled orders |
| `Cancellation_Reason` | Delivered-status label, a late-delivery rule, and sampling from selected remaining reasons |

Sampling reflects the observed category frequencies in expectation; it does not guarantee exact proportions or recover the true missing values. No fixed random seed is supplied in these sampling calls.

### IQR outlier detection and treatment

The script calculates the following for numerical columns:

```text
Q1 = 25th percentile
Q3 = 75th percentile
IQR = Q3 - Q1
Lower bound = Q1 - 1.5 × IQR
Upper bound = Q3 + 1.5 × IQR
```

Values outside these bounds are flagged and counted. Plotly boxplots include reference lines for the limits; the script's boxplot display call is currently commented out.

The food-delivery script applies **specific business-rule caps**, rather than automatically replacing every IQR outlier:

- `Delivery_Time_Min` is capped at **160 minutes**.
- `Final_Amount` is clipped to a minimum of **0**.

The supporting notebook also demonstrates IQR-based age capping on a separate example dataset. That example should not be interpreted as an additional food-delivery transformation.

## Exploratory data analysis

The project combines automated profiling with numerical summaries, category frequencies, grouped comparisons, and interactive charts:

- **Univariate analysis:** distributions, missingness, category counts, and boxplots.
- **Relationship analysis:** encoded correlation heatmap, delivery time versus rating, and distance summaries by delivery category.
- **Segment analysis:** gender, age group, city, cuisine, restaurant, and payment mode.
- **Time-based analysis:** monthly revenue, weekday/weekend patterns, and peak-hour demand.
- **Operational analysis:** cancellations, cancellation reasons, and delivery performance.

`report.html` provides the supplied food-delivery data profile. 

## Feature engineering

| Derived feature | Implementation and analytical purpose |
|---|---|
| `Order_Day_Type` | Copies the existing `Order_Day` field for order-day analysis; it is not recomputed from the date |
| `Peak_Hour_Indicator` | Maps boolean peak-hour values to `Peak Hour` / `Non-Peak Hour` |
| `Profit_Margin_Percentage` | Multiplies `Profit_Margin` by 100 and rounds to two decimals |
| `Delivery_Performance_Category` | Groups times into ≤45, >45–90, and >90 minutes |
| `Customer_Age_Group` | Groups ages using thresholds of ≤30, >30–50, and >50 |
| `Order_month` | Extracts three-letter month names for monthly reporting |
| `Order_year` | Extracts the order year as a nullable integer |

Age-group labels in the code imply ages 18–60, but the conditions do not enforce those outer limits. The first delivery category includes exactly 45 minutes despite its label saying `<45 mins`.

## SQL, MySQL, and SQLAlchemy

The processing script uses Pandas `to_sql()` with a SQLAlchemy engine and the PyMySQL driver to write the processed data to table **`ofd`** in database **`Online_food`**. The database must already exist. The upload uses `if_exists='replace'`, so rerunning it replaces that table.

The dashboard uses SQLAlchemy `text()` and bound filter parameters to execute MySQL queries. Demonstrated SQL includes `SELECT`, `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, `CASE WHEN`, `COUNT`, `SUM`, `AVG`, `ROUND`, `LIMIT`, and MySQL `FIELD()` for month ordering.

### 15 business analyses

| # | Analysis | What the implemented query measures |
|---|---|---|
| 1 | Spending by gender | Sum of final amounts by gender; the dashboard title says “Top Spending Customers,” but this is not an individual-customer ranking |
| 2 | Age group vs order value | Total order value by customer age group |
| 3 | Weekend vs weekday patterns | Final amounts grouped by `Order_Day` and cuisine |
| 4 | Monthly revenue trends | Final amounts by month, ordered January–December |
| 5 | Discounts and profit | Average profit-margin percentage by discount amount |
| 6 | City and cuisine revenue | Revenue by city and by city–cuisine combination |
| 7 | Delivery time by city | Average delivery time per city |
| 8 | Distance and delivery delay | Average distance and order count by delivery-performance category |
| 9 | Delivery rating and time | Average delivery time by delivery rating |
| 10 | Top-rated restaurants | Top 10 average restaurant ratings, restricted to groups with more than 50 orders |
| 11 | Restaurant cancellation rates | Top 10 restaurant groups by cancelled-order percentage |
| 12 | Cuisine performance | Order counts and total order value by cuisine |
| 13 | Peak-hour demand | Order counts and total order value by peak-hour indicator |
| 14 | Payment preferences | Order counts and total order value by payment mode |
| 15 | Cancellation reasons | Counts for Restaurant Issue, Customer Cancelled, and Late Delivery |

These analyses describe associations and aggregated patterns; they do not establish the causal effect of discounts or delays.

## Streamlit and Plotly dashboard

`app_dashboard.py` contains two tabs:

1. **Main Dashboard:** seven KPI cards, monthly order/revenue trends, city performance, cuisine analysis, peak-hour demand, delivery-performance distribution, payment-mode analysis, and a detailed city–cuisine metrics table.
2. **Food Delivery & Sales Analytics:** a selector for the 15 SQL analyses, with query result tables and interactive visualizations.

Sidebar filters cover **city, cuisine, month, and payment mode**. Visualizations include bar, line, scatter/bubble, and donut charts. The main dashboard reads the processed CSV, while the analytical queries read MySQL; both sources must contain the same processed records.

### KPI definitions

The following definitions match the dashboard code and operate on the filtered CSV records:

| KPI | Calculation |
|---|---|
| Total Orders | Number of filtered rows |
| Total Revenue | Sum of `Final_Amount` |
| Average Order Value | Mean of `Order_Value` |
| Average Delivery Time | Mean of `Delivery_Time_Min` |
| Cancellation Rate | Cancelled rows ÷ total rows × 100; returns 0 for an empty selection |
| Average Delivery Rating | Mean of `Delivery_Rating` |
| Profit Margin % | Unweighted mean of `Profit_Margin_Percentage` |

Revenue and delivery metrics are not automatically restricted to delivered orders. Average order value uses `Order_Value`, not revenue divided by order count. Profit Margin % is an average of row-level percentages, not a revenue-weighted margin.

## Project workflow

```text
Raw order data
    → Automated profiling and data understanding
    → Type/date conversion and correlation exploration
    → IQR outlier detection
    → Imputation and selected value caps
    → Business feature engineering
    → Processed CSV and MySQL table
    → SQL analyses and dashboard KPIs
    → Interactive visualizations and documented outputs
```

## Repository structure

The supplied files, plus this README, are:

```text
.
├── README.md
├── app_dashboard.py
├── Masteranalysis_file.py
├── output .docx
└── report.html
```

| File | Purpose |
|---|---|
| `app_dashboard.py` | Streamlit application, KPI calculations, Plotly charts, and SQL queries |
| `Masteranalysis_file_old.py` | Food-delivery preprocessing, feature engineering, CSV export, and MySQL upload |
| `output .docx` | Dashboard and analysis output documentation |
| `report.html` | Generated food-delivery profiling report |

## How to run

### 1. Review the included artifacts

Open `report.html` in a browser and the two `.docx` documents in a compatible document viewer. These can be reviewed without a database. The HTML report may need to be downloaded before viewing because GitHub does not render arbitrary HTML reports as live pages.

### 2. Prepare a Python environment

From the repository folder:

```bash
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Install the packages used by the processing script and dashboard:

```bash
python -m pip install pandas numpy matplotlib plotly streamlit sqlalchemy pymysql scikit-learn ydata-profiling
```

Package versions are not pinned in the supplied files. The script uses Pandas mixed-format date parsing, which requires a version supporting `format='mixed'`.

### 3. Supply data and configure MySQL

- Obtain the source data referenced in the project document and save it locally as `Raw_dataset.csv` in the working directory. Confirm that its column names match the script.
- Start MySQL and create the database:

```sql
CREATE DATABASE IF NOT EXISTS Online_food;
```

- Update the connection settings in **both Python scripts** for your local database. Their connection format is:

```text
mysql+pymysql://YOUR_USER:YOUR_URL_ENCODED_PASSWORD@127.0.0.1:3306/Online_food
```

The supplied scripts contain hard-coded credentials. Replace them before public upload and use your own local settings; this README does not reproduce those credentials.

### 4. Address the older script's setup and logic issues

The supplied processing script needs review before a fresh run:

- Replace its profiling import, `from pandas_profiling import ydata_profiling`, with `import ydata_profiling` to match its existing `ydata_profiling.ProfileReport(...)` call.
- Parenthesize each comparison in the `Final_Amount` conditions. For example, the positive-order-value/missing-final-amount condition should be `(df1['Order_Value'] > 0) & df1['Final_Amount'].isna()`. Apply the same care to the second condition and verify the intended treatment of existing values.
- Review the `Order_Value` imputation: the supplied subtraction of discount from final amount is inconsistent with the earlier relationship `Final_Amount = Order_Value - Discount_Applied`.
- Keep parsed dates as datetimes or use an explicit format when reparsing day-first strings. The current format-to-string/reparse sequence can misinterpret ambiguous dates.

These are preparation notes, not changes already applied to the supplied source files. Validate the resulting financial fields, dates, and remaining nulls before relying on regenerated results.

### 5. Process the data

After completing the preparation above:

```bash
python Masteranalysis_file_old.py
```

The script is intended to generate `report.html`, export `FOOD_DELIVERY_ANALYSIS_final.csv`, and replace MySQL table `Online_food.ofd`. Preserve the supplied report separately if you want to keep its original version.

### 6. Launch the dashboard

Ensure the processed CSV is in the working directory and MySQL contains the matching `ofd` table, then run:

```bash
python -m streamlit run app_dashboard.py
```

Open the local URL shown by Streamlit. Apply sidebar filters and select an analysis to explore the SQL results. The six supplied files alone do not provide a complete runtime dataset, so a fresh end-to-end run requires the data and local setup described above.

## Key skills demonstrated

- **Python and Pandas:** DataFrame manipulation, grouping, conditional transformations, date processing, and CSV handling.
- **Data quality:** Profiling, missing-value assessment, column-specific imputation, IQR detection, and selected capping/clipping.
- **EDA:** Descriptive summaries, distributions, category comparisons, correlations, and temporal analysis.
- **Feature engineering:** Age segmentation, delivery categories, peak-hour labels, percentage conversion, and month/year extraction.
- **SQL and databases:** Aggregations, conditional counts, grouped filtering, ranked results, database connectivity, and data loading.
- **Visualization and reporting:** Interactive Plotly charts, Streamlit filters, KPI definitions, and business-oriented analytical tables.

## Business use cases

- **Delivery operations:** Compare city-level delivery times and review delayed-delivery segments.
- **Restaurant management:** Examine ratings, order volumes, and cancellation rates.
- **Commercial planning:** Compare revenue across cities and cuisines and explore discount–margin relationships.
- **Demand planning:** Understand peak-hour and weekday/weekend patterns.
- **Customer experience:** Explore delivery ratings, cancellation reasons, and payment preferences.
- **Management reporting:** Monitor a consistent set of operational and financial summaries.

These are decision-support applications of the analyses, not claims of measured business improvements.

## Limitations and notes

- **Reproducibility:** Raw/processed CSVs and a pinned dependency environment are not included. A fresh execution has not been verified as part of this README preparation.
- **Imputation uncertainty:** The supplied profile reports substantial missingness, including approximately 50.1% for customer age. Sampling, forward-fill, and fixed delivery-time imputations can affect segment comparisons and operational metrics.
- **Correlation interpretation:** Arbitrary numeric labels for nominal categories can produce misleading Pearson correlations; treat the encoded heatmap as exploratory.
- **Scope of cleaning:** The project brief describes broader corrections, such as invalid ratings and negative profit margins. The supplied food-delivery script does not clearly implement all of those proposed checks.
- **Time coverage:** The dashboard displays a hard-coded January–December 2024 subtitle and groups revenue by month without year. Validate actual dates before interpreting the period or using multi-year data.
- **Metric consistency:** Keep CSV and MySQL data synchronized. Review status handling and imputed values before interpreting revenue, delivery time, ratings, or profitability as operational truth.
- **Dashboard edge cases:** Empty filter selections or unsuitable values for bubble sizes may need additional handling.
- **Project scope:** This is descriptive business analytics. The supplied implementation does not establish forecasting, predictive-model performance, causal effects, or formal feature scaling.

## Conclusion

Online Food Delivery Analysis demonstrates an analytics workflow from profiling and preprocessing through feature engineering, MySQL queries, and a Streamlit dashboard. Its value lies in making customer, revenue, restaurant, and delivery patterns inspectable through clearly defined metrics and interactive analysis, while documenting the data and implementation limits that affect interpretation.
