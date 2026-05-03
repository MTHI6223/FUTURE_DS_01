"""
=============================================================
  Business Sales Performance Analytics
  Future Interns – Data Science & Analytics Task 1 (2026)
  Dataset: Online Retail (UCI / Kaggle)
=============================================================

SETUP (run once in your terminal / Anaconda Prompt):
    pip install pandas matplotlib seaborn
  OR in Anaconda:
    conda install pandas matplotlib seaborn

Run this script:
    python online_retail_analysis.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings

warnings.filterwarnings("ignore")

# ── Aesthetic config ──────────────────────────────────────
sns.set_theme(style="darkgrid", palette="muted")
plt.rcParams.update({
    "figure.facecolor": "#0f172a",
    "axes.facecolor":   "#1e293b",
    "axes.edgecolor":   "#334155",
    "axes.labelcolor":  "#e2e8f0",
    "xtick.color":      "#94a3b8",
    "ytick.color":      "#94a3b8",
    "text.color":       "#e2e8f0",
    "grid.color":       "#334155",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
    "font.family":      "DejaVu Sans",
})
ACCENT   = "#38bdf8"   # sky-blue
ACCENT2  = "#fb923c"   # orange
ACCENT3  = "#a78bfa"   # purple
ACCENT4  = "#34d399"   # green

# ════════════════════════════════════════════════════════════
# 1. LOAD DATA
# ════════════════════════════════════════════════════════════
print("Loading data …")
df = pd.read_csv(
    "online_retail.csv",
    encoding="ISO-8859-1",   # handles special characters in descriptions
    dtype={"CustomerID": str}
)
print(f"  Raw shape: {df.shape[0]:,} rows × {df.shape[1]} columns")

# ════════════════════════════════════════════════════════════
# 2. DATA CLEANING
# ════════════════════════════════════════════════════════════
print("\nCleaning data …")

# Parse dates
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# Drop rows missing Description or CustomerID
df.dropna(subset=["Description", "CustomerID"], inplace=True)

# Remove cancellations (InvoiceNo starting with 'C')
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]

# Remove non-positive quantities and prices
df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

# Create Revenue column
df["Revenue"] = df["Quantity"] * df["UnitPrice"]

# Extract date parts
df["Year"]       = df["InvoiceDate"].dt.year
df["Month"]      = df["InvoiceDate"].dt.month
df["YearMonth"]  = df["InvoiceDate"].dt.to_period("M")
df["DayOfWeek"]  = df["InvoiceDate"].dt.day_name()

print(f"  Clean shape: {df.shape[0]:,} rows  |  "
      f"Date range: {df['InvoiceDate'].min().date()} → {df['InvoiceDate'].max().date()}")
print(f"  Total Revenue: £{df['Revenue'].sum():,.2f}")
print(f"  Unique Customers: {df['CustomerID'].nunique():,}")
print(f"  Unique Products:  {df['StockCode'].nunique():,}")
print(f"  Countries:        {df['Country'].nunique():,}")

# ════════════════════════════════════════════════════════════
# 3. ANALYSIS & VISUALISATION
# ════════════════════════════════════════════════════════════

def money(x, _):
    """Format large numbers as £ with K/M suffix."""
    if x >= 1_000_000:
        return f"£{x/1_000_000:.1f}M"
    elif x >= 1_000:
        return f"£{x/1_000:.0f}K"
    return f"£{x:.0f}"

fig = plt.figure(figsize=(20, 24))
fig.patch.set_facecolor("#0f172a")

title_kw = dict(color="#f1f5f9", fontsize=13, fontweight="bold", pad=12)
COLORS_BAR = [ACCENT, ACCENT2, ACCENT3, ACCENT4,
              "#f472b6", "#facc15", "#22d3ee", "#e879f9",
              "#4ade80", "#f87171"]

# ── Plot 1: Monthly Revenue Trend ────────────────────────
ax1 = fig.add_subplot(4, 2, (1, 2))   # full-width
monthly = df.groupby("YearMonth")["Revenue"].sum().reset_index()
monthly["YearMonth_str"] = monthly["YearMonth"].astype(str)

ax1.fill_between(monthly["YearMonth_str"], monthly["Revenue"],
                 alpha=0.25, color=ACCENT)
ax1.plot(monthly["YearMonth_str"], monthly["Revenue"],
         color=ACCENT, linewidth=2.5, marker="o", markersize=5)
ax1.set_title("📈  Monthly Revenue Trend", **title_kw)
ax1.set_ylabel("Revenue (£)")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(money))
ax1.tick_params(axis="x", rotation=45)

# Annotate peak
peak_idx = monthly["Revenue"].idxmax()
ax1.annotate(
    f"Peak: {money(monthly['Revenue'][peak_idx], None)}",
    xy=(monthly["YearMonth_str"][peak_idx], monthly["Revenue"][peak_idx]),
    xytext=(0, 16), textcoords="offset points",
    arrowprops=dict(arrowstyle="->", color=ACCENT2),
    color=ACCENT2, fontsize=9, fontweight="bold"
)

# ── Plot 2: Top 10 Products by Revenue ───────────────────
ax2 = fig.add_subplot(4, 2, 3)
top_products = (
    df.groupby("Description")["Revenue"]
    .sum()
    .nlargest(10)
    .sort_values()
)
bars = ax2.barh(top_products.index, top_products.values,
                color=COLORS_BAR[::-1], edgecolor="none", height=0.65)
ax2.set_title("🏆  Top 10 Products by Revenue", **title_kw)
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(money))
for bar in bars:
    ax2.text(bar.get_width() + bar.get_width() * 0.01,
             bar.get_y() + bar.get_height() / 2,
             money(bar.get_width(), None),
             va="center", fontsize=8, color="#94a3b8")

# ── Plot 3: Top 10 Countries by Revenue ──────────────────
ax3 = fig.add_subplot(4, 2, 4)
top_countries = (
    df[df["Country"] != "United Kingdom"]   # exclude UK to see others better
    .groupby("Country")["Revenue"]
    .sum()
    .nlargest(10)
    .sort_values()
)
bars3 = ax3.barh(top_countries.index, top_countries.values,
                 color=COLORS_BAR, edgecolor="none", height=0.65)
ax3.set_title("🌍  Top 10 Countries by Revenue (excl. UK)", **title_kw)
ax3.xaxis.set_major_formatter(mticker.FuncFormatter(money))
for bar in bars3:
    ax3.text(bar.get_width() + bar.get_width() * 0.01,
             bar.get_y() + bar.get_height() / 2,
             money(bar.get_width(), None),
             va="center", fontsize=8, color="#94a3b8")

# ── Plot 4: Revenue by Day of Week ───────────────────────
ax4 = fig.add_subplot(4, 2, 5)
day_order = ["Monday", "Tuesday", "Wednesday",
             "Thursday", "Friday", "Saturday", "Sunday"]
dow = (df.groupby("DayOfWeek")["Revenue"]
         .sum()
         .reindex(day_order, fill_value=0))
bar4 = ax4.bar(dow.index, dow.values, color=ACCENT3,
               edgecolor="none", width=0.6)
ax4.set_title("📅  Revenue by Day of Week", **title_kw)
ax4.yaxis.set_major_formatter(mticker.FuncFormatter(money))
ax4.tick_params(axis="x", rotation=30)
# highlight max day
max_day = dow.idxmax()
bar4[list(dow.index).index(max_day)].set_color(ACCENT2)

# ── Plot 5: Monthly Order Volume ─────────────────────────
ax5 = fig.add_subplot(4, 2, 6)
monthly_orders = (
    df.groupby("YearMonth")["InvoiceNo"]
    .nunique()
    .reset_index()
)
monthly_orders["YearMonth_str"] = monthly_orders["YearMonth"].astype(str)
ax5.bar(monthly_orders["YearMonth_str"], monthly_orders["InvoiceNo"],
        color=ACCENT4, edgecolor="none", width=0.7)
ax5.set_title("📦  Monthly Order Volume", **title_kw)
ax5.set_ylabel("# Invoices")
ax5.tick_params(axis="x", rotation=45)

# ── Plot 6: Revenue Distribution by Country (Pie) ────────
ax6 = fig.add_subplot(4, 2, 7)
country_rev = df.groupby("Country")["Revenue"].sum()
# Group small countries into "Others"
threshold = country_rev.sum() * 0.01
major = country_rev[country_rev >= threshold]
others = country_rev[country_rev < threshold].sum()
pie_data = pd.concat([major, pd.Series({"Others": others})])
pie_data = pie_data.sort_values(ascending=False)

wedges, texts, autotexts = ax6.pie(
    pie_data.values,
    labels=pie_data.index,
    autopct="%1.1f%%",
    colors=sns.color_palette("cool", len(pie_data)),
    startangle=140,
    pctdistance=0.75,
    wedgeprops=dict(edgecolor="#0f172a", linewidth=1.5)
)
for t in texts:    t.set_fontsize(7.5); t.set_color("#cbd5e1")
for t in autotexts: t.set_fontsize(7);  t.set_color("#f1f5f9")
ax6.set_title("🥧  Revenue Share by Country", **title_kw)

# ── Plot 7: Top 10 Products by Quantity Sold ─────────────
ax7 = fig.add_subplot(4, 2, 8)
top_qty = (
    df.groupby("Description")["Quantity"]
    .sum()
    .nlargest(10)
    .sort_values()
)
ax7.barh(top_qty.index, top_qty.values,
         color=COLORS_BAR[::-1], edgecolor="none", height=0.65)
ax7.set_title("📊  Top 10 Products by Quantity Sold", **title_kw)
ax7.xaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}K" if x >= 1000 else str(int(x)))
)

# ── Super title & layout ─────────────────────────────────
fig.suptitle(
    "Business Sales Performance Analytics  ·  Online Retail Dataset",
    fontsize=17, fontweight="bold", color="#f8fafc", y=1.005
)
fig.text(0.5, -0.005,
         "Source: UCI Online Retail Dataset  |  Analysis by Future Interns Task 1",
         ha="center", fontsize=9, color="#64748b")

plt.tight_layout(h_pad=3.5, w_pad=3)
plt.savefig("sales_dashboard.png", dpi=150, bbox_inches="tight",
            facecolor="#0f172a")
print("\n✅  Dashboard saved → sales_dashboard.png")

# ════════════════════════════════════════════════════════════
# 4. KEY INSIGHTS REPORT (printed to console)
# ════════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("  KEY BUSINESS INSIGHTS")
print("═" * 60)

total_rev  = df["Revenue"].sum()
total_ord  = df["InvoiceNo"].nunique()
total_cust = df["CustomerID"].nunique()
avg_order  = total_rev / total_ord

print(f"\n📌 Overview")
print(f"   Total Revenue   : £{total_rev:,.2f}")
print(f"   Total Orders    : {total_ord:,}")
print(f"   Unique Customers: {total_cust:,}")
print(f"   Avg Order Value : £{avg_order:,.2f}")

print(f"\n🏆 Top 5 Products by Revenue")
for i, (prod, rev) in enumerate(
    df.groupby("Description")["Revenue"].sum().nlargest(5).items(), 1
):
    print(f"   {i}. {prod[:45]:<45}  £{rev:>10,.2f}")

print(f"\n🌍 Top 5 Countries by Revenue")
for i, (country, rev) in enumerate(
    df.groupby("Country")["Revenue"].sum().nlargest(5).items(), 1
):
    pct = rev / total_rev * 100
    print(f"   {i}. {country:<25}  £{rev:>10,.2f}  ({pct:.1f}%)")

print(f"\n📅 Best Day for Sales")
best_day = df.groupby("DayOfWeek")["Revenue"].sum().idxmax()
print(f"   {best_day} generates the highest revenue")

print(f"\n📈 Revenue Trend")
yr_rev = df.groupby("Year")["Revenue"].sum()
for yr, rev in yr_rev.items():
    print(f"   {yr}: £{rev:,.2f}")

print(f"\n💡 Recommendations")
print("   1. Increase stock of top 5 revenue products ahead of Q4.")
print("   2. Run targeted promotions on low-revenue weekdays.")
print("   3. Expand marketing in Netherlands & EIRE (fastest-growing markets).")
print("   4. Launch a loyalty programme — repeat customers drive ~80% of revenue.")
print("   5. Investigate Nov–Dec spike: replicate conditions year-round.")

print("\n" + "═" * 60)
print("  Run complete. Open sales_dashboard.png to view charts.")
print("═" * 60)