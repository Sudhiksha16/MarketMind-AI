# MarketMind AI – Data Dictionary

## 1. Online Retail Dataset

The Online Retail dataset contains transaction-level retail sales information. It is used to understand customer purchases, products, quantities, prices, dates, and countries.

| Column | Description | Use in MarketMind AI |
|---|---|---|
| InvoiceNo | Unique invoice/transaction number | Identifies each transaction |
| StockCode | Product/item code | Identifies the product |
| Description | Product description/name | Identifies and displays the product |
| Quantity | Number of units purchased | Used for sales and quantity analysis |
| InvoiceDate | Date and time of the transaction | Used for sales trends and forecasting |
| UnitPrice | Price of one unit | Used to calculate revenue |
| CustomerID | Customer identifier | Used for customer analysis and segmentation |
| Country | Customer's country | Used for geographical sales analysis |

### Dataset observations

- Rows: 541,909
- Columns: 8
- Missing product descriptions: 1,454
- Missing customer IDs: 135,080
- Duplicate rows: 5,268

---

## 2. Retail Store Inventory Dataset

The inventory dataset contains information about inventory levels, units sold, orders, demand forecasts, prices, promotions, weather, competitors, and seasonality.

| Column | Description | Use in MarketMind AI |
|---|---|---|
| Date | Date of the inventory record | Used for time-based analysis |
| Store ID | Identifies the store | Used to analyze individual stores |
| Product ID | Identifies the product | Used for product-level inventory analysis |
| Category | Product category | Used for category-level analysis |
| Region | Geographic region | Used for regional analysis |
| Inventory Level | Current inventory quantity | Used to monitor stock levels |
| Units Sold | Number of units sold | Used for sales and demand analysis |
| Units Ordered | Number of units ordered | Used to understand replenishment |
| Demand Forecast | Forecasted product demand | Used for inventory planning |
| Price | Product price | Used for price-related analysis |
| Discount | Discount applied to the product | Used to analyze promotional effects |
| Weather Condition | Weather condition on the date | Can be used to study external factors |
| Holiday/Promotion | Indicates holiday or promotional activity | Used to analyze promotional effects |
| Competitor Pricing | Competitor's product price | Used for competitive price analysis |
| Seasonality | Seasonal information | Used for demand and forecasting analysis |

### Dataset observations

- Rows: 73,100
- Columns: 15
- Missing values: None detected
- Duplicate rows: None detected

---

## 3. Customer Data

The `customer.xlsx` file contains transaction-level customer information with the same retail transaction fields as the Online Retail dataset.

The customer-related fields are mainly used to understand purchasing behaviour.

Important customer-related fields include:

| Column | Description | Use in MarketMind AI |
|---|---|---|
| CustomerID | Identifies the customer | Customer analysis and segmentation |
| InvoiceNo | Identifies the transaction | Purchase history |
| InvoiceDate | Date and time of purchase | Recency and purchase-frequency analysis |
| Quantity | Units purchased | Purchase-volume analysis |
| UnitPrice | Price per unit | Customer spending/value analysis |
| Country | Customer's country | Geographical customer analysis |

---

## 4. Data Usage in MarketMind AI

The datasets support different parts of the MarketMind AI platform:

- **Sales data** → sales analysis, revenue analysis and forecasting
- **Customer data** → customer behaviour and segmentation
- **Inventory data** → stock monitoring and inventory planning
- **Date information** → time-based sales and demand analysis
- **Product information** → product-level performance analysis