import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from google.oauth2.service_account import Credentials

# --- 1. CONFIG & CONNECTION ---
st.set_page_config(page_title="Sales Tracker", layout="wide")

# Connect using Streamlit Secrets
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

# Use the ID instead of the name
SHEET_ID = "1h2A8Hj0Q3-UVl_JTgBetMGjae6k01Ei2upPSKVJZLX0" 
sh = client.open_by_key(SHEET_ID).sheet1

# Open the sheet (Make sure the Sheet Name matches exactly)
#SHEET_NAME = "Cricket Sales" 
#sh = client.open(SHEET_NAME).sheet1

# --- 2. DATA ENTRY SECTION ---
st.sidebar.header("Add New Sale")
with st.sidebar.form("entry_form", clear_on_submit=True):
    date = st.date_input("Sale Date")
    category = st.selectbox("Category", ["Bats", "Balls", "Gloves", "Pads", "Helmets"])
    amount = st.number_input("Amount", min_value=0.0, step=10.0)
    status = st.selectbox("Payment Status", ["Paid", "Pending", "Cancelled"])
    
    submit = st.form_submit_button("Submit Sale")
    if submit:
        sh.append_row([str(date), category, amount, status])
        st.sidebar.success("Data Saved!")
        st.rerun()

# --- 3. DATA PROCESSING & AGGREGATION ---
st.title("📊 Sales Analytics Dashboard")

# Pull data and convert to DataFrame
raw_data = sh.get_all_records()
if not raw_data:
    st.warning("No data found in the Google Sheet.")
    st.stop()

df = pd.DataFrame(raw_data)

# Ensure 'Date' is a datetime object and 'Amount' is numeric
df['Date'] = pd.to_datetime(df['Date'])
df['Amount'] = pd.to_numeric(df['Amount'])

# Create Time Dimensions
df['Week'] = df['Date'].dt.to_period('W').apply(lambda r: r.start_time)
df['Month'] = df['Date'].dt.to_period('M').apply(lambda r: r.start_time)
df['Quarter'] = df['Date'].dt.to_period('Q').apply(lambda r: r.start_time)

# --- 4. VISUALIZATION ---

# Row 1: Category Breakdown
st.subheader("Total Sales by Category")
cat_total = df.groupby("Category")["Amount"].sum().reset_index()
fig_cat = px.bar(cat_total, x="Category", y="Amount", color="Category", text_auto=True)
st.plotly_chart(fig_cat, use_container_width=True)

# Row 2: Time Aggregates
st.subheader("Time-Based Aggregates")
view_option = st.radio("Select View:", ["Daily", "Weekly", "Monthly", "Quarterly"], horizontal=True)

if view_option == "Daily":
    time_df = df.groupby("Date")["Amount"].sum().reset_index()
    x_axis = "Date"
elif view_option == "Weekly":
    time_df = df.groupby("Week")["Amount"].sum().reset_index()
    x_axis = "Week"
elif view_option == "Monthly":
    time_df = df.groupby("Month")["Amount"].sum().reset_index()
    x_axis = "Month"
else: # Quarterly
    time_df = df.groupby("Quarter")["Amount"].sum().reset_index()
    x_axis = "Quarter"

fig_time = px.line(time_df, x=x_axis, y="Amount", markers=True)
st.plotly_chart(fig_time, use_container_width=True)

# Show Raw Data
with st.expander("View Raw Data Table"):
    st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)
