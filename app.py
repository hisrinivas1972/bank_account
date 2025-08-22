import streamlit as st
from datetime import date

# In-memory user "database"
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {}

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
        else:
            st.error("Invalid username or password")

def dashboard():
    st.title(f"Welcome to Bank of Tanakala, {st.session_state['username']}")

    user_data = st.session_state['users_db'][st.session_state['username']]

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
        else:
            st.error("Enter a valid deposit amount.")

    # --- Send Payment ---
    st.subheader("Send Payment")
    recipient = st.text_input("Recipient username")
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

    if st.button("Log out"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None

# --- Main App Logic ---
if 'mode' not in st.session_state:
    st.session_state['mode'] = 'login'

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = None

# Navigation buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Go to Login"):
        st.session_state['mode'] = 'login'
with col2:
    if st.button("Go to Register"):
        st.session_state['mode'] = 'register'

if st.session_state['logged_in']:
    dashboard()
else:
    if st.session_state['mode'] == 'login':
        login()
    else:
        register()
