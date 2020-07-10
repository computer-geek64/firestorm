#!/usr/bin/python3
# errors_blueprint.py

import os
from flask import Blueprint, render_template


errors_blueprint = Blueprint('errors_blueprint', __name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))


# Error handlers
@errors_blueprint.errorhandler(404)
def error_404(e):
    return render_template("error_templates/404.html"), 404


@errors_blueprint.errorhandler(400)
def error_400(e):
    return "HTTP 400 - Bad Request", 400


@errors_blueprint.errorhandler(500)
def error_500(e):
    return render_template("error_templates/500.html"), 500


@errors_blueprint.errorhandler(403)
def error_403(e):
    return render_template("error_templates/403.html"), 403


@errors_blueprint.errorhandler(401)
def error_401(e):
    return render_template("error_templates/401.html")
