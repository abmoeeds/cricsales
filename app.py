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
# --- 2. DATA ENTRY SECTION ---
st.sidebar.header("📝 New Sale Entry")

with st.sidebar.form("entry_form", clear_on_submit=True):
    # Existing Fields
    date = st.date_input("Sale Date")
    customer = st.text_input("Customer Name")
    item = st.text_input("Item Name")
    category = st.selectbox("Category", ["Bats", "Balls", "Gloves", "Pads", "Helmets", "Clothing", "Accessories"])
    size = st.selectbox("Size", ["N/A", "Small", "Medium", "Large", "Full Size", "Harrow", "6", "5", "4"])
    
    quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
    unit_price = st.number_input("Unit Price", min_value=0.0, step=1.0)
    discount = st.number_input("Adjustment / Discount (-)", min_value=0.0, step=1.0)
    
    status = st.selectbox("Payment Status", ["Paid", "Pending", "Cancelled"])
    payment_date = st.date_input("Payment Date (If Paid)")
    
    # NEW FIELDS
    payment_type = st.selectbox("Payment Type", ["N/A", "Cash", "Card", "Bank Transfer"])
    notes = st.text_area("Notes", placeholder="e.g. Special request or delivery info")
    
    submit = st.form_submit_button("Submit Sale")
    
    if submit:
        total_calculated = (unit_price * quantity) - discount
        
        # Prepare row (13 Columns Total)
        new_row = [
            str(date),          # A: Date
            item,               # B: Item Name
            category,           # C: Category
            size,               # D: Size
            int(quantity),      # E: Quantity
            float(unit_price),  # F: Unit Price
            float(discount),    # G: Adjustments
            float(total_calculated), # H: Amount
            customer,           # I: Customer Name
            status,             # J: Payment Status
            str(payment_date),  # K: Payment Date
            payment_type,       # L: Payment Type (NEW)
            notes               # M: Notes (NEW)
        ]
        
        sh.append_row(new_row)
        st.sidebar.success(f"Added! Method: {payment_type}")
        st.rerun()


# --- 3. DATA PROCESSING ---
raw_data = sh.get_all_records()
df = pd.DataFrame(raw_data)

if not df.empty:
    # Convert Dates
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Payment Date'] = pd.to_datetime(df['Payment Date'], errors='coerce')
    df = df.dropna(subset=['Date']) 

    # Force Numeric Types
    numeric_cols = ['Unit Price', 'Quantity', 'Adjustments', 'Amount']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Re-calculate to ensure dashboard accuracy
    df['Amount'] = (df['Unit Price'] * df['Quantity']) - df['Adjustments']

    # --- Metrics Section ---
    st.subheader("Key Performance Indicators")
    k1, k2, k3 = st.columns(3)
    k1.metric("Net Revenue", f"${df['Amount'].sum():,.2f}")
    k2.metric("Total Discounts", f"-${df['Adjustments'].sum():,.2f}")
    k3.metric("Items Sold", int(df['Quantity'].sum()))

# --- 3. DATA PROCESSING ---
# ... (Keep your previous numeric conversion logic for Amount/Quantity) ...

if not df.empty:
    st.subheader("Payment Method Breakdown")
    # Group by Payment Type
    pay_stats = df.groupby("Payment Type")["Amount"].sum().reset_index()
    fig_pay = px.pie(pay_stats, values="Amount", names="Payment Type", hole=0.4, 
                     title="Revenue by Payment Type")
    st.plotly_chart(fig_pay, use_container_width=True)
    

  # --- 4. DELETE LOGIC ---
st.markdown("---")
st.subheader("🗑️ Delete Record")
display_df = df.sort_values("Date", ascending=False).copy()
to_delete = st.selectbox("Select Record:", options=display_df.index,
                         format_func=lambda x: f"{display_df.loc[x, 'Date'].strftime('%d-%m-%Y')} - {display_df.loc[x, 'Customer Name']}")

if st.button("Delete Permanently", type="primary"):
    # Target row = Index + 2 (1 for header, 1 for 0-indexing)
    sh.delete_rows(int(to_delete) + 2)
    st.success("Deleted!")
    st.rerun()

# --- 5. EDIT LOGIC ---
st.subheader("✏️ Bulk Edit All Records")
edited_df = st.data_editor(df, use_container_width=True)

if st.button("💾 Save All Edits"):
    save_df = edited_df.copy()
    # Format dates correctly for Google Sheets
    save_df['Date'] = pd.to_datetime(save_df['Date']).dt.strftime('%Y-%m-%d')
    save_df['Payment Date'] = pd.to_datetime(save_df['Payment Date']).dt.strftime('%Y-%m-%d')
    
    # Fill empty notes with empty string to avoid API errors
    save_df['Notes'] = save_df['Notes'].fillna("")
    
    sh.clear()
    sh.update('A1', [save_df.columns.values.tolist()]) # Headers
    sh.update('A2', save_df.values.tolist())          # Data
    st.success("Google Sheet Fully Synced!")
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
