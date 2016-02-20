from datetime import date

from flask import Flask
from flask.json import JSONEncoder as _JSONEncoder

# from .jsonapi import jsonapi
from .models import db


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()
        return JSONEncoder.default(self, o)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/jsonapi'
app.debug = True
app.json_encoder = JSONEncoder
db.init_app(app)

# jsonapi.init_app(app)
