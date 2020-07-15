#!/usr/bin/python3
# config.py

IP = '0.0.0.0'
PORT = 443

SSL_CERTIFICATE_FILE = ''  # Path to SSL certificate file
SSL_KEY_FILE = ''  # Path to SSL key file

SESSION_SECRET_KEY = ''  # Session variables secret key

SHA512_SALT = ''  # SHA-512 hash salt
USERNAME = ''  # Root user username
PASSWORD_HASH = ''  # Root user SHA-512 password hash

VIDEOS_LOCATION = ''  # Path to videos folder
MUSIC_LOCATION = ''  # Path to music folder

DB_USER = ''  # PostgreSQL database user
DB_PASSWORD = ''  # PostgreSQL database user password
PROJECTS_DB_NAME = 'projects'  # PostgreSQL projects database name

GIT_PATH = '/git'  # Path to folder for bare git repositories
GIT_USER_NAME = ''  # Git config user.name
GIT_USER_EMAIL = ''  # Git config user.email

USB_KEY_UUID = ''  # USB key UUID
