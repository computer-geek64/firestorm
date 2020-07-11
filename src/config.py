#!/usr/bin/python3
# config.py

IP = '0.0.0.0'
PORT = 80

SESSION_SECRET_KEY = ''  # Session variables secret key

SHA512_SALT = ''  # SHA-512 hash salt
USERNAME = ''  # Root user username
PASSWORD_HASH = ''  # Root user SHA-512 password hash

VIDEOS_LOCATION = ''  # Path to videos folder
MUSIC_LOCATION = ''  # Path to music folder

DB_USER = ''  # PostgreSQL database user
DB_PASSWORD = ''  # PostgreSQL database user password
PROJECTS_DB_NAME = 'projects'  # PostgreSQL projects database name

GIT_FOLDER = '/git'  # Folder for bare git repositories
