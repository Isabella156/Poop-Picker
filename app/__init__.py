from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import logging
from logging.handlers import TimedRotatingFileHandler

app = Flask(__name__)

UPLOAD_FOLDER = 'app/static/uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'cairocoders-ednalan'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

db.create_all()

logging.basicConfig(level=logging.DEBUG)

handler = logging.FileHandler('flask.log')
handler.setLevel(logging.DEBUG)
logging_format = logging.Formatter('[%(asctime)s][%(filename)s-%(lineno)d][%(levelname)s][%(thread)d] - %(message)s')
handler.setFormatter(logging_format)
app.logger.addHandler(handler)

from app import user, models, pet, note
