import psycopg2
from datetime import datetime
from subprocess import Popen, PIPE
from config import PROJECTS_DB_NAME, DB_USER, DB_PASSWORD, GIT_PATH
from flask import Blueprint, render_template, request, session, jsonify
# Additional functions
def snake_case_to_title(s):
    return [' '.join([x.capitalize() if x not in ['of', 'as', 'the'] else x for x in s.split('_')])]


    conn = psycopg2.connect(database=PROJECTS_DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    cursor.execute('''
SELECT "label"
  FROM "organization_type";
''')
    organization_types = cursor.fetchall()
    organization_types = [{'label': snake_case_to_title(x[0]), 'value': x[0]} for x in organization_types]
    conn.close()
    return render_template('projects/projects.html', organization_types=organization_types)


@projects_blueprint.route('/projects/create', methods=['GET'])
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