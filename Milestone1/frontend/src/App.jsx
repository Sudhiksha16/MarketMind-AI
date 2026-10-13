
import { useEffect, useMemo, useState } from "react";
import "./App.css";

// Use the configured backend URL.
// The localhost value is used for local development only.
const API = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

const NAVIGATION = [
  { group: "WORKSPACE", items: [
    { id: "overview", label: "Overview", icon: "◫" },
    { id: "sales", label: "Sales Analytics", icon: "↗" },
    { id: "customers", label: "Customers", icon: "♙" },
    { id: "segments", label: "Customer Segments", icon: "◎" },
    { id: "forecast", label: "Revenue Forecast", icon: "⌁" },
  ]},
  { group: "INTELLIGENCE", items: [
    { id: "recommendations", label: "Recommendations", icon: "✳" },
    { id: "churn", label: "Churn Risk", icon: "♡" },
    { id: "anomalies", label: "Anomaly Alerts", icon: "△" },
  ]},
  { group: "OPERATIONS", items: [
    { id: "inventory", label: "Inventory", icon: "▤" },
    { id: "reports", label: "Reports", icon: "▧" },
    { id: "users", label: "User Management", icon: "♧" },
  ]},
];

const TITLES = {
  overview: ["Business Overview", "Your business performance at a glance."],
  sales: ["Sales Analytics", "Explore sales performance and historical trends."],
  customers: ["Customer Insights", "Understand your customer base."],
  segments: ["Customer Segments", "Explore customer groups based on purchasing behavior."],
  forecast: ["Revenue Forecast", "Review the generated future revenue estimates."],
  recommendations: ["Product Recommendations", "Personalized suggestions and products purchased together."],
  churn: ["Customer Churn Risk", "Review predicted customer risk categories."],
  anomalies: ["Anomaly Alerts", "Investigate unusual transaction patterns."],
  inventory: ["Inventory", "Review available inventory information and alerts."],
  reports: ["Business Reports", "Access business analytics and report information."],
  users: ["User Management", "Account and access management information."],
};

