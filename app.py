import streamlit as st
from datetime import datetime

# -------------------- Session State Initialization --------------------
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
            "transactions": [],
            "account_number": "BOT1001"
        }
    }
    st.session_state['next_account_num'] = 1002

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'is_banker' not in st.session_state:
    st.session_state['is_banker'] = False
if 'login_time' not in st.session_state:
    st.session_state['login_time'] = None
if 'mode' not in st.session_state:
    st.session_state['mode'] = 'login'

# -------------------- Helpers --------------------
def generate_account_number():
    acc_num = f"BOT{st.session_state['next_account_num']}"
    st.session_state['next_account_num'] += 1
    return acc_num

def logout():
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['is_banker'] = False
    st.session_state['login_time'] = None
    st.success("Logged out successfully.")

# -------------------- Pages --------------------
def register():
    st.title("🏦 Bank of Tanakala - Register")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    st.subheader("Personal Information")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    address = st.text_input("Address", value="123 Nth Avenue, New York City")
    country = st.text_input("Country", value="United States")
    state = st.text_input("State", value="New York")
    zip_code = st.text_input("Zip", value="10004")
    ssn = st.text_input("SSN", value="111-22-3333")
    birthday = st.date_input("Birthday")
    timezone = st.selectbox("Timezone", ["(GMT-05:00) Eastern Time (US & Canada)", "(GMT+00:00) UTC"])

    if st.button("Register"):
        if username in st.session_state['users_db']:
            st.error("Username already exists.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        elif not username or not password:
            st.error("Username and password required.")
        else:
            acc_number = generate_account_number()
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
                "account_number": acc_number
            }
            st.success(f"Registered successfully! Your account number is {acc_number}. Please login.")
            st.session_state['mode'] = 'login'

def login():
    st.title("🏦 Bank of Tanakala - Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Sign In"):
        user_db = st.session_state['users_db']
        if username in user_db and user_db[username]['password'] == password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['is_banker'] = (username == 'admin')
            st.session_state['login_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            st.error("Invalid credentials.")

def user_dashboard():
    user = st.session_state['users_db'][st.session_state['username']]
    st.title(f"👋 Welcome, {user['first_name']} {user['last_name']}!")

    st.markdown(f"**Account Number:** `{user['account_number']}`")
    st.markdown(f"**Balance:** `${user['balance']:.2f}`")
    st.markdown(f"**Login Time:** `{st.session_state['login_time']}`")

    st.subheader("💰 Deposit")
    deposit = st.number_input("Amount to deposit", min_value=0.01, step=0.01, key="deposit_amount")
    if st.button("Deposit"):
        user['balance'] += deposit
        user['transactions'].append({
            "type": "credit",
            "amount": deposit,
            "label": "Deposit",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.success(f"${deposit:.2f} deposited successfully!")

    st.subheader("📤 Send Money")

    # Prepare recipient options (exclude self)
    recipient_options = []
    for uname, udata in st.session_state['users_db'].items():
        if uname != st.session_state['username']:
            recipient_options.append(f"{uname} ({udata['account_number']})")
    
    recipient_selection = st.selectbox("Recipient Username and Account", options=recipient_options)

    amount = st.number_input("Amount to send", min_value=0.01, step=0.01, key="send_amount")
    if st.button("Send"):
        if not recipient_selection:
            st.error("Please select a recipient.")
        else:
            recipient_username = recipient_selection.split()[0]  # Extract username before space (before '(')
            if recipient_username not in st.session_state['users_db']:
                st.error("Recipient not found.")
            elif user['balance'] < amount:
                st.error("Insufficient balance.")
            else:
                # Debit from sender
                user['balance'] -= amount
                user['transactions'].append({
                    "type": "debit",
                    "amount": amount,
                    "label": f"Sent to {recipient_username}",
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                # Credit to recipient
                recipient_user = st.session_state['users_db'][recipient_username]
                recipient_user['balance'] += amount
                recipient_user['transactions'].append({
                    "type": "credit",
                    "amount": amount,
                    "label": f"Received from {st.session_state['username']}",
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success(f"${amount:.2f} sent to {recipient_username}.")

    st.subheader("📜 Transaction History")
    if user['transactions']:
        for txn in reversed(user['transactions']):
            st.write(f"{txn['date']} | {txn['type'].capitalize()} | {txn['label']} | ${txn['amount']:.2f}")
    else:
        st.info("No transactions yet.")

def banker_dashboard():
    st.title("🏛️ Banker Dashboard - Overview")

    total_balance = 0.0
    combined_transactions = []

    for username, data in st.session_state['users_db'].items():
        total_balance += data['balance']
        account_number = data['account_number']
        for txn in data['transactions']:
            label = txn["label"]

            # Enrich label with account number if it has username references
            if "Sent to" in label:
                recipient_username = label.split("Sent to")[-1].strip()
                recipient_data = st.session_state['users_db'].get(recipient_username)
                recipient_acc = recipient_data['account_number'] if recipient_data else "N/A"
                label = f"Sent to {recipient_username} ({recipient_acc})"
            elif "Received from" in label:
                sender_username = label.split("Received from")[-1].strip()
                sender_data = st.session_state['users_db'].get(sender_username)
                sender_acc = sender_data['account_number'] if sender_data else "N/A"
                label = f"Received from {sender_username} ({sender_acc})"

            combined_transactions.append({
                "username": username,
                "account_number": account_number,
                "date": txn["date"],
                "type": txn["type"],
                "label": label,
                "amount": txn["amount"]
            })

    # Display bank (admin) summary
    st.markdown("### 👤 User: admin")
    st.markdown("**Name:** Bank of Tanakala")
    st.markdown("**Account Number:** BOT1001")
    st.markdown(f"**Balance:** ${total_balance:.2f}")

    st.markdown("### 📜 All Transactions")
    if combined_transactions:
        combined_transactions.sort(key=lambda x: x["date"], reverse=True)
        for txn in combined_transactions:
            st.write(f"{txn['date']} | {txn['type'].capitalize()} | {txn['label']} | "
                     f"${txn['amount']:.2f} | User: {txn['username']} ({txn['account_number']})")
    else:
        st.info("No transactions.")

# -------------------- Sidebar Logout --------------------
def sidebar():
    with st.sidebar:
        if st.session_state['logged_in']:
            st.markdown("## ⚙️ Settings")
            st.markdown(f"👤 Logged in as: `{st.session_state['username']}`")
            st.markdown(f"🕒 Login time: `{st.session_state['login_time']}`")
            if st.button("🚪 Logout"):
                logout()

# -------------------- App Controller --------------------
def main():
    sidebar()

    if st.session_state['logged_in']:
        if st.session_state['is_banker']:
            banker_dashboard()
        else:
            user_dashboard()
    else:
        if st.session_state['mode'] == 'login':
            login()
            if st.button("Go to Register"):
                st.session_state['mode'] = 'register'
        else:
            register()
            if st.button("Go to Login"):
                st.session_state['mode'] = 'login'

if __name__ == "__main__":
    main()
