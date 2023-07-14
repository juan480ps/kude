from flask import Flask
from flask_restful import Api

app = Flask(__name__)

app.config.from_pyfile('config.py')# se importa el archivo config.py que contiene la apikey de los ws

api_key = app.config.get('API_KEY')# se asigna a una variable la apikey contenida en el archivo config.py

api = Api(app)

from api.resources.kude import GetToken, Select, Logout, KnowMyToken# importaion de las clases para agregar como recursos. Se realiza en esta linea para evitar error de recursividad 

api.add_resource(GetToken, '/api/getlogin')
api.add_resource(Select, '/api/select')
api.add_resource(Logout, '/api/logout')
api.add_resource(KnowMyToken, '/api/mytoken')