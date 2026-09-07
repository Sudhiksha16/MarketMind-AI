# MarketMind AI – Data Exploration

## 1. Purpose

The purpose of this exploration is to understand the structure and quality of the datasets before data cleaning and preprocessing.

The datasets were inspected for:

- Number of rows and columns
- Column names
- Sample records
- Missing values
- Duplicate records
- Data types

---

## 2. Online Retail Sales Dataset

### Dataset Size

- Rows: 541,909
- Columns: 8

### Columns

- InvoiceNo
- StockCode
- Description
- Quantity
- InvoiceDate
- UnitPrice
- CustomerID
- Country

### Data Quality Findings

| Issue | Count |
|---|---:|
| Missing Description | 1,454 |
| Missing CustomerID | 135,080 |
| Duplicate Rows | 5,268 |

### Data Types

- InvoiceNo: object
- StockCode: object
- Description: object
- Quantity: integer
- InvoiceDate: object
- UnitPrice: float
- CustomerID: float
- Country: object

### Observation

The sales dataset contains a large number of transaction records. Some product descriptions and customer IDs are missing, and duplicate records are present. These issues will be handled during the Data Preparation stage.

---

## 3. Customer Dataset

The customer Excel dataset was inspected to understand its structure and suitability for customer-related analysis.

The dataset was loaded using Python Pandas and its rows, columns, data types, missing values, and duplicate records were examined.

Customer-related information can be used to understand purchasing behaviour and support customer segmentation.

---

## 4. Retail Store Inventory Dataset

The inventory dataset was inspected to understand inventory levels, sales, orders, demand forecasts, pricing, promotions, competitor pricing, and seasonality.

The dataset contains information useful for inventory monitoring and demand analysis.

---

## 5. Initial Findings

The initial exploration shows that:

1. Sales data contains transaction-level information.
2. Customer information can be used to analyse purchasing behaviour.
3. Inventory data contains stock and demand-related information.
4. The sales dataset contains missing values and duplicate records that require cleaning.
5. Data preparation will be performed before using the datasets for analytics and AI modules.

---

## 6. Next Step

The identified data quality issues will be handled during the Data Preparation stage.

The cleaned datasets will then be used by the MarketMind AI platform for analytics and future AI-based features.