#!/usr/bin/env python3
"""
Bank Management System — PRO STYLED VERSION
Features:
 - Styled CLI (colorama)
 - Secure PIN hashing (salt + SHA256)
 - Create / Deposit / Withdraw / Transfer
 - Transaction history (timestamped) with transaction IDs
 - Admin panel (list, view, delete, change admin creds, export)
 - Interest calculation (simple annual)
 - Search (by name / account substring)
 - Safe JSON DB read/write (atomic temp write)
 - Input validation + helpful messages
"""
from pathlib import Path
import json
import random
import string
import hashlib
import os
from datetime import datetime
from uuid import uuid4
from typing import Optional, Dict, Any, List
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

DB_PATH = Path("bank_db.json")
DB_EXPORT_DIR = Path(".")
DEFAULT_ADMIN = {"username": "roshan", "password": "roshan8084"}  # change after first run!

# ---------------- Utility functions ----------------
def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def atomic_write(path: Path, data: dict):
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    tmp.replace(path)

def gen_account_number() -> str:
    # 4 uppercase letters + 6 digits
    letters = ''.join(random.choices(string.ascii_uppercase, k=4))
    digits = ''.join(random.choices(string.digits, k=6))
    return f"{letters}{digits}"

def gen_tx_id() -> str:
    return uuid4().hex

def hash_pin(pin: str, salt: Optional[str] = None): #-> (str, str):
    if salt is None:
        salt = os.urandom(8).hex()
    hashed = hashlib.sha256((salt + pin).encode()).hexdigest()
    return salt, hashed

def verify_pin(pin: str, salt: str, hashed: str) -> bool:
    return hashlib.sha256((salt + pin).encode()).hexdigest() == hashed

# ---------------- Database ----------------
def load_db() -> dict:
    if not DB_PATH.exists():
        db = {"meta": {"created_at": now_iso(), "admin": DEFAULT_ADMIN}, "accounts": []}
        atomic_write(DB_PATH, db)
        return db
    try:
        with DB_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        # Backup corrupted DB and create new
        backup = DB_PATH.with_suffix(".corrupt." + datetime.utcnow().strftime("%Y%m%d%H%M%S") + ".json")
        DB_PATH.replace(backup)
        print(Fore.RED + f"[WARN] DB corrupted - moved to {backup.name}. New DB created.")
        db = {"meta": {"created_at": now_iso(), "admin": DEFAULT_ADMIN}, "accounts": []}
        atomic_write(DB_PATH, db)
        return db

def save_db(db: dict):
    atomic_write(DB_PATH, db)

# ---------------- Helpers ----------------
def find_account(db: dict, acc_no: str) -> Optional[dict]:
    return next((a for a in db["accounts"] if a["account_no"] == acc_no), None)

def search_accounts(db: dict, query: str) -> List[dict]:
    q = query.strip().lower()
    return [a for a in db["accounts"] if q in a["name"].lower() or q in a["account_no"].lower()]

def print_header(title: str):
    print(Fore.CYAN + Style.BRIGHT + "\n" + "="*40)
    print(Fore.CYAN + Style.BRIGHT + f"   {title}")
    print(Fore.CYAN + Style.BRIGHT + "="*40 + "\n")

def safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\n" + Fore.RED + "Input interrupted. Returning to menu.")
        return ""

