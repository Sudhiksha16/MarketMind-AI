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
app = FastAPI(
    title="MarketMind AI API",
    description="Small Business Sales Intelligence Platform",
    version="1.0.0"
)


# --------------------------------------------------
# Register Authentication Routes
# --------------------------------------------------

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
# STEP 3: Find the project folders
# --------------------------------------------------

# __file__ means this current Python file:
#
# MarketMind AI
#     └── Milestone1
#           └── backend
#                 └── main.py
#
# .parent gives us:
#     Milestone1/backend
#
# .parent.parent gives us:
#     Milestone1
#
# .parent.parent.parent gives us:
#     MarketMind AI
#
# We keep BASE_DIR for Milestone 1 files.
# We use PROJECT_ROOT for Milestone 2 files.

BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_ROOT = BASE_DIR.parent


# --------------------------------------------------
# STEP 4: Tell Python where our Milestone 1
# cleaned datasets are
# --------------------------------------------------

# Our cleaned files are stored here:
#
# Milestone1
#     └── preprocessing
#           └── processed

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
# STEP 5: Milestone 2 file paths
# --------------------------------------------------

# Milestone 2 customer segmentation results:
#
# MarketMind AI
#     └── Milestone2
#           └── segmentation
#                 └── processed
#                       └── segment_summary.csv

SEGMENT_FILE = (
    PROJECT_ROOT
    / "Milestone2"
    / "segmentation"
    / "processed"
    / "segment_summary.csv"
)


# Milestone 2 Prophet forecasting results:
#
# MarketMind AI
#     └── Milestone2
#           └── forecasting
#                 └── processed
#                       └── prophet_forecast.csv

FORECAST_FILE = (
    PROJECT_ROOT
    / "Milestone2"
    / "forecasting"
    / "processed"
    / "prophet_forecast.csv"
)


# --------------------------------------------------
# STEP 6: Create the Home API
# --------------------------------------------------

@app.get("/")
def root():

    # Return a simple response to confirm
    # that the backend is running.

    return {
        "message": "MarketMind AI backend is running",
        "status": "success"
    }


# --------------------------------------------------
# STEP 7: Create the Sales Summary API
# --------------------------------------------------

@app.get("/sales/summary")
def sales_summary():

    # Read our cleaned sales CSV file.
    df = pd.read_csv(SALES_FILE)

    # Total revenue.
    total_revenue = df["TotalAmount"].sum()

    # Count total cleaned sales records.
    total_orders = len(df)

    # Total quantity sold.
    total_quantity = df["Quantity"].sum()

    # Find the top-selling product based on
    # total quantity sold.
    top_product = (
        df.groupby("Description")["Quantity"]
        .sum()
        .idxmax()
    )

    # Return the results as JSON.
    return {
        "total_revenue": round(float(total_revenue), 2),
        "total_orders": int(total_orders),
        "total_quantity_sold": int(total_quantity),
        "top_product": str(top_product)
    }


# --------------------------------------------------
# STEP 8: Create the Sales Trend API
# --------------------------------------------------

@app.get("/sales/trend")
def sales_trend():

    # Load the cleaned sales data.
    df = pd.read_csv(SALES_FILE)

    # Convert InvoiceDate into datetime.
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"]
    )

    # Group sales by date and calculate
    # total revenue for each date.
    trend = (
        df.groupby(
            df["InvoiceDate"].dt.date
        )["TotalAmount"]
        .sum()
        .reset_index()
    )

    # Rename columns for frontend use.
    trend.columns = [
        "date",
        "revenue"
    ]

    # Keep the latest 30 available sales dates.
    trend = trend.tail(30)

    # Convert the DataFrame into JSON.
    return {
        "sales_trend": trend.to_dict(
            orient="records"
        )
    }


# --------------------------------------------------
# STEP 9: Create the Inventory Alerts API
# --------------------------------------------------

