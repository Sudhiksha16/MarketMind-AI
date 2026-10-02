// --------------------------------------------------
// MARKETMIND AI - MAIN DASHBOARD
// --------------------------------------------------

// useEffect runs code when the page loads.
// useState stores data that can change while the app runs.
import { useEffect, useState } from "react";

// App.css contains the design/style of our dashboard.
import "./App.css";


function App() {

  // --------------------------------------------------
  // STEP 1: Create variables to store API data
  // --------------------------------------------------

  // Sales summary data.
  const [sales, setSales] = useState(null);

  // Customer summary data.
  const [customers, setCustomers] = useState(null);

  // Inventory alert data.
  const [inventory, setInventory] = useState(null);

  // Sales trend data.
  const [trend, setTrend] = useState([]);

  // Customer segmentation data.
  const [segments, setSegments] = useState([]);

  // Revenue forecast data.
  const [forecast, setForecast] = useState([]);

  // Predicted revenue value returned by the backend.
  const [predictedRevenue, setPredictedRevenue] = useState(null);

  // Name of the forecasting model.
  const [forecastModel, setForecastModel] = useState("");

  // Loading state.
  const [loading, setLoading] = useState(true);

  // Error message.
  const [error, setError] = useState("");


  // --------------------------------------------------
  // STEP 2: Load dashboard data
  // --------------------------------------------------

  useEffect(() => {

    async function loadDashboard() {

      try {

        // --------------------------------------------------
        // SALES SUMMARY
        // --------------------------------------------------

        // Call the Sales Summary API.
        const salesResponse = await fetch(
          "http://127.0.0.1:8000/sales/summary"
        );

        if (!salesResponse.ok) {
          throw new Error("Sales API failed.");
        }

        // Convert response into JSON.
        const salesData = await salesResponse.json();

        // Store sales information.
        setSales(salesData);


        // --------------------------------------------------
        // CUSTOMER SUMMARY
        // --------------------------------------------------

        // Call the Customer Summary API.
        const customerResponse = await fetch(
          "http://127.0.0.1:8000/customers/summary"
        );

        if (!customerResponse.ok) {
          throw new Error("Customer API failed.");
        }

        const customerData = await customerResponse.json();

        // Store customer information.
        setCustomers(customerData);


        // --------------------------------------------------
        // INVENTORY ALERTS
        // --------------------------------------------------

        // Call the Inventory Alerts API.
        const inventoryResponse = await fetch(
          "http://127.0.0.1:8000/inventory/alerts"
        );

        if (!inventoryResponse.ok) {
          throw new Error("Inventory API failed.");
        }

        const inventoryData = await inventoryResponse.json();

        // Store inventory information.
        setInventory(inventoryData);


        // --------------------------------------------------
        // SALES TREND
        // --------------------------------------------------

        // Call the Sales Trend API.
        const trendResponse = await fetch(
          "http://127.0.0.1:8000/sales/trend"
        );

        if (!trendResponse.ok) {
          throw new Error("Sales trend API failed.");
        }

        const trendData = await trendResponse.json();

        // Store the sales trend.
        setTrend(trendData.sales_trend || []);


        // --------------------------------------------------
        // CUSTOMER SEGMENTS
        // --------------------------------------------------

        // Call the new Milestone 2 segmentation API.
        const segmentResponse = await fetch(
          "http://127.0.0.1:8000/segments"
        );

        if (!segmentResponse.ok) {
          throw new Error("Customer segmentation API failed.");
        }

        const segmentData = await segmentResponse.json();

        // Store customer segmentation information.
        setSegments(
          Array.isArray(segmentData)
            ? segmentData
            : segmentData.segments || []
        );


        // --------------------------------------------------
        // LOGIN FOR FORECAST API
        // --------------------------------------------------

        // The revenue forecast endpoint is protected
        // using JWT authentication.

        const loginResponse = await fetch(
          "http://127.0.0.1:8000/auth/login",
          {
            method: "POST",

            headers: {
              "Content-Type": "application/json"
            },

            body: JSON.stringify({
              email: "owner@marketmind.com",
              password: "password123"
            })
          }
        );

        if (!loginResponse.ok) {
          throw new Error("Authentication failed.");
        }

        // Convert login response into JSON.
        const loginData = await loginResponse.json();

        // Get the JWT access token.
        const accessToken = loginData.access_token;


        // --------------------------------------------------
        // REVENUE FORECAST
        // --------------------------------------------------

        // Call the protected forecast endpoint.
        const forecastResponse = await fetch(
          "http://127.0.0.1:8000/forecast/revenue",
          {
            headers: {
              Authorization: `Bearer ${accessToken}`
            }
          }
        );

        if (!forecastResponse.ok) {
          throw new Error("Revenue forecast API failed.");
        }

        // Convert forecast response into JSON.
        const forecastData = await forecastResponse.json();

        // Store predicted revenue.
        setPredictedRevenue(
          forecastData.predicted_revenue ?? null
        );

        // Store forecasting model name.
        setForecastModel(
          forecastData.model_used || "Prophet"
        );

        // Store forecast records.
        setForecast(
          Array.isArray(forecastData.forecast)
            ? forecastData.forecast
            : []
        );


        // --------------------------------------------------
        // ALL DATA LOADED SUCCESSFULLY
        // --------------------------------------------------

        setLoading(false);

      } catch (err) {

        // Print technical error in browser console.
        console.error(err);

        // Show user-friendly error.
        setError(
          "Unable to load MarketMind AI dashboard data."
        );

        setLoading(false);
      }
    }


    // Run dashboard loading function.
    loadDashboard();

  }, []);


  // --------------------------------------------------
  // STEP 3: Loading screen
  // --------------------------------------------------

  if (loading) {

    return (
      <div className="app">

        <h1>MarketMind AI</h1>

        <p>
          Loading dashboard and Milestone 2 analytics...
        </p>

      </div>
    );
  }


  // --------------------------------------------------
  // STEP 4: Error screen
  // --------------------------------------------------

  if (error) {

    return (
      <div className="app">

        <h1>MarketMind AI</h1>

        <p className="error">
          {error}
        </p>

        <p>
          Make sure the FastAPI backend is running
          on port 8000.
        </p>

      </div>
    );
  }


  // --------------------------------------------------
  // STEP 5: Main dashboard
  // --------------------------------------------------

  return (

    <div className="app">


      {/* -------------------------------------------- */}
      {/* HEADER                                      */}
      {/* -------------------------------------------- */}

      <header className="header">

        <div>

          <h1>
            MarketMind AI
          </h1>

          <p>
            Small Business Sales Intelligence Platform
          </p>

        </div>

        <div className="user-info">
          Milestone 2 Dashboard
        </div>

      </header>


      {/* -------------------------------------------- */}
      {/* SUMMARY CARDS                               */}
      {/* -------------------------------------------- */}

      <section className="cards">


        {/* Total Revenue */}

        <div className="card">

          <h3>
            Total Revenue
          </h3>

          <p className="value">

            ₹
            {sales?.total_revenue?.toLocaleString()}

          </p>

          <span>
            From cleaned sales data
          </span>

        </div>


        {/* Total Orders */}

        <div className="card">

          <h3>
            Total Orders
          </h3>

          <p className="value">

            {sales?.total_orders?.toLocaleString()}

          </p>

          <span>
            Valid sales records
          </span>

        </div>


        {/* Quantity Sold */}

        <div className="card">

          <h3>
            Quantity Sold
          </h3>

          <p className="value">

            {sales?.total_quantity_sold?.toLocaleString()}

          </p>

          <span>
            Products sold
          </span>

        </div>


        {/* Total Customers */}

        <div className="card">

          <h3>
            Total Customers
          </h3>

          <p className="value">

            {customers?.total_customers?.toLocaleString()}

          </p>

          <span>

            Across {customers?.countries} countries

          </span>

        </div>


      </section>


      {/* -------------------------------------------- */}
      {/* TOP PRODUCT + INVENTORY                     */}
      {/* -------------------------------------------- */}

      <section className="dashboard-grid">


        {/* Top Product */}

        <div className="panel">

          <h2>
            Top Product
          </h2>

          <p className="top-product">

            {sales?.top_product}

          </p>

          <p>
            Product with the highest quantity sold
          </p>

        </div>


        {/* Inventory Alerts */}

        <div className="panel">

          <h2>
            Inventory Alerts
          </h2>

          <p>
            Products requiring inventory attention
          </p>


          <div className="inventory-list">

            {inventory?.low_stock_products?.length > 0 ? (

              inventory.low_stock_products.map(
                (product, index) => (

                  <div
                    className="inventory-item"
                    key={index}
                  >

                    <strong>
                      {product["Product ID"]}
                    </strong>

                    <span>
                      Stock: {product["Inventory Level"]}
                    </span>

                  </div>

                )
              )

            ) : (

              <p>
                No inventory alerts found.
              </p>

            )}

          </div>

        </div>


      </section>


      {/* -------------------------------------------- */}
      {/* CUSTOMER SEGMENTATION - MILESTONE 2         */}
      {/* -------------------------------------------- */}

      <section className="panel">

        <h2>
          Customer Segmentation
        </h2>

        <p>
          Customers grouped according to their
          purchasing behavior.
        </p>


        <div className="trend-list">

          {segments.length > 0 ? (

            segments.map((segment, index) => (

              <div
                className="trend-item"
                key={index}
              >

                <span>
                  {segment.customer_segment}
                </span>

                <strong>
                  {Number(
                    segment.customer_count || 0
                  ).toLocaleString()} customers
                </strong>

              </div>

            ))

          ) : (

            <p>
              No customer segment data available.
            </p>

          )}

        </div>

      </section>


      {/* -------------------------------------------- */}
      {/* CUSTOMER SEGMENT DETAILS                     */}
      {/* -------------------------------------------- */}

      <section className="dashboard-grid">


        {segments.map((segment, index) => (

          <div
            className="panel"
            key={index}
          >

            <h2>
              {segment.customer_segment}
            </h2>

            <p>
              Customers:
              {" "}
              {Number(
                segment.customer_count || 0
              ).toLocaleString()}
            </p>

            <p>
              Purchase Frequency:
              {" "}
              {Number(
                segment.average_purchase_frequency || 0
              ).toFixed(2)}
            </p>

            <p>
              Average Purchase Value:
              {" "}
              ₹
              {Number(
                segment.average_purchase_value || 0
              ).toLocaleString()}
            </p>

            <p>
              Average Activity:
              {" "}
              {Number(
                segment.average_activity_days || 0
              ).toFixed(2)}
              {" "}days
            </p>

          </div>

        ))}

      </section>


      {/* -------------------------------------------- */}
      {/* SALES TREND                                 */}
      {/* -------------------------------------------- */}

      <section className="panel sales-panel">

        <h2>
          30-Day Sales Trend
        </h2>

        <p>
          Daily revenue from the latest available
          sales dates.
        </p>


        <div className="trend-list">

          {trend.map((item, index) => (

            <div
              className="trend-item"
              key={index}
            >

              <span>
                {item.date}
              </span>

              <strong>
                ₹
                {Number(
                  item.revenue
                ).toLocaleString()}
              </strong>

            </div>

          ))}

        </div>

      </section>


      {/* -------------------------------------------- */}
      {/* REVENUE FORECAST - MILESTONE 2               */}
      {/* -------------------------------------------- */}

      <section className="panel sales-panel">

        <h2>
          Revenue Forecast
        </h2>

        <p>
          Predicted revenue for the upcoming
          forecasting period.
        </p>


        {/* Forecast summary */}

        <div className="card">

          <h3>
            Predicted Revenue
          </h3>

          <p className="value">

            {predictedRevenue !== null
              ? `₹${Number(
                  predictedRevenue
                ).toLocaleString()}`
              : "Not available"}

          </p>

          <span>
            Model: {forecastModel}
          </span>

        </div>


        {/* Forecast values */}

        <div className="trend-list">

          {forecast.length > 0 ? (

            forecast.map((item, index) => (

              <div
                className="trend-item"
                key={index}
              >

                <span>
                  {item.ds}
                </span>

                <strong>

                  ₹
                  {Number(
                    item.yhat || 0
                  ).toLocaleString()}

                </strong>

              </div>

            ))

          ) : (

            <p>
              No forecast data available.
            </p>

          )}

        </div>

      </section>


      {/* -------------------------------------------- */}
      {/* FOOTER                                      */}
      {/* -------------------------------------------- */}

      <footer>

        <p>
          MarketMind AI • Milestone 2
        </p>

      </footer>


    </div>
  );
}


// Export App so that main.jsx can display it.
export default App;