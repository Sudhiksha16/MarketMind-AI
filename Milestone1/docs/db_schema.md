# MarketMind AI – Database Design

## 1. Overview

The MarketMind AI database stores information required for sales, customers, products, inventory, invoices, and users.

The database is organized into separate tables so that related information can be stored and accessed efficiently.

---

## 2. Users Table

Stores information about users who access the platform.

| Field | Description |
|---|---|
| id | Unique user ID |
| name | User name |
| email | User email |
| role | User role |

Supported roles:

- Business Owner
- Store Manager
- Sales Executive
- Administrator

---

## 3. Customers Table

Stores customer information.

| Field | Description |
|---|---|
| id | Unique customer ID |
| name | Customer name |
| contact_info | Customer contact information |

---

## 4. Products Table

Stores product information.

| Field | Description |
|---|---|
| id | Unique product ID |
| name | Product name |
| category | Product category |
| unit_price | Price per unit |

---

## 5. Sales Table

Stores sales transaction information.

| Field | Description |
|---|---|
| id | Unique sale ID |
| product_id | Product involved in the sale |
| customer_id | Customer involved in the sale |
| quantity | Number of units sold |
| sale_date | Date of the sale |

---

## 6. Inventory Table

Stores inventory information for products.

| Field | Description |
|---|---|
| id | Unique inventory record ID |
| product_id | Product associated with inventory |
| stock_level | Current stock quantity |
| reorder_point | Stock level at which reordering may be required |

---

## 7. Invoices Table

Stores invoice information associated with sales.

| Field | Description |
|---|---|
| id | Unique invoice ID |
| sale_id | Sale associated with the invoice |
| amount | Invoice amount |
| payment_status | Current payment status |

---

## 8. Table Relationships

### Sales → Products

`product_id` in the Sales table refers to the product in the Products table.

### Sales → Customers

`customer_id` in the Sales table refers to the customer in the Customers table.

### Inventory → Products

`product_id` in the Inventory table refers to the product in the Products table.

### Invoices → Sales

`sale_id` in the Invoices table refers to the sale in the Sales table.

---

## 9. Simplified Relationship Diagram

```text
             USERS
               |
               |
          APPLICATION
               |
     ┌─────────┴─────────┐
     ↓                   ↓
 CUSTOMERS            PRODUCTS
     │                   │
     │                   ├────────── INVENTORY
     │                   │
     └─────── SALES ─────┘
                │
                │
                ↓
             INVOICES