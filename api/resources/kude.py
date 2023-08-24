from flask_restful import Resource
from flask import jsonify, request
from api import API_KEY, AMBIENTE_DB, APP_CONTEXT, DEFAULT_PAGE_SIZE, DEFAULT_PAGE_NUMBER, AUTH_USER, AUTH_PASS
import logging, json
from lib import validate, query_result_pager as qrp
from utils.format_json import set_format_json# se importa la libreria validador que se encarga de validar el token y la sesion 
from api.resources.auth.auth import GetToken as gt

token = ''
api_key_auth = {"apikey" : API_KEY}
vencimiento_token = ''
api_key_pool = ''
session_closed = False

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

# Esta clase se encarga de enviar una consulta al jde y el resultado se muestra en json. Recibe el json con un formato especifico que debe contener el la operacion y el campo a consultar. Este Json
# se envia al pooljde si es que ya se cuenta con una sesion activa, que antes de ser enviado la solicitud, se realiza una validacion de la sesion. 
# Este trabajo lo hace el validador mediante la funcion oper_validator(). Esta funcion recibe ciertos parametros para poder funcionar.
class GetMailByRuc(Resource):
    def post(self):
        global token, momento, vencimiento_token, api_key_pool, api_key_auth, credentials_auth, session_closed# se sobreescriben los valores de las variables de la aplicacion
        logging.debug("/Select")
        operacion = 'get_token'
        codigo = -99999
        descripcion = 'No se a procesado la peticion'
        arrayJson = [] 
        json_data = {"json":"parse"}
        respuesta = None
        objetoJson = {}
        try:
            ############################################### auto-login ###############################################
          
            token_object = gt()        
            response = token_object.check_session()
            codigo = response['codigo']
            descripcion = response['descripcion']
            objetoJson = response['objetoJson']
            token = objetoJson['token']
            vencimiento_token = objetoJson['vencimiento_token']
            credentials_auth = {"username": AUTH_USER, "password" : AUTH_PASS, "apikey" : API_KEY,  "authcontext" : APP_CONTEXT}
            credentials_auth = set_format_json(credentials_auth, operacion) #formateael json con el estandard del jdewsring01
            
            operation = credentials_auth['operation']
            params = credentials_auth['params']
            
            if operation == "get_token":
                if codigo < 0:
                    respuesta = validate.validator(request, token, session_closed, api_key_auth, APP_CONTEXT)
                    json_data = respuesta[0]
                    codigo = json_data['codigo']
                    descripcion = json_data['descripcion']
                    token = respuesta[1]
                    momento = respuesta[2]
                    vencimiento_token = respuesta[3]
                    token_is_expired = respuesta[4]
                    session_closed = respuesta[5]            

        #############################################################################################################
        
            json_data = set_format_json(json_data, "select")
            res = validate.oper_validator(request, token, api_key_auth, vencimiento_token, json_data, AMBIENTE_DB)
            codigo = res['codigo']
            descripcion = res['descripcion']                    
            if codigo == 1000:
                arrayJson = res['arrayJson']
                api_key_pool = arrayJson['apikey']
                data = request.get_json()
                if api_key_pool:                            
                    operation = data['operation']
                    params = data['params']
                    ruc = params['ruc']
                    objetoJson = { "ruc" : ruc }                              
                    arrayJson = make_response_by_query(AMBIENTE_DB, ruc, data)                            
                    #logging.info('@REQUEST GET ' + request.full_path + ' @RESPONSE ' + json.dumps(respuesta))
                    
                    respuesta = {"codigo": codigo, "descripcion": descripcion, "objetoJson": objetoJson, "arrayJson" : arrayJson}
                
                    ############################################### cookies para el cliente ###############################################
                    
                    respuesta = jsonify(respuesta)
                    respuesta.set_cookie('cookie', token)
                    
                    return respuesta                    

                    ########################################################################################################################
                else:
                    descripcion = 'Hubo un problema al recuperar la Api-Key'
                    codigo = -1000
                    logging.error("Peticion finalizada con error: " + descripcion + " " + str(codigo), exc_info = True)
                    
            else:
                codigo = res['codigo']
                descripcion = res['descripcion']
                respuesta = {"codigo": codigo, "descripcion": descripcion, "objetoJson": {}, "arrayJson" : []}
                logging.info('@REQUEST GET ' + request.full_path + ' @RESPONSE ' + json.dumps(respuesta))
                return respuesta
            # else:
            #     descripcion = 'Operación inválida'
            #     codigo = -1002
            #     logging.error("Peticion finalizada con error: " + descripcion + " " + str(codigo), exc_info = True)
                
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
        respuesta = {'codigo': codigo, 'descripcion': descripcion, 'objetoJson' : objetoJson, 'arrayJson': arrayJson }
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
            descripcion = 'No se encuentra el parametro: ' + str(e)
            codigo = -1001
            logging.debug(e)
            logging.error("Peticion finalizada con error: " + descripcion + " " + str(codigo), exc_info = True)
        except Exception as e:
            descripcion = str(e)
            codigo = -1000
            logging.debug(e)
            logging.error("Peticion finalizada con error: " + descripcion + " " + str(codigo), exc_info = True)
        respuesta = {'codigo': codigo, 'descripcion': descripcion, 'objetoJson' : objetoJson, 'arrayJson': arrayJson }
        logging.info('@REQUEST GET ' + request.full_path + ' @RESPONSE ' + json.dumps(respuesta))
        return respuesta
    
    
def get_query_mail_by_ruc(ambiente, ruc):
    query = f"""
                SELECT trim(EAEMAL) email
                FROM {ambiente}.F0101, {ambiente}.F01151
                WHERE ABAN8 = EAAN8
                AND EAETP = 'E'
                AND trim(ABTAX) = '{ruc}'
                AND EAECLASS = 'KUD'
            """
    return query
    
    
def make_response_by_query(ambiente, ruc, data):
    global api_key_pool        
    kudeRucArray = []

    query = get_query_mail_by_ruc(ambiente, ruc)
    query_result_pager = qrp.QueryResultPager()
    arrayJson = query_result_pager.get_rows_select(data, token, api_key_pool, query, DEFAULT_PAGE_NUMBER, DEFAULT_PAGE_SIZE)
    
    for row in arrayJson:
        email = row['EMAIL']
        arrayList = {
            "email" : email
        }
        
        kudeRucArray.append(arrayList)
    return kudeRucArray