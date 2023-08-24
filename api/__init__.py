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
APP_CONTEXT = app_config_data['APP_CONTEXT']

BASE_URL_POOL = app_config_data['BASE_URL_POOL']
BASE_URL_AUTH = app_config_data['BASE_URL_AUTH']
URL_AUTH_GET_API = app_config_data['URL_AUTH_GET_API']
AUTH_USER = app_config_data['AUTH_USER']
AUTH_PASS = app_config_data['AUTH_PASS']
BY_PASS_AUTH = app_config_data['BY_PASS_AUTH']

DEFAULT_PAGE_SIZE = app_config_data['DEFAULT_PAGE_SIZE']
DEFAULT_PAGE_NUMBER = app_config_data['DEFAULT_PAGE_NUMBER']

app = Flask(__name__)
api = Api(app)

from api.resources.kude import GetToken, GetMailByRuc, Logout, KnowMyToken

api.add_resource(GetToken, '/api/getlogin')
api.add_resource(GetMailByRuc, '/api/getmailbyruc')
api.add_resource(Logout, '/api/logout')
api.add_resource(KnowMyToken, '/api/mytoken')