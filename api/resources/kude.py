from flask_restful import Resource
from flask import request
from api import api_key
import requests, base64, datetime as dt, sys 

sys.path.append('/opt/flask/')
sys.argv.append("cliente_")#nombre de la bd 

from validator import validate 

APP_CONTEXT = "APP_CONTRI"

# url_jde = 'http://localhost:5000/api/jdedb'

url_jde = 'http://192.168.150.156:6000/api/jdedb'

db = "cliente_"

api_key_auth = {"apikey" : api_key}
token = ''
ambiente = 'testdta'
cookie = ''
momento = dt.datetime.fromtimestamp(1688410986) - dt.timedelta(days=20*365)
vencimiento_token = dt.datetime.fromtimestamp(1688410986) - dt.timedelta(days=20*365)
token_is_expired = False
session_closed = False
api_key_pool = ''

class GetToken(Resource):
    def post(self):
        global cookie, token, momento, vencimiento_token, token_is_expired, session_closed
        try:
            if request.is_json:
                data = request.get_json()
                operation = data['operation']
                params = data['params']
                if operation == "get_token":
                    respuesta = validate.validator(request, token, session_closed, api_key_auth, APP_CONTEXT)
                    token = respuesta[2]
                    momento = respuesta[3]
                    vencimiento_token = respuesta[4]
                    token_is_expired = respuesta[5]
                    session_closed = respuesta[6]
                    return respuesta[0]
                else:
                    descripcion = 'Operación inválida'
                    codigo = -1002
            else:
                descripcion = 'Json necesario para ingresar'
                codigo = -1002
        except KeyError as e :
            descripcion = 'No se encuentra el parametro: ' + str(e)
            codigo = -1001
        except Exception as e:
            descripcion = str(e)
            codigo = -1000
        respuesta = {'codigo': codigo, 'descripcion': descripcion,'objetoJson' : {}, 'arrayJson' : []}
        return respuesta

class Select(Resource):
    def post(self):
        global token, momento, vencimiento_token, api_key_pool, api_key_auth
        try:
            if request.is_json:
                data = request.get_json()
                operation = data['operation']
                params = data['params']
                if operation == "get_email":
                    res = validate.oper_validator(request, token, cookie, api_key_auth, vencimiento_token, data, ambiente)
                    codigo = res['codigo']
                    descripcion = res['descripcion']
                    
                    if codigo == 1000:
                        arrayJson = res['arrayJson']
                        api_key_pool = arrayJson['apikey']
                        data = request.get_json()
                        if api_key_pool:
                            respuesta = send_query_select(data, token, api_key_pool)
                            return respuesta
                        else:
                            descripcion = 'Hubo un problema al recuperar la Api-Key'
                            codigo = -1000
                else:
                    descripcion = 'Operación inválida'
                    codigo = -1002
            else:
                descripcion = 'Json necesario para ingresar'
                codigo = -1002
        except KeyError as e :
            descripcion = 'No se encuentra el parametro: ' + str(e)
            codigo = -1001
        except Exception as e:
            descripcion = str(e)
            codigo = -1000
        respuesta = {'codigo': codigo, 'descripcion': descripcion, 'objetoJson' : {}, 'arrayJson': [] }
        return respuesta

class Logout(Resource):
    def post(self):
        global cookie, token, session_closed
        
        respuesta = validate.logout(token)
        codigo = respuesta['codigo']
        descripcion = respuesta['descripcion']   
        
        respuesta = {'codigo': codigo, 'descripcion': descripcion, 'objetoJson' : {}, 'arrayJson' : []}
        return respuesta

class KnowMyToken(Resource):
    def post(self):
        global cookie, token, momento, vencimiento_token, token_is_expired
        arrayJson = []
        objetoJson = {}
        val = validate.check_my_token()
        codigo = val[0]['codigo']
        descripcion = val[0]['descripcion']
        if codigo == 1000:
            token = val[2]
            momento = val[3].strftime('%m/%d/%Y %H:%M:%S')
            vencimiento_token = val[4].strftime('%m/%d/%Y %H:%M:%S')
            arrayJson = {
                            "token" : token,
                            "momento" : momento,
                            "vencimiento" : vencimiento_token
                        }
        respuesta = {'codigo': codigo, 'descripcion': descripcion, 'objetoJson' : objetoJson, 'arrayJson' : arrayJson}
        return respuesta

def send_query_select(data, token, api_key_pool):
    try:
        objetoJson = {}
        arrayJson = []
        operation = data['operation']
        params = data['params']
        ruc = params['ruc']
        query = f"""
                    SELECT trim(EAEMAL) email
                    FROM {ambiente}.F0101, TESTDTA.F01151
                    WHERE ABAN8 = EAAN8
                    AND EAETP = 'E'
                    AND trim(ABTAX) = '{ruc}'
                """
        encoded_query = base64.b64encode(query.encode("utf-8")).decode("utf-8")
        body = {
                "operation": "select",
                "params" : {
                            "apikey" : api_key_pool,
                            "token" : token,
                            "query": encoded_query
                            }
                }
        pool_res = requests.post(url_jde, json = body)
        data = pool_res.json()
        codigo = data['codigo']
        descripcion = data['descripcion']
        arrayJson = data['arrayJson']
    except KeyError as e :
        codigo = -1001
        descripcion = 'No se encuentra el parametro: ' + str(e)
    except Exception as e:
        codigo = -1000
        descripcion = str(e)
    respuesta =  {'codigo': codigo, 'descripcion': descripcion, 'objetoJson': objetoJson, 'arrayJson': arrayJson}
    return respuesta