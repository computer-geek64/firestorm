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

PROJECTS_DB = 'projects'  # PostgreSQL projects database name
PROJECTS_DB_USER = ''  # PostgreSQL projects database user
PROJECTS_DB_PASSWORD = ''  # PostgreSQL projects database user password
