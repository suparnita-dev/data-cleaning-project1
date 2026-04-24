# ============================================================
# PERSONAL BUDGET & EXPENSE TRACKER
# Data Cleaning & Visualization
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import os

# ── Setup ────────────────────────────────────────────────────
sns.set_theme(style="whitegrid")
os.makedirs("outputs", exist_ok=True)

print("=" * 50)
print("  STEP 1: LOADING THE DATA")
print("=" * 50)
df = pd.read_csv("data.csv")
print(df.to_string())
print(f"\nShape: {df.shape[0]} rows, {df.shape[1]} columns")


# ── Step 2: Inspect ──────────────────────────────────────────
print("\n" + "=" * 50)
print("  STEP 2: INSPECTING THE DATA")
print("=" * 50)
print("\n--- Missing Values ---")
print(df.isnull().sum())
print(f"\n--- Duplicates Found: {df.duplicated().sum()} ---")


# ── Step 3: Clean ────────────────────────────────────────────
print("\n" + "=" * 50) 
print("  STEP 3: CLEANING THE DATA")
print("=" * 50)

# Remove duplicates
df = df.drop_duplicates()
print(f"✓ Duplicates removed. Rows now: {len(df)}")

# Fill missing Category
df["Category"] = df["Category"].fillna("Uncategorized")
print("✓ Filled missing Category with 'Uncategorized'")

# Fill missing Amount with median
median_amount = df["Amount"].median()
df["Amount"] = df["Amount"].fillna(median_amount)
print(f"✓ Filled missing Amount with median (${median_amount})")

# Remove outliers in Amount (anything over 1000 flagged)
before = len(df)
df = df[df["Amount"] <= 1000]
print(f"✓ Removed {before - len(df)} outlier amount(s) over $1000")

# Convert Date column
df["Date"] = pd.to_datetime(df["Date"])
print("✓ Converted Date to datetime")

# Fix Month order
month_order = ["January", "February", "March", "April",
               "May", "June", "July", "August",
               "September", "October", "November", "December"]
df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)

print("\n--- Cleaned Data ---")
print(df.to_string(index=False))


# ── Step 4: Summarize ────────────────────────────────────────
print("\n" + "=" * 50)
print("  STEP 4: SUMMARY STATISTICS")
print("=" * 50)
print(df[["Amount"]].describe().round(2))
print(f"\nTotal Spent:   ${df['Amount'].sum():.2f}")
print(f"Average Spend: ${df['Amount'].mean():.2f}")
print(f"Biggest Spend: ${df['Amount'].max():.2f}")


# ── Step 5: Visualize ────────────────────────────────────────
print("\n" + "=" * 50)
print("  STEP 5: CREATING DASHBOARD")
print("=" * 50)

fig = plt.figure(figsize=(16, 12))
fig.suptitle("$ Personal Budget Dashboard", fontsize=20,
             fontweight="bold", y=0.98)
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

colors = sns.color_palette("pastel")

# Chart 1 — Spending by Category (bar)
ax1 = fig.add_subplot(gs[0, 0])
cat_spend = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
bars = ax1.bar(cat_spend.index, cat_spend.values,
               color=colors, edgecolor="white", linewidth=0.8)
for bar in bars:
    ax1.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 1,
             f"${bar.get_height():.0f}",
             ha="center", va="bottom", fontsize=8, fontweight="bold")
ax1.set_title("Spending by Category", fontweight="bold")
ax1.set_xlabel("Category")
ax1.set_ylabel("Total Spent ($)")
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=20, ha="right", fontsize=8)

# Chart 2 — Spending by Month (bar)
ax2 = fig.add_subplot(gs[0, 1])
month_spend = df.groupby("Month", observed=True)["Amount"].sum()
bars2 = ax2.bar(month_spend.index, month_spend.values,
                color=sns.color_palette("Set2"), edgecolor="white")
for bar in bars2:
    ax2.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 1,
             f"${bar.get_height():.0f}",
             ha="center", va="bottom", fontsize=9, fontweight="bold")
ax2.set_title("Spending by Month", fontweight="bold")
ax2.set_xlabel("Month")
ax2.set_ylabel("Total Spent ($)")

# Chart 3 — Category share (pie)
ax3 = fig.add_subplot(gs[0, 2])
ax3.pie(cat_spend, labels=cat_spend.index, autopct="%1.0f%%",
        colors=colors, startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 2})
ax3.set_title("Expense Breakdown", fontweight="bold")

# Chart 4 — Payment Method (bar)
ax4 = fig.add_subplot(gs[1, 0])
pay_spend = df.groupby("PaymentMethod")["Amount"].sum().sort_values(ascending=False)
ax4.bar(pay_spend.index, pay_spend.values,
        color=sns.color_palette("muted"), edgecolor="white")
ax4.set_title("Spending by Payment Method", fontweight="bold")
ax4.set_xlabel("Payment Method")
ax4.set_ylabel("Total Spent ($)")
plt.setp(ax4.xaxis.get_majorticklabels(), rotation=15, ha="right", fontsize=8)

# Chart 5 — Daily spending over time (line)
ax5 = fig.add_subplot(gs[1, 1])
daily = df.groupby("Date")["Amount"].sum().sort_index()
ax5.plot(daily.index, daily.values, marker="o", color="#6c5ce7",
         linewidth=2, markersize=7, markerfacecolor="white", markeredgewidth=2)
ax5.fill_between(daily.index, daily.values, alpha=0.15, color="#6c5ce7")
ax5.set_title("Daily Spending Over Time", fontweight="bold")
ax5.set_xlabel("Date")
ax5.set_ylabel("Amount ($)")
plt.setp(ax5.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=8)

# Chart 6 — Top 5 individual expenses (horizontal bar)
ax6 = fig.add_subplot(gs[1, 2])
top5 = df.nlargest(5, "Amount")[["Description", "Amount"]]
ax6.barh(top5["Description"], top5["Amount"],
         color=sns.color_palette("flare"), edgecolor="white")
ax6.set_title("Top 5 Biggest Expenses", fontweight="bold")
ax6.set_xlabel("Amount ($)")
ax6.invert_yaxis()

# Save
output_path = "outputs/budget_dashboard.png"
plt.savefig(output_path, dpi=150, bbox_inches="tight",
            facecolor="white", edgecolor="none")
print(f"\n Dashboard saved → {output_path}")
plt.show()

print("\n Done! Check outputs/budget_dashboard.png")