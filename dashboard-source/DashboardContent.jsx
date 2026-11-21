import React, { useState } from "react";
import { EvidenceChart, MetricCard, useDataApp } from "../../data-app-public.jsx";
import "./dashboard.css";

const dollars = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
const count = new Intl.NumberFormat("en-US");
const charts = [
  ["monthly", "Monthly sales", "bar", "sales", "Sales (USD)"],
  ["categories", "Sales by cuisine", "horizontalBar", "sales", "Sales (USD)"],
  ["hourly", "Sales by hour", "line", "sales", "Sales (USD)"],
  ["weekday", "Sales by weekday", "bar", "sales", "Sales (USD)"],
  ["items", "Top menu items by sales", "horizontalBar", "sales", "Sales (USD)"],
  ["pairs", "Most frequent item pairs", "horizontalBar", "orders", "Orders"],
];

export function DashboardContent() {
  const [month, setMonth] = useState("All");
  const [category, setCategory] = useState("All");
  const { queries } = useDataApp();
  const rowsFor = (id) => queries[id].rows
    .filter((row) => row.scope === month + "|" + category)
    .map(({ scope, ...row }) => row);
  const totals = rowsFor("totals");
  const current = totals[0];
  const metrics = [
    ["sales", "Sales", dollars.format(current.sales)],
    ["orders", "Orders with matched items", count.format(current.orders)],
    ["items", "Items sold", count.format(current.items)],
    ["average", "Sales per matched order", dollars.format(current.average)],
  ];

  return (
    <section className="restaurant">
      <div className="restaurant-intro">
        <div>
          <h1>Restaurant sales &amp; menu performance</h1>
          <p>January–March 2023 · Maven Analytics sample restaurant</p>
        </div>
        <div className="restaurant-filters">
          <label>Month
            <select value={month} onChange={(event) => setMonth(event.target.value)}>
              {["All", "Jan", "Feb", "Mar"].map((value) =>
                <option key={value} value={value}>{value === "All" ? "All months" : value}</option>)}
            </select>
          </label>
          <label>Cuisine
            <select value={category} onChange={(event) => setCategory(event.target.value)}>
              {["All", "American", "Asian", "Italian", "Mexican"].map((value) =>
                <option key={value} value={value}>{value === "All" ? "All cuisines" : value}</option>)}
            </select>
          </label>
        </div>
      </div>
      <div className="restaurant-metrics">
        {metrics.map(([id, title, value]) =>
          <MetricCard key={id} id={id} queryId="totals" title={title} value={value} sourceRows={totals} displayRows={totals} />)}
      </div>
      <p className="restaurant-note">Sales sum listed menu prices. The source includes 137 order lines without a matched menu item, which are excluded.</p>
      <div className="restaurant-charts">
        {charts.map(([id, title, type, y, yLabel]) => {
          const rows = rowsFor(id);
          return <EvidenceChart key={id} id={id} queryId={id} title={title} variant="card"
            spec={{ type, x: "name", y, yLabel, showXAxisLabel: false, ...(id === "hourly" ? { xScale: "category" } : {}) }}
            rows={rows} sourceRows={rows} height={id === "items" || id === "pairs" ? 330 : 250} />;
        })}
      </div>
    </section>
  );
}
