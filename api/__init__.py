import logging.config, yaml
from flask import Flask
from flask_restful import Api

logging_file = open('config/log/logging.yaml', 'r')
logging_data = yaml.safe_load(logging_file)
logging_file.close()
logging.config.dictConfig(logging_data)

app_config_file = open('config/app_config.yaml', 'r')
app_config_data = yaml.safe_load(app_config_file)
app_config_file.close()

API_KEY = app_config_data['API_KEY']
AMBIENTE_DB = app_config_data['AMBIENTE_DB']

app = Flask(__name__)
api = Api(app)

from api.resources.kude import GetToken, Select, Logout, KnowMyToken

api.add_resource(GetToken, '/api/getlogin')
api.add_resource(Select, '/api/select')
api.add_resource(Logout, '/api/logout')
api.add_resource(KnowMyToken, '/api/mytoken')