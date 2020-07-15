#!/usr/bin/python3
# projects_blueprint.py

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shutil
import psycopg2
from datetime import datetime
from auth import authenticate
from errors_blueprint import *
from subprocess import Popen, PIPE
from config import PROJECTS_DB_NAME, DB_USER, DB_PASSWORD, GIT_PATH, GIT_USER_NAME, GIT_USER_EMAIL
from flask import Blueprint, render_template, request, redirect, jsonify


projects_blueprint = Blueprint('projects_blueprint', __name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))


# Additional functions
def snake_case_to_title(s):
    return ' '.join([x.capitalize() if x not in ['of', 'as', 'the'] else x for x in s.split('_')])


def get_size_string(size):
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    length = len(str(size))
    if length % 3 == 0:
        number = str(size)[:(length % 3) + 3]
        unit = units[int(length / 3) - 1]
    else:
        number = str(size)[:length % 3]
        unit = units[int(length / 3)]
    return number + ' ' + unit


def generate_post_receive(project):
    return '''#!/usr/bin/python3
import os
import sys
sys.path.append('{CONFIG_FILE_PATH}')
import shutil
import psycopg2
from subprocess import Popen, PIPE
from config import GIT_PATH, PROJECTS_DB_NAME, DB_USER, DB_PASSWORD


project = '{project}'
Popen(['git', 'clone', os.path.join(GIT_PATH, project + '.git'), os.path.join(GIT_PATH, project)], stdout=PIPE, stderr=PIPE).communicate()
conn = psycopg2.connect(database=PROJECTS_DB_NAME, user=DB_USER, password=DB_PASSWORD)
cursor = conn.cursor()
cursor.execute(\'\'\'
DELETE FROM "project_language"
      WHERE "project" = %s;
\'\'\', (project,))
conn.commit()
cursor.execute(\'\'\'
SELECT "name",
       "extension"
  FROM "language";
\'\'\')
languages = {{language[1]: language[0] for language in cursor.fetchall()}}
project_languages = {{}}
total_size = 0
for root, dirs, files in os.walk(os.path.join(GIT_PATH, project)):
    if root == os.path.join(GIT_PATH, project):
        dirs[:] = [x for x in dirs if x != '.git']
    for file in files:
        ext = os.path.splitext(file)[-1][1:]
        if languages.get(ext):
            if not project_languages.get(languages.get(ext)):
                project_languages[languages.get(ext)] = {{'size': 0, 'files': 0, 'lines': 0}}
            size = os.path.getsize(os.path.join(root, file))
            project_languages[languages.get(ext)]['size'] += size
            project_languages[languages.get(ext)]['files'] += 1
            with open(os.path.join(root, file), 'r') as f:
                project_languages[languages.get(ext)]['lines'] += sum(1 for x in f)
            total_size += size
params = []
primary_language = None
max_percentage = 0
for k in project_languages.keys():
    project_languages[k]['percentage'] = project_languages[k]['size'] / total_size
    params += [project, k, project_languages[k]['percentage'], project_languages[k]['size'], project_languages[k]['files'], project_languages[k]['lines']]
    if project_languages[k]['percentage'] > max_percentage:
        primary_language = k
        max_percentage = project_languages[k]['percentage']
if project_languages:
    cursor.execute(\'\'\'
INSERT INTO "project_language"
            (
                "project",
                "language",
                "percentage",
                "size",
                "files",
                "lines"
            )
     VALUES
\'\'\' + ', '.join(['(%s, %s, %s, %s, %s, %s)'] * len(project_languages)) + ';', params)
        cursor.execute(\'\'\'
UPDATE "project"
   SET "language" = %s
 WHERE "name" = %s;
\'\'\', (primary_language, project))
    conn.commit()
conn.close()
shutil.rmtree(os.path.join(GIT_PATH, project))
'''.format(project=project, CONFIG_FILE_PATH=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Projects
# Get projects listing
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
           "p"."archived",
           "p"."created"
      FROM "project"
        AS "p"
INNER JOIN "organization"
        AS "o"
        ON "p"."organization" = "o"."name"
LEFT JOIN "language"
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
    projects_query = projects_query.replace('AND', 'WHERE', 1) + ' ORDER BY "p"."starred" DESC, "p"."name" ASC;'
    cursor.execute(projects_query, params)
    projects = []
    for project in cursor.fetchall():
        if request.args.get('search') and request.args.get('search').lower() not in project[0].lower() and request.args.get('search').lower() not in project[1].lower():
            continue
        projects.append({
            'name': project[0],
            'description': project[1],
            'organization': project[2],
            'language': project[4],
            'language_color': project[5],
            'starred': '-o' * int(not project[6]),
            'archived': project[7],
            'created': datetime.strftime(project[8], '%Y-%m-%d')
        })
    conn.close()
    return render_template('projects/projects.html', organization_types=organization_types, organizations=organizations, languages=languages, projects=projects), 200


# Get project
@projects_blueprint.route('/projects/<string:project>/', methods=['GET'])
@authenticate
def get_project(project):
    conn = psycopg2.connect(database=PROJECTS_DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    cursor.execute('''
SELECT "description",
       "organization",
       "starred",
       "archived",
       "created"
  FROM "project"
 WHERE "name" = %s;
''', (project,))
    query_results = cursor.fetchall()
    if not query_results:
        return error_404(404)
    description, organization, starred, archived, created = query_results[0]
    cursor.execute('''
    SELECT "pl"."language",
           "pl"."percentage",
           "pl"."size",
           "pl"."files",
           "pl"."lines",
           "l"."extension",
           "l"."color"
      FROM "project_language"
        AS "pl"
INNER JOIN "language"
        AS "l"
        ON "pl"."language" = "l"."name"
     WHERE "pl"."project" = %s;
''', (project,))
    languages = [{'name': language[0], 'percentage': round(language[1] * 100, 1), 'size': get_size_string(language[2]), 'files': language[3], 'lines': language[4], 'extension': language[5], 'color': language[6]} for language in cursor.fetchall()]
    conn.close()
    default_branch = 'master'
    branches = Popen(['git', '-C', os.path.join(GIT_PATH, project + '.git'), 'branch'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().rstrip().split('\n')
    for i in range(len(branches)):
        if branches[i].startswith('*'):
            default_branch = branches[i][2:]
        branches[i] = {'name': branches[i][2:], 'default': branches[i].startswith('*')}
    for i in range(len(branches)):
        behind, ahead = [x for x in Popen(['git', '-C', os.path.join(GIT_PATH, project + '.git'), 'rev-list', '--left-right', '--count', default_branch + '...' + branches[i]['name']], stdout=PIPE, stderr=PIPE).communicate()[0].decode().strip().replace('\t', ' ').split(' ') if x]
        branches[i]['name'] = branches[i]['name'].ljust(15).replace(' ', '&nbsp;') + (behind + '|').rjust(5).replace(' ', '&nbsp;') + ahead
    git_log = Popen(['git', '-C', os.path.join(GIT_PATH, project + '.git'), 'log', '--oneline', '--graph', '--decorate', '--all', '-500'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().replace('\n', '<br>')
    return render_template('projects/project.html', name=project, description=description, organization=organization, starred=starred, archived=archived, created=created, branches=branches, languages=languages, git_log=git_log), 200


# Post project
@projects_blueprint.route('/projects/<string:project>/', methods=['POST'])
@authenticate
def post_project(project):
    conn = psycopg2.connect(database=PROJECTS_DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()

    if request.form.get('delete'):
        cursor.execute('''
DELETE FROM "project"
      WHERE "name" = %s;
''', (project,))
        conn.commit()
        conn.close()
        shutil.rmtree(os.path.join(GIT_PATH, project + '.git'))
        return redirect('/projects/'), 302
    if request.form.get('name'):
        cursor.execute('''
UPDATE "project"
   SET "name" = %s
 WHERE "name" = %s;
''', (request.form.get('name'), project))
        os.rename(os.path.join(GIT_PATH, project + '.git'), os.path.join(GIT_PATH, request.form.get('name') + '.git'))
        project = request.form.get('name')
    if request.form.get('description'):
        cursor.execute('''
UPDATE "project"
   SET "description" = %s
 WHERE "name" = %s;
''', (request.form.get('description'), project))
    if request.form.get('starred'):
        cursor.execute('''
UPDATE "project"
   SET "starred" = %s
 WHERE "name" = %s;
''', (request.form.get('starred'), project))

    if request.form.get('archived'):
        cursor.execute('''
UPDATE "project"
   SET "archived" = %s
 WHERE "name" = %s;
''', (request.form.get('archived'), project))
        if request.form.get('archived') == 'true':
            os.chmod(os.path.join(GIT_PATH, project + '.git'), 0o555)
        else:
            os.chmod(os.path.join(GIT_PATH, project + '.git'), 0o775)
    conn.commit()
    conn.close()
    return redirect(os.path.join('/projects', project + '/')), 302


@projects_blueprint.route('/projects/create/', methods=['GET'])
@authenticate
def get_create_project():
    conn = psycopg2.connect(database=PROJECTS_DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    cursor.execute('''
SELECT "name"
  FROM "organization";
''')
    organizations = [x[0] for x in cursor.fetchall()]
    return render_template('projects/create.html', organizations=organizations), 200


# Post create project
@projects_blueprint.route('/projects/create/', methods=['POST'])
@authenticate
def post_create_project():
    if not request.form.get('name') or not request.form.get('description') or not request.form.get('organization'):
        return redirect('/projects/create/'), 302
    name = request.form.get('name')
    description = request.form.get('description')
    organization = request.form.get('organization')
    conn = psycopg2.connect(database=PROJECTS_DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    cursor.execute('''
INSERT INTO "project"
            (
                "name",
                "description",
                "organization"
            )
     VALUES (
                %s,
                %s,
                %s
            );
''', (name, description, organization))
    conn.commit()
    conn.close()

    date = datetime.now()
    current_date = date.strftime('%B %-d')
    current_date += 'th' if 4 <= date.day <= 20 or 24 <= date.day <= 30 else ['st', 'nd', 'rd'][date.day % 10 - 1]
    current_date += ', ' + date.strftime('%Y')
    os.makedirs(os.path.join(GIT_PATH, name + '.git'))
    Popen(['git', 'init', '--bare', os.path.join(GIT_PATH, name + '.git', '.git')], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['git', '-C', os.path.join(GIT_PATH, name + '.git'), 'config', 'user.name', GIT_USER_NAME], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['git', '-C', os.path.join(GIT_PATH, name + '.git'), 'config', 'user.email', GIT_USER_EMAIL], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['git', '-C', os.path.join(GIT_PATH, name + '.git'), 'config', 'core.bare', 'false'], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['git', '-C', os.path.join(GIT_PATH, name + '.git'), 'apply', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(input='''diff --git a/.gitconfig b/.gitconfig
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
    Popen(['git', '-C', os.path.join(GIT_PATH, name + '.git'), 'add', '.'], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['git', '-C', os.path.join(GIT_PATH, name + '.git'), 'commit', '-m', 'Initial commit'], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['git', '-C', os.path.join(GIT_PATH, name + '.git'), 'config', 'core.bare', 'true'], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['git', '-C', os.path.join(GIT_PATH, name + '.git'), 'branch', 'develop'], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['git', '-C', os.path.join(GIT_PATH, name + '.git'), 'branch', 'stable'], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['git', '-C', os.path.join(GIT_PATH, name + '.git'), 'branch', 'hotfix'], stdout=PIPE, stderr=PIPE).communicate()

    root, dirs, files = next(os.walk(os.path.join(GIT_PATH, name + '.git')))
    dirs.remove('.git')
    for dir in dirs:
        shutil.rmtree(os.path.join(root, dir))
    for file in files:
        os.remove(os.path.join(root, file))

    root, dirs, files = next(os.walk(os.path.join(GIT_PATH, name + '.git', '.git')))
    for file in dirs + files:
        shutil.move(os.path.join(root, file), os.path.join(GIT_PATH, name + '.git'))
    os.rmdir(os.path.join(GIT_PATH, name + '.git', '.git'))
    with open(os.path.join(GIT_PATH, name + '.git', 'hooks', 'post-receive'), 'w') as f:
        f.write(generate_post_receive(name))
    Popen(['chmod', '-R', '775', os.path.join(GIT_PATH, name + '.git')], stdout=PIPE, stderr=PIPE).communicate()
    Popen(['chown', '-R', 'git:git', os.path.join(GIT_PATH, name + '.git')], stdout=PIPE, stderr=PIPE).communicate()
    return redirect('/projects/' + name + '/'), 302
