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
    date = st.date_input("Sale Date")
    customer = st.text_input("Customer Name")
    item = st.text_input("Item Name")
    category = st.selectbox("Category", ["Helmet","Shoes","Tennis Ball","Wooden Stumps","Toe Guard","Bat Grip","Bat Handle Replacement","Bat Refurbishing","Bat Stickers","Cricket Bat English Willow","Batting Gloves","Batting Pads","Thigh Pads","Abdominal Guard","Kit Bag","Red Ball","Bat Knocking","SG GLOVES","NIVI PU BALLS","SS COMPLETE KIT","BAT CRACK REPAIR","Bat Binding","BAT REPAIR","Cricket Bat Kashmir Willow","Mallet","Scuff Sheet","Batting Inner Gloves","Plastic Stumps","supporter","Arm Guard","cricket wear","Bat weight Reduction","Other Bats"
])
    size = st.selectbox("Size", ["N/A", "Small", "Medium", "Large", "Full Size", "Harrow", "6", "5", "4","7", "8", "9", "10", "11","12"])
    
    # Input Quantity and Unit Price
    quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
    unit_price = st.number_input("Unit Price", min_value=0.0, step=1.0, format="%.2f")
    
    status = st.selectbox("Payment Status", ["Paid", "Pending", "Cancelled"])
    
    submit = st.form_submit_button("Submit Sale")
    
  # Updated append_row logic
if submit:
    if customer and item:
        # 1. Perform the calculation
        total_calculated = unit_price * quantity
        
        # 2. Build the list to match the sheet's columns EXACTLY
        # Make sure the order here matches the table above
        new_row = [
            str(date),          # A: Date
            item,               # B: Item Name
            category,           # C: Category
            size,               # D: Size
            quantity,           # E: Quantity
            unit_price,         # F: Unit Price
            total_calculated,   # G: Amount (Total)
            customer,           # H: Customer Name
            status              # I: Payment Status
        ]
        
        try:
            sh.append_row(new_row)
            st.sidebar.success(f"Added sale for {customer}!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error writing to sheet: {e}")


# --- 3. DATA PROCESSING ---
raw_data = sh.get_all_records()
df = pd.DataFrame(raw_data)

if not df.empty:
    # Standardize data types
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date']) 
    df['Unit Price'] = pd.to_numeric(df['Unit Price'], errors='coerce').fillna(0)
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
    df['Amount'] = df['Unit Price'] * df['Quantity']

    # CRITICAL: Define display_df HERE so it's available for everything below
    display_df = df.sort_values("Date", ascending=False).copy()

    # --- 4. MANAGE RECORDS (DELETE) ---
    st.markdown("---")
    st.subheader("🗑️ Delete a Record")
    
    # Selection box for picking a record to delete
    # We use the original index to find the exact row in Google Sheets
    to_delete = st.selectbox(
        "Select Sale to Remove:",
        options=display_df.index,
        format_func=lambda x: f"{display_df.loc[x, 'Date'].strftime('%d-%m-%Y')} | {display_df.loc[x, 'Customer Name']} | {display_df.loc[x, 'Item Name']}"
    )

    if st.button("Delete Permanently", type="primary"):
        # Google Sheets is 1-indexed + 1 row for Header = Index + 2
        # However, since display_df is sorted, we must use the ORIGINAL index from 'df'
        actual_row = to_delete + 2 
        sh.delete_rows(actual_row)
        st.success("Record Deleted!")
        st.rerun()

    # --- 5. DATA EDITOR (FOR EDITING) ---
    st.markdown("---")
    st.subheader("✏️ Edit Records")
    st.write("Change any cell below and click 'Save' to update the Google Sheet.")
    
    # The Data Editor is the easiest way to handle EDITS
    edited_df = st.data_editor(df, use_container_width=True, hide_index=True)
    
    if st.button("💾 Save All Edits"):
        # Convert dates back to strings for Google Sheets
        save_df = edited_df.copy()
        save_df['Date'] = save_df['Date'].dt.strftime('%Y-%m-%d')
        
        # Overwrite Sheet: Keep headers, replace data
        sh.clear()
        sh.update('A1', [df.columns.values.tolist()]) # Headers
        sh.update('A2', save_df.values.tolist())      # Data
        st.success("Sheet Updated!")
        st.rerun()











# --- 3. DATA PROCESSING ---
#raw_data = sh.get_all_records()
#df = pd.DataFrame(raw_data)

#if not df.empty:
    # 1. Standardize the Date
#    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
#    df = df.dropna(subset=['Date']) 

#    # 2. FORCE NUMERIC TYPES (This fixes the math error)
    # 'coerce' turns non-numbers into NaN, then .fillna(0) makes them 0
 #   df['Unit Price'] = pd.to_numeric(df['Unit Price'], errors='coerce').fillna(0)
 #   df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)

    # 3. NOW calculate the Amount
#    df['Amount'] = df['Unit Price'] * df['Quantity']

# --- 4. VISUALIZATION ---
st.subheader("Key Performance Indicators")
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric("Total Revenue", f"${df['Amount'].sum():,.2f}")
with kpi2:
    st.metric("Total Qty Sold", int(df['Quantity'].sum()))
with kpi3:
    # Calculate Average Unit Price
    avg_unit = df['Unit Price'].mean() if not df.empty else 0
    st.metric("Avg Unit Price", f"${avg_unit:,.2f}")


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

# New Metric: Total Items Sold
total_items = df['Quantity'].sum()
st.metric("Total Items Sold", int(total_items))

# Updated Chart: Sales vs Quantity
fig_qty = px.bar(df.groupby("Category")[["Amount", "Quantity"]].sum().reset_index(), 
                 x="Category", y="Quantity", title="Quantity Sold by Category")
st.plotly_chart(fig_qty, use_container_width=True)



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
