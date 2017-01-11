import os

DEBUG = True
SECRET_KEY = 'my precious'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
HOST = 'localhost'
PORT = int(os.environ.get('PORT', 5000))
GOOGLE_LOGIN_CLIENT_ID = '587685920544-gc9mn3euijkephv5buceqslf638rv3hq.apps.googleusercontent.com'
GOOGLE_LOGIN_CLIENT_SECRET = 'NVR3cU79x3XiYAf64z2Thp8-'
GOOGLE_LOGIN_REDIRECT_URI = 'http://localhost:5000/oauth2callback'
