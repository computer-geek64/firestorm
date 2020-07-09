#!/usr/bin/python3
# server.py

import os
from pwd import getpwuid
from datetime import datetime
from subprocess import Popen, PIPE
from flask import Flask, jsonify, redirect, request, render_template, send_file, session, safe_join


app = Flask(__name__, template_folder='templates')


# Additional functions
def get_size_string(size):
    units = ["B", "KB", "MB", "GB", "TB"]
    length = len(str(size))
    if length % 3 == 0:
        number = str(size)[:(length % 3) + 3]
        unit = units[int(length / 3) - 1]
    else:
        number = str(size)[:length % 3]
        unit = units[int(length / 3)]
    return number + " " + unit


# Home
@app.route('/', methods=['GET'])
def get_home():
    return 'Welcome to Firestorm!', 200


# Public files
@app.route('/public/', methods=['GET'])
def get_public_files_root_index():
    return get_public_files_index('.')


@app.route('/public/<path:path>', methods=['GET'])
def get_public_files_index(path):
    if not request.path.endswith('/'):
        return redirect(request.path + '/'), 302
    local_path = os.path.join(app.static_folder, path)
    if not os.path.exists(local_path):
        #return error_404(404)
        return '404'
    root, dirs, files = next(os.walk(local_path))
    items = []
    for item in sorted(dirs + files):
        if root == os.path.join(app.static_folder, '.') and item == 'assets':
            continue
        items.append({})
        items[-1]['name'] = safe_join('/', 'static', path, item)
        items[-1]['name'] += '/' if item in dirs else ''
        items[-1]['size'] = os.path.getsize(os.path.join(root, item))
        items[-1]['modified'] = str(datetime.fromtimestamp(os.path.getmtime(os.path.join(root, item))).strftime('%Y-%m-%d %H:%M:%S'))
        items[-1]['owner'] = getpwuid(os.stat(os.path.join(root, item)).st_uid).pw_name
    if 's' in request.args and request.args['s'] == 'A':
        items = sorted(items, key=lambda k: k['name'])
        items.reverse()
    elif 's' in request.args and request.args['s'] == 's':
        items = sorted(items, key=lambda k: k['size'] if not k['name'].endswith('/') else 0)
    elif 's' in request.args and request.args['s'] == 'S':
        items = sorted(items, key=lambda k: k['size'] if not k['name'].endswith('/') else 0)
        items.reverse()
    elif 's' in request.args and request.args['s'] == 'm':
        items = sorted(items, key=lambda k: k['modified'])
    elif 's' in request.args and request.args['s'] == 'M':
        items = sorted(items, key=lambda k: k['modified'])
        items.reverse()
    elif 's' in request.args and request.args['s'] == 'o':
        items = sorted(items, key=lambda k: k['owner'])
    elif 's' in request.args and request.args['s'] == 'O':
        items = sorted(items, key=lambda k: k['owner'])
        items.reverse()
    else:
        items = sorted(items, key=lambda k: k['name'])
    for i in range(len(items)):
        items[i]['size'] = get_size_string(items[i]['size'])
    path = '' if path == '.' else path
    return render_template('public_file_index.html', root=path, files=items)


if __name__ == '__main__':
    app.run('0.0.0.0', 81)
