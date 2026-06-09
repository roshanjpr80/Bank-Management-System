import json
import hashlib
import secrets
import random
import os

DB_FILE = "database.json"


def load_db():
    if not os.path.exists(DB_FILE):
        return {
            "meta": {
                "admin": {
                    "username": "admin",
                    "password": "admin123"
                }
            },
            "accounts": []
        }

    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


def gen_account_number():
    return str(random.randint(10000000, 99999999))


def hash_pin(pin):
    salt = secrets.token_hex(16)

    hashed = hashlib.sha256(
        (pin + salt).encode()
    ).hexdigest()

    return salt, hashed


def verify_pin(pin, salt, stored_hash):
    hashed = hashlib.sha256(
        (pin + salt).encode()
    ).hexdigest()

    return hashed == stored_hash