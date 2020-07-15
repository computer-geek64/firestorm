#!/usr/bin/python3
# auth.py

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import hashlib
from flask import session
from functools import wraps
from errors_blueprint import *
from config import USERNAME, PASSWORD_HASH, SHA512_SALT


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in session or 'password' not in session:
            return error_403(403)
        if verify_credentials(session.get('username'), session.get('password')):
            return func(*args, **kwargs)
        return error_401(401)
    return wrapper


def verify_credentials(username, password):
    password_hash = hashlib.sha512((SHA512_SALT + password).encode()).hexdigest()
    return username == USERNAME and password_hash == PASSWORD_HASH
