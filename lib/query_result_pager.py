import base64, requests
from api import BASE_URL_POOL

class QueryResultPager:
    def __init__(self):
        self.has_more_pages = True
    def get_rows_select(self, data, token, api_key_pool, query, page_number, page_size):
        objetoJson = {}
        arrayJson = []
        results = []
        while self.has_more_pages:
            # operation = data['operation']
            # params = data['params']
            encoded_query = base64.b64encode(query.encode("utf-8")).decode("utf-8")
            body = {
                    "operation": "select",
                    "params" : {
                                "apikey" : api_key_pool,
                                "token" : token,
                                "query": encoded_query,
                                "page_number" : page_number,
                                "page_size" : page_size
                                }
                    }
            pool_res = requests.post(BASE_URL_POOL, json = body)
            data = pool_res.json()
            codigo = data['codigo']
            descripcion = data['descripcion']
            objetoJson = data['objetoJson']
            arrayJson = data['arrayJson']
            if data:
                results.extend(arrayJson)
                page_number += 1
                self.has_more_pages = objetoJson.get('has_more_pages')
            else:                
                self.has_more_pages = objetoJson.get('has_more_pages')
            return results