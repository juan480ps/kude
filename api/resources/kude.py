from flask_restful import Resource
from flask import request
from api import API_KEY, AMBIENTE_DB, APP_CONTEXT
import requests, base64, datetime as dt, sys, logging, json

sys.path.append('/opt/flask/')# se coloca la ruta para porder importar el validador
sys.argv.append("cliente_")# nombre de la bd del ws para obtener datos del token

from validator import validate # se importa la libreria validador que se encarga de validar el token y la sesion 

 # se asigna el nombre de la aplicacion o ws. Este campo debe estar mapeado con el usuario para poder autenticarse

url_jde = 'http://localhost:5000/api/jdedb'
# url_jde = 'http://192.168.150.156:6000/api/jdedb' #url del pool

api_key_auth = {"apikey" : API_KEY} # diccionario que contiene la apikei del auth

#variables
token = ''
#ambiente = 'testdta'
momento = dt.datetime.fromtimestamp(1688410986) - dt.timedelta(days=20*365)
vencimiento_token = dt.datetime.fromtimestamp(1688410986) - dt.timedelta(days=20*365)
token_is_expired = False
session_closed = False
api_key_pool = ''

# Esta clase se encarga de obtener el token de sesion. Recibe el json con un formato especifico que debe contener el usuario y la contraseña para poder autenticarse. Este Json
# se envia al autenticador. Este trabajo lo hace el validador mediante la funcion validator(). Esta funcion recibe ciertos parametros para poder funcionar.
class GetToken(Resource):
    def post(self):
        global token, momento, vencimiento_token, token_is_expired, session_closed # se sobreescriben los valores de las variables de la aplicacion
        logging.debug("GetToken")
        try:
            logging.debug("HTTP REQUEST HEADERS: " + str(request.headers))
            logging.debug("HTTP REQUEST DATA: " + str(request.data))
            if request.is_json:
                data = request.get_json()
                logging.info('@REQUEST POST ' + json.dumps(data))
                operation = data['operation']
                params = data['params']
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
            else:
                descripcion = 'Json necesario para ingresar'
                codigo = -1002
        except KeyError as e :
            logging.debug(e)
            logging.error("Peticion finalizada con error", exc_info = True)
            descripcion = 'No se encuentra el parametro: ' + str(e)
            codigo = -1001
        except Exception as e:
            logging.debug(e)
            logging.error("Peticion finalizada con error", exc_info = True)
            descripcion = str(e)
            codigo = -1000
        respuesta = {'codigo': codigo, 'descripcion': descripcion,'objetoJson' : {}, 'arrayJson' : []}        
        logging.info('@REQUEST GET ' + request.full_path + ' @RESPONSE ' + json.dumps(respuesta))
        return respuesta

# Esta clase se encarga de enviar una consulta al jde y el resultado se muestra en json. Recibe el json con un formato especifico que debe contener el la operacion y el campo a consultar. Este Json
# se envia al pooljde si es que ya se cuenta con una sesion activa, que antes de ser enviado la solicitud, se realiza una validacion de la sesion. 
# Este trabajo lo hace el validador mediante la funcion oper_validator(). Esta funcion recibe ciertos parametros para poder funcionar.
class Select(Resource):
    def post(self):
        global token, momento, vencimiento_token, api_key_pool, api_key_auth# se sobreescriben los valores de las variables de la aplicacion
        logging.debug("/Select")
        try:
            logging.debug("HTTP REQUEST HEADERS: " + str(request.headers))
            logging.debug("HTTP REQUEST DATA: " + str(request.data))
            if request.is_json:
                data = request.get_json()
                logging.info('@REQUEST POST ' + json.dumps(data))
                operation = data['operation']
                params = data['params']
                if operation == "get_email":
                    res = validate.oper_validator(request, token, api_key_auth, vencimiento_token, data, AMBIENTE_DB)
                    codigo = res['codigo']
                    descripcion = res['descripcion']
                    
                    if codigo == 1000:
                        arrayJson = res['arrayJson']
                        api_key_pool = arrayJson['apikey']
                        data = request.get_json()
                        if api_key_pool:
                            respuesta = send_query_select(data, token, api_key_pool)
                            logging.info('@REQUEST GET ' + request.full_path + ' @RESPONSE ' + json.dumps(respuesta))
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
            logging.debug(e)
            logging.error("Peticion finalizada con error", exc_info = True)
            descripcion = 'No se encuentra el parametro: ' + str(e)
            codigo = -1001
        except Exception as e:
            logging.debug(e)
            logging.error("Peticion finalizada con error", exc_info = True)
            descripcion = str(e)
            codigo = -1000
        respuesta = {'codigo': codigo, 'descripcion': descripcion, 'objetoJson' : {}, 'arrayJson': [] }
        logging.info('@REQUEST GET ' + request.full_path + ' @RESPONSE ' + json.dumps(respuesta))
        return respuesta
    
