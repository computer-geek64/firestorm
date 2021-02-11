#!/usr/bin/python3 -B
# calendar_blueprint.py

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import psycopg2
import calendar
import holidays
from auth import authenticate
from errors_blueprint import *
from datetime import datetime, date, timedelta
from config import CALENDAR_DB_NAME, DB_USER, DB_PASSWORD, CALENDAR_SPECIAL_DATES
from flask import Blueprint, render_template, request, redirect


calendar_blueprint = Blueprint('calendar_blueprint', __name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))


# Get calendar
@calendar_blueprint.route('/calendar/', methods=['GET'])
@authenticate
def get_calendar():
    current_date = date(int(request.args.get('year')), int(request.args.get('month')), 1) if request.args.get('month') and request.args.get('year') else datetime.now().date()
    previous_month = {'month': current_date.month - 1, 'year': current_date.year} if current_date.month > 1 else {'month': 12, 'year': current_date.year - 1}
    next_month = {'month': current_date.month + 1, 'year': current_date.year} if current_date.month < 12 else {'month': 1, 'year': current_date.year + 1}

    special_dates = {}
    for k, v in CALENDAR_SPECIAL_DATES.items():
        try:
            special_date = datetime.strptime(k, '%Y-%m-%d')
        except ValueError:
            special_date = datetime.strptime(str(current_date.year) + k, '%Y%m-%d')
        special_dates[special_date] = v

    us_holidays = holidays.UnitedStates()
    us_holidays.append(special_dates)

    month_range = list(calendar.Calendar(firstweekday=6).itermonthdates(current_date.year, current_date.month))
    calendar_dates = [{'date': d.day, 'timestamp': datetime(d.year, d.month, d.day).timestamp(), 'filler_date': d.month != current_date.month, 'holiday': us_holidays.get(d), 'today': d == datetime.now().date(), 'calendar_items': []} for d in month_range]

    conn = psycopg2.connect(database=CALENDAR_DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()

    cursor.execute('''
SELECT "percentage",
       "label"
  FROM "status";
''')
    task_status_lookup = {percentage: label for percentage, label in cursor.fetchall()}

    cursor.execute('''
SELECT *
  FROM "calendar_view"
 WHERE "end_time" >= %s
   AND "end_time" <= %s;
''', (month_range[0], datetime(month_range[-1].year, month_range[-1].month, month_range[-1].day, 23, 59, 59, 999999)))

    for calendar_item in cursor.fetchall():
        if calendar_item[0] == 'event':
            starting_date_index = (calendar_item[3].date() - month_range[0]).days
            event_days = (calendar_item[4].date() - calendar_item[3].date()).days + 1
            for event_day in range(starting_date_index, starting_date_index + event_days):
                calendar_dates[event_day]['calendar_items'].append({
                    'type': calendar_item[0],
                    'label': calendar_item[1] + f' Day {event_day - starting_date_index + 1}' * int(event_days > 1),
                    'description': calendar_item[2],
                    'start_time': calendar_item[3].strftime('%-I:%M %p') if event_day == starting_date_index else (calendar_item[3] + timedelta(days=event_day - starting_date_index)).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%-I:%M %p'),
                    'end_time': calendar_item[4].strftime('%-I:%M %p') if event_day == starting_date_index + event_days - 1 else (calendar_item[4] + timedelta(days=event_day - starting_date_index)).replace(hour=23, minute=59, second=59, microsecond=999999).strftime('%-I:%M %p'),
                    'priority': calendar_item[5],
                    'status': calendar_item[6],
                    'location': calendar_item[7],
                    'url': calendar_item[8],
                    'page': f'{calendar_item[1]}_{calendar_item[4].timestamp()}'
                })
        else:
            calendar_dates[(calendar_item[4].date() - month_range[0]).days]['calendar_items'].append({
                'type': calendar_item[0],
                'label': calendar_item[1],
                'description': calendar_item[2],
                'deadline': calendar_item[4].strftime('%B %-d' + ('th' if 4 <= calendar_item[4].day <= 20 or 24 <= calendar_item[4].day <= 30 else ['st', 'nd', 'rd'][calendar_item[4].day % 10 - 1]) + ', %-I:%M %p'),
                'priority': calendar_item[5],
                'status': task_status_lookup[calendar_item[6]],
                'location': calendar_item[7],
                'url': calendar_item[8],
                'page': f'{calendar_item[1]}_{calendar_item[4].timestamp()}'
            })

    conn.close()
    return render_template('calendar/calendar.html', current_month={'month': current_date.strftime('%B'), 'year': current_date.year}, previous_month=previous_month, next_month=next_month, calendar_dates=calendar_dates), 200


@calendar_blueprint.route('/calendar/<string:name>_<float:timestamp>/', methods=['GET'])
@authenticate
def get_calendar_item(name, timestamp):
    conn = psycopg2.connect(database=CALENDAR_DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()

    cursor.execute('''
SELECT *
  FROM "calendar_view"
 WHERE "label" = %s
   AND "end_time" = %s
''', (name, datetime.fromtimestamp(timestamp)))
    item = cursor.fetchall()
    if not item:
        return error_404(404)
    item = item[0]

    if item[0] == 'event':
        item = {
            'calendar_item_type': item[0],
            'name': item[1],
            'description': item[2],
            'start_time': item[3],
            'end_time': item[4],
            'priority': item[5],
            'status': item[6],
            'location': item[7],
            'url': item[8]
        }
    else:
        cursor.execute('''
SELECT "percentage",
       "label"
  FROM "status";
''')
        task_status_lookup = {percentage: label for percentage, label in cursor.fetchall()}

        cursor.execute('''
    SELECT *
      FROM "status"
  ORDER BY "id" ASC;
''')
        statuses = list(cursor.fetchall())

        item = {
            'calendar_item_type': item[0],
            'name': item[1],
            'description': item[2],
            'deadline': item[4],
            'priority': item[5],
            'status': task_status_lookup[item[6]],
            'location': item[7],
            'url': item[8],
            'statuses': statuses
        }

    cursor.execute('''
    SELECT *
      FROM "priority"
  ORDER BY "id" DESC;
''')
    priorities = list(cursor.fetchall())

    conn.close()
    return render_template('calendar/calendar_item.html', priorities=priorities, **item), 200


@calendar_blueprint.route('/calendar/<string:name>_<float:timestamp>/', methods=['POST'])
@authenticate
def post_calendar_item(name, timestamp):
    conn = psycopg2.connect(database=CALENDAR_DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()

    cursor.execute('''
SELECT *
  FROM "calendar_view"
 WHERE "label" = %s
   AND "end_time" = %s
''', (name, datetime.fromtimestamp(timestamp)))
    item = cursor.fetchall()
    if not item:
        return error_404(404)
    calendar_item_type = item[0][0]

    if request.form.get('name'):
        if calendar_item_type == 'event':
            query = '''
UPDATE "event"
   SET "label" = %s
 WHERE "label" = %s
   AND "end_time" = %s;
'''
        else:
            query = '''
UPDATE "task"
   SET "label" = %s
 WHERE "label" = %s
   AND "deadline" = %s;
'''
        cursor.execute(query, (request.form.get('name'), name, datetime.fromtimestamp(timestamp)))
        name = request.form.get('name')

    if request.form.get('delete'):
        if calendar_item_type == 'event':
            query = '''
DELETE FROM "event"
      WHERE "label" = %s
        AND "end_time" = %s;
'''
        else:
            query = '''
DELETE FROM "task"
      WHERE "label" = %s
        AND "deadline" = %s;
'''
        cursor.execute(query, (name, datetime.fromtimestamp(timestamp)))
        conn.commit()
        conn.close()
        return redirect('/calendar/'), 302

    if request.form.get('description') or request.form.get('description') == '':
        if calendar_item_type == 'event':
            query = '''
UPDATE "event"
   SET "description" = %s
 WHERE "label" = %s
   AND "end_time" = %s;
'''
        else:
            query = '''
UPDATE "task"
   SET "description" = %s
 WHERE "label" = %s
   AND "deadline" = %s;
'''
        cursor.execute(query, (request.form.get('description'), name, datetime.fromtimestamp(timestamp)))

    if request.form.get('from_date') and request.form.get('from_time') and calendar_item_type == 'event':
        cursor.execute('''
UPDATE "event"
   SET "start_time" = %s
 WHERE "label" = %s
   AND "end_time" = %s;
''', (datetime.strptime(request.form.get('from_date') + request.form.get('from_time'), '%Y-%m-%d%H:%M'), name, datetime.fromtimestamp(timestamp)))

    if request.form.get('to_date') and request.form.get('to_time') and calendar_item_type == 'event':
        cursor.execute('''
UPDATE "event"
   SET "end_time" = %s
 WHERE "label" = %s
   AND "end_time" = %s;
''', (datetime.strptime(request.form.get('to_date') + request.form.get('to_time'), '%Y-%m-%d%H:%M'), name, datetime.fromtimestamp(timestamp)))
        timestamp = datetime.strptime(request.form.get('to_date') + request.form.get('to_time'), '%Y-%m-%d%H:%M').timestamp()

    if request.form.get('date') and request.form.get('time') and calendar_item_type == 'task':
        cursor.execute('''
UPDATE "task"
   SET "deadline" = %s
 WHERE "label" = %s
   AND "deadline" = %s;
''', (datetime.strptime(request.form.get('date') + request.form.get('time'), '%Y-%m-%d%H:%M'), name, datetime.fromtimestamp(timestamp)))
        timestamp = datetime.strptime(request.form.get('date') + request.form.get('time'), '%Y-%m-%d%H:%M').timestamp()

    if request.form.get('location') or request.form.get('location') == '':
        if calendar_item_type == 'event':
            query = '''
UPDATE "event"
   SET "location" = %s
 WHERE "label" = %s
   AND "end_time" = %s;
'''
        else:
            query = '''
UPDATE "task"
   SET "location" = %s
 WHERE "label" = %s
   AND "deadline" = %s;
'''
        cursor.execute(query, (request.form.get('location'), name, datetime.fromtimestamp(timestamp)))

    if request.form.get('priority'):
        if calendar_item_type == 'event':
            query = '''
UPDATE "event"
   SET "priority" = %s
 WHERE "label" = %s
   AND "end_time" = %s;
'''
        else:
            query = '''
UPDATE "task"
   SET "priority" = %s
 WHERE "label" = %s
   AND "deadline" = %s;
'''
        cursor.execute(query, (int(request.form.get('priority')), name, datetime.fromtimestamp(timestamp)))

    if request.form.get('status') and calendar_item_type == 'task':
        cursor.execute('''
UPDATE "task"
   SET "status" = %s
 WHERE "label" = %s
   AND "deadline" = %s;
''', (int(request.form.get('status')), name, datetime.fromtimestamp(timestamp)))

    if request.form.get('url') or request.form.get('url') == '':
        if calendar_item_type == 'event':
            query = '''
UPDATE "event"
   SET "url" = %s
 WHERE "label" = %s
   AND "end_time" = %s;
'''
        else:
            query = '''
UPDATE "task"
   SET "url" = %s
 WHERE "label" = %s
   AND "deadline" = %s;
'''
        cursor.execute(query, (request.form.get('url'), name, datetime.fromtimestamp(timestamp)))

    conn.commit()
    conn.close()
    return redirect(f'/calendar/{name}_{timestamp}/'), 302


@calendar_blueprint.route('/calendar/create/', methods=['POST'])
@authenticate
def post_calendar_item_create():
    if not request.form.get('type') or not request.form.get('name') or not request.form.get('timestamp'):
        return redirect('/calendar/'), 302

    conn = psycopg2.connect(database=CALENDAR_DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()

    if request.form.get('type') == 'event':
        cursor.execute('''
INSERT INTO "event"
            (
                "label",
                "description",
                "start_time",
                "end_time",
                "priority",
                "location",
                "url"
            )
     VALUES (
                %s,
                '',
                %s,
                %s,
                1,
                '',
                ''
            );
''', (request.form.get('name'), datetime.fromtimestamp(float(request.form.get('timestamp'))), datetime.fromtimestamp(float(request.form.get('timestamp')))))
    else:
        cursor.execute('''
INSERT INTO "task"
            (
                "label",
                "description",
                "deadline",
                "priority",
                "status",
                "location",
                "url"
            )
     VALUES (
                %s,
                '',
                %s,
                1,
                1,
                '',
                ''
            );
''', (request.form.get('name'), datetime.fromtimestamp(float(request.form.get('timestamp')))))

    conn.commit()
    conn.close()
    return redirect('/calendar/' + request.form.get('name') + '_' + request.form.get('timestamp') + '/'), 302
