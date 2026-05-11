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
st.sidebar.header("📝 New Sale Entry")

with st.sidebar.form("entry_form", clear_on_submit=True):
    # Field 1: Date
    date = st.date_input("Sale Date")
    
    # Field 2: Customer Name
    customer = st.text_input("Customer Name", placeholder="e.g. John Doe")
    
    # Field 3: Item Name
    item = st.text_input("Item Name", placeholder="e.g. Kookaburra Bat")
    
    # Field 4: Category Dropdown
    category = st.selectbox("Category", [
        "Helmet","Shoes","Tennis Ball","Wooden Stumps","Toe Guard","Bat Grip","Bat Handle Replacement","Bat Refurbishing","Bat Stickers","Cricket Bat English Willow","Batting Gloves","Batting Pads","Thigh Pads","Abdominal Guard","Kit Bag","Red Ball","Bat Knocking","SG GLOVES","NIVI PU BALLS","SS COMPLETE KIT","BAT CRACK REPAIR","Bat Binding","Bat repair","Cricket Bat Kashmir Willow","Mallet","Scuff Sheet","Batting Inner Gloves","Plastic Stumps","supporter","Arm Guard","cricket wear","Bat weight Reduction","Bats"
    ])
    
    # Field 5: Amount
    amount = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f")
    
    # Field 6: Payment Status
    status = st.selectbox("Payment Status", ["Paid", "Pending", "Cancelled"])
    
    # Submit Button
    submit = st.form_submit_button("Submit Sale")
    
    if submit:
        if customer and item: # Basic validation
            # Sending 6 fields to match your updated sheet structure
            new_row = [str(date), customer, item, category, amount, status]
            sh.append_row(new_row)
            st.sidebar.success(f"Successfully recorded sale for {customer}!")
            st.rerun()
        else:
            st.sidebar.error("Please fill in Customer and Item names.")

# --- 3. DATA PROCESSING & AGGREGATION ---
# Pull data and convert to DataFrame
raw_data = sh.get_all_records()
df = pd.DataFrame(raw_data)

# Ensure data exists and format types
if not df.empty:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    df = df.dropna(subset=['Date']) 
    
    # Create the display formats for the Table
    display_df = df.sort_values("Date", ascending=False).copy()
    display_df['Date'] = display_df['Date'].dt.strftime('%d-%m-%Y')

# --- 4. VISUALIZATION ---

# Row 1: Category Breakdown
st.subheader("Total Sales by Category")
cat_total = df.groupby("Category")["Amount"].sum().reset_index()
fig_cat = px.bar(cat_total, x="Category", y="Amount", color="Category", text_auto=True)
st.plotly_chart(fig_cat, use_container_width=True)

# Row 1.5: Top Customers & Items
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Customers (by Value)")
    cust_total = df.groupby("Customer Name")["Amount"].sum().nlargest(5).reset_index()
    fig_cust = px.bar(cust_total, x="Amount", y="Customer Name", orientation='h', text_auto=True)
    st.plotly_chart(fig_cust, use_container_width=True)

with col2:
    st.subheader("Top Selling Items")
    item_counts = df["Item Name"].value_counts().nlargest(5).reset_index()
    item_counts.columns = ["Item Name", "Count"]
    fig_item = px.pie(item_counts, values="Count", names="Item Name", hole=0.4)
    st.plotly_chart(fig_item, use_container_width=True)

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

# --- 5. RAW DATA DISPLAY ---
with st.expander("View Raw Data Table"):
    # 1. Create a copy for display so we don't break the charts
    display_df = df.copy()
    
    # 2. Sort by date first (so the most recent sales are at the top)
    display_df = display_df.sort_values("Date", ascending=False)
    
    # 3. Reformat the Date column to your preferred string format
    # This changes the look to DD-MM-YYYY
    display_df['Date'] = display_df['Date'].dt.strftime('%d-%m-%Y')
    
    # 4. Show the table
    st.dataframe(
        display_df, 
        use_container_width=True,
        hide_index=True  # Optional: hides the index column for a cleaner look
    )
