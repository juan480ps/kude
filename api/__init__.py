from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

app = Flask(__name__)

app.config.from_pyfile('config.py')

api_key = app.config.get('API_KEY')

api = Api(app)

jwt = JWTManager(app)

from api.resources.kude import GetToken, Select, Logout, KnowMyToken

api.add_resource(GetToken, '/api/getlogin')
api.add_resource(Select, '/api/select')
api.add_resource(Logout, '/api/logout')
api.add_resource(KnowMyToken, '/api/mytoken')