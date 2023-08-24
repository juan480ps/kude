############################################### get_token ############################################### 
import requests, base64, datetime as dt, sys, logging, json
from flask import request
from flask_restful import Resource
from lib import validate
from api import API_KEY, BASE_URL_POOL, AUTH_USER, AUTH_PASS, BASE_URL_AUTH, APP_CONTEXT
from utils.format_json import set_format_json

api_key_auth = {"apikey" : API_KEY} 

#variables
token = ''
#ambiente = 'testdta'
momento = ''#dt.datetime.fromtimestamp(1688410986) - dt.timedelta(days=20*365)
vencimiento_token = ''#dt.datetime.fromtimestamp(1688410986) - dt.timedelta(days=20*365)
token_is_expired = False
session_closed = False
api_key_pool = ''

class GetToken(Resource):        
    def check_session(self):
        global token_is_expired, token, vencimiento_token
        objectJson = validate.check_my_token()
        codigo = objectJson[0]['codigo']
        descripcion = objectJson[0]['descripcion']
        vencimiento_token = objectJson[3]
        token_is_expired = objectJson[4]
        token = objectJson[1]
        
        vencimiento_token = vencimiento_token.strftime("%d/%m/%Y, %H:%M:%S")
        
        objetoJson = {
            "token" : token,
            "vencimiento_token" : vencimiento_token
        }
        # self.token = token
        # self.momento = momento
        # self.vencimiento_token = vencimiento_token
        # self.token_is_expired = hola[4]
        # self.session_closed = session_closed
        respuesta = {'codigo': codigo, 'descripcion': descripcion, 'objetoJson' : objetoJson, 'arrayJson' : []}        
        logging.info('@REQUEST GET ' + request.full_path + ' @RESPONSE ' + json.dumps(respuesta))
        return respuesta
    
    def get(self, ambiente):
        return {'Utilizar': 'metodo POST '+  ambiente}
    
    def post(self, ambiente):
        global token, momento, vencimiento_token, token_is_expired, session_closed # se sobreescriben los valores de las variables de la aplicacion
        
        credentials_auth = {"username": AUTH_USER, "password" : AUTH_PASS, "apikey" : API_KEY,  "authcontext" : APP_CONTEXT}
        credentials_auth = set_format_json(credentials_auth, 'get_token') #formateael json con el estandard del jdewsring01
        
        logging.debug("GetToken")
        try:
            logging.debug("HTTP REQUEST HEADERS: " + str(request.headers))
            logging.debug("HTTP REQUEST DATA: " + str(request.data))
            if request.is_json:
                data = request.get_json()
                logging.info('@REQUEST POST ' + json.dumps(data))
                operation = credentials_auth['operation']
                params = credentials_auth['params']
                if operation == "get_token":
                    respuesta = validate.validator(request, token, session_closed, api_key_auth, APP_CONTEXT)
                    token = respuesta[1]
                    momento = respuesta[2]
                    vencimiento_token = respuesta[3]
                    token_is_expired = respuesta[4]
                    session_closed = respuesta[5]
                    try: #se mete dentro de un try porque da problemas al convertir respuesta con cookies en json
                        logging.info('@REQUEST GET ' + request.full_path + ' @RESPONSE ' + json.dumps(respuesta[0]))
                    except Exception as e:
                        logging.info('@REQUEST GET ' + request.full_path + ' @RESPONSE ' + str(respuesta[0].response))
                    return respuesta[0]
                else:
                    descripcion = 'Operación inválida'
                    codigo = -1002
                    logging.error("Peticion finalizada con error: " + descripcion + " " + str(codigo), exc_info = True)
            else:
                descripcion = 'Json necesario para ingresar'
                codigo = -1002
                logging.error("Peticion finalizada con error: " + descripcion + " " + str(codigo), exc_info = True)
        except KeyError as e :
            descripcion = 'No se encuentra el parametro: ' + str(e)
            codigo = -1001
            logging.debug(e)
            logging.error("Peticion finalizada con error: " + descripcion + " " + str(codigo), exc_info = True)
        except Exception as e:
            descripcion = str(e)
            codigo = -1000
            logging.debug(e)
            logging.error("Peticion finalizada con error: " + descripcion + " " + str(codigo), exc_info = True)
        respuesta = {'codigo': codigo, 'descripcion': descripcion,'objetoJson' : {}, 'arrayJson' : []}        
        logging.info('@REQUEST GET ' + request.full_path + ' @RESPONSE ' + json.dumps(respuesta))
        return respuesta