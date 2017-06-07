import os
API_KEY = os.environ['API_KEY']
ERROR_REPORTS_CHAT = os.environ['TG_DEBUG_CHAT']
SQLALCHEMY_DATABASE_URI = os.environ['DB_URI']
CELERY_BROKER_URL = os.environ['CELERY_BACKEND']
CELERY_RESULT_BACKEND = os.environ['CELERY_BACKEND']
___basedir = os.path.abspath(os.path.dirname(__file__))