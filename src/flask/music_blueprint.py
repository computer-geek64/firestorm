#!/usr/bin/python3
# music_blueprint.py

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import youtube_dl
from auth import authenticate
from errors_blueprint import *
from config import MUSIC_LOCATION
from flask import Blueprint, render_template, safe_join, request, redirect, send_from_directory


music_blueprint = Blueprint('music_blueprint', __name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))


def get_youtube_music(url, directory):
    youtube_dl_options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3'
        }],
        'nocheckcertificate': True,
        'outtmpl': os.path.join(directory, '%(title)s.%(ext)s')
    }
    try:
        with youtube_dl.YoutubeDL(youtube_dl_options) as ydl:
            ydl.download([url])
            return True
    except:
        return False


@music_blueprint.route('/music/', methods=['GET'])
@authenticate
def get_music():
    music = []
    for root, dirs, files in os.walk(MUSIC_LOCATION):
        music += [{'path': safe_join('/music', 'src', root.split(MUSIC_LOCATION)[-1], file), 'name': os.path.basename(os.path.splitext(file)[0])} for file in files if file.endswith('.mp3')]
    return render_template('music/music.html', music=sorted(music, key=lambda k: k['name'])), 200


@music_blueprint.route('/music/', methods=['POST'])
@authenticate
def post_music():
    if request.form.get('url'):
        get_youtube_music(request.form.get('url'), os.path.join(MUSIC_LOCATION, 'download'))
    return redirect('/music/'), 302


@music_blueprint.route('/music/src/<path:path>/', methods=['GET'])
@authenticate
def get_music_source(path):
    local_path = os.path.join(MUSIC_LOCATION, path)
    if os.path.isfile(local_path):
        directory, filename = os.path.split(local_path)
        return send_from_directory(directory, filename)
    return error_404(404)
