#!/usr/bin/python3
# files_blueprint.py

import os
from pwd import getpwuid
from auth import authenticate
from datetime import datetime
from markdown import markdown
from errors_blueprint import *
from flask import Blueprint, request, safe_join, render_template, redirect, send_from_directory, session


files_blueprint = Blueprint('files_blueprint', __name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))


# Additional functions
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


def markdown_to_html(filename):
    with open(filename, "r") as file:
        content = file.read().replace("  ", "    ").replace("\\R", "\\mathbb{R}").replace("\\Q", "\\mathbb{Q}").replace("\\Z", "\\mathbb{Z}").replace("\\N", "\\mathbb{N}").replace("\\C", "\\mathbb{C}").replace("\\{", "\\\\{").replace("\\}", "\\\\}").replace("<", "&lt;").replace(">", "&gt;")
    while "\\begin{matrix}" in content:
        start = content.index("\\begin{matrix}")
        end = content.index("\\end{matrix}")
        table_data = "<tr>" + "</tr><tr>".join(["<td><div lang=\"latex\">" + "</div></td><td><div lang=\"latex\">".join(x.split("&")) + "</div></td>" for x in content[start + 14:end].split("\\\\")]) + "</tr>"
        content = content[:start + 14] + table_data + content[end:]
        content = content.replace("\\begin{matrix}", "</div><table>", 1).replace("\\end{matrix}", "</table><div lang=\"latex\">", 1)
    content = content.split("$")
    output = ""
    c = 0
    for i in range(len(content)):
        if i == len(content) - 1:
            output += content[i]
            break
        if not content[i].endswith("\\"):
            if c % 2 == 0:
                output += content[i] + "<div lang=\"latex\">"
            else:
                output += content[i] + "</div>"
            c += 1
        else:
            output += content[i][:-1] + "$"
    #content = output.split("|")
    #output = ""
    #for i in range(len(content)):
    #    if not content[i].endswith("\\"):
    #        output += ("<tr>" if content[i].count("\n") > 1 else "") + "<td>" + content[i] + "</td>"
    #    else:
    #        output += content[i][:-1] + "|"
    return markdown(output).replace("<code>", "<pre>").replace("</code>", "</pre>")


# Public files
@files_blueprint.route('/public/', methods=['GET'])
def get_public_files_root_index():
    return get_public_files_index('.')


@files_blueprint.route('/public/<path:path>', methods=['GET'])
def get_public_files_index(path):
    if not request.path.endswith('/'):
        return redirect(request.path + '/'), 302
    local_path = os.path.join(files_blueprint.static_folder, path)
    if not os.path.exists(local_path):
        return error_404(404)
    root, dirs, files = next(os.walk(local_path))
    items = []
    for item in sorted(dirs + files):
        if root == os.path.join(files_blueprint.static_folder, '.') and item == 'assets':
            continue
        items.append({})
        try:
            items[-1]['name'] = safe_join('/', 'static', path, item)
            items[-1]['name'] += '/' if item in dirs else ''
            items[-1]['size'] = os.path.getsize(os.path.join(root, item))
            items[-1]['modified'] = str(datetime.fromtimestamp(os.path.getmtime(os.path.join(root, item))).strftime('%Y-%m-%d %H:%M:%S'))
            items[-1]['owner'] = getpwuid(os.stat(os.path.join(root, item)).st_uid).pw_name
        except FileNotFoundError:
            items.pop(-1)
    if request.args.get('s') == 'A':
        items = sorted(items, key=lambda k: k['name'])
        items.reverse()
    elif request.args.get('s') == 's':
        items = sorted(items, key=lambda k: k['size'] if not k['name'].endswith('/') else 0)
    elif request.args.get('s') == 'S':
        items = sorted(items, key=lambda k: k['size'] if not k['name'].endswith('/') else 0)
        items.reverse()
    elif request.args.get('s') == 'm':
        items = sorted(items, key=lambda k: k['modified'])
    elif request.args.get('s') == 'M':
        items = sorted(items, key=lambda k: k['modified'])
        items.reverse()
    elif request.args.get('s') == 'o':
        items = sorted(items, key=lambda k: k['owner'])
    elif request.args.get('s') == 'O':
        items = sorted(items, key=lambda k: k['owner'])
        items.reverse()
    else:
        items = sorted(items, key=lambda k: k['name'])
    for i in range(len(items)):
        items[i]['size'] = get_size_string(items[i]['size'])
    path = '' if path == '.' else path
    return render_template('public_file_index.html', root=path, files=items), 200


# Private files
@files_blueprint.route('/files/', methods=['GET'])
def get_files_root_index():
    return get_files_index('.')


@files_blueprint.route('/files/<path:path>', methods=['GET'])
@authenticate
def get_files_index(path):
    local_path = os.path.join('/', path)
    path = '' if path == '.' else path
    if not os.path.exists(local_path):
        return error_404(404)
    if os.path.isfile(local_path):
        if os.path.splitext(local_path)[-1] == '.md':
            return render_template('markdown.html', markdown=markdown_to_html(local_path), title=os.path.basename(local_path)), 200
        return send_from_directory(os.path.dirname(local_path), filename=os.path.basename(local_path)), 200
    if not request.path.endswith('/'):
        return redirect(request.path + '/'), 302
    root, dirs, files = next(os.walk(local_path))
    items = []
    for item in sorted(dirs + files):
        items.append({})
        try:
            items[-1]['name'] = safe_join('/', path, item)
            items[-1]['name'] += '/' if item in dirs else ''
            items[-1]['size'] = os.path.getsize(os.path.join(root, item))
            items[-1]['modified'] = str(datetime.fromtimestamp(os.path.getmtime(os.path.join(root, item))).strftime('%Y-%m-%d %H:%M:%S'))
            items[-1]['owner'] = getpwuid(os.stat(os.path.join(root, item)).st_uid).pw_name
        except FileNotFoundError:
            items.pop(-1)
    if request.args.get('s') == 'A':
        items = sorted(items, key=lambda k: k['name'])
        items.reverse()
    elif request.args.get('s') == 's':
        items = sorted(items, key=lambda k: k['size'] if not k['name'].endswith('/') else 0)
    elif request.args.get('s') == 'S':
        items = sorted(items, key=lambda k: k['size'] if not k['name'].endswith('/') else 0)
        items.reverse()
    elif request.args.get('s') == 'm':
        items = sorted(items, key=lambda k: k['modified'])
    elif request.args.get('s') == 'M':
        items = sorted(items, key=lambda k: k['modified'])
        items.reverse()
    elif request.args.get('s') == 'o':
        items = sorted(items, key=lambda k: k['owner'])
    elif request.args.get('s') == 'O':
        items = sorted(items, key=lambda k: k['owner'])
        items.reverse()
    else:
        items = sorted(items, key=lambda k: k['name'])
    for i in range(len(items)):
        items[i]['size'] = get_size_string(items[i]['size'])
    return render_template('file_index.html', root=path, files=items), 200