async function apiGet(path, token) {
  const response = await fetch(`${API}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  if (!response.ok) {
    throw new Error(`${path} returned HTTP ${response.status}`);
  }

  return response.json();
}

function records(data, preferredKeys = []) {
  if (Array.isArray(data)) return data;
  if (!data || typeof data !== "object") return [];

  for (const key of preferredKeys) {
    if (Array.isArray(data[key])) return data[key];
  }

  const arrayValue = Object.values(data).find(Array.isArray);
  return arrayValue || [];
}

function number(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function money(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(number(value));
}

function prettyKey(key) {
  return String(key)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function Table({ rows, emptyMessage = "No records available." }) {
  const columns = useMemo(() => {
    const keys = [...new Set(rows.flatMap((row) =>
      row && typeof row === "object" ? Object.keys(row) : []
    ))];
    return keys.slice(0, 8);
  }, [rows]);

  if (!rows.length) {
    return <div className="empty-state">{emptyMessage}</div>;
  }

  if (!columns.length) {
    return (
      <div className="record-list">
        {rows.slice(0, 30).map((item, index) => (
          <div className="record-row" key={index}>
            {String(item)}
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>{columns.map((key) => <th key={key}>{prettyKey(key)}</th>)}</tr>
        </thead>
        <tbody>
          {rows.slice(0, 100).map((row, index) => (
            <tr key={index}>
              {columns.map((key) => (
                <td key={key}>
                  {row[key] === null || row[key] === undefined
                    ? "—"
                    : typeof row[key] === "object"
                      ? JSON.stringify(row[key])
                      : String(row[key])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length > 100 && (
        <p className="table-note">Showing 100 of {rows.length} records.</p>
      )}
    </div>
  );
}

function Metric({ label, value, hint, symbol }) {
  return (
    <article className="metric-card">
      <div className="metric-top">
        <span>{label}</span>
        <span className="metric-symbol">{symbol}</span>
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-hint">{hint}</div>
    </article>
  );
}

function Panel({ title, subtitle, action, children }) {
  return (
    <section className="content-panel">
      <div className="panel-heading">
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

function LoginScreen({ onLogin, busy, error }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function submit(event) {
    event.preventDefault();
    onLogin(email, password);
  }

  return (
    <main className="login-screen">
      <form className="login-card" onSubmit={submit}>
        <div className="brand-mark">M</div>
        <p className="eyebrow">SMALL BUSINESS INTELLIGENCE</p>
        <h1>Welcome to MarketMind AI</h1>
        <p className="muted">Sign in with your application account.</p>

        {error && <div className="notice notice-error">{error}</div>}

        <label htmlFor="email">Email address</label>
        <input
          id="email"
          type="email"
          autoComplete="username"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@company.com"
          required
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Enter your password"
          required
        />

        <button className="primary-button full-width" disabled={busy}>
          {busy ? "Signing in…" : "Sign in"}
        </button>
        <p className="login-footnote">
          Use credentials configured for your backend.
        </p>
      </form>
    </main>
  );
}

export default function App() {
  const [activePage, setActivePage] = useState("overview");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [token, setToken] = useState("");
  const [user, setUser] = useState(null);
  const [loginBusy, setLoginBusy] = useState(false);
  const [loginError, setLoginError] = useState("");
  const [loading, setLoading] = useState(false);
  const [pageError, setPageError] = useState("");
  const [data, setData] = useState({});
  const [lastUpdated, setLastUpdated] = useState("");

  async function login(email, password) {
    setLoginBusy(true);
    setLoginError("");

    try {
      const response = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error("Login failed. Check your email and password.");
      }

      const result = await response.json();

      if (!result.access_token) {
        throw new Error("The login API did not return an access token.");
      }

      setToken(result.access_token);
      setUser({
        email,
        role: result.role || result.user?.role || "Authenticated user",
      });
    } catch (error) {
      setLoginError(error.message || "Unable to sign in.");
    } finally {
      setLoginBusy(false);
    }
  }

  function logout() {
    setToken("");
    setUser(null);
    setData({});
    setActivePage("overview");
  }

  // Load each section from its corresponding backend API.
  useEffect(() => {
    if (!token) return;

    const endpoints = {
      overview: [
        ["sales", "/sales/summary"],
        ["customers", "/customers/summary"],
        ["inventory", "/inventory/alerts"],
      ],
      sales: [["trend", "/sales/trend"], ["sales", "/sales/summary"]],
      customers: [["customers", "/customers/summary"]],
      segments: [["segments", "/segments"]],
      forecast: [["forecast", "/forecast/revenue"]],
      recommendations: [
        ["recommendations", "/recommendations"],
        ["rules", "/recommendations/association-rules"],
      ],
      churn: [
        ["churn", "/churn/predictions"],
        ["churnMetrics", "/churn/model-comparison"],
      ],
      anomalies: [
        ["anomalies", "/anomalies/alerts"],
        ["statisticalAnomalies", "/anomalies/statistical"],
        ["forestAnomalies", "/anomalies/isolation-forest"],
      ],
      inventory: [["inventory", "/inventory/alerts"]],
      reports: [],
      users: [],
    };

    const requested = endpoints[activePage] || [];
    let cancelled = false;

    async function loadPage() {
      setLoading(true);
      setPageError("");

      const results = await Promise.allSettled(
        requested.map(async ([key, path]) => [key, await apiGet(path, token)])
      );

      if (cancelled) return;

      const nextData = {};
      const failures = [];

      results.forEach((result, index) => {
        if (result.status === "fulfilled") {
          const [key, value] = result.value;
          nextData[key] = value;
        } else {
          failures.push(requested[index][1]);
        }
      });

      setData((previous) => ({ ...previous, ...nextData }));
      setLastUpdated(new Date().toLocaleTimeString());

      if (failures.length) {
        setPageError(`Some data could not be loaded: ${failures.join(", ")}. Check the backend and permissions.`);
      }

      setLoading(false);
    }

    loadPage();

    return () => {
      cancelled = true;
    };
  }, [activePage, token]);

  if (!token) {
    return (
      <LoginScreen onLogin={login} busy={loginBusy} error={loginError} />
    );
  }

  const sales = data.sales || {};
  const customers = data.customers || {};
  const inventory = data.inventory || {};
  const trend = records(data.trend, ["sales_trend", "trend"]);
  const segments = records(data.segments, ["segments"]);
  const forecastData = data.forecast || {};
  const forecast = records(forecastData.forecast, ["forecast"]);
  const recommendations = records(data.recommendations);
  const rules = records(data.rules);
  const churn = records(data.churn);
  const churnMetrics = records(data.churnMetrics);
  const anomalies = records(data.anomalies);
  const statisticalAnomalies = records(data.statisticalAnomalies);
  const forestAnomalies = records(data.forestAnomalies);
  const lowStock = records(inventory.low_stock_products, ["low_stock_products"]);
  const title = TITLES[activePage] || TITLES.overview;

  function navigate(id) {
    setActivePage(id);
    setMobileNavOpen(false);
  }

  function segmentName(item) {
    return item.segment_name || item.segment || item.segment_label || "Customer segment";
  }

  return (
    <div className="app-shell">
      {mobileNavOpen && (
        <button
          className="nav-backdrop"
          aria-label="Close navigation"
          onClick={() => setMobileNavOpen(false)}
        />
      )}

      <aside className={`sidebar ${mobileNavOpen ? "sidebar-open" : ""}`}>
        <button className="brand" onClick={() => navigate("overview")}>
          <span className="brand-mark">M</span>
          <span className="brand-text">
            <strong>MarketMind AI</strong>
            <small>Business Intelligence</small>
          </span>
        </button>

        <div className="workspace-label"></div>
        <div className="nav-scroll">
          {NAVIGATION.map((group) => (
            <div className="nav-group" key={group.group}>
              <p className="nav-group-title">{group.group}</p>
              {group.items.map((item) => (
                <button
                  key={item.id}
                  className={`nav-link ${activePage === item.id ? "active" : ""}`}
                  onClick={() => navigate(item.id)}
                >
                  <span className="nav-icon">{item.icon}</span>
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
          ))}
        </div>

        <div className="sidebar-bottom">
          <div className="connection-indicator">
            <span className="status-dot" />
            Connected session
          </div>
          <button className="logout-button" onClick={logout}>↪ Sign out</button>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setMobileNavOpen(true)}
            aria-label="Open navigation"
          >
            ☰
          </button>
          <div className="breadcrumb">MarketMind AI <span>/</span> {title[0]}</div>
          <div className="topbar-user">
            <div className="avatar">{(user?.email || "U").charAt(0).toUpperCase()}</div>
            <div className="user-label">
              <strong>{user?.email}</strong>
              <small>{user?.role}</small>
            </div>
          </div>
        </header>

        <div className="page-content">
          <div className="page-heading">
            <div>
              <p className="eyebrow">BUSINESS INTELLIGENCE</p>
              <h1>{title[0]}</h1>
              <p className="muted">{title[1]}</p>
            </div>
            <button
              className="secondary-button"
              onClick={() => {
                setData({});
                setActivePage((current) => {
                  // Trigger a fresh request by briefly changing the page state.
                  return current;
                });
              }}
              title="Use the page navigation to reload current data"
            >
              <span>●</span> Live workspace
            </button>
          </div>

          {pageError && <div className="notice notice-warning">{pageError}</div>}
          {loading && <div className="loading-bar"><span /></div>}

          {activePage === "overview" && (
            <>
              <div className="metric-grid">
                <Metric label="Total Revenue" value={money(sales.total_revenue)} hint="Revenue in the prepared sales dataset" symbol="₹" />
                <Metric label="Sales Records" value={number(sales.total_orders).toLocaleString("en-IN")} hint="Cleaned sales records" symbol="▤" />
                <Metric label="Quantity Sold" value={number(sales.total_quantity_sold).toLocaleString("en-IN")} hint="Units recorded in sales" symbol="↗" />
                <Metric label="Customers" value={number(customers.total_customers).toLocaleString("en-IN")} hint={`${customers.countries ?? "—"} countries represented`} symbol="♙" />
              </div>

              <div className="two-column">
                <Panel title="Sales Performance" subtitle="Latest available daily sales records" action={<button className="text-button" onClick={() => navigate("sales")}>View analytics →</button>}>
                  <Table rows={trend.slice(-6).reverse()} emptyMessage="Sales trend data will appear here." />
                </Panel>
                <Panel title="Inventory Attention" subtitle="Items flagged by the existing inventory rule" action={<button className="text-button" onClick={() => navigate("inventory")}>View inventory →</button>}>
                  <Table rows={lowStock.slice(0, 6)} emptyMessage="No inventory alerts returned." />
                </Panel>
              </div>

              <Panel title="Customer Segments" subtitle="Summary of customer purchasing behavior" action={<button className="text-button" onClick={() => navigate("segments")}>Explore segments →</button>}>
                <Table rows={segments} emptyMessage="No segment summary returned." />
              </Panel>
            </>
          )}

          {activePage === "sales" && (
            <>
              <div className="metric-grid">
                <Metric label="Total Revenue" value={money(sales.total_revenue)} hint="Prepared sales dataset" symbol="₹" />
                <Metric label="Sales Records" value={number(sales.total_orders).toLocaleString("en-IN")} hint="Cleaned records" symbol="▤" />
                <Metric label="Quantity Sold" value={number(sales.total_quantity_sold).toLocaleString("en-IN")} hint="Recorded quantity" symbol="↗" />
                <Metric label="Top Product" value={sales.top_product || "—"} hint="Highest quantity sold" symbol="★" />
              </div>
              <Panel title="Sales Trend" subtitle="Daily revenue from the latest available sales dates">
                <Table rows={trend} emptyMessage="No sales trend is available." />
              </Panel>
            </>
          )}

          {activePage === "customers" && (
            <Panel title="Customer Summary" subtitle="Summary from the customer analytics API">
              <div className="detail-grid">
                {Object.entries(customers).map(([key, value]) => (
                  <div className="detail-card" key={key}>
                    <span>{prettyKey(key)}</span>
                    <strong>{typeof value === "number" ? value.toLocaleString("en-IN") : String(value ?? "—")}</strong>
                  </div>
                ))}
              </div>
            </Panel>
          )}

          {activePage === "segments" && (
            <Panel title="Customer Segments" subtitle="Segment results generated by your clustering workflow">
              <Table rows={segments} emptyMessage="No segmentation results returned." />
            </Panel>
          )}

          {activePage === "forecast" && (
            <>
              <div className="metric-grid metric-grid-single">
                <Metric label="Predicted Revenue" value={money(forecastData.predicted_revenue)} hint={`Forecast model: ${forecastData.model_used || "Configured model"}. This is an estimate, not a guarantee.`} symbol="⌁" />
              </div>
              <Panel title="Revenue Forecast" subtitle="Forecast records returned by the backend">
                <Table rows={forecast} emptyMessage="No forecast records returned. Check forecast API access." />
              </Panel>
            </>
          )}

          {activePage === "recommendations" && (
            <>
              <Panel title="Recommended Products" subtitle="Combined recommendation results">
                <Table rows={recommendations} emptyMessage="No combined recommendations are available." />
              </Panel>
              <Panel title="Frequently Bought Together" subtitle="Association rules based on products in the same order">
                <Table rows={rules} emptyMessage="No association rules returned." />
              </Panel>
            </>
          )}

          {activePage === "churn" && (
            <>
              <div className="metric-grid">
                <Metric label="Predictions" value={churn.length.toLocaleString("en-IN")} hint="Rows returned by the churn prediction API" symbol="♙" />
                <Metric label="High Risk" value={churn.filter((row) => String(row.risk_category || row.risk_level || "").toLowerCase().includes("high")).length.toLocaleString("en-IN")} hint="Predicted high-risk rows" symbol="△" />
                <Metric label="Model Comparisons" value={churnMetrics.length.toLocaleString("en-IN")} hint="Evaluation result rows" symbol="◎" />
                <Metric label="Status" value="Available" hint="Generated predictions loaded from backend" symbol="✓" />
              </div>
              <Panel title="Customer Churn Predictions" subtitle="Customer-level predictions and risk categories">
                <Table rows={churn} emptyMessage="No churn predictions returned." />
              </Panel>
              <Panel title="Model Comparison" subtitle="Evaluation metrics from the model comparison output">
                <Table rows={churnMetrics} emptyMessage="No model comparison results returned." />
              </Panel>
            </>
          )}

          {activePage === "anomalies" && (
            <>
              <div className="metric-grid">
                <Metric label="Alert Records" value={anomalies.length.toLocaleString("en-IN")} hint="Generated alert rows" symbol="△" />
                <Metric label="Statistical Results" value={statisticalAnomalies.length.toLocaleString("en-IN")} hint="Z-score detection output" symbol="σ" />
                <Metric label="Isolation Forest" value={forestAnomalies.length.toLocaleString("en-IN")} hint="Model detection output" symbol="◎" />
                <Metric label="Alert Status" value={anomalies.length ? "Review" : "No data"} hint="Review alerts before taking action" symbol="!" />
              </div>
              <Panel title="Anomaly Alerts" subtitle="Generated alerts and severity information">
                <Table rows={anomalies} emptyMessage="No anomaly alerts returned." />
              </Panel>
              <Panel title="Statistical Anomalies" subtitle="Z-score detection results">
                <Table rows={statisticalAnomalies} emptyMessage="No statistical anomalies returned." />
              </Panel>
              <Panel title="Isolation Forest Results" subtitle="Detected unusual transactions">
                <Table rows={forestAnomalies} emptyMessage="No Isolation Forest results returned." />
              </Panel>
            </>
          )}

          {activePage === "inventory" && (
            <Panel title="Inventory Alerts" subtitle="Items returned by the existing inventory API">
              <Table rows={lowStock} emptyMessage="No inventory items returned." />
            </Panel>
          )}

          {activePage === "reports" && (
            <Panel title="Business Reports" subtitle="Report availability">
              <div className="report-card">
                <div className="report-icon">▧</div>
                <div>
                  <h3>Business Analytics Report</h3>
                  <p>Your generated Excel report is currently stored in the project files. A public download action needs a backend file-download endpoint before it can be downloaded from this page.</p>
                </div>
              </div>
            </Panel>
          )}

          {activePage === "users" && (
            <Panel title="User Management" subtitle="Current signed-in session">
              <div className="detail-grid">
                <div className="detail-card"><span>Signed-in account</span><strong>{user?.email || "—"}</strong></div>
                <div className="detail-card"><span>Role</span><strong>{user?.role || "—"}</strong></div>
              </div>
              <div className="notice notice-warning">
                Account creation, user editing and role changes are not implemented by the current backend. This page shows session details only.
              </div>
            </Panel>
          )}

          <footer className="app-footer">
            <span>MarketMind AI · Small Business Intelligence</span>
            <span>{lastUpdated ? `Last data request: ${lastUpdated}` : "Ready"}</span>
          </footer>
        </div>
      </main>
    </div>
  );
}
