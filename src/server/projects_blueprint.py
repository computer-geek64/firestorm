#!/usr/bin/python3
# projects_blueprint.py

import os
from auth import authenticate
from errors_blueprint import *
from flask import Blueprint, render_template, request, session


projects_blueprint = Blueprint('projects_blueprint', __name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))


# Projects
@projects_blueprint.route('/projects/', methods=['GET'])
@authenticate
def get_projects():
    return render_template('projects/projects.html')
