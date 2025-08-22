import streamlit as st
from datetime import datetime

# --- Sample users database ---
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {
        "sri": {
            "username": "sri",
            "first_name": "Sri",
            "last_name": "A",
            "account_number": "BOT1002",
            "balance": 10000.00,
            "transactions": [
                {"date": "2025-08-22 06:00:00", "type": "debit", "amount": 100.00, "label": "Sent to sri1"},
                {"date": "2025-08-22 06:05:00", "type": "credit", "amount": 10000.00, "label": "Deposit"},
                {"date": "2025-08-22 06:10:00", "type": "credit", "amount": 100.00, "label": "Received from sri1"},
            ]
        },
        "sri1": {
            "username": "sri1",
            "first_name": "Sri",
            "last_name": "One",
            "account_number": "BOT1003",
            "balance": 20000.00,
            "transactions": [
                {"date": "2025-08-22 06:15:00", "type": "credit", "amount": 100.00, "label": "Received from sri"},
                {"date": "2025-08-22 06:20:00", "type": "debit", "amount": 100.00, "label": "Sent to sri"},
                {"date": "2025-08-22 06:25:00", "type": "credit", "amount": 10000.00, "label": "Deposit"},
            ]
        },
        "admin": {
            "username": "admin",
            "first_name": "Admin",
            "last_name": "User",
            "account_number": "BOT1001",
            "balance": 50000.00,
            "transactions": []
        }
    }

# Initialize login time for demo
if 'login_time' not in st.session_state:
    st.session_state['login_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Initialize logged in user (for demo purpose, default to 'sri')
if 'username' not in st.session_state:
    st.session_state['username'] = 'sri'  # Change to 'admin' for banker view

def format_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%b %d")  # e.g., "Aug 22"

def format_transaction_line(txn, account_number):
    date_str = format_date(txn['date']).ljust(7)
    type_str = ("● Credit" if txn['type'] == "credit" else "● Debit").ljust(9)
    account_str = account_number.ljust(13)
    label_str = txn['label'][:30].ljust(30)
    amount_sign = "+" if txn['type'] == "credit" else "-"
    amount_str = f"{amount_sign}${txn['amount']:.2f}".rjust(10)
    return f"{date_str}| {type_str}| {account_str}| {label_str}| {amount_str}"

def format_transaction_line_with_user(txn, account_number, username):
    date_str = format_date(txn['date']).ljust(7)
    type_str = ("● Credit" if txn['type'] == "credit" else "● Debit").ljust(9)
    account_str = account_number.ljust(13)
    label_str = txn['label'][:30].ljust(30)
    user_str = f"User: {username} ({account_number})".ljust(25)
    amount_sign = "+" if txn['type'] == "credit" else "-"
    amount_str = f"{amount_sign}${txn['amount']:.2f}".rjust(10)
    return f"{date_str}| {type_str}| {account_str}| {label_str}| {user_str}| {amount_str}"

def user_dashboard():
    user = st.session_state['users_db'][st.session_state['username']]
    st.markdown(f"⚙️ Settings  \n👤 Logged in as: **{user['username']}**  \n🕒 Login time: {st.session_state['login_time']}")
    st.title(f"👋 Welcome, {user['first_name']} {user['last_name']}!")
    st.markdown(f"**Account Number:** `{user['account_number']}`")
    st.markdown(f"**Balance:** `${user['balance']:.2f}`")
    st.markdown(f"**Login Time:** `{st.session_state['login_time']}`")

    st.subheader("💰 Deposit")
    deposit = st.number_input("Amount to deposit", min_value=0.01, step=0.01)
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
    recipient = st.text_input("Recipient Username")
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
                "label": f"Sent to {recipient}",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            recipient_user = st.session_state['users_db'][recipient]
            recipient_user['balance'] += amount
            recipient_user['transactions'].append({
                "type": "credit",
                "amount": amount,
                "label": f"Received from {user['username']}",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success(f"${amount:.2f} sent to {recipient}.")

    st.subheader("📜 Transaction History")
    if user['transactions']:
        header = "Date   | Type     | Account      | Label                         | Amount"
        separator = "-" * len(header)
        st.text(header)
        st.text(separator)

        lines = []
        for txn in reversed(user['transactions']):
            line = format_transaction_line(txn, user['account_number'])
            st.text(line)
            lines.append(line)

        statement = "Transaction Statement\n\n" + header + "\n" + separator + "\n" + "\n".join(lines)
        st.download_button(
            label="Download Statement",
            data=statement,
            file_name=f"transaction_statement_{user['username']}.txt",
            mime="text/plain"
        )
    else:
        st.info("No transactions yet.")

def banker_dashboard():
    st.markdown(f"⚙️ Settings  \n👤 Logged in as: admin  \n🕒 Login time: {st.session_state['login_time']}")
    st.title("🏛️ Banker Dashboard - Overview")

    total_balance = 0.0
    combined_transactions = []

    for username, data in st.session_state['users_db'].items():
        total_balance += data['balance']
        account_number = data['account_number']
        for txn in data['transactions']:
            label = txn["label"]
            # Enrich label with account numbers for transfers if applicable
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

    st.markdown(f"**Total Balance:** ${total_balance:.2f}")

    st.markdown("### 📜 All Transactions")
    if combined_transactions:
        combined_transactions.sort(key=lambda x: x["date"], reverse=True)
        header = "Date   | Type     | Account      | Label                         | User                     | Amount"
        separator = "-" * len(header)
        st.text(header)
        st.text(separator)

        for txn in combined_transactions:
            line = format_transaction_line_with_user(txn, txn['account_number'], txn['username'])
            st.text(line)
    else:
        st.info("No transactions.")

def main():
    st.sidebar.title("Bank of Tanakala")
    # Simple user switch for demo
    user_select = st.sidebar.selectbox("Login as", options=["sri", "sri1", "admin"])
    st.session_state['username'] = user_select

    if user_select == "admin":
        banker_dashboard()
    else:
        user_dashboard()

if __name__ == "__main__":
    main()
