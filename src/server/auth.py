#!/usr/bin/python3
# auth.py

import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import hashlib
from config import USERNAME, PASSWORD_HASH, SHA512_SALT


def authenticate(username, password):
    password_hash = hashlib.sha512((SHA512_SALT + password).encode()).hexdigest()
    return username == USERNAME and password_hash == PASSWORD_HASH