# ---------------- Business Logic ----------------
def create_account(db: dict):
    print_header("CREATE ACCOUNT")
    name = safe_input("Full name: ").strip()
    if not name:
        print(Fore.RED + "Name cannot be empty.")
        return
    try:
        age = int(safe_input("Age: ").strip())
    except ValueError:
        print(Fore.RED + "Invalid age.")
        return
    if age < 18:
        print(Fore.RED + "Must be 18+ to open account.")
        return
    mobile = safe_input("Mobile (10 digits): ").strip()
    if not (mobile.isdigit() and len(mobile) == 10):
        print(Fore.RED + "Invalid mobile.")
        return
    email = safe_input("Email: ").strip()
    aadhaar = safe_input("Aadhaar (12 digits): ").strip()
    if not (aadhaar.isdigit() and len(aadhaar) == 12):
        print(Fore.RED + "Invalid Aadhaar.")
        return
    pan = safe_input("PAN (10 chars): ").strip().upper()
    if len(pan) != 10:
        print(Fore.RED + "Invalid PAN.")
        return
    address = safe_input("Address: ").strip()
    pin = safe_input("Set 4-digit PIN: ").strip()
    if not (pin.isdigit() and len(pin) == 4):
        print(Fore.RED + "PIN must be 4 digits.")
        return
    # generate unique account number
    for _ in range(10):
        acc_no = gen_account_number()
        if not find_account(db, acc_no):
            break
    else:
        print(Fore.RED + "Failed to generate account number. Try again later.")
        return
    salt, hashed = hash_pin(pin)
    acct = {
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
        "created_at": now_iso()
    }
    db["accounts"].append(acct)
    save_db(db)
    print(Fore.GREEN + f"\n✅ Account created successfully! Account No: {Fore.YELLOW + acc_no}")
    print(Fore.MAGENTA + "⚠️  Remember your account number and PIN. PIN is stored securely (hashed).")

def record_tx(acct: dict, tx_type: str, amount: float, note: str = ""):
    acct["transactions"].append({
        "tx_id": gen_tx_id(),
        "type": tx_type,
        "amount": amount,
        "balance_after": acct["balance"],
        "note": note,
        "ts": now_iso()
    })

def deposit(db: dict):
    print_header("DEPOSIT")
    acc_no = safe_input("Account number: ").strip()
    acct = find_account(db, acc_no)
    if not acct:
        print(Fore.RED + "Account not found.")
        return
    try:
        amt = float(safe_input("Amount to deposit: ").strip())
    except ValueError:
        print(Fore.RED + "Invalid amount.")
        return
    if amt <= 0:
        print(Fore.RED + "Amount must be positive.")
        return
    acct["balance"] += amt
    record_tx(acct, "deposit", amt, "deposit via CLI")
    save_db(db)
    print(Fore.GREEN + f"✅ Deposit successful. New balance: {Fore.YELLOW + f'₹{acct['balance']:.2f}'}")

def withdraw(db: dict):
    print_header("WITHDRAW")
    acc_no = safe_input("Account number: ").strip()
    acct = find_account(db, acc_no)
    if not acct:
        print(Fore.RED + "Account not found.")
        return
    pin = safe_input("Enter 4-digit PIN: ").strip()
    if not verify_pin(pin, acct["pin_salt"], acct["pin_hash"]):
        print(Fore.RED + "Incorrect PIN.")
        return
    try:
        amt = float(safe_input("Amount to withdraw: ").strip())
    except ValueError:
        print(Fore.RED + "Invalid amount.")
        return
    if amt <= 0:
        print(Fore.RED + "Amount must be positive.")
        return
    if amt > acct["balance"]:
        print(Fore.RED + "Insufficient balance.")
        return
    acct["balance"] -= amt
    record_tx(acct, "withdraw", amt, "withdraw via CLI")
    save_db(db)
    print(Fore.GREEN + f"✅ Withdrawal successful. New balance: {Fore.YELLOW + f'₹{acct['balance']:.2f}'}")

def transfer(db: dict):
    print_header("TRANSFER")
    from_acc = safe_input("Your account number: ").strip()
    acct_from = find_account(db, from_acc)
    if not acct_from:
        print(Fore.RED + "Source account not found.")
        return
    pin = safe_input("Enter your 4-digit PIN: ").strip()
    if not verify_pin(pin, acct_from["pin_salt"], acct_from["pin_hash"]):
        print(Fore.RED + "Incorrect PIN.")
        return
    to_acc = safe_input("Destination account number: ").strip()
    acct_to = find_account(db, to_acc)
    if not acct_to:
        print(Fore.RED + "Destination account not found.")
        return
    if to_acc == from_acc:
        print(Fore.RED + "Cannot transfer to the same account.")
        return
    try:
        amt = float(safe_input("Amount to transfer: ").strip())
    except ValueError:
        print(Fore.RED + "Invalid amount.")
        return
    if amt <= 0:
        print(Fore.RED + "Amount must be positive.")
        return
    if amt > acct_from["balance"]:
        print(Fore.RED + "Insufficient balance.")
        return
    acct_from["balance"] -= amt
    acct_to["balance"] += amt
    record_tx(acct_from, "transfer_out", amt, f"to {to_acc}")
    record_tx(acct_to, "transfer_in", amt, f"from {from_acc}")
    save_db(db)
    print(Fore.GREEN + "✅ Transfer completed successfully.")