@app.get("/inventory/alerts")
def inventory_alerts():

    # Load the cleaned inventory dataset.
    df = pd.read_csv(INVENTORY_FILE)

    # Identify low-stock records.
    #
    # We compare Inventory Level with Units Ordered.
    low_stock = df[
        df["Inventory Level"]
        <= df["Units Ordered"]
    ]

    # Columns we want to display.
    columns = [
        "Product ID",
        "Product Name",
        "Inventory Level"
    ]

    # Keep only columns that actually exist.
    available_columns = [
        column
        for column in columns
        if column in low_stock.columns
    ]

    low_stock = low_stock[
        available_columns
    ]

    # Return only the first 20 alerts.
    low_stock = low_stock.head(20)

    return {
        "low_stock_products":
        low_stock.to_dict(
            orient="records"
        )
    }


# --------------------------------------------------
# STEP 10: Create the Customer Summary API
# --------------------------------------------------

@app.get("/customers/summary")
def customer_summary():

    # Load our cleaned customer dataset.
    df = pd.read_csv(CUSTOMER_FILE)

    # Count customers.
    total_customers = len(df)

    # Count different countries.
    countries = df["Country"].nunique()

    return {
        "total_customers": int(total_customers),
        "countries": int(countries)
    }


# --------------------------------------------------
# STEP 11: Create a Health Check API
# --------------------------------------------------

@app.get("/health")
def health_check():

    return {
        "status": "healthy",

        # True means the file exists.
        "sales_data": SALES_FILE.exists(),

        "customer_data": CUSTOMER_FILE.exists(),

        "inventory_data": INVENTORY_FILE.exists(),

        # Milestone 2 files
        "segment_data": SEGMENT_FILE.exists(),

        "forecast_data": FORECAST_FILE.exists()
    }


# ==================================================
# MILESTONE 2
# CUSTOMER SEGMENTATION API
# ==================================================

@app.get("/segments")
def get_customer_segments():

    # Check whether the Milestone 2 segmentation file exists.
    if not SEGMENT_FILE.exists():
        return {
            "error": "Customer segmentation file not found"
        }

    # Load the segment summary generated by
    # analyze_segments.py.
    segment_df = pd.read_csv(
        SEGMENT_FILE
    )

    # Convert the DataFrame into JSON.
    return segment_df.to_dict(
        orient="records"
    )


# ==================================================
# MILESTONE 2
# REVENUE FORECAST API
# ==================================================

@app.get("/forecast/revenue")
def get_revenue_forecast(
    user=Depends(
        require_role([
            "Business Owner",
            "Store Manager",
            "Administrator"
        ])
    )
):

    # Check whether the forecast file exists.
    if not FORECAST_FILE.exists():
        return {
            "error": "Forecast file not found"
        }

    # Load the Prophet forecast.
    forecast_df = pd.read_csv(
        FORECAST_FILE
    )

    # Convert forecast date to datetime.
    forecast_df["ds"] = pd.to_datetime(
        forecast_df["ds"]
    )

    # The final 30 records represent
    # the 30-day future forecast generated
    # by our Prophet model.
    future_forecast = forecast_df.tail(30).copy()

    # Calculate the total predicted revenue
    # for the forecast period.
    predicted_revenue = (
        future_forecast["yhat"].sum()
    )

    return {
        "period": "Next 30 Days",

        "predicted_revenue": round(
            float(predicted_revenue),
            2
        ),

        "model_used": "Prophet",

        # Return the detailed forecast too,
        # so the React dashboard can later
        # display the forecast trend.
        "forecast": future_forecast[
            [
                "ds",
                "yhat",
                "yhat_lower",
                "yhat_upper"
            ]
        ].to_dict(
            orient="records"
        )
    }


# ==================================================
# MILESTONE 1
# PROTECTED BUSINESS ANALYTICS ENDPOINT
# ==================================================

# Only these roles can access this endpoint:
#
# Business Owner
# Store Manager
#
# Sales Executive and Administrator are denied.

@app.get("/protected/business-analytics")
def protected_business_analytics(
    user=Depends(
        require_role([
            "Business Owner",
            "Store Manager"
        ])
    )
):

    return {
        "message":
            "You can access business analytics",

        "user_email":
            user["email"],

        "role":
            user["role"]
    }