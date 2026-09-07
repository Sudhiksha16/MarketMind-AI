# --------------------------------------------------
# STEP 1: Import the libraries we need
# --------------------------------------------------

# Import RBAC tools.
# get_current_user identifies the logged-in user.
# require_role checks whether the user's role is allowed.
from Milestone1.auth.rbac import get_current_user, require_role

# Import the authentication router so that
# login APIs become part of our FastAPI application.
from Milestone1.auth.auth_routes import router as auth_router

# FastAPI is used to create our backend API.
from fastapi import FastAPI, Depends

# CORSMiddleware allows our React frontend
# to communicate with our FastAPI backend.
from fastapi.middleware.cors import CORSMiddleware

# Path helps us locate our project folders.
from pathlib import Path

# Pandas is used to read and analyse our datasets.
import pandas as pd


# --------------------------------------------------
# STEP 2: Create the FastAPI application
# --------------------------------------------------

# This creates our MarketMind AI backend application.
#
# FastAPI will allow our React frontend to communicate
# with the backend using API endpoints.

app = FastAPI(
    title="MarketMind AI API",
    description="Small Business Sales Intelligence Platform",
    version="1.0.0"
)

# Register the authentication routes with FastAPI.
#
# This makes our login endpoint available at:
# http://127.0.0.1:8000/auth/login
app.include_router(auth_router)

# --------------------------------------------------
# Allow React Frontend to communicate with FastAPI
# --------------------------------------------------

# Our React application runs on:
# http://localhost:5173
#
# Our FastAPI backend runs on:
# http://127.0.0.1:8000
#
# Because these are different origins,
# the browser needs permission to allow communication
# between them.

app.add_middleware(
    CORSMiddleware,

    # Allow requests from our React development server.
    allow_origins=["http://localhost:5173"],

    # Allow cookies/authentication later.
    allow_credentials=True,

    # Allow GET, POST, PUT, DELETE, etc.
    allow_methods=["*"],

    # Allow all required request headers.
    allow_headers=["*"],
)

# --------------------------------------------------
# STEP 3: Find the Milestone1 folder
# --------------------------------------------------

# __file__ means this current Python file:
#     Milestone1/backend/main.py
#
# .parent gives us:
#     Milestone1/backend
#
# Another .parent gives us:
#     Milestone1
#
# So BASE_DIR represents our Milestone1 folder.

BASE_DIR = Path(__file__).resolve().parent.parent


# --------------------------------------------------
# STEP 4: Tell Python where our cleaned datasets are
# --------------------------------------------------

# Our cleaned files are stored here:
#
# Milestone1
#     └── preprocessing
#           └── processed
#
# We are NOT using the original datasets directly.
# We are using the cleaned datasets created during Day 5–6.

SALES_FILE = (
    BASE_DIR
    / "preprocessing"
    / "processed"
    / "cleaned_sales.csv"
)

CUSTOMER_FILE = (
    BASE_DIR
    / "preprocessing"
    / "processed"
    / "cleaned_customer.csv"
)

INVENTORY_FILE = (
    BASE_DIR
    / "preprocessing"
    / "processed"
    / "cleaned_inventory.csv"
)


# --------------------------------------------------
# STEP 5: Create the Home API
# --------------------------------------------------

# @app.get("/") means:
#
# When someone visits:
#     http://127.0.0.1:8000/
#
# FastAPI will run the function below.

@app.get("/")
def root():

    # We return a simple JSON response.
    # This lets us check whether our backend is running.

    return {
        "message": "MarketMind AI backend is running",
        "status": "success"
    }


# --------------------------------------------------
# STEP 6: Create the Sales Summary API
# --------------------------------------------------

# This endpoint will be used by our dashboard
# to get basic sales information.
#
# URL:
#     /sales/summary

@app.get("/sales/summary")
def sales_summary():

    # Read our cleaned sales CSV file.
    #
    # Pandas loads the CSV into a DataFrame.
    # A DataFrame is basically a table in Python.

    df = pd.read_csv(SALES_FILE)


    # --------------------------------------------------
    # Calculate total revenue
    # --------------------------------------------------

    # TotalAmount was created during our cleaning stage:
    #
    # TotalAmount = Quantity × UnitPrice
    #
    # .sum() adds all transaction amounts together.

    total_revenue = df["TotalAmount"].sum()


    # --------------------------------------------------
    # Count total sales records
    # --------------------------------------------------

    # len(df) tells us how many rows are present
    # in the cleaned sales dataset.

    total_orders = len(df)


    # --------------------------------------------------
    # Calculate total quantity sold
    # --------------------------------------------------

    # Quantity contains the number of products sold
    # in each transaction.
    #
    # .sum() gives us the total number of products sold.

    total_quantity = df["Quantity"].sum()


    # --------------------------------------------------
    # Find the top-selling product
    # --------------------------------------------------

    # First, group the data by product description.
    #
    # Then add the quantity sold for each product.
    #
    # idxmax() finds the product with the highest
    # total quantity sold.

    top_product = (
        df.groupby("Description")["Quantity"]
        .sum()
        .idxmax()
    )


    # --------------------------------------------------
    # Send the result back to the frontend
    # --------------------------------------------------

    # FastAPI automatically converts this dictionary
    # into JSON.

    return {
        "total_revenue": round(float(total_revenue), 2),
        "total_orders": int(total_orders),
        "total_quantity_sold": int(total_quantity),
        "top_product": str(top_product)
    }