def show_details(db: dict):
    print_header("ACCOUNT DETAILS")
    acc_no = safe_input("Account number: ").strip()
    acct = find_account(db, acc_no)
    if not acct:
        print(Fore.RED + "Account not found.")
        return
    pin = safe_input("Enter 4-digit PIN: ").strip()
    if not verify_pin(pin, acct["pin_salt"], acct["pin_hash"]):
        print(Fore.RED + "Incorrect PIN.")
        return
    print(Fore.GREEN + f"\nName: {acct['name']}")
    print(Fore.YELLOW + f"Account No: {acct['account_no']}")
    print(Fore.YELLOW + f"Balance: ₹{acct['balance']:.2f}")
    print(Fore.YELLOW + f"Created: {acct['created_at']}")
    print(Fore.CYAN + "\nRecent Transactions:")
    for tx in reversed(acct["transactions"][-10:]):  # last 10
        print(Fore.MAGENTA + f" - [{tx['ts']}] {tx['type']} {tx['amount']:.2f} -> Bal: {tx['balance_after']:.2f} ({tx.get('note','')})")

def calc_interest(db: dict):
    print_header("INTEREST CALCULATION")
    acc_no = safe_input("Account number: ").strip()
    acct = find_account(db, acc_no)
    if not acct:
        print(Fore.RED + "Account not found.")
        return
    try:
        rate = float(safe_input("Annual interest rate (percent): ").strip())
        years = float(safe_input("Years (e.g., 1): ").strip())
    except ValueError:
        print(Fore.RED + "Invalid input.")
        return
    if rate < 0 or years <= 0:
        print(Fore.RED + "Rate must be >=0 and years > 0.")
        return
    principal = acct["balance"]
    interest = principal * (rate/100.0) * years
    print(Fore.YELLOW + f"\nPrincipal: ₹{principal:.2f}")
    print(Fore.GREEN + f"Interest for {years} yrs at {rate}%: ₹{interest:.2f}")
    apply_now = safe_input("Apply interest to account? (y/N): ").strip().lower()
    if apply_now == "y":
        acct["balance"] += interest
        record_tx(acct, "interest", interest, f"{rate}% for {years} yrs")
        save_db(db)
        print(Fore.GREEN + f"✅ Interest applied. New balance: ₹{acct['balance']:.2f}")

# ---------------- Admin ----------------
def admin_login(db: dict) -> bool:
    print_header("ADMIN LOGIN")
    username = safe_input("Admin username: ").strip()
    password = safe_input("Admin password: ").strip()
    saved = db.get("meta", {}).get("admin", DEFAULT_ADMIN)
    if username == saved.get("username") and password == saved.get("password"):
        print(Fore.GREEN + "Admin authenticated.")
        return True
    print(Fore.RED + "Admin auth failed.")
    return False

