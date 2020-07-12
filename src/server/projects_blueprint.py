#!/usr/bin/python3
# projects_blueprint.py

import os
import psycopg2
from datetime import datetime
from auth import authenticate
from errors_blueprint import *
from subprocess import Popen, PIPE
from config import PROJECTS_DB_NAME, DB_USER, DB_PASSWORD, GIT_PATH
from flask import Blueprint, render_template, request, session, jsonify


projects_blueprint = Blueprint('projects_blueprint', __name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))


# Additional functions
def snake_case_to_title(s):
    return ' '.join([x.capitalize() if x not in ['of', 'as', 'the'] else x for x in s.split('_')])


# Projects
@projects_blueprint.route('/projects/', methods=['GET'])
@authenticate
def get_projects():
    conn = psycopg2.connect(database=PROJECTS_DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    cursor.execute('''
SELECT "label"
  FROM "organization_type";
''')
    organization_types = [{'label': snake_case_to_title(x[0]), 'value': x[0]} for x in cursor.fetchall()]
    cursor.execute('''
SELECT "name"
  FROM "organization";
''')
    organizations = [{'label': x[0], 'value': x[0]} for x in cursor.fetchall()]
    cursor.execute('''
SELECT "name"
  FROM "language";
''')
    languages = [{'label': x[0], 'value': x[0]} for x in cursor.fetchall()]
    projects_query = '''
    SELECT "p"."name",
           "p"."description",
           "p"."organization",
           "o"."type",
           "p"."language",
           "l"."color",
           "p"."starred",
           "p"."created"
      FROM "project"
        AS "p"
INNER JOIN "organization"
        AS "o"
        ON "p"."organization" = "o"."name"
INNER JOIN "language"
        AS "l"
        ON "p"."language" = "l"."name"
'''
    params = []
    if request.args.get('organization_type', 'all') != 'all':
        projects_query += ' AND "o"."type" = %s'
        params.append(request.args.get('organization_type', 'all'))
    if request.args.get('organization', 'all') != 'all':
        projects_query += ' AND "p"."organization" = %s'
        params.append(request.args.get('organization', 'all'))
    if request.args.get('language', 'all') != 'all':
        projects_query += ' AND "p"."language" = %s'
        params.append(request.args.get('language', 'all'))
    projects_query = projects_query.replace('AND', 'WHERE', 1) + ';'
    cursor.execute(projects_query, params)
    projects = cursor.fetchall()
    for i in range(len(projects)):
        projects[i] = {
            'name': projects[i][0],
            'description': projects[i][1],
            'organization': projects[i][2],
            'language': projects[i][4],
            'language_color': projects[i][5],
            'starred': '-o' * int(not projects[i][6]),
            'created': datetime.strftime(projects[i][7], '%Y-%m-%d')
        }
    conn.close()
    return render_template('projects/projects.html', organization_types=organization_types, organizations=organizations, languages=languages, projects=projects)


#@projects_blueprint.route('/projects/<string:project>/', methods=['GET'])
#@authenticate
#def get_project(project):
#    return project


@projects_blueprint.route('/projects/<string:project>/', methods=['GET'])
@authenticate
def post_star_project(project):
    if request.args.get('starred'):
        conn = psycopg2.connect(database=PROJECTS_DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()
        cursor.execute('''
UPDATE "project"
   SET "starred" = %s
 WHERE "name" = %s;
''', (request.args.get('starred'), project))
        conn.commit()
        conn.close()
    return 'Success!', 200


@projects_blueprint.route('/projects/create/', methods=['GET'])
@authenticate
def get_create_project():
    #conn = psycopg2.connect(database=PROJECTS_DB_NAME, user=DB_USER, password=DB_PASSWORD)
    #cursor = conn.cursor()
    name = 'Firestorm'
    description = 'Personal headless CentOS 8 server'
    date = datetime.now()
    current_date = date.strftime('%B %-d')
    current_date += 'th' if 4 <= date.day <= 20 or 24 <= date.day <= 30 else ['st', 'nd', 'rd'][date.day % 10 - 1]
    current_date += ', ' + date.strftime('%Y')
    os.makedirs(os.path.join(GIT_PATH, name))
    Popen(['git', 'init', '--bare', os.path.join(GIT_PATH, name, '.git')], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['git', '-C', os.path.join(GIT_PATH, name), 'config', 'core.bare', 'false'], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['git', '-C', os.path.join(GIT_PATH, name), 'apply', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(input='''diff --git a/.gitconfig b/.gitconfig
new file mode 100644
index 0000000..2483976
--- /dev/null
+++ b/.gitconfig
@@ -0,0 +1,2 @@
+.idea/
+__pycache__/
diff --git a/LICENSE b/LICENSE
new file mode 100644
index 0000000..5bd9575
--- /dev/null
+++ b/LICENSE
@@ -0,0 +1,13 @@
+License
+
+Copyright (c) {YEAR} Ashish D'Souza
+
+No permission whatsoever will be granted to any person to obtain a copy of this
+software and associated documentation files (the "Software"). The Software is
+at no point in time to be used, copied, modified, merged, published,
+distributed, sublicensed, and/or sold, except under the express direction by
+the author (Ashish D'Souza) or his successor in the event of the author's
+death.
+
+The above copyright notice and this permission notice shall be included in all
+copies or substantial portions of the Software.
diff --git a/README.md b/README.md
new file mode 100644
index 0000000..892ef3c
--- /dev/null
+++ b/README.md
@@ -0,0 +1,7 @@
+# {NAME}
+
+*{DATE}*
+
+---
+
+{DESCRIPTION}
'''.replace('{NAME}', name).replace('{DESCRIPTION}', description).replace('{DATE}', current_date).replace('{YEAR}', str(datetime.now().year)).encode())
    Popen(['git', '-C', os.path.join(GIT_PATH, name), 'add', '.'], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['git', '-C', os.path.join(GIT_PATH, name), 'commit', '-m', 'Initial commit'], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['git', '-C', os.path.join(GIT_PATH, name), 'config', 'core.bare', 'true'], stdout=PIPE, stderr=PIPE).communicate()
