import os
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=dotenv_path, override=True)

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
# Configure JSON formatting for better readability
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.json.sort_keys = False

db = SQLAlchemy(app)

from routes import *

if __name__ == "__main__":
    app.run(debug=True)
