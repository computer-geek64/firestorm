#!/usr/bin/python3
# server.py

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask
from config import SSL_CERTIFICATE_FILE, SSL_KEY_FILE, SESSION_SECRET_KEY, IP, PORT
from files_blueprint import files_blueprint
from login_blueprint import login_blueprint
from power_blueprint import power_blueprint
from projects_blueprint import projects_blueprint
from errors_blueprint import errors_blueprint, error_404


app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))
app.register_blueprint(files_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(power_blueprint)
app.register_blueprint(projects_blueprint)
app.register_blueprint(errors_blueprint)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = SESSION_SECRET_KEY


# Fix blueprint 404 HTTP error handler wit)h override
@app.errorhandler(404)
def error_404_override(e):
    return error_404(e)


# Home
@app.route('/', methods=['GET'])
def get_home():
    return 'Welcome to Firestorm!', 200


if __name__ == '__main__':
    app.run(IP, PORT, ssl_context=(SSL_CERTIFICATE_FILE, SSL_KEY_FILE))
