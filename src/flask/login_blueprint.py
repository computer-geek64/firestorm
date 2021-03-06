#!/usr/bin/python3
# login_blueprint.py

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
import psycopg2
from datetime import datetime
from errors_blueprint import *
from subprocess import Popen, PIPE
from auth import authenticate, verify_credentials
from config import CALENDAR_DB_NAME, DB_USER, DB_PASSWORD, IFTTT_WEBHOOK
from flask import Blueprint, render_template, request, redirect, session


login_blueprint = Blueprint('login_blueprint', __name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))


# Login
@login_blueprint.route('/login/', methods=['GET'])
def get_login():
    if 'login_attempts' in session and session.get('login_attempts') > 2:
        return error_403(403)
    if 'username' in session and 'password' in session and verify_credentials(session.get('username'), session.get('password')):
        return redirect('/dashboard'), 302
    return render_template('login.html'), 200


@login_blueprint.route('/login/', methods=['POST'])
def post_login():
    if 'login_attempts' in session:
        if session.get('login_attempts') > 2:
            return error_403(403)
        session['login_attempts'] = int(session.get('login_attempts')) + 1
    else:
        session['login_attempts'] = 1
    username = request.form.get('username')
    password = request.form.get('password')
    if not verify_credentials(username, password):
        if session.get('login_attempts') > 2:
            return error_403(403)
        return error_401(401)
    requests.post(IFTTT_WEBHOOK, json={'value1': 'Firestorm Login', 'value2': 'A new login to Firestorm was detected.'})
    session['username'] = username
    session['password'] = password
    session.pop('login_attempts')
    return redirect('/dashboard'), 302


# Logout
@login_blueprint.route('/logout/', methods=['GET'])
@authenticate
def get_logout():
    session.clear()
    return redirect('/'), 302


# Dashboard
@login_blueprint.route('/dashboard/', methods=['GET'])
@authenticate
def get_dashboard():
    date = datetime.now()
    current_date = date.strftime('%A, %B %-d')
    current_date += 'th' if 4 <= date.day <= 20 or 24 <= date.day <= 30 else ['st', 'nd', 'rd'][date.day % 10 - 1]
    current_date += ', ' + date.strftime('%Y')

    uptime = Popen(['uptime', '-p'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().capitalize() + ' since '
    uptime += datetime.strptime(Popen(['uptime', '-s'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().strip(), '%Y-%m-%d %H:%M:%S').strftime('%a %b %d %-I:%M:%S %p')

    system_info = Popen(['uname', '-snrmo'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().strip()

    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as file:
        celsius = float(file.read()) / 1000
        temperature = round(celsius * 9 / 5 + 32, 2)

    #updates = Popen(['pacman', '-Qu'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().count('\n')
    updates = 0
    services = [x == 'active' for x in Popen(['systemctl', 'is-active', 'firestorm', 'sshd', 'NetworkManager'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().strip().split('\n')]
    services = {
        'Firestorm Web Server': services[0],
        'OpenSSH Server': services[1],
        'Network Manager': services[2]
    }

    who = Popen(['who'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().strip().split('\n')
    if who == ['']:
        who = []
    for i in range(len(who)):
        who[i] = [x for x in who[i].split(' ') if x]
        who[i][2] = who[i][2] + ' ' + who[i].pop(3)

    fs_info = [[y for y in x.split(' ') if y] for x in Popen(['df', '--output=source,fstype,size,used,avail,pcent,target', '-H', '-x', 'tmpfs', '-x', 'devtmpfs'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().split('\n')[1:] if not ('fn' + 'op'[::-1] + 'nr'[::-1] + str(4))[2:-1] in x]

    conn = psycopg2.connect(database=CALENDAR_DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    cursor.execute('''
SELECT *
  FROM "calendar_view"
 WHERE "status" < 1
   AND "end_time" < to_timestamp(extract(epoch FROM current_timestamp) + %s);
''', (604800,))
    to_do = [{'type': row[0], 'label': row[1], 'description': row[2], 'start_time': row[3], 'end_time': row[4], 'priority': row[5], 'status': row[6], 'location': row[7], 'url': row[8]} for row in cursor.fetchall()]
    conn.close()
    return render_template('dashboard.html', current_date=current_date, uptime=uptime, system_info=system_info, temperature=temperature, updates=updates, services=services, who=who, fs_info=fs_info, to_do=to_do), 200
