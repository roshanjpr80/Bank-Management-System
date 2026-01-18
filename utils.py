def find_account(db, acc_no):
    return next((a for a in db["accounts"] if a["account_no"] == acc_no), None)


def search_accounts(db, query):
    q = query.lower().strip()
    return [
        a for a in db["accounts"]
        if q in a["name"].lower() or q in a["account_no"].lower()
    ]


def record_tx(acct, tx_type, amount, note=""):
    from db import gen_tx_id, now_iso
    acct["transactions"].append({
        "tx_id": gen_tx_id(),
        "type": tx_type,
        "amount": amount,
        "balance_after": acct["balance"],
        "note": note,
        "ts": now_iso()
    })








