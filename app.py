import streamlit as st
from datetime import datetime

# Initialize session_state on first run
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {
        "admin": {
            "password": "admin123",
            "first_name": "Bank",
            "last_name": "Tanakala",
            "balance": 0.0,
            "transactions": []
        }
    }
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'login_time' not in st.session_state:
    st.session_state['login_time'] = None
if 'mode' not in st.session_state:
    st.session_state['mode'] = 'login'

# Logout sidebar (shows only if logged in)
def logout_sidebar():
    if st.session_state['logged_in']:
        with st.sidebar:
            st.write(f"Logged in as: {st.session_state['username']}")
            st.write(f"Login time: {st.session_state['login_time']}")
            if st.button("Logout"):
                st.session_state['logged_in'] = False
                st.session_state['username'] = None
                st.session_state['login_time'] = None
                st.experimental_rerun()

# Login function
def login():
    st.title("Bank of Tanakala - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign In"):
        users = st.session_state['users_db']
        if username in users and users[username]['password'] == password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['login_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success(f"Welcome, {username}!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# Register function
def register():
    st.title("Bank of Tanakala - Register")
    username = st.text_input("Choose Username")
    password = st.text_input("Choose Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        users = st.session_state['users_db']
        if not username or not password:
            st.error("Username and password cannot be empty.")
        elif username in users:
            st.error("Username already exists.")
        elif password != confirm:
            st.error("Passwords do not match.")
        else:
            users[username] = {
                "password": password,
                "first_name": "",
                "last_name": "",
                "balance": 0.0,
                "transactions": []
            }
            st.success("Registration successful! Please login.")
            st.session_state['mode'] = 'login'
            st.experimental_rerun()

# Dashboard for normal users
def dashboard():
    st.title(f"Welcome, {st.session_state['username']}")
    user = st.session_state['users_db'][st.session_state['username']]
    
    st.write(f"Balance: ${user['balance']:.2f}")
    st.subheader("Transactions:")
    if user['transactions']:
        for t in user['transactions']:
            st.write(f"{t['type'].capitalize()} ${t['amount']:.2f} - {t['label']}")
    else:
        st.write("No transactions yet.")
    
    st.subheader("Deposit Money")
    amount = st.number_input("Deposit amount", min_value=0.01, step=0.01, format="%.2f")
    if st.button("Deposit"):
        user['balance'] += amount
        user['transactions'].append({"type": "credit", "amount": amount, "label": "Deposit"})
        st.success(f"Deposited ${amount:.2f}")
        st.experimental_rerun()

    st.subheader("Send Payment")
    recipient = st.text_input("Recipient username")
    pay_amount = st.number_input("Amount to send", min_value=0.01, step=0.01, format="%.2f", key="pay_amount")
    if st.button("Send"):
        users = st.session_state['users_db']
        if recipient == st.session_state['username']:
            st.error("Cannot send to yourself")
        elif recipient not in users:
            st.error("Recipient not found")
        elif pay_amount > user['balance']:
            st.error("Insufficient balance")
        else:
            user['balance'] -= pay_amount
            user['transactions'].append({"type": "debit", "amount": pay_amount, "label": f"Payment to {recipient}"})
            users[recipient]['balance'] += pay_amount
            users[recipient]['transactions'].append({"type": "credit", "amount": pay_amount, "label": f"Received from {st.session_state['username']}"})
            st.success(f"Sent ${pay_amount:.2f} to {recipient}")
            st.experimental_rerun()

# Banker dashboard
def banker_dashboard():
    st.title("🏛️ Banker Dashboard - User Overviews")
    users = st.session_state['users_db']
    for uname, data in users.items():
        st.markdown(f"**User:** {uname}")
        st.write(f"Name: {data.get('first_name', '')} {data.get('last_name', '')}")
        st.write(f"Balance: ${data['balance']:.2f}")
        st.write("Transactions:")
        if data['transactions']:
            for t in data['transactions']:
                st.write(f" - {t['type'].capitalize()} ${t['amount']:.2f} - {t['label']}")
        else:
            st.write(" - No transactions")
        st.markdown("---")

# Main app logic
logout_sidebar()

if st.session_state['logged_in']:
    if st.session_state['username'] == 'admin':
        banker_dashboard()
    else:
        dashboard()
else:
    if st.session_state['mode'] == 'login':
        login()
    else:
        register()

# Navigation buttons to switch between login and register
col1, col2 = st.columns(2)
with col1:
    if st.button("Go to Login"):
        st.session_state['mode'] = 'login'
        st.experimental_rerun()
with col2:
    if st.button("Go to Register"):
        st.session_state['mode'] = 'register'
        st.experimental_rerun()
