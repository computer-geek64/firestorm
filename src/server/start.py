#!/usr/bin/python3
# start.py

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from config import USB_KEY_UUID, IFTTT_WEBHOOK
from subprocess import Popen, PIPE


if os.path.exists(os.path.join('/dev/disk/by-uuid', USB_KEY_UUID)):
    Popen(['/usr/bin/umount', os.path.join('/dev/disk/by-uuid', USB_KEY_UUID)], stdout=PIPE, stderr=PIPE).communicate()
    requests.post(IFTTT_WEBHOOK, json={'value1': 'Unplug USB Key', 'value2': 'Firestorm has unlocked all drives successfully.'})
