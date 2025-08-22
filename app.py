import streamlit as st
from datetime import datetime, date

# Initialize session state keys
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {
        "admin": {
            "password": "admin123",
            "first_name": "Appala",
            "last_name": "T",
            "address": "123 Nth Avenue, New York City",
            "country": "United States",
            "state": "New York",
            "zip": "10004",
            "ssn": "111-22-3333",
            "birthday": "1970-01-01",
            "timezone": "(GMT-05:00) Eastern Time (US & Canada)",
            "balance": 0.0,
            "transactions": [],
            "account_number": "BOT1001"
        }
    }
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'login_time' not in st.session_state:
    st.session_state['login_time'] = None
if 'is_banker' not in st.session_state:
    st.session_state['is_banker'] = False
if 'next_account_num' not in st.session_state:
    st.session_state['next_account_num'] = 1002  # start after BOT1001
if 'mode' not in st.session_state:
    st.session_state['mode'] = 'login'  # default mode is login

def generate_account_number():
    acc_num = f"BOT{st.session_state['next_account_num']}"
    st.session_state['next_account_num'] += 1
    return acc_num

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
            account_number = generate_account_number()
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
                "transactions": [],
                "account_number": account_number
            }
            st.success(f"Registration successful! Your account number is {account_number}. You can now login.")
            st.session_state['mode'] = "login"
            st.experimental_rerun()

def login():
    st.title("Bank of Tanakala - Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Sign In"):
        if username in st.session_state['users_db'] and st.session_state['users_db'][username]['password'] == password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['login_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state['is_banker'] = (username == "admin")
            st.success(f"Welcome, {username}!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

def user_dashboard():
    st.title(f"Welcome to Bank of Tanakala, {st.session_state['username']}")

    user_data = st.session_state['users_db'][st.session_state['username']]

    st.markdown(f"**Account Number:** {user_data['account_number']}")
    st.markdown(f"🕒 **Login Time:** {st.session_state.get('login_time', 'N/A')}")

    st.subheader("Current Balance")
    st.write(f"${user_data['balance']:.2f}")

    st.subheader("Deposit Funds")
    deposit_amount = st.number_input("Amount to deposit", min_value=0.0, step=0.01, format="%.2f", key="deposit_amount")
    if st.button("Deposit"):
        if deposit_amount > 0:
            user_data['balance'] += deposit_amount
            user_data['transactions'].append({
                "type": "credit",
                "amount": deposit_amount,
                "label": "Deposit",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success(f"Deposited ${deposit_amount:.2f} successfully!")
            st.experimental_rerun()
        else:
            st.error("Enter a valid deposit amount.")

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
                "label": f"Payment to {recipient}",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            # Add to recipient
            recipient_data = st.session_state['users_db'][recipient]
            recipient_data['balance'] += payment_amount
            recipient_data['transactions'].append({
                "type": "credit",
                "amount": payment_amount,
                "label": f"Received from {st.session_state['username']}",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success(f"Sent ${payment_amount:.2f} to {recipient} successfully!")
            st.experimental_rerun()

    st.subheader("Transaction History")
    if user_data['transactions']:
        for txn in reversed(user_data['transactions']):  # newest first
            st.write(f"{txn['date']} | {txn['type'].capitalize()} | {txn['label']} | ${txn['amount']:.2f}")
    else:
        st.write("No transactions yet.")

def banker_dashboard():
    st.title("🏛️ Banker Dashboard - User Overviews")
    st.markdown(f"🕒 **Login Time:** {st.session_state.get('login_time', 'N/A')}")
    st.markdown("### Users Overview")

    for username, data in st.session_state['users_db'].items():
        full_name = f"{data['first_name']} {data['last_name']}"
        st.markdown(f"---\n👤 **User:** {username}")
        st.markdown(f"Name: {full_name}")
        st.markdown(f"Account Number: {data['account_number']}")
        st.markdown(f"Balance: ${data['balance']:.2f}")

        st.markdown("📜 **Transaction History:**")
        if data['transactions']:
            for txn in reversed(data['transactions']):  # newest first
                st.write(f"{txn['date']} | {txn['type'].capitalize()} | {txn['label']} | ${txn['amount']:.2f}")
        else:
            st.write("No transactions.")

def logout_sidebar():
    if st.session_state.get('logged_in', False):
        with st.sidebar:
            st.markdown("## ⚙️ Settings")
            st.markdown(f"👤 Logged in as: `{st.session_state.get('username', '')}`")
            st.markdown(f"🕒 Login time: `{st.session_state.get('login_time', 'N/A')}`
