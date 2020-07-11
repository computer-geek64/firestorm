#!/usr/bin/python3
# projects_blueprint.py

import os
import psycopg2
from auth import authenticate
from errors_blueprint import *
from config import PROJECTS_DB_NAME, PROJECTS_DB_USER, PROJECTS_DB_PASSWORD
from flask import Blueprint, render_template, request, session


projects_blueprint = Blueprint('projects_blueprint', __name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))


# Projects
@projects_blueprint.route('/projects/', methods=['GET'])
@authenticate
def get_projects():
    conn = psycopg2.connect(database=PROJECTS_DB_NAME, user=PROJECTS_DB_USER, password=PROJECTS_DB_PASSWORD, host='localhost', port=5432)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects;')
    cursor.fetchall()
    conn.commit()
    conn.close()
    return render_template('projects/projects.html')
