import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server'))
from server import app as application
