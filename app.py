import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------- Page Config -------------------- #
st.set_page_config(page_title="Healthy Diet Cost Dashboard", layout="wide")

st.title("🌍 Global Healthy Diet Cost Dashboard")

# -------------------- Load Data -------------------- #
@st.cache_data
def load_data():
    df = pd.read_csv("price_of_healthy_diet_clean.csv")
    return df

df = load_data()

# -------------------- Sidebar Filters -------------------- #
st.sidebar.header("🔎 Filters")

# Region Filter
selected_regions = st.sidebar.multiselect(
    "Select Region",
    df["region"].unique(),
    default=df["region"].unique()
)

df_region = df[df["region"].isin(selected_regions)]

# Country Filter (depends on region)
selected_countries = st.sidebar.multiselect(
    "Select Country",
    df_region["country"].unique(),
    default=df_region["country"].unique()
)

# Year Range Filter
year_min, year_max = int(df["year"].min()), int(df["year"].max())
selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max)
)

# Cost Category Filter
selected_category = st.sidebar.multiselect(
    "Cost Category",
    df["cost_category"].unique(),
    default=df["cost_category"].unique()
)

# Apply Filters
filtered_df = df[
    (df["region"].isin(selected_regions)) &
    (df["country"].isin(selected_countries)) &
    (df["year"].between(selected_years[0], selected_years[1])) &
    (df["cost_category"].isin(selected_category))
]

# -------------------- KPI Section -------------------- #
st.markdown("## 📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

avg_daily_cost = filtered_df["cost_healthy_diet_ppp_usd"].mean()
avg_annual_cost = filtered_df["annual_cost_healthy_diet_usd"].mean()

country_avg_cost = filtered_df.groupby("country")["cost_healthy_diet_ppp_usd"].mean()
highest_cost_country = country_avg_cost.idxmax()
lowest_cost_country = country_avg_cost.idxmin()

col1.metric("Avg Daily Cost (PPP USD)", f"${avg_daily_cost:.2f}")
col2.metric("Avg Annual Cost (USD)", f"${avg_annual_cost:.2f}")
col3.metric("Highest Cost Country", highest_cost_country)
col4.metric("Lowest Cost Country", lowest_cost_country)

st.markdown("---")

# -------------------- Charts -------------------- #

# 1. Yearly Trend
st.markdown("### 📈 Yearly Trend of Healthy Diet Cost")
yearly_avg = filtered_df.groupby("year")["cost_healthy_diet_ppp_usd"].mean().reset_index()
fig1 = px.line(yearly_avg, x="year", y="cost_healthy_diet_ppp_usd", markers=True,
               title="Yearly Average Cost of Healthy Diet")
st.plotly_chart(fig1, use_container_width=True)

# 2. Region-wise Bar Chart
st.markdown("### 🌎 Average Cost by Region")
region_avg = filtered_df.groupby("region")["cost_healthy_diet_ppp_usd"].mean().reset_index()
fig2 = px.bar(region_avg, x="region", y="cost_healthy_diet_ppp_usd", title="Average Cost by Region")
st.plotly_chart(fig2, use_container_width=True)

# 3. Top 10 Most Expensive Countries
st.markdown("### 🔴 Top 10 Most Expensive Countries")
top10 = country_avg_cost.sort_values(ascending=False).head(10).reset_index()
fig3 = px.bar(top10, x="country", y="cost_healthy_diet_ppp_usd", title="Top 10 Most Expensive Countries")
st.plotly_chart(fig3, use_container_width=True)

# 4. Top 10 Least Expensive Countries
st.markdown("### 🟢 Top 10 Least Expensive Countries")
bottom10 = country_avg_cost.sort_values().head(10).reset_index()
fig4 = px.bar(bottom10, x="country", y="cost_healthy_diet_ppp_usd", title="Top 10 Least Expensive Countries")
st.plotly_chart(fig4, use_container_width=True)

# 5. Cost Category Pie Chart
st.markdown("### 🥧 Cost Category Distribution")
cat_data = filtered_df["cost_category"].value_counts().reset_index()
cat_data.columns = ["cost_category", "count"]
fig5 = px.pie(cat_data, names="cost_category", values="count", title="Cost Category Distribution")
st.plotly_chart(fig5, use_container_width=True)

# 6. Box Plot by Region
st.markdown("### 📦 Cost Distribution by Region")
fig6 = px.box(filtered_df, x="region", y="cost_healthy_diet_ppp_usd", title="Cost Distribution by Region")
st.plotly_chart(fig6, use_container_width=True)

# -------------------- Data Table -------------------- #
st.markdown("## 📄 Filtered Dataset")
st.dataframe(filtered_df, use_container_width=True)

# -------------------- Download Button -------------------- #
csv_data = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv_data,
    file_name="filtered_healthy_diet_data.csv",
    mime="text/csv"
)

# -------------------- Auto Insights -------------------- #
st.markdown("## 🧠 Automatic Insights")

if not yearly_avg.empty and not region_avg.empty:
    cost_change = yearly_avg.iloc[-1]["cost_healthy_diet_ppp_usd"] - yearly_avg.iloc[0]["cost_healthy_diet_ppp_usd"]
    highest_region = region_avg.sort_values("cost_healthy_diet_ppp_usd", ascending=False).iloc[0]["region"]

    st.write(f"""
    - The cost of a healthy diet changed by **${cost_change:.2f}** between {selected_years[0]} and {selected_years[1]}.
    - **{highest_region}** is the most expensive region in the selected filters.
    - **{highest_cost_country}** is the most expensive country, while **{lowest_cost_country}** is the least expensive.
    - On average, a person spends **${avg_daily_cost:.2f} per day** or **${avg_annual_cost:.2f} per year** on a healthy diet.
    """)
