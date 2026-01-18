import streamlit as st
from db import load_db, save_db, hash_pin, verify_pin
from utils import find_account, search_accounts, record_tx
from styles import apply_style

apply_style()
st.set_page_config(page_title="Bank PRO Streamlit", layout="centered")

db = load_db()

# ---------- FRONT PAGE UI ----------
st.markdown(
    """
    <style>
        .welcome-box {
            background: linear-gradient(135deg, #2c3e50, #4ca1af);
            padding: 40px;
            border-radius: 18px;
            text-align: center;
            color: white;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
            margin-bottom: 25px;
        }
        .welcome-title {
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 10px;
        }
        .welcome-sub {
            font-size: 20px;
            opacity: 0.9;
        }
    </style>

    <div class="welcome-box">
        <div class="welcome-title">🏦 Welcome to PRO Bank System</div>
        <div class="welcome-sub">Manage accounts | Transfer money | View history | Secure banking</div>
    </div>
    """,
    unsafe_allow_html=True
)


# Sidebar menu
menu = st.sidebar.selectbox(
    "Navigation",
    ["Create Account", "Deposit", "Withdraw", "Transfer",
     "Account Details", "Interest Calculator", "Search Accounts",
     "Admin Panel"]
)

# ---------------- CREATE ACCOUNT ----------------
if menu == "Create Account":
    st.markdown("<div class='title'>Create New Account</div>", unsafe_allow_html=True)

    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=18, max_value=100)
    mobile = st.text_input("Mobile (10 digits)")
    email = st.text_input("Email")
    aadhaar = st.text_input("Aadhaar (12 digits)")
    pan = st.text_input("PAN (10 chars)")
    address = st.text_area("Address")
    pin = st.text_input("Set 4-digit PIN", type="password")

    if st.button("Create Account"):
        if not (mobile.isdigit() and len(mobile) == 10):
            st.error("Invalid mobile number")
        elif not (aadhaar.isdigit() and len(aadhaar) == 12):
            st.error("Invalid Aadhaar")
        elif len(pan) != 10:
            st.error("Invalid PAN")
        elif not (pin.isdigit() and len(pin) == 4):
            st.error("PIN must be 4 digits")
        else:
            acc_no = None
            for _ in range(10):
                candidate = __import__("db").gen_account_number()
                if not find_account(db, candidate):
                    acc_no = candidate
                    break

            salt, hashed = hash_pin(pin)

            db["accounts"].append({
                "account_no": acc_no,
                "name": name,
                "age": age,
                "mobile": mobile,
                "email": email,
                "aadhaar": aadhaar,
                "pan": pan,
                "address": address,
                "pin_salt": salt,
                "pin_hash": hashed,
                "balance": 0.0,
                "transactions": [],
            })
            save_db(db)
            st.success(f"Account Created! Account No: {acc_no}")

# ---------------- DEPOSIT ----------------
if menu == "Deposit":
    st.markdown("<div class='title'>Deposit Money</div>", unsafe_allow_html=True)

    acc_no = st.text_input("Account Number")
    amount = st.number_input("Amount", min_value=1.0)

    if st.button("Deposit Amount"):
        acct = find_account(db, acc_no)
        if acct:
            acct["balance"] += amount
            record_tx(acct, "deposit", amount)
            save_db(db)
            st.success(f"Deposit Successful! New Balance ₹{acct['balance']:.2f}")
        else:
            st.error("Account not found")

# ---------------- WITHDRAW ----------------
if menu == "Withdraw":
    st.markdown("<div class='title'>Withdraw Money</div>", unsafe_allow_html=True)

    acc_no = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    amount = st.number_input("Amount", min_value=1.0)

    if st.button("Withdraw"):
        acct = find_account(db, acc_no)
        if not acct:
            st.error("Account not found")
        elif not verify_pin(pin, acct["pin_salt"], acct["pin_hash"]):
            st.error("Incorrect PIN!")
        elif amount > acct["balance"]:
            st.error("Insufficient balance")
        else:
            acct["balance"] -= amount
            record_tx(acct, "withdraw", amount)
            save_db(db)
            st.success(f"Withdrawal Successful! New Balance ₹{acct['balance']:.2f}")

# ---------------- TRANSFER ----------------
if menu == "Transfer":
    st.markdown("<div class='title'>Transfer Money</div>", unsafe_allow_html=True)

    f_acc = st.text_input("From Account")
    pin = st.text_input("PIN", type="password")
    t_acc = st.text_input("To Account")
    amount = st.number_input("Amount", min_value=1.0)

    if st.button("Transfer"):
        a = find_account(db, f_acc)
        b = find_account(db, t_acc)

        if not a:
            st.error("Source account not found")
        elif not b:
            st.error("Destination account not found")
        elif not verify_pin(pin, a["pin_salt"], a["pin_hash"]):
            st.error("Wrong PIN")
        elif amount > a["balance"]:
            st.error("Insufficient balance")
        else:
            a["balance"] -= amount
            b["balance"] += amount
            record_tx(a, "transfer_out", amount, f"to {t_acc}")
            record_tx(b, "transfer_in", amount, f"from {f_acc}")
            save_db(db)
            st.success("Transfer Successful ✔")

# ---------------- ACCOUNT DETAILS ----------------
if menu == "Account Details":
    st.markdown("<div class='title'>Account Details</div>", unsafe_allow_html=True)

    acc_no = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")

    if st.button("Get Details"):
        acct = find_account(db, acc_no)
        if acct and verify_pin(pin, acct["pin_salt"], acct["pin_hash"]):
            st.json({k: v for k, v in acct.items() if k not in ("pin_hash", "pin_salt")})
        else:
            st.error("Invalid account or PIN")

# ---------------- INTEREST ----------------
if menu == "Interest Calculator":
    st.markdown("<div class='title'>Interest Calculation</div>", unsafe_allow_html=True)

    acc_no = st.text_input("Account Number")
    rate = st.number_input("Rate (%)", min_value=0.0)
    years = st.number_input("Years", min_value=0.1)

    if st.button("Calculate"):
        acct = find_account(db, acc_no)
        if not acct:
            st.error("Account not found")
        else:
            interest = acct["balance"] * (rate / 100) * years
            st.info(f"Interest Amount: ₹{interest:.2f}")

            if st.button("Apply to Account"):
                acct["balance"] += interest
                record_tx(acct, "interest", interest)
                save_db(db)
                st.success("Interest Applied ✔")

# ---------------- SEARCH ----------------
if menu == "Search Accounts":
    st.markdown("<div class='title'>Search Accounts</div>", unsafe_allow_html=True)

    query = st.text_input("Search Name or Account No")

    if st.button("Search"):
        results = search_accounts(db, query)
        if results:
            st.json(results)
        else:
            st.warning("No results found")

# ---------------- ADMIN PANEL ----------------
if menu == "Admin Panel":
    st.markdown("<div class='title'>Admin Panel</div>", unsafe_allow_html=True)

    username = st.text_input("Admin Username")
    password = st.text_input("Admin Password", type="password")

    if st.button("Login"):
        admin = db["meta"]["admin"]
        if username == admin["username"] and password == admin["password"]:
            st.success("Admin Login Successful ✔")

            st.subheader("All Accounts")
            st.json(db["accounts"])

        else:
            st.error("Invalid admin credentials")












# Run Python File :- python -m streamlit run app.py















