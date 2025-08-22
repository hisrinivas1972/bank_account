import streamlit as st
from datetime import datetime
import pandas as pd

def main():
    # Sample user data (replace with real DB if needed)
    if "users_db" not in st.session_state:
        st.session_state.users_db = {
            "sri1": {
                "first_name": "sri1",
                "last_name": "t",
                "account_number": "BOT1003",
                "balance": 10000.0,
                "transactions": [
                    {"date": "2025-08-22", "type": "credit", "label": "Deposit", "amount": 10000.0},
                ],
            }
        }
    if "username" not in st.session_state:
        st.session_state.username = "sri1"
    if "login_time" not in st.session_state:
        st.session_state.login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    user_dashboard()


def user_dashboard():
    user = st.session_state.users_db[st.session_state.username]

    st.title(f"Bank of Tanakala")
    st.write(f"Logged in as: {st.session_state.username}")
    st.markdown("---")

    st.write(f"👋 Welcome, {user['first_name']} {user['last_name']}!")
    st.write(f"**Account Number:** {user['account_number']}")
    st.write(f"**Balance:** ${user['balance']:.2f}")
    st.write(f"**Login Time:** {st.session_state.login_time}")
    st.markdown("---")

    tabs = ["💰 Deposit", "📤 Send Money", "📜 Transaction History"]

    # Use new API to get query params
    query_params = st.query_params
    tab_from_url = query_params.get("tab", [None])[0]

    if "selected_tab" not in st.session_state:
        # Defensive check: set default if invalid or missing
        if tab_from_url in tabs:
            st.session_state.selected_tab = tab_from_url
        else:
            st.session_state.selected_tab = "📜 Transaction History"
    else:
        # If selected_tab set but not in tabs (can happen on code reload)
        if st.session_state.selected_tab not in tabs:
            st.session_state.selected_tab = "📜 Transaction History"

    def on_tab_change():
        # Update URL query params with the selected tab string
        st.experimental_set_query_params(tab=st.session_state.selected_tab)

    selected_tab = st.radio(
        "Navigate",
        options=tabs,
        index=tabs.index(st.session_state.selected_tab),
        key="selected_tab",
        on_change=on_tab_change,
        horizontal=True,
    )

    if selected_tab == "💰 Deposit":
        deposit_amount = st.number_input("Amount to deposit", min_value=0.01, step=0.01, format="%.2f")
        if st.button("Deposit"):
            if deposit_amount > 0:
                user['balance'] += deposit_amount
                user['transactions'].append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "credit",
                    "label": "Deposit",
                    "amount": deposit_amount
                })
                st.success(f"Successfully deposited ${deposit_amount:.2f}!")
            else:
                st.error("Please enter an amount greater than 0.")

    elif selected_tab == "📤 Send Money":
        recipient = st.text_input("Recipient Username")
        send_amount = st.number_input("Amount to send", min_value=0.01, step=0.01, format="%.2f")
        if st.button("Send Money"):
            if recipient == st.session_state.username:
                st.error("You cannot send money to yourself.")
            elif recipient not in st.session_state.users_db:
                st.error("Recipient username does not exist.")
            elif send_amount <= 0:
                st.error("Please enter an amount greater than 0.")
            elif send_amount > user['balance']:
                st.error("Insufficient balance.")
            else:
                # Deduct from sender
                user['balance'] -= send_amount
                user['transactions'].append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "debit",
                    "label": f"Sent to {recipient}",
                    "amount": -send_amount
                })
                # Credit to recipient
                recipient_user = st.session_state.users_db[recipient]
                recipient_user['balance'] += send_amount
                recipient_user['transactions'].append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "credit",
                    "label": f"Received from {st.session_state.username}",
                    "amount": send_amount
                })
                st.success(f"Successfully sent ${send_amount:.2f} to {recipient}!")

    else:  # Transaction History
        st.subheader("Transaction History")
        if user['transactions']:
            df = pd.DataFrame(user['transactions'])
            df['Amount'] = df['amount'].apply(lambda x: f"+${x:.2f}" if x > 0 else f"-${-x:.2f}")
            df_display = df[['date', 'type', 'label', 'Amount']]
            df_display.columns = ['Date', 'Type', 'Label', 'Amount']
            st.table(df_display)
        else:
            st.info("No transactions found.")


if __name__ == "__main__":
    main()
