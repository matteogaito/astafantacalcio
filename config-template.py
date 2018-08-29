import os
import logging
from logging.handlers import RotatingFileHandler
from app import app

BASEDIR = os.path.abspath(os.path.dirname(__file__))

ADSENSE_CLIENT = "ca-pub-xxxxxxxxxxx"

SECRET_KEY = os.environ.get('SECRET_KEY') or 'NzE0ZTk4MjA1'
DEBUG = True

# HTTP Request
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 " +
    "(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
}

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Logging into File
LOGFILE = BASEDIR + '/af.log'
formatter = logging.Formatter("%(asctime)s - [%(process)d] - %(levelname)s %(module)s: %(message)s")
handlerFile = RotatingFileHandler(LOGFILE, maxBytes=10000, backupCount=1)
handlerFile.setLevel(logging.INFO)
handlerFile.setFormatter(formatter)
# Logging to Console for dockerized application
handlerConsole = logging.StreamHandler()
handlerConsole.setFormatter(formatter)
# Set Log Level
app.logger.setLevel(logging.INFO)
# Add Log handler
app.logger.addHandler(handlerConsole)
app.logger.addHandler(handlerFile)

# Database configurations
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}

