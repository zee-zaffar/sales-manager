from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

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
