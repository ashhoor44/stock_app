import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- SECURITY ---
# Simple hardcoded users for this test. 
# (In a real app, we would use a secure database or Streamlit Secrets)
USERS = {
    "admin": "password123",  # Username: admin, Password: password123
    "staff": "stock2024"     # Username: staff, Password: stock2024
}

def check_password():
    """Returns `True` if the user had a correct password."""
    
    # Initialize session state for login
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # If already logged in, return True immediately
    if st.session_state["logged_in"]:
        return True

    # Show Login Inputs
    st.title("🔒 Login Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Log In"):
        if username in USERS and USERS[username] == password:
            st.session_state["logged_in"] = True
            st.rerun()  # Reload the app to show the dashboard
        else:
            st.error("😕 Incorrect username or password")
            
    return False

# --- MAIN APP ---
if check_password():
    # Everything below here only runs IF logged in
    
    CSV_FILE = 'stock_data.csv'

    def load_data():
        if os.path.exists(CSV_FILE):
            return pd.read_csv(CSV_FILE)
        else:
            return pd.DataFrame(columns=["Date", "Item", "Quantity", "Status", "Notes"])

    st.sidebar.success("✅ Logged in")
    if st.sidebar.button("Log Out"):
        st.session_state["logged_in"] = False
        st.rerun()

    st.title("📦 Warehouse Stock Entry")

    with st.form("stock_update_form"):
        st.write("### Update Stock Status")
        item_name = st.selectbox("Select Item", ["iPhone 15", "Samsung S24", "MacBook Air", "Dell XPS"])
        quantity = st.number_input("Quantity", min_value=1, step=1)
        status = st.selectbox("Status Update", ["Received", "In Transit", "Damaged", "Delivered"])
        notes = st.text_area("Additional Notes (Optional)")
        
        submitted = st.form_submit_button("Submit Update")

        if submitted:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_data = pd.DataFrame({
                "Date": [timestamp],
                "Item": [item_name],
                "Quantity": [quantity],
                "Status": [status],
                "Notes": [notes]
            })
            
            write_header = not os.path.exists(CSV_FILE)
            new_data.to_csv(CSV_FILE, mode='a', header=write_header, index=False)
            st.success(f"✅ Saved: {quantity}x {item_name}")

    st.write("---")
    st.write("### 📊 Live Data Log")
    df = load_data()
    st.dataframe(df, use_container_width=True)