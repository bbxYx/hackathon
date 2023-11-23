from flask import Flask
import os
from flask import current_app as app

app = Flask(__name__)
app.run(debug=True)

from hangle.hangle import hangle_bs as hangle
from ocr.ocr import trans_ocr as ocr

app.register_blueprint(hangle)
app.register_blueprint(ocr)

RESULT_FOLDER = os.path.join('static')
app.config['RESULT_FOLDER'] = RESULT_FOLDER