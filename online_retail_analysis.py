import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ── load & clean ──────────────────────────────────────────
df = pd.read_csv("online_retail.csv", encoding="ISO-8859-1", dtype={"CustomerID": str})
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df.dropna(subset=["Description", "CustomerID"], inplace=True)
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
df["Revenue"]   = df["Quantity"] * df["UnitPrice"]
df["YearMonth"] = df["InvoiceDate"].dt.to_period("M")
df["DayOfWeek"] = df["InvoiceDate"].dt.day_name()
df["Year"]      = df["InvoiceDate"].dt.year

total_rev  = df["Revenue"].sum()
total_ord  = df["InvoiceNo"].nunique()
total_cust = df["CustomerID"].nunique()
avg_order  = total_rev / total_ord

# ── colour system ─────────────────────────────────────────
BG       = "#050d1a"
CARD     = "#0d1f35"
CARD2    = "#0a1828"
BORDER   = "#1a3a5c"
CYAN     = "#00d4ff"
GOLD     = "#ffd700"
ORANGE   = "#ff6b35"
PURPLE   = "#a855f7"
GREEN    = "#10b981"
PINK     = "#f472b6"
TEXT     = "#e2e8f0"
MUTED    = "#64748b"
WHITE    = "#f8fafc"

BAR_PAL  = [CYAN, ORANGE, PURPLE, GREEN, PINK,
            "#facc15", "#22d3ee", "#e879f9", "#4ade80", "#f87171"]

def fmt(x, _=None):
    if x >= 1_000_000: return f"£{x/1_000_000:.1f}M"
    if x >= 1_000:     return f"£{x/1_000:.0f}K"
    return f"£{x:.0f}"

# ── figure ────────────────────────────────────────────────
fig = plt.figure(figsize=(28, 16), facecolor=BG)
gs  = gridspec.GridSpec(
    3, 4,
    figure=fig,
    hspace=0.52,
    wspace=0.38,
    left=0.04, right=0.97,
    top=0.84,  bottom=0.07
)

def style_ax(ax, title):
    ax.set_facecolor(CARD)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
        spine.set_linewidth(0.8)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.set_title(title, color=WHITE, fontsize=10.5,
                 fontweight="bold", pad=10, loc="left")
    ax.grid(color=BORDER, linestyle="--", linewidth=0.5, alpha=0.6)
    ax.set_axisbelow(True)

# ── KPI cards row ─────────────────────────────────────────
kpis = [
    ("TOTAL REVENUE",    f"£{total_rev/1_000_000:.2f}M", CYAN,   "12-month online retail"),
    ("TOTAL ORDERS",     f"{total_ord:,}",               GOLD,   "Unique invoices"),
    ("UNIQUE CUSTOMERS", f"{total_cust:,}",              GREEN,  "Active buyers"),
    ("AVG ORDER VALUE",  f"£{avg_order:.0f}",            ORANGE, "Per invoice"),
]
for col, (label, val, color, sub) in enumerate(kpis):
    ax_k = fig.add_subplot(gs[0, col])
    ax_k.set_facecolor(CARD2)
    for spine in ax_k.spines.values():
        spine.set_edgecolor(color)
        spine.set_linewidth(1.5)
    ax_k.set_xticks([]); ax_k.set_yticks([])

    ax_k.text(0.5, 0.72, val, transform=ax_k.transAxes,
              ha="center", va="center",
              fontsize=26, fontweight="bold", color=color)
    ax_k.text(0.5, 0.35, label, transform=ax_k.transAxes,
              ha="center", va="center",
              fontsize=8.5, fontweight="bold", color=MUTED)
    ax_k.text(0.5, 0.12, sub, transform=ax_k.transAxes,
              ha="center", va="center",
              fontsize=7.5, color=MUTED)
    # accent bar at top
    ax_k.axhline(y=ax_k.get_ylim()[1] if ax_k.get_ylim()[1] != 1.0 else 0.98,
                 xmin=0.1, xmax=0.9, color=color, linewidth=2.5)

# ── Chart 1: Monthly Revenue Trend (spans 2 cols) ─────────
ax1 = fig.add_subplot(gs[1, :2])
style_ax(ax1, "📈  Monthly Revenue Trend")

monthly = df.groupby("YearMonth")["Revenue"].sum().reset_index()
monthly["lbl"] = monthly["YearMonth"].astype(str)
x = np.arange(len(monthly))

ax1.fill_between(x, monthly["Revenue"], alpha=0.18, color=CYAN)
ax1.plot(x, monthly["Revenue"], color=CYAN, linewidth=2.5,
         marker="o", markersize=5, zorder=3)

# gradient glow effect
ax1.fill_between(x, monthly["Revenue"], alpha=0.06, color=CYAN)

peak = monthly["Revenue"].idxmax()
ax1.scatter(x[peak], monthly["Revenue"][peak], color=GOLD,
            s=120, zorder=5, edgecolors=BG, linewidths=1.5)
ax1.annotate(
    f"  Peak {fmt(monthly['Revenue'][peak])}",
    xy=(x[peak], monthly["Revenue"][peak]),
    color=GOLD, fontsize=8.5, fontweight="bold", va="bottom"
)

ax1.set_xticks(x[::2])
ax1.set_xticklabels(monthly["lbl"].iloc[::2], rotation=40, ha="right", fontsize=7.5)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(fmt))
ax1.set_ylabel("Revenue (£)", color=MUTED, fontsize=8)


