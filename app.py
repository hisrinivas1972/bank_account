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


def format_date(date_str):
    # Expects date_str format: "%Y-%m-%d %H:%M:%S"
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%b %d")  # e.g., Aug 22


def format_transaction_line(txn, account_number):
    # Fixed width for columns
    date_str = format_date(txn['date']).ljust(7)
    type_str = ("● Credit" if txn['type'] == "credit" else "● Debit").ljust(9)
    account_str = account_number.ljust(13)
    label_str = txn['label'][:24].ljust(24)
    amount_sign = "+" if txn['type'] == "credit" else "-"
    amount_str = f"{amount_sign}${txn['amount']:.2f}".rjust(10)
    return f"{date_str}| {type_str}| {account_str}| {label_str}| {amount_str}"


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
    recipient = st.text_input("Recipient Username", key="send_username")
    amount = st.number_input("Amount to send", min_value=0.01, step=0.01, key="send_amount")
    if st.button("Send"):
        if recipient not in st.session_state['users_db']:
            st.error("Recipient not found.")
        elif recipient == st.session_state['username']:
            st.error("You cannot send money to yourself.")
        elif user['balance'] < amount:
            st.error("Insufficient balance.")
        else:
            user['balance'] -= amount
            user['transactions'].append({
                "type": "debit",
                "amount": amount,
                "label": f"Sent to {recipient} ({st.session_state['users_db'][recipient]['account_number']})",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            recipient_user = st.session_state['users_db'][recipient]
            recipient_user['balance'] += amount
            recipient_user['transactions'].append({
                "type": "credit",
                "amount": amount,
                "label": f"Received from {st.session_state['username']} ({user['account_number']})",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success(f"${amount:.2f} sent to {recipient}.")

    st.subheader("📜 Transaction History")

    # Prepare formatted transaction lines
    if user['transactions']:
        header = "Date   | Type     | Account      | Label                   |    Amount"
        separator = "-" * len(header)
        st.text(header)
        st.text(separator)
        lines = []
        for txn in reversed(user['transactions']):
            line = format_transaction_line(txn, user['account_number'])
            st.text(line)
            lines.append(line)

        # Download statement button
        statement_text = "Transaction Statement\n\n" + header + "\n" + separator + "\n" + "\n".join(lines)
        st.download_button(
            label="Download Statement",
            data=statement_text,
            file_name=f"statement_{user['account_number']}.txt",
            mime="text/plain"
        )
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

            # Enrich label with account number if needed
            if "Sent to" in label:
                recipient_username = label.split("Sent to")[-1].strip().split(" ")[0]
                recipient_data = st.session_state['users_db'].get(recipient_username)
                recipient_acc = recipient_data['account_number'] if recipient_data else "N/A"
                label = f"Sent to {recipient_username} ({recipient_acc})"
            elif "Received from" in label:
                sender_username = label.split("Received from")[-1].strip().split(" ")[0]
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

    st.markdown("### 👤 User: admin")
    st.markdown("**Name:** Bank of Tanakala")
    st.markdown("**Account Number:** BOT1001")
    st.markdown(f"**Balance:** ${total_balance:.2f}")

    st.markdown("### 📜 All Transactions")
    if combined_transactions:
        combined_transactions.sort(key=lambda x: x["date"], reverse=True)
        header = "Date   | Type     | Account      | Label                   |    Amount | User"
        separator = "-" * len(header)
        st.text(header)
        st.text(separator)
        for txn in combined_transactions:
            date_str = format_date(txn['date']).ljust(7)
            type_str = ("● Credit" if txn['type'] == "credit" else "● Debit").ljust(9)
            account_str = txn['account_number'].ljust(13)
            label_str = txn['label'][:24].ljust(24)
            amount_sign = "+" if txn['type'] == "credit" else "-"
            amount_str = f"{amount_sign}${txn['amount']:.2f}".rjust(10)
            user_str = f"User: {txn['username']} ({txn['account_number']})"
            line = f"{date_str}| {type_str}| {account_str}| {label_str}| {amount_str} | {user_str}"
            st.text(line)
    else:
        st.info("No transactions available.")


def main():
    st.sidebar.title("Bank of Tanakala")
    if st.session_state['logged_in']:
        st.sidebar.write(f"👤 Logged in as: {st.session_state['username']}")
        st.sidebar.button("Logout", on_click=logout)
    else:
        mode = st.sidebar.radio("Select Mode", ['Login', 'Register'])
        st.session_state['mode'] = mode

    if not st.session_state['logged_in']:
        if st.session_state['mode'] == 'Login':
            login()
        else:
            register()
    else:
        if st.session_state['is_banker']:
            banker_dashboard()
        else:
            user_dashboard()


if __name__ == "__main__":
    main()
