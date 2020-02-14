import logging
import sys
import os
PROJECT_ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
#sys.path.append(PROJECT_ROOT_DIR)
sys.path.insert(0, PROJECT_ROOT_DIR)
logging.basicConfig(stream=sys.stderr)
from main import app as application


