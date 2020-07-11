#!/usr/bin/python3
# power_blueprint.py

import os
from auth import authenticate
from errors_blueprint import *
from subprocess import Popen, PIPE
from flask import Blueprint, render_template, request, session


power_blueprint = Blueprint('power_blueprint', __name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))


# Power
@power_blueprint.route('/power/', methods=['GET'])
@authenticate
def get_power():
    return render_template('power/power.html', title='Power'), 200


@power_blueprint.route('/power/<string:action>', methods=['GET'])
@authenticate
def get_power_action(action):
    actions = {'shutdown': '-P', 'restart': '-r'}
    if action not in actions:
        return error_404(404)
    Popen(['/usr/bin/sudo', '/usr/sbin/shutdown', actions[action], 'now'], stdout=PIPE, stderr=PIPE)
    return render_template('power/power.html', message=action.capitalize() + ' scheduled', title='Power'), 200


@power_blueprint.route('/power/<string:action>', methods=['POST'])
@authenticate
def power_action(action):
    try:
        minutes = request.form.get('time', 'now')
        int(minutes)
    except ValueError:
        return render_template('power/power.html', message='Invalid number', title='Power'), 200
    actions = {'shutdown': '-P', 'restart': '-r'}
    if action not in actions:
        return error_404(404)
    Popen(['/usr/bin/sudo', '/usr/sbin/shutdown', actions[action], minutes], stdout=PIPE, stderr=PIPE)
    return render_template('power/power.html', message=action.capitalize() + ' scheduled', title='Power'), 200
