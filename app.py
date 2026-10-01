
# =====================================================
# ATM Transaction Analysis Dashboard
# =====================================================

import pandas as pd
import streamlit as st
import plotly.express as px

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="ATM Transaction Dashboard",layout="wide")

# -------------------------------
# Load Data (Cached for Speed)
# -------------------------------
@st.cache_data
def load_data():
    conn = sqlite3.connect("ATM_Transaction_Analysis.db")
    query = "SELECT * FROM atm_transactions;"
    df = pd.read_sql_query(query, conn)
    conn.close()
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("🔍 Filters")

city_filter = st.sidebar.multiselect(
    "Select City", options=sorted(df["City"].unique())
)
atm_filter = st.sidebar.multiselect(
    "Select ATM ID", options=sorted(df["ATM_ID"].unique())
)
status_filter = st.sidebar.multiselect(
    "Select Status", options=sorted(df["Status"].unique())
)
txn_type_filter = st.sidebar.multiselect(
    "Select Transaction Type", options=sorted(df["Transaction_Type"].unique())
)

date_min, date_max = df["Date"].min(), df["Date"].max()
date_range = st.sidebar.date_input(
    "Select Date Range", value=(date_min, date_max),
    min_value=date_min, max_value=date_max
)

# Apply Filters
filtered_df = df.copy()

if city_filter:
    filtered_df = filtered_df[filtered_df["City"].isin(city_filter)]
if atm_filter:
    filtered_df = filtered_df[filtered_df["ATM_ID"].isin(atm_filter)]
if status_filter:
    filtered_df = filtered_df[filtered_df["Status"].isin(status_filter)]
if txn_type_filter:
    filtered_df = filtered_df[filtered_df["Transaction_Type"].isin(txn_type_filter)]
if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[(filtered_df["Date"] >= start_date) & (filtered_df["Date"] <= end_date)]

st.sidebar.markdown(f"**Filtered Records:** {len(filtered_df)}")

# -------------------------------
# Dashboard Title & Description
# -------------------------------
st.title("🏧 ATM Transaction Analysis Dashboard")
st.write("This Dashboard provides Descriptive Analytics of ATM Transactions in the BFSI Domain.")
st.markdown("---")

# -------------------------------
# KPI Calculations
# -------------------------------
total_transactions = len(filtered_df)
total_amount = filtered_df["Amount"].sum()
avg_amount = filtered_df[filtered_df["Amount"] > 0]["Amount"].mean() if total_transactions > 0 else 0
successful_txn = len(filtered_df[filtered_df["Status"] == "Successful"])
failed_txn = len(filtered_df[filtered_df["Status"] == "Failed"])
success_rate = round((successful_txn / total_transactions) * 100, 2) if total_transactions > 0 else 0
failed_rate = round((failed_txn / total_transactions) * 100, 2) if total_transactions > 0 else 0

# -------------------------------
# KPI Cards Section
# -------------------------------
st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Transactions", f"{total_transactions:,}")
col2.metric("Total Amount", f"₹{total_amount:,.0f}")
col3.metric("Success Rate", f"{success_rate}%")
col4.metric("Failed Rate", f"{failed_rate}%")

col5, col6, col7 = st.columns(3)
col5.metric("Average Transaction", f"₹{avg_amount:,.2f}")
col6.metric("Successful Transactions", f"{successful_txn:,}")
col7.metric("Failed Transactions", f"{failed_txn:,}")

st.markdown("---")

# -------------------------------
# Charts Section
# -------------------------------
st.subheader("📈 Transaction Insights")

if total_transactions == 0:
    st.warning("No data available for the selected filters. Please adjust your filters.")
else:
    # Row 1: City & ATM
    c1, c2 = st.columns(2)

    transactions_by_city = filtered_df.groupby("City").size().reset_index(name="Transaction_Count")
    fig_city = px.bar(transactions_by_city, x="City", y="Transaction_Count",
                       title="Transactions by City", color="Transaction_Count")
    c1.plotly_chart(fig_city, use_container_width=True)

    transactions_by_atm = filtered_df.groupby("ATM_ID").size().reset_index(name="Transaction_Count")
    fig_atm = px.bar(transactions_by_atm, x="ATM_ID", y="Transaction_Count",
                      title="Transactions by ATM", color="Transaction_Count")
    c2.plotly_chart(fig_atm, use_container_width=True)

    # Row 2: Transaction Type & Status
    c3, c4 = st.columns(2)

    transaction_type_distribution = filtered_df.groupby("Transaction_Type").size().reset_index(name="Transaction_Count")
    fig_type = px.pie(transaction_type_distribution, names="Transaction_Type", values="Transaction_Count",
                       title="Transaction Type Distribution")
    c3.plotly_chart(fig_type, use_container_width=True)

    status_distribution = filtered_df.groupby("Status").size().reset_index(name="Transaction_Count")
    fig_status = px.bar(status_distribution, x="Status", y="Transaction_Count",
                         title="Successful vs Failed Transactions", color="Status")
    c4.plotly_chart(fig_status, use_container_width=True)

    # Row 3: Amount by City & Amount by Type
    c5, c6 = st.columns(2)

    amount_by_city = filtered_df.groupby("City")["Amount"].sum().reset_index()
    fig_amount_city = px.bar(amount_by_city, x="City", y="Amount",
                              title="Transaction Amount by City", color="Amount")
    c5.plotly_chart(fig_amount_city, use_container_width=True)

    amount_by_type = filtered_df.groupby("Transaction_Type")["Amount"].sum().reset_index()
    fig_amount_type = px.bar(amount_by_type, x="Transaction_Type", y="Amount",
                              title="Transaction Amount by Transaction Type", color="Amount")
    c6.plotly_chart(fig_amount_type, use_container_width=True)

    # Row 4: Monthly Trend (Full Width)
    monthly_trend = filtered_df.groupby(filtered_df["Date"].dt.to_period("M")).size().reset_index(name="Transaction_Count")
    monthly_trend["Date"] = monthly_trend["Date"].astype(str)
    fig_monthly = px.line(monthly_trend, x="Date", y="Transaction_Count",
                           title="Monthly Transaction Trend", markers=True)
    st.plotly_chart(fig_monthly, use_container_width=True)

    # -------------------------------
    # Raw Data Table (Expandable)
    # -------------------------------
    st.markdown("---")
    with st.expander("🔎 View Raw Transaction Data"):
        st.dataframe(filtered_df, use_container_width=True)


from pyngrok import ngrok
ngrok.set_auth_token('3I74cf9rWMvW86aSSqIgtFYn5Og_7sqyRBEoYEs57dsQXgwhS')
public_url = ngrok.connect(8501)
print("Dashboard URL:", public_url)
