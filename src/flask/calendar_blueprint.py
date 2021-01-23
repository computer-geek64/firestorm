#!/usr/bin/python3 -B
# calendar_blueprint.py

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import psycopg2
import calendar
import holidays
from datetime import datetime, date
from auth import authenticate
from config import CALENDAR_DB_NAME, DB_USER, DB_PASSWORD
from flask import Blueprint, render_template, request


calendar_blueprint = Blueprint('calendar_blueprint', __name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))


# Get calendar
@calendar_blueprint.route('/calendar/', methods=['GET'])
@authenticate
def get_calendar():
    current_date = date(int(request.args.get('year')), int(request.args.get('month')), 1) if request.args.get('month') and request.args.get('year') else datetime.now().date()
    previous_month = {'month': current_date.month - 1, 'year': current_date.year} if current_date.month > 1 else {'month': 12, 'year': current_date.year - 1}
    next_month = {'month': current_date.month + 1, 'year': current_date.year} if current_date.month < 12 else {'month': 1, 'year': current_date.year + 1}

    us_holidays = holidays.UnitedStates()
    calendar_dates = [{'date': d.day, 'filler_date': d.month != current_date.month, 'holiday': us_holidays.get(d), 'today': d == datetime.now().date()} for d in calendar.Calendar(firstweekday=6).itermonthdates(current_date.year, current_date.month)]
    return render_template('calendar/calendar.html', previous_month=previous_month, next_month=next_month, calendar_dates=calendar_dates), 200