# ── Chart 2: Top 10 Products (spans 2 cols) ───────────────
ax2 = fig.add_subplot(gs[1, 2:])
style_ax(ax2, "🏆  Top 10 Products by Revenue")

top_p = df.groupby("Description")["Revenue"].sum().nlargest(10).sort_values()
# shorten long names
short = [n[:38] + "…" if len(n) > 38 else n for n in top_p.index]
colors_bar = BAR_PAL[::-1]

bars = ax2.barh(short, top_p.values, color=colors_bar,
                edgecolor="none", height=0.65)
for bar, val in zip(bars, top_p.values):
    ax2.text(bar.get_width() + top_p.max() * 0.01,
             bar.get_y() + bar.get_height() / 2,
             fmt(val), va="center", fontsize=8, color=MUTED)

ax2.xaxis.set_major_formatter(mticker.FuncFormatter(fmt))
ax2.set_xlabel("Revenue (£)", color=MUTED, fontsize=8)
ax2.tick_params(axis="y", labelsize=7.8)


# ── Chart 3: Revenue by Day of Week ───────────────────────
ax3 = fig.add_subplot(gs[2, 0])
style_ax(ax3, "📅  Revenue by Day")

days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
day_map = {"Monday":"Mon","Tuesday":"Tue","Wednesday":"Wed",
           "Thursday":"Thu","Friday":"Fri","Saturday":"Sat","Sunday":"Sun"}
dow = df.groupby("DayOfWeek")["Revenue"].sum()
dow.index = dow.index.map(day_map)
dow = dow.reindex(days, fill_value=0)

bar_colors_d = [ORANGE if d == day_map[df.groupby("DayOfWeek")["Revenue"].sum().idxmax()]
                else PURPLE for d in days]
b3 = ax3.bar(dow.index, dow.values, color=bar_colors_d,
             edgecolor="none", width=0.6)
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(fmt))


# ── Chart 4: Top Countries ────────────────────────────────
ax4 = fig.add_subplot(gs[2, 1])
style_ax(ax4, "🌍  Top Markets (excl. UK)")

top_c = (df[df["Country"] != "United Kingdom"]
         .groupby("Country")["Revenue"].sum()
         .nlargest(8).sort_values())
b4 = ax4.barh(top_c.index, top_c.values,
              color=BAR_PAL[:len(top_c)], edgecolor="none", height=0.6)
ax4.xaxis.set_major_formatter(mticker.FuncFormatter(fmt))
ax4.tick_params(axis="y", labelsize=8)


# ── Chart 5: Revenue Share Pie ────────────────────────────
ax5 = fig.add_subplot(gs[2, 2])
ax5.set_facecolor(CARD)
for spine in ax5.spines.values():
    spine.set_edgecolor(BORDER); spine.set_linewidth(0.8)
ax5.set_title("🥧  Revenue by Country", color=WHITE,
              fontsize=10.5, fontweight="bold", pad=10, loc="left")

cr = df.groupby("Country")["Revenue"].sum()
cut = cr.sum() * 0.015
big = cr[cr >= cut]
sm  = cr[cr < cut].sum()
pie_data = pd.concat([big, pd.Series({"Others": sm})]).sort_values(ascending=False)

wedges, texts, autotexts = ax5.pie(
    pie_data.values,
    labels=pie_data.index,
    autopct="%1.0f%%",
    colors=sns.color_palette("cool", len(pie_data)),
    startangle=140,
    pctdistance=0.78,
    wedgeprops=dict(edgecolor=BG, linewidth=2),
    radius=0.95
)
for t in texts:    t.set_fontsize(7.5); t.set_color(TEXT)
for t in autotexts: t.set_fontsize(7);  t.set_color(WHITE); t.set_fontweight("bold")


# ── Chart 6: Top Products by Qty ──────────────────────────
ax6 = fig.add_subplot(gs[2, 3])
style_ax(ax6, "📦  Top Products by Units")

top_q = df.groupby("Description")["Quantity"].sum().nlargest(8).sort_values()
short_q = [n[:30] + "…" if len(n) > 30 else n for n in top_q.index]
ax6.barh(short_q, top_q.values, color=BAR_PAL[::-1][:len(top_q)],
         edgecolor="none", height=0.6)
ax6.xaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}K" if x >= 1000 else str(int(x)))
)
ax6.tick_params(axis="y", labelsize=7.5)


# ── Header ────────────────────────────────────────────────
fig.text(0.04, 0.955,
         "BUSINESS SALES PERFORMANCE ANALYTICS",
         fontsize=22, fontweight="bold", color=WHITE,
         va="bottom")
fig.text(0.04, 0.925,
         "Online Retail Dataset  ·  Dec 2010 – Dec 2011  ·  541,909 transactions  ·  37 countries",
         fontsize=10, color=MUTED, va="bottom")

# accent line under header
line = plt.Line2D([0.04, 0.97], [0.915, 0.915],
                  transform=fig.transFigure,
                  color=CYAN, linewidth=1.2, alpha=0.5)
fig.add_artist(line)

# badge top-right
fig.text(0.97, 0.955,
         "Future Interns  ·  DS Task 1  ·  2026",
         fontsize=9, color=MUTED, va="bottom", ha="right")

# footer
fig.text(0.5, 0.022,
         "Data: UCI Online Retail Dataset (Kaggle)  ·  Analysis: Python · pandas · matplotlib · seaborn",
         fontsize=8.5, color=MUTED, ha="center")

plt.savefig("sales_dashboard.png", dpi=180,
            bbox_inches="tight", facecolor=BG)
print("Done — sales_dashboard.png saved")