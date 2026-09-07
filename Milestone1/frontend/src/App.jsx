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

  // Each useState variable stores one type of information
  // that we receive from our FastAPI backend.

  const [sales, setSales] = useState(null);
  const [customers, setCustomers] = useState(null);
  const [inventory, setInventory] = useState(null);
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  // --------------------------------------------------
  // STEP 2: Get data from FastAPI
  // --------------------------------------------------

  // useEffect runs automatically when the dashboard loads.

  useEffect(() => {

    // This function calls our FastAPI endpoints.

    async function loadDashboard() {

      try {

        // Call the Sales Summary API.
        const salesResponse = await fetch(
          "http://127.0.0.1:8000/sales/summary"
        );

        // Convert the API response from JSON into JavaScript data.
        const salesData = await salesResponse.json();

        // Store the sales information.
        setSales(salesData);


        // Call the Customer Summary API.
        const customerResponse = await fetch(
          "http://127.0.0.1:8000/customers/summary"
        );

        const customerData = await customerResponse.json();

        // Store customer information.
        setCustomers(customerData);


        // Call the Inventory Alerts API.
        const inventoryResponse = await fetch(
          "http://127.0.0.1:8000/inventory/alerts"
        );

        const inventoryData = await inventoryResponse.json();

        // Store inventory information.
        setInventory(inventoryData);


        // Call the Sales Trend API.
        const trendResponse = await fetch(
          "http://127.0.0.1:8000/sales/trend"
        );

        const trendData = await trendResponse.json();

        // Store the sales trend.
        setTrend(trendData.sales_trend);


        // All API calls were successful.
        setLoading(false);

      } catch (err) {

        // If something goes wrong, show an error message.
        console.error(err);

        setError(
          "Unable to connect to the MarketMind AI backend."
        );

        setLoading(false);
      }
    }


    // Run the function.
    loadDashboard();

  }, []);


  // --------------------------------------------------
  // STEP 3: Show loading message
  // --------------------------------------------------

  // While the backend data is being loaded,
  // show a simple loading message.

  if (loading) {
    return (
      <div className="app">
        <h1>MarketMind AI</h1>
        <p>Loading dashboard...</p>
      </div>
    );
  }


  // --------------------------------------------------
  // STEP 4: Show error message
  // --------------------------------------------------

  // If React cannot communicate with FastAPI,
  // display the error instead of a blank screen.

  if (error) {
    return (
      <div className="app">
        <h1>MarketMind AI</h1>
        <p className="error">{error}</p>
      </div>
    );
  }


  // --------------------------------------------------
  // STEP 5: Display the dashboard
  // --------------------------------------------------

  return (
    <div className="app">

      {/* -------------------------------------------- */}
      {/* Header                                      */}
      {/* -------------------------------------------- */}

      <header className="header">

        <div>
          <h1>MarketMind AI</h1>

          <p>
            Small Business Sales Intelligence Platform
          </p>
        </div>

        <div className="user-info">
          Dashboard
        </div>

      </header>


      {/* -------------------------------------------- */}
      {/* Summary Cards                               */}
      {/* -------------------------------------------- */}

      <section className="cards">

        {/* Revenue Card */}
        <div className="card">

          <h3>Total Revenue</h3>

          <p className="value">
            ₹{sales?.total_revenue?.toLocaleString()}
          </p>

          <span>
            From cleaned sales data
          </span>

        </div>


        {/* Orders Card */}
        <div className="card">

          <h3>Total Orders</h3>

          <p className="value">
            {sales?.total_orders?.toLocaleString()}
          </p>

          <span>
            Valid sales records
          </span>

        </div>


        {/* Quantity Card */}
        <div className="card">

          <h3>Quantity Sold</h3>

          <p className="value">
            {sales?.total_quantity_sold?.toLocaleString()}
          </p>

          <span>
            Products sold
          </span>

        </div>


        {/* Customer Card */}
        <div className="card">

          <h3>Total Customers</h3>

          <p className="value">
            {customers?.total_customers?.toLocaleString()}
          </p>

          <span>
            Across {customers?.countries} countries
          </span>

        </div>

      </section>


      {/* -------------------------------------------- */}
      {/* Main Content                                */}
      {/* -------------------------------------------- */}

      <section className="dashboard-grid">


        {/* ---------------------------------------- */}
        {/* Top Product                             */}
        {/* ---------------------------------------- */}

        <div className="panel">

          <h2>Top Product</h2>

          <p className="top-product">
            {sales?.top_product}
          </p>

          <p>
            Product with the highest quantity sold
          </p>

        </div>


        {/* ---------------------------------------- */}
        {/* Inventory Alerts                        */}
        {/* ---------------------------------------- */}

        <div className="panel">

          <h2>Inventory Alerts</h2>

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

              <p>No inventory alerts found.</p>

            )}

          </div>

        </div>

      </section>


      {/* -------------------------------------------- */}
      {/* Sales Trend                                */}
      {/* -------------------------------------------- */}

      <section className="panel sales-panel">

        <h2>30-Day Sales Trend</h2>

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
                ₹{Number(item.revenue).toLocaleString()}
              </strong>

            </div>

          ))}

        </div>

      </section>


      {/* -------------------------------------------- */}
      {/* Footer                                     */}
      {/* -------------------------------------------- */}

      <footer>

        <p>
          MarketMind AI • Milestone 1
        </p>

      </footer>

    </div>
  );
}


// Export App so that main.jsx can display it.
export default App;