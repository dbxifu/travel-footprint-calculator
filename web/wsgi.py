import os
import sys

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(ROOT_DIR)

from flaskr import create_app

app = create_app('flaskr.settings.ProductionConfig')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
