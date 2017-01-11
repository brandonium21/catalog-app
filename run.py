'''
from app import app


if __name__ == '__main__':
    app.run(debug=True)
'''
import logging

from flask import Flask, request as req
from app.controllers import pages
from flask_sqlalchemy import SQLAlchemy



from flask_googlelogin import GoogleLogin


app = Flask(__name__)
app.config.from_object('config.development')

app.register_blueprint(pages.blueprint)


googlelogin = GoogleLogin(app)
db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(debug=True)