#Esta clase se encarga de cerrar la sesion actual, hecho mas bien para pruebas. Lo que hace es actualiza la fecha de cracion del token igual al vencimiento para que al verificar salte el mensaje de token expirado
class Logout(Resource):
    def post(self):
        global token, session_closed# se sobreescriben los valores de las variables de la aplicacion        
        
        logging.debug("/Logout")
        
        logging.debug("HTTP REQUEST HEADERS: " + str(request.headers))
        logging.debug("HTTP REQUEST DATA: " + str(request.data))
        
        respuesta = validate.logout(token)
        codigo = respuesta['codigo']
        descripcion = respuesta['descripcion']   
        
        respuesta = {'codigo': codigo, 'descripcion': descripcion, 'objetoJson' : {}, 'arrayJson' : []}
        logging.info('@REQUEST GET ' + request.full_path + ' @RESPONSE ' + json.dumps(respuesta))
        return respuesta
#esta clase se encarga de mostrar la info del token asignado. Por ej. el nro. del token, y la fecha y hora del vencimiento. Hecho para pruebas
class KnowMyToken(Resource):
    def post(self):
        global token, momento, vencimiento_token, token_is_expired# se sobreescriben los valores de las variables de la aplicacion
        logging.debug("/KnowMyToken")
        try:
            logging.debug("HTTP REQUEST HEADERS: " + str(request.headers))
            logging.debug("HTTP REQUEST DATA: " + str(request.data))
            
            arrayJson = []
            objetoJson = {}
            val = validate.check_my_token()
            codigo = val[0]['codigo']
            descripcion = val[0]['descripcion']
            if codigo == 1000:
                token = val[1]
                momento = val[2].strftime('%Y/%m/%d %H:%M:%S')#'%m/%d/%Y %H:%M:%S'
                vencimiento_token = val[3].strftime('%Y/%m/%d %H:%M:%S')
                arrayJson = {
                                "token" : token,
                                "momento" : momento,
                                "vencimiento" : vencimiento_token
                            }
        except KeyError as e :
            logging.debug(e)
            logging.error("Peticion finalizada con error", exc_info = True)
            descripcion = 'No se encuentra el parametro: ' + str(e)
            codigo = -1001
        except Exception as e:
            logging.debug(e)
            logging.error("Peticion finalizada con error", exc_info = True)
            descripcion = str(e)
            codigo = -1000
        respuesta = {'codigo': codigo, 'descripcion': descripcion, 'objetoJson' : objetoJson, 'arrayJson': arrayJson }
        logging.info('@REQUEST GET ' + request.full_path + ' @RESPONSE ' + json.dumps(respuesta))
        return respuesta

    
#Funcion que se encarga de armar el query de consulta al pool y el json con el formato correcto
def send_query_select(data, token, api_key_pool):
    try:
        objetoJson = {}
        arrayJson = []
        operation = data['operation']
        params = data['params']
        ruc = params['ruc']
        query = f"""
                    SELECT trim(EAEMAL) email
                    FROM {AMBIENTE_DB}.F0101, {AMBIENTE_DB}.F01151
                    WHERE ABAN8 = EAAN8
                    AND EAETP = 'E'
                    AND trim(ABTAX) = '{ruc}'
                """
        encoded_query = base64.b64encode(query.encode("utf-8")).decode("utf-8")# sel encripta con base 64 y se desencripta en el pool para realizar la consulta
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