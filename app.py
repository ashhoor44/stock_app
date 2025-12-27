import streamlit as st
import pandas as pd
from datetime import datetime
import os
from streamlit_option_menu import option_menu

# --- PAGE CONFIG (Tab Title & Icon) ---
st.set_page_config(page_title="Stock Portal", page_icon="📦", layout="wide")

# --- HIDE STREAMLIT BRANDING ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp > header {display: none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- SECURITY ---
USERS = {
    "admin": "password123",
    "staff": "stock2024"
}

def check_password():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        return True

    # Login Screen Design
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔒 Login Required")
        st.info("Please enter your credentials to access the Warehouse System.")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Log In", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("😕 Incorrect username or password")
    return False

# --- DATA HANDLING ---
CSV_FILE = 'stock_data.csv'

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=["Date", "Item", "Quantity", "Status", "Notes", "User"])

def save_entry(item, qty, status, notes, user):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame({
        "Date": [timestamp],
        "Item": [item],
        "Quantity": [qty],
        "Status": [status],
        "Notes": [notes],
        "User": [user]
    })
    write_header = not os.path.exists(CSV_FILE)
    new_data.to_csv(CSV_FILE, mode='a', header=write_header, index=False)

# --- MAIN APP LOGIC ---
if check_password():
    
    # sidebar navigation
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2897/2897785.png", width=100) # Placeholder Logo
        st.write(f"Welcome, **Admin**")
        
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Data Logs", "Dashboard"],
            icons=["house", "table", "bar-chart-line"], # Bootstrap Icons
            menu_icon="cast",
            default_index=0,
        )
        
        st.markdown("---")
        if st.button("Log Out", use_container_width=True):
            st.session_state["logged_in"] = False
            st.rerun()

    # --- PAGE 1: HOME (Entry) ---
    if selected == "Home":
        st.title("📦 New Entry")
        st.markdown("Record incoming or outgoing stock below.")
        
        # Load data to show quick stats at top
        df = load_data()
        today_count = len(df[df['Date'].str.contains(datetime.now().strftime("%Y-%m-%d"))])
        
        # Top Metric Cards
        m1, m2, m3 = st.columns(3)
        m1.metric("Entries Today", today_count)
        m2.metric("Last Item", df.iloc[-1]['Item'] if not df.empty else "N/A")
        m3.metric("System Status", "Online", delta_color="normal")
        
        st.write("---")
        
        # The Form - Using Columns for better layout
        with st.form("entry_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                item_name = st.selectbox("Select Item", ["iPhone 15", "Samsung S24", "MacBook Air", "Dell XPS", "Accessories"])
                quantity = st.number_input("Quantity", min_value=1, step=1)
            with c2:
                status = st.selectbox("Status Update", ["Received", "In Transit", "Damaged", "Delivered"])
                notes = st.text_area("Notes", placeholder="Any damage details or serial numbers?")
            
            submitted = st.form_submit_button("✅ Submit Entry", use_container_width=True)

            if submitted:
                save_entry(item_name, quantity, status, notes, "Admin")
                st.success(f"Saved: {quantity}x {item_name} ({status})")

    # --- PAGE 2: DATA LOGS (Table) ---
    if selected == "Data Logs":
        st.title("📋 Data Logs")
        df = load_data()
        
        # Search/Filter
        search = st.text_input("🔍 Search Logs", placeholder="Type item name or status...")
        if search:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
        
        st.dataframe(df, use_container_width=True, height=500)

    # --- PAGE 3: DASHBOARD (Visuals) ---
    if selected == "Dashboard":
        st.title("📈 Stock Analytics")
        df = load_data()
        
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Items by Status")
                status_counts = df['Status'].value_counts()
                st.bar_chart(status_counts)
            
            with col2:
                st.subheader("Total Quantity per Item")
                item_counts = df.groupby("Item")["Quantity"].sum()
                st.bar_chart(item_counts)
        else:
            st.info("No data available to generate charts.")