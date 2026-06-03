import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from google.oauth2.service_account import Credentials
from fpdf import FPDF
import io
import numpy as np
import streamlit.components.v1 as components


# --- PASSWORD PROTECTION FUNCTION ---
# --- PASSWORD PROTECTION FUNCTION ---
def check_password():
    """Returns True if the user had the correct password."""

    # Initialize the session state variable if it doesn't exist yet
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # If already logged in, return True immediately
    if st.session_state["password_correct"]:
        return True

    # Show the login screen
    st.title("🔒 SMZ Sports Dashboard")
    st.subheader("Please log in to access the system")
    
    # 1. Capture the input value directly into a variable
    pwd_input = st.text_input("Enter Password:", type="password")
    
    # 2. Add a full-width mobile button
    if st.button("🔓 Unlock Dashboard", use_container_width=True):
        if pwd_input == "SMZSports2026":
            st.session_state["password_correct"] = True
            st.rerun()  # Instantly opens up the app!
        else:
            st.session_state["password_error"] = True

    # Show error message if login failed
    if "password_error" in st.session_state and st.session_state["password_error"]:
        st.error("😕 Incorrect password. Please try again.")
        
    return False

    # First run or password incorrect: show input form
    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        st.title("🔒 SMZ Sports Dashboard")
        st.subheader("Please log in to access the system")
        
        # 1. Password entry field
        st.text_input(
            "Enter Password:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        
        # 2. 🆕 Mobile Friendly Login Button
        if st.button("🔓 Unlock Dashboard", use_container_width=True):
            password_entered()
            st.rerun() # Forces the page to instantly refresh and open up!
        
        # Show error message if they tried and failed
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 Incorrect password. Please try again.")
            
        return False
    return True

# --- CHECK PASSWORD GATEWAY ---
if not check_password():
    st.stop()  # Stop executing the rest of the app if not logged in

# 1. Force the page to scale nicely on mobile screens
st.set_page_config(page_title="SMZ Sports", page_icon="🏏", layout="centered")

# 2. Inject both iOS and Android App Manifest Tags
import streamlit as st

# 1. Force the page to scale nicely on mobile screens
st.set_page_config(page_title="SMZ Sports", page_icon="🏏", layout="centered")



# 1. Page Configuration
st.set_page_config(page_title="SMZ Sports", page_icon="🏏", layout="centered")

# 2. Inject Mobile Headers Silently using a hidden component
components.html(
    """
    <script>
        // Inject meta tags directly into the real parent head of the app
        var meta1 = document.createElement('meta');
        meta1.name = 'viewport';
        meta1.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
        document.getElementsByTagName('head')[0].appendChild(meta1);

        var meta2 = document.createElement('meta');
        meta2.name = 'mobile-web-app-capable';
        meta2.content = 'yes';
        document.getElementsByTagName('head')[0].appendChild(meta2);

        var meta3 = document.createElement('meta');
        meta3.name = 'apple-mobile-web-app-capable';
        meta3.content = 'yes';
        document.getElementsByTagName('head')[0].appendChild(meta3);

        var meta4 = document.createElement('meta');
        meta4.name = 'apple-mobile-web-app-status-bar-style';
        meta4.content = 'black-translucent';
        document.getElementsByTagName('head')[0].appendChild(meta4);
    </script>
    """,
    height=0, # Makes the component completely invisible on screen
    width=0
)

# ====================================================================
# YOUR EXISTING APP CODE STARTS HERE
# (All your sh.get_all_records(), dataframes, and charts go down here)
# ====================================================================




# Custom CSS to make the app look better on iPhone
st.markdown("""
    <style>
        /* Make buttons bigger and easier to tap with thumbs */
        .stButton button {
            width: 100%;
            height: 3.5em;
            border-radius: 10px;
            font-weight: bold;
        }
        
        /* Improve spacing for mobile metrics */
        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
        }

        /* Make data editor rows taller for easier tapping */
        .stDataEditor div {
            font-size: 14px;
        }
    </style>
""", unsafe_allow_html=True) # <-- Corrected parameter name



# --- 1. CONFIG & CONNECTION ---
st.set_page_config(page_title="SMZ Sports", layout="wide", initial_sidebar_state="collapsed")
#st.set_page_config(page_title="Sales Tracker", layout="wide")

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


# --- 1. HEADER & TOP ACTIONS ---
st.title("🏏 SMZ Sports Cricket Sales Analytics")

# Floating Action Button for New Sale
with st.popover("➕ Add New Sale Record", use_container_width=True):
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Sale Date")
            customer = st.text_input("Customer Name")
            item = st.text_input("Item Name")
            category = st.selectbox("Category", ["Helmet","Shoes","Tennis Ball","Tennis Bat","Wooden Stumps","Toe Guard","Bat Grip","Bat Handle Replacement","Bat Refurbishing","Bat Stickers","Cricket Bat English Willow","Batting Gloves","Batting Pads","Thigh Pads","Abdominal Guard","Kit Bag","Red Ball","Bat Knocking","SG GLOVES","NIVI PU BALLS","SS COMPLETE KIT","BAT CRACK REPAIR","Bat Binding","BAT REPAIR","Cricket Bat Kashmir Willow","Mallet","Scuff Sheet","Batting Inner Gloves","Plastic Stumps","supporter","Arm Guard","cricket wear","Bat weight Reduction","Bats"])
        with col2:
            size = st.selectbox("Size", ["N/A", "Small", "Medium", "Large", "Full Size", "Harrow", "6", "5", "4", "7","8","9","10","3","11","12"])
            quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
            unit_price = st.number_input("Unit Price (£)", min_value=0.0, format="%.2f")
            discount = st.number_input("Adjustment / Discount (£)", min_value=0.0, format="%.2f")

        st.markdown("---")
        c3, c4 = st.columns(2)
        with c3:
            status = st.selectbox("Payment Status", ["Paid", "Pending", "Cancelled"])
            payment_date = st.date_input("Payment Date")
        with c4:
            payment_type = st.selectbox("Payment Type", ["N/A", "Cash", "Card", "Bank Transfer"])
            notes = st.text_area("Notes")

        submit = st.form_submit_button("Submit Sale", use_container_width=True)
        
        if submit:
            total_calculated = (unit_price * quantity) - discount
            new_row = [str(date), item, category, size, int(quantity), float(unit_price), 
                       float(discount), float(total_calculated), customer, status, 
                       str(payment_date), payment_type, notes]
            sh.append_row(new_row)
            st.success(f"Sale for {customer} saved! Total: £{total_calculated:,.2f}")
            st.rerun()








# --- 3. DATA PROCESSING ---
raw_data = sh.get_all_records()
df = pd.DataFrame(raw_data)

df.columns = df.columns.str.strip() # Removes accidental spaces
df.columns = df.columns.str.title() # Forces "category" to become "Category"



if not df.empty:
    # Now this line will work perfectly!
    cat_total = df.groupby("Category")["Amount"].sum().reset_index()
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
    
    
    # Define which categories are Services
    service_list = ["Toe Guard","Bat Handle Replacement","Bat Refurbishing","Bat Knocking","BAT CRACK REPAIR","Bat Binding","BAT REPAIR","Bat weight Reduction"]
    
    # (After your existing df cleaning code)
    

    # Function to classify the row
    def classify_type(category):
        if category in service_list:
            return "🛠️ Service"
        else:
            return "📦 Goods"
    
    # Apply the classification
    df['Type'] = df['Category'].apply(classify_type)

import datetime

# ==========================================
# 📊 TOP ROW: REAL-TIME SALES METRICS
# ==========================================
st.markdown("### 📈 Revenue Performance Overview")

# Ensure Date column is in datetime format for comparison
if not df.empty and 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date']).dt.date

    # 1. Get reference dates based on current time (2026)
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    seven_days_ago = today - datetime.timedelta(days=7)

    # 2. Compute specific timeframe metrics
    sales_today = df[df['Date'] == today]['Amount'].sum()
    sales_yesterday = df[df['Date'] == yesterday]['Amount'].sum()
    sales_7days = df[(df['Date'] >= seven_days_ago) & (df['Date'] <= today)]['Amount'].sum()

    # 3. Render Top Metric Row
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("Today's Sales", f"£{sales_today:,.2f}")
    with m_col2:
        st.metric("Yesterday's Sales", f"£{sales_yesterday:,.2f}")
    with m_col3:
        st.metric("Last 7 Days", f"£{sales_7days:,.2f}")

    # --- CUSTOM DATE RANGE EXPANDER ---
    st.write("") # Tiny spacer
    with st.expander("📅 Calculate Custom Date Range Sales"):
        # Date selection inputs (defaulting to last 30 days)
        date_range = st.date_input(
            "Select Start and End Dates:",
            value=(today - datetime.timedelta(days=30), today),
            max_value=today
        )
        
        # Streamlit date_input returns a tuple when selecting ranges
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            
            # Filter and sum for custom range
            custom_filtered = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
            custom_total = custom_filtered['Amount'].sum()
            custom_orders = len(custom_filtered)
            
            # Display results in clean card sub-columns
            c1, c2 = st.columns(2)
            with c1:
                st.metric(
                    label=f"Revenue ({start_date.strftime('%d %b')} - {end_date.strftime('%d %b')})", 
                    value=f"£{custom_total:,.2f}"
                )
            with c2:
                st.metric(
                    label="Orders Processed", 
                    value=f"{custom_orders} Jobs"
                )
        else:
            st.info("Please select both a start date and an end date on the calendar drop-down.")

st.markdown("---") # Visual separator before your dropdown graphs begin


# --- GOODS VS SERVICES ANALYSIS ---
with st.expander("⚖️ View Goods vs Services Revenue Split"):
    
    # Calculate totals
    goods_total = df[df['Type'] == "📦 Goods"]['Amount'].sum()
    services_total = df[df['Type'] == "🛠️ Service"]['Amount'].sum()
    
    # Create columns inside the expander for metrics
    t1, t2 = st.columns(2)
    
    with t1:
        st.metric("Total Goods Revenue", f"£{goods_total:,.2f}")
    with t2:
        st.metric("Total Service Revenue", f"£{services_total:,.2f}")
        
    # Small bar chart to visualize the split underneath the metrics
    fig_split = px.bar(
        df.groupby('Type')['Amount'].sum().reset_index(),
        x='Type', 
        y='Amount',
        color='Type',
        color_discrete_map={"📦 Goods": "#00CC96", "🛠️ Service": "#636EFA"},
        title="Revenue Distribution",
        text_auto=True, # Shows the exact value on top of the bars
        height=300      # Optimized for iPhone screens
    )
    
    # Format layout and currency tags
    fig_split.update_traces(texttemplate='£%{y:,.2f}', textposition='outside')
    fig_split.update_layout(yaxis_tickprefix='£', yaxis_tickformat=',.2f', showlegend=False)
    
    st.plotly_chart(fig_split, use_container_width=True)


with st.expander("🔍 Detailed Service Breakdown"):
    service_df = df[df['Type'] == "🛠️ Service"]
    if not service_df.empty:
        service_stats = service_df.groupby("Category").agg({
            "Amount": "sum",
            "Quantity": "sum"
        }).reset_index()
        st.table(service_stats.style.format({"Amount": "£{:.2f}"}))
    else:
        st.write("No service data found yet.")


# --- Metrics Section ---
   # st.subheader("Key Performance Indicators")
#k1, k2, k3 = st.columns(3)
    #k1.metric("Net Revenue", f"${df['Amount'].sum():,.2f}")
    #k2.metric("Total Discounts", f"-${df['Adjustments'].sum():,.2f}")
    #k3.metric("Items Sold", int(df['Quantity'].sum()))

#--- 3. DATA PROCESSING ---
# ... (Keep your previous numeric conversion logic for Amount/Quantity) ...
# --- 2. ANALYTICS SECTION ---
if not df.empty:
    # KPI Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Revenue", f"£{df['Amount'].sum():,.2f}")
    m2.metric("Total Items", int(df['Quantity'].sum()))
    m3.metric("Avg. Order", f"£{df['Amount'].mean():,.2f}")
    m4.metric("Discounts", f"-£{df['Adjustments'].sum():,.2f}")

   # --- MAIN CHARTS EXPANDER ---
with st.expander("📊 View Detailed Sales Trends & Payment Methods"):

    # Main Tabs inside the expander
    tab1, tab2 = st.tabs(["📊 Sales Trends", "💳 Payment Methods"])
    with tab1:
        # Group data by Date
        trend_data = df.groupby('Date')['Amount'].sum().reset_index()
        
        # 1. Added text_auto=True to generate the text labels automatically
        fig_trend = px.bar(
            trend_data, 
            x='Date', 
            y='Amount', 
            title="Revenue Over Time",
            text_auto=True, 
            height=320 # Slightly increased height to make room for labels above the bars
        )
        
        # 2. Format the labels to show as currency and place them cleanly on top
        fig_trend.update_traces(
            texttemplate='£%{y:,.2f}', 
            textposition='outside'
        )
        
        # Apply currency formatting to the side Y-axis as well
        fig_trend.update_layout(yaxis_tickprefix='£', yaxis_tickformat=',.2f')
        st.plotly_chart(fig_trend, use_container_width=True)

    with tab2:
        fig_pay = px.pie(
            df, 
            values="Amount", 
            names="Payment Type", 
            hole=0.4,
            height=300 # Mobile friendly height
        )
        fig_pay.update_traces(textinfo='percent+label', hovertemplate='£%{value:,.2f}') 
        st.plotly_chart(fig_pay, use_container_width=True)


if not df.empty:
    with st.expander("Payment Method Breakdown"):
        # Group by Payment Type
        pay_stats = df.groupby("Payment Type")["Amount"].sum().reset_index()
        fig_pay = px.pie(pay_stats, values="Amount", names="Payment Type", hole=0.4, 
                     title="Revenue by Payment Type")
        st.plotly_chart(fig_pay, use_container_width=True)
    





#   --- 3. DATA PROCESSING ---
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



                            


# Row 1: Category Breakdown
with st.expander("Total Sales by Category"):
    cat_stats = df.groupby("Category")["Amount"].sum().reset_index()
    fig_cat = px.bar(cat_stats, x="Category", y="Amount", title="Revenue by Category")
    fig_cat.update_layout(yaxis_tickprefix='£')
    st.plotly_chart(fig_cat, use_container_width=True)



#cat_total = df.groupby("Category")["Amount"].sum().reset_index()
#fig_cat = px.bar(cat_total, x="Category", y="Amount", color="Category", text_auto=True)
#st.plotly_chart(fig_cat, use_container_width=True)

# Row 1.5: Top Customers & Items
# --- TOP PERFORMANCE LEADERBOARDS ---
with st.expander("🏆 View Top Customers & Best Selling Items"):
    
    # Recreate your two columns inside the expander
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Customers (by Value)")
        cust_total = df.groupby("Customer Name")["Amount"].sum().nlargest(5).reset_index()
        fig_cust = px.bar(
            cust_total, 
            x="Amount", 
            y="Customer Name", 
            orientation='h', 
            text_auto=True,
            height=300 # Keeps it compact on mobile
        )
        fig_cust.update_layout(xaxis_tickprefix='£', yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_cust, use_container_width=True)

    with col2:
        st.subheader("Top Selling Items")
        item_counts = df["Item Name"].value_counts().nlargest(5).reset_index()
        item_counts.columns = ["Item Name", "Count"]
        fig_item = px.pie(
            item_counts, 
            values="Count", 
            names="Item Name", 
            hole=0.4,
            height=300 # Keeps it compact on mobile
        )
        st.plotly_chart(fig_item, use_container_width=True)

# New Metric: Total Items Sold
total_items = df['Quantity'].sum()
st.metric("Total Items Sold", int(total_items))

# Updated Chart: Sales vs Quantity
# --- QUANTITY ANALYSIS ---
with st.expander("📦 View Quantity Sold by Category"):
    qty_data = df.groupby("Category")[["Amount", "Quantity"]].sum().reset_index()
    
    fig_qty = px.bar(
        qty_data, 
        x="Category", 
        y="Quantity", 
        title="Quantity Sold by Category",
        text_auto=True, # Shows the exact number right on top of the bars
        height=300      # Keeps it friendly for iPhone screens
    )
    
    # Clean up the chart display
    fig_qty.update_layout(xaxis_title="Category", yaxis_title="Units Sold")
    st.plotly_chart(fig_qty, use_container_width=True)
    



# Row 2: Time Aggregates
# --- 3. TIME-BASED AGGREGATES ---

with st.expander("🗓️ View Sales Trends Over Time"):
    st.subheader("Time-Based Sales Analysis")
    view_choice = st.selectbox("Select View:", ["Last 7 Days", "Daily", "Weekly", "Monthly"])
# Create a clean, independent copy directly from your master dataframe (df)
trend_df = df.copy()

# 1. Safely convert 'Date' into a datetime object for processing
trend_df['Date'] = pd.to_datetime(trend_df['Date'])

# 2. Run clean Groupby Aggregations based on your selection
if view_choice == "Last 7 Days":
    # 🆕 Filter for records within the last 7 days only
    today = pd.Timestamp.now().normalize()
    seven_days_ago = today - pd.Timedelta(days=7)
    trend_df = trend_df[(trend_df['Date'] >= seven_days_ago) & (trend_df['Date'] <= today)]
    
    # Group by day
    agg_df = trend_df.groupby(trend_df['Date'].dt.to_period('D'))['Amount'].sum().reset_index()
    agg_df['Date'] = agg_df['Date'].dt.strftime('%a (%d %b)') # e.g., "Mon (25 May)" looks great on mobile!

elif view_choice == "Daily":
    agg_df = trend_df.groupby(trend_df['Date'].dt.to_period('D'))['Amount'].sum().reset_index()
    agg_df['Date'] = agg_df['Date'].dt.strftime('%Y-%m-%d')
    
elif view_choice == "Weekly":
    agg_df = trend_df.groupby(trend_df['Date'].dt.to_period('W'))['Amount'].sum().reset_index()
    agg_df['Date'] = agg_df['Date'].dt.start_time.dt.strftime('%Y-%m-%d')
    
elif view_choice == "Monthly":
    agg_df = trend_df.groupby(trend_df['Date'].dt.to_period('M'))['Amount'].sum().reset_index()
    agg_df['Date'] = agg_df['Date'].dt.strftime('%Y-%m')

# --- Plotting the Result ---
if not agg_df.empty:
    fig_time = px.bar(
        agg_df, 
        x='Date', 
        y='Amount', 
        title=f"{view_choice} Revenue Trend",
        text_auto=True, 
        height=320       
    )
    
    # Format bar labels to show clean currency text
    fig_time.update_traces(
        texttemplate='£%{y:,.2f}', 
        textposition='outside'
    )
    
    # Apply currency formatting to the Y side-axis
    fig_time.update_layout(yaxis_tickprefix='£', yaxis_tickformat=',.2f')
    st.plotly_chart(fig_time, use_container_width=True)
else:
    st.write("No data available for the selected period.")

# --- Plotting the Result ---
    if not agg_df.empty:
        # 🔄 Changed from px.line to px.bar
        fig_time = px.bar(
            agg_df, 
            x='Date', 
            y='Amount', 
            title=f"{view_choice} Revenue Trend",
            text_auto=True,  # Added missing comma here
            height=320       # Formatted for iPhone screens
        )
        
        # Format the text labels to show clean currency layout (e.g. £120.00)
        fig_time.update_traces(
            texttemplate='£%{y:,.2f}', 
            textposition='outside'
        )
        
        # Apply currency formatting to the Y axis
        fig_time.update_layout(yaxis_tickprefix='£', yaxis_tickformat=',.2f')
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.write("No data available for the selected period.")






# --- 5. RAW DATA DISPLAY ---
with st.expander("View Raw Data Table"):
    # 1. Create a copy for display so we don't break the charts
    display_df = df.copy()
    
    # 2. Sort by date first (so the most recent sales are at the top)
    display_df = display_df.sort_values("Date", ascending=False)
    
    # 3. Reformat the Date column to your preferred string format
   
    # Force it to a datetime object right before formatting to keep `.dt` happy
    display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%d-%m-%Y')
    # 4. Show the table
    st.dataframe(
        display_df, 
        use_container_width=True,
        hide_index=True  # Optional: hides the index column for a cleaner look
    )






# --- 3. MANAGEMENT SECTION (BOTTOM) ---
st.markdown("---")
st.subheader("⚙️ Database Management")

with st.expander("🗑️ Delete a Record"):
    # Create a nice label for selection
    display_df = df.sort_values("Date", ascending=False).copy()
    to_delete = st.selectbox("Select record to permanently remove:", options=display_df.index,
                             format_func=lambda x: f"{display_df.loc[x, 'Date'].strftime('%d-%m-%Y')} - {display_df.loc[x, 'Customer Name']} (${display_df.loc[x, 'Amount']})")
    
    if st.button("Confirm Delete", type="primary"):
        # Calculate Google Sheets row (Header + 0-index offset)
        actual_row = int(to_delete) + 2
        sh.delete_rows(actual_row)
        st.warning("Record deleted from Google Sheets.")
        st.rerun()

with st.expander("📝 Filter & Bulk Edit Records"):
    st.info("Use the filters below to find specific records, edit them in the table, and click Save.")
    
    # 1. Create Filter Columns (Split into 3 for Customer, Date, and Status)
    f_col1, f_col2, f_col3 = st.columns(3)
    
 
    
    
    
    with f_col1:
        # Get unique customers for the filter
        cust_list = ["All"] + sorted(df['Customer Name'].unique().tolist())
        filter_cust = st.selectbox("Filter by Customer:", cust_list)
        
        
    with f_col2:
        # 🔐 Fix: Wrap df['Date'] in pd.to_datetime to keep the .dt accessor happy
        date_list = ["All"] + sorted(pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d').unique().tolist(), reverse=True)
        filter_date = st.selectbox("Filter by Date:", date_list)

    # 2. Apply Filtering to the DataFrame
    filtered_df = df.copy()
    if filter_cust != "All":
        filtered_df = filtered_df[filtered_df['Customer Name'] == filter_cust]
    if filter_date != "All":
        # 🔐 Fix: Wrap filtered_df['Date'] here as well so the filtering matches cleanly
        filtered_df = filtered_df[pd.to_datetime(filtered_df['Date']).dt.strftime('%Y-%m-%d') == filter_date]

    with f_col3:
        # 🆕 Get unique statuses for the filter (e.g., Paid, Pending)
        status_list = ["All"] + sorted(df['Status'].unique().tolist())
        filter_status = st.selectbox("Filter by Status:", status_list)

    # 2. Apply Filtering to the DataFrame

    filtered_df = df.copy()
    
    if filter_cust != "All":
        filtered_df = filtered_df[filtered_df['Customer Name'] == filter_cust]
        
    if filter_date != "All":
        # 🔐 Fix: Force the subset's Date column to datetime right before checking against the filter date
        filtered_df = filtered_df[pd.to_datetime(filtered_df['Date']).dt.strftime('%Y-%m-%d') == filter_date]
    
    if filter_status != "All":
        # 🆕 Apply the Payment Status filter
        filtered_df = filtered_df[filtered_df['Status'] == filter_status]

    # 3. Display the Data Editor with the Filtered Results
    edited_filtered_df = st.data_editor(
        filtered_df, 
        use_container_width=True, 
        hide_index=False,
        column_config={
            "Amount": st.column_config.NumberColumn("Total Amount", format="£%.2f"),
            "Unit Price": st.column_config.NumberColumn("Unit Price", format="£%.2f"),
            "Adjustments": st.column_config.NumberColumn("Adjustments", format="£%.2f")
        }
    )    
    if st.button("💾 Save Changes to Google Sheet", use_container_width=True):
        # 1. Sync the edits into the master dataframe
        df.update(edited_filtered_df)
        
        # 2. Prepare the data for JSON (The "Sanity Check")
        save_df = df.copy()
        
        # Convert dates to strings and handle empty values
        for col in save_df.columns:
            if 'Date' in col:
                save_df[col] = pd.to_datetime(save_df[col], errors='coerce').dt.strftime('%Y-%m-%d')
        
        # Replace ALL problematic values (NaN, Infinity) with safe values
        save_df = save_df.replace([np.inf, -np.inf], np.nan).fillna("")

        # 3. THE SAFETY LOCK
        # We only clear the sheet if we successfully created the data list
        try:
            data_to_upload = save_df.values.tolist()
            header_to_upload = [save_df.columns.values.tolist()]
            
            # ONLY NOW do we touch the Google Sheet
            sh.clear() 
            sh.update('A1', header_to_upload)
            sh.update('A2', data_to_upload)
            
            st.success("Changes saved successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Save aborted to protect your data! Error: {e}")





# --- INVOICE GENERATOR FUNCTION ---
def create_pdf(customer_name, customer_data):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Company Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "SMZ Sports", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, "149 St Pauls Avenue, Slough SL2 5EN", ln=True, align='C')
    pdf.ln(10)
    
    # 2. Invoice Title & Customer Info
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"INVOICE: {customer_name}", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Date: {pd.Timestamp.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)
    
    # 3. Table Header
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(70, 10, "Item", 1, 0, 'C', True)
    pdf.cell(30, 10, "Qty", 1, 0, 'C', True)
    pdf.cell(40, 10, "Unit Price", 1, 0, 'C', True)
    pdf.cell(40, 10, "Total", 1, 1, 'C', True)
    
    # 4. Table Content
    pdf.set_font("Arial", '', 10)
    total_invoice_amount = 0
    for _, row in customer_data.iterrows():
        pdf.cell(70, 10, str(row['Item Name']), 1)
        pdf.cell(30, 10, str(int(row['Quantity'])), 1, 0, 'C')
        pdf.cell(40, 10, f"GBP {row['Unit Price']:.2f}", 1, 0, 'R')
        pdf.cell(40, 10, f"GBP {row['Amount']:.2f}", 1, 1, 'R')
        total_invoice_amount += row['Amount']
        
    # 5. Grand Total
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, "Grand Total", 1, 0, 'R')
    pdf.cell(40, 10, f"GBP {total_invoice_amount:.2f}", 1, 1, 'R')
    
    # 6. FOOTER: Thank You Message
    # Move to 20mm from bottom
    pdf.set_y(-40) 
    pdf.set_font("Arial", 'I', 10) # 'I' for Italic
    pdf.cell(0, 10, "Thank you for your business!", ln=True, align='C')
    
    # Optional: Add a line for a signature or stamp
    pdf.line(70, pdf.get_y(), 140, pdf.get_y())
    
    return pdf.output(dest='S').encode('latin-1')

# --- INVOICE UI SECTION ---
st.markdown("---")
st.subheader("🧾 Generate Customer Invoice")

col_inv1, col_inv2 = st.columns([2, 1])

with col_inv1:
    # Select distinct customers from your data
    all_customers = sorted(df['Customer Name'].unique())
    selected_customer = st.selectbox("Select Customer for Invoice", all_customers)

with col_inv2:
    st.write("##") # Alignment
    if selected_customer:
        # Filter data for this specific customer
        customer_items = df[df['Customer Name'] == selected_customer]
        
        # Generate the PDF in memory
        pdf_bytes = create_pdf(selected_customer, customer_items)
        
        st.download_button(
            label="📥 Download PDF Invoice",
            data=pdf_bytes,
            file_name=f"Invoice_{selected_customer.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# Show a preview of what's going into the invoice
if selected_customer:
    st.write(f"Previewing items for **{selected_customer}**:")
    st.dataframe(customer_items[['Date', 'Item Name', 'Quantity', 'Amount']], use_container_width=True, hide_index=True)