# --------------------------------------------------
# STEP 7: Create the Sales Trend API
# --------------------------------------------------

# This endpoint will provide sales information
# that we can later display as a chart.

@app.get("/sales/trend")
def sales_trend():

    # Load the cleaned sales data.

    df = pd.read_csv(SALES_FILE)


    # Convert InvoiceDate from text into
    # an actual date/time value.

    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"]
    )


    # Group sales by date and calculate
    # the total revenue for each day.

    trend = (
        df.groupby(
            df["InvoiceDate"].dt.date
        )["TotalAmount"]
        .sum()
        .reset_index()
    )


    # Rename the columns to simple names
    # that are easier for the frontend to use.

    trend.columns = [
        "date",
        "revenue"
    ]


    # Keep only the latest 30 days.
    #
    # This gives us the basic 30-day sales trend
    # required for our dashboard.

    trend = trend.tail(30)


    # Convert the DataFrame into a list of dictionaries
    # so FastAPI can return it as JSON.

    return {
        "sales_trend": trend.to_dict(
            orient="records"
        )
    }


# --------------------------------------------------
# STEP 8: Create the Inventory Alerts API
# --------------------------------------------------

# This endpoint will identify products that need
# inventory attention.

@app.get("/inventory/alerts")
def inventory_alerts():

    # Load the cleaned inventory dataset.

    df = pd.read_csv(INVENTORY_FILE)


    # Find records where inventory is low.
    #
    # Here we compare the current Inventory Level
    # with Units Ordered.

    low_stock = df[
        df["Inventory Level"]
        <= df["Units Ordered"]
    ]


    # These are the columns we would like
    # to show on the dashboard.

    columns = [
        "Product ID",
        "Product Name",
        "Inventory Level"
    ]


    # Some datasets may not contain all of these
    # columns.
    #
    # So we keep only the columns that actually exist.

    available_columns = [
        column
        for column in columns
        if column in low_stock.columns
    ]


    low_stock = low_stock[
        available_columns
    ]


    # We don't want to return thousands of records
    # to the dashboard.
    #
    # For now, return only the first 20 alerts.

    low_stock = low_stock.head(20)


    # Return the low-stock information as JSON.

    return {
        "low_stock_products":
        low_stock.to_dict(
            orient="records"
        )
    }


# --------------------------------------------------
# STEP 9: Create the Customer Summary API
# --------------------------------------------------

# This endpoint provides basic customer information
# for the dashboard.

@app.get("/customers/summary")
def customer_summary():

    # Load our cleaned customer dataset.

    df = pd.read_csv(CUSTOMER_FILE)


    # Count the number of customers.

    total_customers = len(df)


    # Count how many different countries
    # are represented in the customer data.

    countries = df["Country"].nunique()


    # Return the results as JSON.

    return {
        "total_customers": int(total_customers),
        "countries": int(countries)
    }


# --------------------------------------------------
# STEP 10: Create a Health Check API
# --------------------------------------------------

# This endpoint helps us check whether our backend
# and required data files are available.

@app.get("/health")
def health_check():

    return {
        "status": "healthy",

        # True means the file exists.
        # False means the file cannot be found.

        "sales_data": SALES_FILE.exists(),
        "customer_data": CUSTOMER_FILE.exists(),
        "inventory_data": INVENTORY_FILE.exists()
    }

# ---------------------------------------------------------
# PROTECTED BUSINESS ANALYTICS ENDPOINT
# ---------------------------------------------------------
# Only these roles can access this endpoint:
#
# Business Owner
# Store Manager
#
# Sales Executive and Administrator will be denied.
# ---------------------------------------------------------

@app.get("/protected/business-analytics")
def protected_business_analytics(
    user=Depends(
        require_role([
            "Business Owner",
            "Store Manager"
        ])
    )
):

    # If the user's role is allowed, this message is returned.
    return {
        "message": "You can access business analytics",
        "user_email": user["email"],
        "role": user["role"]
    }