def admin_panel(db: dict):
    if not admin_login(db):
        return
    while True:
        print_header("ADMIN PANEL")
        print(Fore.YELLOW + "1) List accounts (summary)")
        print(Fore.YELLOW + "2) View account full details")
        print(Fore.YELLOW + "3) Delete account")
        print(Fore.YELLOW + "4) Change admin credentials")
        print(Fore.YELLOW + "5) Export DB")
        print(Fore.YELLOW + "6) Show bank totals")
        print(Fore.YELLOW + "7) Back to main menu")
        choice = safe_input("Choice: ").strip()
        if choice == "1":
            print(Fore.CYAN + f"\nTotal accounts: {len(db['accounts'])}")
            for a in db["accounts"]:
                print(Fore.MAGENTA + f" - {a['account_no']} | {a['name']} | ₹{a['balance']:.2f} | Created: {a['created_at']}")
        elif choice == "2":
            acc = safe_input("Account number: ").strip()
            a = find_account(db, acc)
            if not a:
                print(Fore.RED + "Not found.")
            else:
                safe_show = {k:v for k,v in a.items() if k not in ("pin_hash","pin_salt")}
                print(json.dumps(safe_show, indent=4, ensure_ascii=False))
        elif choice == "3":
            acc = safe_input("Account number to delete: ").strip()
            a = find_account(db, acc)
            if not a:
                print(Fore.RED + "Not found.")
            else:
                confirm = safe_input(f"Type DELETE to confirm deletion of {acc}: ").strip()
                if confirm == "DELETE":
                    db["accounts"].remove(a)
                    save_db(db)
                    print(Fore.GREEN + "Account deleted.")
                else:
                    print(Fore.YELLOW + "Deletion aborted.")
        elif choice == "4":
            un = safe_input("New admin username: ").strip()
            pw = safe_input("New admin password: ").strip()
            if un and pw:
                db.setdefault("meta", {})["admin"] = {"username": un, "password": pw}
                save_db(db)
                print(Fore.GREEN + "Admin credentials updated.")
            else:
                print(Fore.RED + "Invalid input.")
        elif choice == "5":
            fname = f"bank_db_export_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
            path = DB_EXPORT_DIR / fname
            with path.open("w", encoding="utf-8") as f:
                json.dump(db, f, indent=4, ensure_ascii=False)
            print(Fore.GREEN + f"DB exported to {path.name}")
        elif choice == "6":
            total = sum(a["balance"] for a in db["accounts"])
            print(Fore.CYAN + f"Total deposits across bank: ₹{total:.2f}")
            print(Fore.CYAN + f"Total accounts: {len(db['accounts'])}")
        elif choice == "7":
            break
        else:
            print(Fore.RED + "Invalid option.")

# ---------------- Search + Utility Menus ----------------
def search_menu(db: dict):
    print_header("SEARCH ACCOUNTS")
    q = safe_input("Search (name or account substring): ").strip()
    if not q:
        print(Fore.RED + "Empty query.")
        return
    results = search_accounts(db, q)
    if not results:
        print(Fore.YELLOW + "No matches.")
        return
    print(Fore.CYAN + f"Found {len(results)} match(es):")
    for a in results:
        print(Fore.MAGENTA + f" - {a['account_no']} | {a['name']} | ₹{a['balance']:.2f}")

def show_all_accounts(db: dict):
    print_header("ALL ACCOUNTS")
    if not db["accounts"]:
        print(Fore.YELLOW + "No accounts yet.")
        return
    for a in db["accounts"]:
        print(Fore.MAGENTA + f"{a['account_no']} | {a['name']} | ₹{a['balance']:.2f}")

# ---------------- Main CLI ----------------
def main():
    db = load_db()
    while True:
        print(Fore.CYAN + Style.BRIGHT + "\n=== BANK PRO - MAIN MENU ===")
        print(Fore.YELLOW + "1) Create account")
        print(Fore.YELLOW + "2) Deposit")
        print(Fore.YELLOW + "3) Withdraw")
        print(Fore.YELLOW + "4) Transfer")
        print(Fore.YELLOW + "5) Show account details")
        print(Fore.YELLOW + "6) Interest calculation / apply")
        print(Fore.YELLOW + "7) Search accounts")
        print(Fore.YELLOW + "8) Admin panel")
        print(Fore.YELLOW + "9) Show all accounts")
        print(Fore.YELLOW + "0) Exit")
        choice = safe_input("\nEnter choice: ").strip()
        if choice == "1":
            create_account(db)
        elif choice == "2":
            deposit(db)
        elif choice == "3":
            withdraw(db)
        elif choice == "4":
            transfer(db)
        elif choice == "5":
            show_details(db)
        elif choice == "6":
            calc_interest(db)
        elif choice == "7":
            search_menu(db)
        elif choice == "8":
            admin_panel(db)
        elif choice == "9":
            show_all_accounts(db)
        elif choice == "0":
            print(Fore.GREEN + "Goodbye — thank you for using Bank PRO.")
            break
        else:
            print(Fore.RED + "Invalid choice. Enter a number from the menu.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + Fore.RED + "Interrupted. Exiting...")













