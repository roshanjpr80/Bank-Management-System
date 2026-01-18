from pathlib import Path
import json
import os
import hashlib
from datetime import datetime
import uuid

DB_PATH = Path("bank_db.json")

DEFAULT_ADMIN = {"username": "roshan", "password": "roshan8084"}


def now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def atomic_write(path: Path, data: dict):
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    tmp.replace(path)


def load_db():
    if not DB_PATH.exists():
        db = {"meta": {"created_at": now_iso(), "admin": DEFAULT_ADMIN}, "accounts": []}
        atomic_write(DB_PATH, db)
        return db
    with DB_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_db(db: dict):
    atomic_write(DB_PATH, db)


def hash_pin(pin: str, salt=None):
    if salt is None:
        salt = os.urandom(8).hex()
    hashed = hashlib.sha256((salt + pin).encode()).hexdigest()
    return salt, hashed


def verify_pin(pin: str, salt: str, hashed: str):
    return hashlib.sha256((salt + pin).encode()).hexdigest() == hashed


def gen_account_number():
    import random, string
    letters = ''.join(random.choices(string.ascii_uppercase, k=4))
    digits = ''.join(random.choices(string.digits, k=6))
    return letters + digits


def gen_tx_id():
    return uuid.uuid4().hex













