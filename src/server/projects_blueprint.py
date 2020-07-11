#!/usr/bin/python3
# projects_blueprint.py

import os
from auth import authenticate
from errors_blueprint import *
from flask import Blueprint, render_template, request, session


projects_blueprint = Blueprint('projects_blueprint', __name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))


# Projects
@projects_blueprint.route('/projects/', methods=['GET'])
def get_projects():
    if 'username' not in session or 'password' not in session:
        return error_403(403)
    if not authenticate(session.get('username'), session.get('password')):
        return error_401(401)
    return 'Hi'