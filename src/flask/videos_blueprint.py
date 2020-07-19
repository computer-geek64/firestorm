#!/usr/bin/python3
# videos_blueprint.py

import os
import re
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import authenticate
from errors_blueprint import *
from subprocess import Popen, PIPE
from config import VIDEOS_LOCATION
from flask import Blueprint, render_template, Response, request, safe_join, send_from_directory


videos_blueprint = Blueprint('videos_blueprint', __name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'), static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'))


# Get video categories
@videos_blueprint.route('/videos/', methods=['GET'])
@authenticate
def get_video_categories():
    return render_template('videos/video_categories.html'), 200


# Get videos
@videos_blueprint.route('/videos/<string:category>/', methods=['GET'])
@authenticate
def get_videos(category):
    categories = {'movies': 'Movies', 'real': 'Real', 'scenes': 'Scenes', 'shows': 'TV Shows', 'tmp': 'Temp'}
    videos = [x.split(os.path.join(VIDEOS_LOCATION, category) + '/')[-1] for x in Popen(['find', os.path.join(VIDEOS_LOCATION, category), '-name', '*.mp4'], stdout=PIPE, stderr=PIPE).communicate()[0].decode().strip().split('\n')]
    videos = sorted([[x, os.path.basename(os.path.splitext(x)[0])] for x in videos])
    return render_template('videos/videos.html', category=categories[category], videos=videos), 200


# Get video
@videos_blueprint.route('/videos/<string:category>/<path:path>', methods=['GET'])
@authenticate
def get_video(category, path):
    if os.path.splitext(path)[-1] == '.mp4':
        local_path = os.path.join(VIDEOS_LOCATION, category, path)
        if not os.path.exists(local_path):
            return error_404(404)

        def get_chunk(byte1=None, byte2=None):
            file_size = os.stat(local_path).st_size
            start = 0
            length = 102400

            if byte1 < file_size:
                start = byte1
            if byte2:
                length = byte2 + 1 - byte1
            else:
                length = file_size - start

            with open(local_path, 'rb') as f:
                f.seek(start)
                chunk = f.read(length)
            return chunk, start, length, file_size

        range_header = request.headers.get('Range', None)
        byte1, byte2 = 0, None
        if range_header:
            match = re.search(r'(\d+)-(\d*)', range_header)
            groups = match.groups()

            if groups[0]:
                byte1 = int(groups[0])
            if groups[1]:
                byte2 = int(groups[1])

        chunk, start, length, file_size = get_chunk(byte1, byte2)
        return Response(chunk, 206, mimetype='video/mp4', content_type='video/mp4', direct_passthrough=True, headers={'Content-Range': 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size)})
    else:
        local_path = os.path.join(VIDEOS_LOCATION, category, path + '.mp4')
        if not os.path.exists(local_path):
            return error_404(404)
        subtitles = None
        if os.path.exists(os.path.join(VIDEOS_LOCATION, category, 'subtitles', os.path.splitext(path)[0] + ' Subtitles.vtt')):
            subtitles = safe_join('/videos', category, 'subtitles', path)
        return render_template('videos/video.html', video=safe_join('/videos', category, path + '.mp4'), subtitles=subtitles, name=os.path.basename(path)), 200


# Get subtitles
@videos_blueprint.route('/videos/<string:category>/subtitles/<path:path>', methods=['GET'])
@authenticate
def get_subtitles(category, path):
    local_path = os.path.join(VIDEOS_LOCATION, category, 'subtitles', os.path.splitext(path)[0] + ' Subtitles.vtt')
    if not os.path.exists(local_path):
        return error_404(404)
    directory, filename = os.path.split(local_path)
    return send_from_directory(directory, filename), 200
