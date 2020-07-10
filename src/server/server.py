#!/usr/bin/python3
# server.py

import os
from files_blueprint import files_blueprint
from errors_blueprint import errors_blueprint
from datetime import datetime
from subprocess import Popen, PIPE
from flask import Flask, jsonify, redirect, request, render_template, send_file, session, safe_join


app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))
app.register_blueprint(files_blueprint)
app.register_blueprint(errors_blueprint)


# Home
@app.route('/', methods=['GET'])
def get_home():
    return 'Welcome to Firestorm!', 200


if __name__ == '__main__':
    app.run('0.0.0.0', 81)
