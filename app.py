import streamlit as st
from datetime import datetime, date

# In-memory user "database" (for demo purposes)
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {
        "admin": {
            "password": "admin123",
            "first_name": "Bank of",
            "last_name": "Tanakala",
            "address": "123 Nth Avenue, New York City",
            "country": "United States",
            "state": "New York",
            "zip": "10004",
            "ssn": "111-22-3333",
            "birthday": "1970-01-01",
            "timezone": "(GMT-05:00) Eastern Time (US & Canada)",
            "balance": 0.0,
            "transactions": []
        }
    }

# --- Universal Logout Sidebar ---
if st.session_state.get('logged_in', False):
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        st.markdown(f"👤 Logged in as: `{st.session_state.get('username', '')}`")
        st.markdown(f"🕒 Login time: `{st.session_state.get('login_time', 'N/A')}`")
        if st.button("🚪 Log Out"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = None
            st.session_state['is_banker'] = False
            st.session_state['login_time'] = None
            st.success("Logged out successfully.")
            st.experimental_rerun()


def register():
    st.title("Bank of Tanakala - Register")

    username = st.text_input("Username", key="reg_username")
    password = st.text_input("Password", type="password", key="reg_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")

    st.subheader("Personal Information")
    first_name = st.text_input("First name", key="reg_first_name")
    last_name = st.text_input("Last name", key="reg_last_name")
    address = st.text_input("Address", value="123 Nth Avenue, New York City", key="reg_address")
    country = st.text_input("Country", value="United States", key="reg_country")
    state = st.text_input("State", value="New York", key="reg_state")
    zip_code = st.text_input("Zip", value="10004", key="reg_zip")
    ssn = st.text_input("SSN", value="111-22-3333", key="reg_ssn")
    birthday = st.date_input("Birthday", key="reg_birthday")
    timezone = st.selectbox("Timezone", options=["(GMT-05:00) Eastern Time (US & Canada)", "(GMT+00:00) UTC"], key="reg_timezone")

    if st.button("Register"):
        if username in st.session_state['users_db']:
            st.error("Username already taken.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        elif not username or not password:
            st.error("Username and password cannot be empty.")
        else:
            st.session_state['users_db'][username] = {
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "address": address,
                "country": country,
                "state": state,
                "zip": zip_code,
                "ssn": ssn,
                "birthday": str(birthday),
                "timezone": timezone,
                "balance": 0.0,
                "transactions": []
            }
            st.success("Registration successful! You can now login.")
            st.session_state['mode'] = "login"


def login():
    st.title("Bank of Tanakala - Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Sign In"):
        if username in st.session_state['users_db'] and st.session_state['users_db'][username]['password'] == password:
            st.success(f"Welcome, {username}!")
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['login_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state['is_banker'] = (username == "admin")
            st.experimental_rerun()  # reload app to show dashboard immediately
        else:
            st.error("Invalid username or password")


def dashboard():
    st.title(f"Welcome to Bank of Tanakala, {st.session_state['username']}")

    user_data = st.session_state['users_db'][st.session_state['username']]

    st.markdown(f"🕒 **Login Time:** {st.session_state.get('login_time', 'N/A')}")

    st.subheader("Account Overview")
    st.write(f"Balance: ${user_data['balance']:.2f}")

    st.subheader("Transaction History")
    if user_data['transactions']:
        for txn in user_data['transactions']:
            st.write(f"{txn['type'].capitalize()}: ${txn['amount']} - {txn['label']}")
    else:
        st.write("No transactions yet.")

    # --- Deposit Money ---
    st.subheader("Deposit Money")
    deposit_amount = st.number_input("Amount to deposit", min_value=0.0, step=0.01, format="%.2f")
    if st.button("Deposit"):
        if deposit_amount > 0:
            user_data['balance'] += deposit_amount
            user_data['transactions'].append({
                "type": "credit",
                "amount": deposit_amount,
                "label": "Deposit"
            })
            st.success(f"Deposited ${deposit_amount:.2f} successfully!")
            st.experimental_rerun()
        else:
            st.error("Enter a valid deposit amount.")

    # --- Send Payment ---
    st.subheader("Send Payment")
    recipient = st.text_input("Recipient username", key="recipient_input")
    payment_amount = st.number_input("Amount to send", min_value=0.0, step=0.01, format="%.2f", key="payment_amount")
    if st.button("Send Payment"):
        if payment_amount <= 0:
            st.error("Enter a valid payment amount.")
        elif recipient == st.session_state['username']:
            st.error("You cannot send money to yourself.")
        elif recipient not in st.session_state['users_db']:
            st.error("Recipient username does not exist.")
        elif user_data['balance'] < payment_amount:
            st.error("Insufficient balance.")
        else:
            # Deduct from sender
            user_data['balance'] -= payment_amount
            user_data['transactions'].append({
                "type": "debit",
                "amount": payment_amount,
                "label": f"Payment to {recipient}"
            })
            # Add to recipient
            recipient_data = st.session_state['users_db'][recipient]
            recipient_data['balance'] += payment_amount
            recipient_data['transactions'].append({
                "type": "credit",
                "amount": payment_amount,
                "label": f"Received from {st.session_state['username']}"
            })
            st.success(f"Sent ${payment_amount:.2f} to {recipient} successfully!")
            st.experimental_rerun()


def banker_dashboard():
    st.title("🏛️ Banker Dashboard - User Overviews")

    st.markdown(f"🕒 **Login Time:** {st.session_state.get('login_time', 'N/A')}")
    st.markdown(f"👤 **ADMIN - Appala T**")

    for username, data in st.session_state['users_db'].items():
        full_name = f"{data['first_name']} {data['last_name']}"
        st.markdown(f"---\n👤 **User:** {username}")
        st.markdown(f"Name: {full_name}")
        st.markdown(f"Balance: ${data['balance']:.2f}")

        st.markdown("📜 **Transaction History**")
        if data['transactions']:
            for txn in data['transactions']:
                st.write(f"• {txn['type'].capitalize()}: ${txn['amount']} - {txn['label']}")
        else:
            st.write("No transactions.")


# --- Main App Logic ---

if 'mode' not in st.session_state:
    st.session_state['mode'] = 'login'

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['is_banker'] = False
    st.session_state['login_time'] = None

# Navigation buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("🔐 Go to Login"):
        st.session_state['mode'] = 'login'
with col2:
    if st.button("📝 Go to Register"):
        st.session_state['mode'] = 'register'

# Routing
if st.session_state['logged_in']:
    if st.session_state['is_banker']:
        banker_dashboard()
    else:
        dashboard()
else:
    if st.session_state['mode'] == 'login':
        login()
    else:
        register()
