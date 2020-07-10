#!/usr/bin/python3
# login_blueprint.py

from errors_blueprint import *
from flask import Blueprint, render_template, request, redirect, session


login_blueprint = Blueprint('login_blueprint', __name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))


# Additional functions


# Login
@login_blueprint.route('/login/', methods=['GET'])
def get_login():
    if 'login_attempts' in session.keys() and session['login_attempts'] > 2:
        return error_403(403)
    if 'username' in session.keys() and 'password' in session.keys() and authenticate(session['username'], session['password']):
        return redirect('/dashboard'), 302
    return render_template('login.html'), 200


@login_blueprint.route('/login/', methods=['POST'])
def post_login():
    if 'login_attempts' in session.keys():
        if session['login_attempts'] > 2:
            return error_403(403)
        session['login_attempts'] = int(session['login_attempts']) + 1
    else:
        session['login_attempts'] = 1
    username = request.form.get('username')
    password = request.form.get('password')
    if not authenticate(username, password):
        if session['login_attempts'] > 2:
            return error_403(403)
        return error_401(401)
    session['username'] = username
    session['password'] = password
    session.pop('login_attempts')
    return redirect('/dashboard'), 302


# Logout
@app.route(safe_join(app.config['HOME'], 'logout'), methods=['GET'])
def get_logout():
    if 'username' not in session.keys() or 'password' not in session.keys():
        return error_403(403)
    if not authenticate(session['username'], session['password']):
        return error_401(401)
    session.clear()
    return redirect(app.config['HOME']), 302

# Dashboard
@app.route(safe_join(app.config['HOME'], 'dashboard'), methods=['GET'])
def get_dashboard():
    if 'username' not in session.keys() or 'password' not in session.keys():
        return error_403(403)
    if not authenticate(session['username'], session['password']):
        return error_401(401)
    permissions = get_permissions(session['username'])
    date = datetime.now()
    current_date = date.strftime('%A, %B %-d')
    current_date += 'th' if 4 <= date.day <= 20 or 24 <= date.day <= 30 else ['st', 'nd', 'rd'][date.day % 10 - 1]
    current_date += ', ' + date.strftime('%Y')
    current_time = date.strftime('%-I:%M:%S %p')
    uptime = Popen(['uptime', '-p'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().capitalize() + ' since '
    uptime += datetime.strptime(Popen(['uptime', '-s'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().strip(), '%Y-%m-%d %H:%M:%S').strftime('%a %b %d %-I:%M:%S %p')
    #raw_response_text = requests.get('http://wttr.in?0?T?q', timeout=5).text
    #weather = raw_response_text.split('\n')[1][15:].strip() + ', ' + raw_response_text.split('\n')[2][15:].strip() + ' in ' + raw_response_text.split('\n')[0]
    system_info = Popen(['uname', '-snrmo'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().strip()
    temperature = -1
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as file:
        celsius = float(file.read()) / 1000
        temperature = round(celsius * 9 / 5 + 32, 2)
    updates = Popen(['aptitude', 'search', '~U'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().count('\n')
    services = [x == 'active' for x in Popen(['systemctl', 'is-active', 'apache2', 'ssh', 'tor', 'network-manager', 'networking'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().strip().split('\n')]
    services = {
        'Apache HTTP Server': services[0],
        'OpenSSH Server': services[1],
        'TOR Service': services[2],
        'Network Manager': services[3],
        'Networking': services[4]
    }
    who = Popen(['who', '--ips'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().strip().split('\n')
    if who == ['']:
        who = []
    for i in range(len(who)):
        who[i] = [x for x in who[i].split(' ') if x]
        who[i][2] = who[i][2] + ' ' + who[i].pop(3)
    screens = Popen(['screen', '-ls'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().strip()
    screens = [x.strip().split('\t') for x in screens.split('\n') if x.startswith('\t')] if screens.startswith('There') else False
    fs_info = [[y for y in x.split(' ') if y] for x in Popen(['df', '--output=source,fstype,size,used,avail,pcent,target', '-H', '-x', 'tmpfs', '-x', 'devtmpfs'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().split('\n')[1:] if not ('fn' + 'op'[::-1] + 'nr'[::-1] + str(4))[2:-1] in x]
    return render_template('dashboard.html', current_date=current_date, current_time=current_time, uptime=uptime, system_info=system_info, temperature=temperature, updates=updates, services=services, who=who, screens=screens, fs_info=fs_info, title=session['username'].capitalize() + '\'s Dashboard', permissions=permissions, active_sidenav='dashboard'), 200
