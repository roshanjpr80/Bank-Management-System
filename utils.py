from datetime import datetime
import uuid


def find_account(db, acc_no):

    for acc in db["accounts"]:

        if acc["account_no"] == acc_no:
            return acc

    return None


def search_accounts(db, query):

    query = query.lower()

    return [
        acc
        for acc in db["accounts"]
        if query in acc["name"].lower()
        or query in acc["account_no"]
    ]


def generate_tx_id():
    return str(uuid.uuid4())[:8]


def record_tx(account, tx_type, amount, note=""):

    account["transactions"].append({
        "tx_id": generate_tx_id(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": tx_type,
        "amount": amount,
        "note": note
    })