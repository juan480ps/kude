def set_format_json(json_, oper = None):
    
    json_data = json_
    
    objetoJson = {
        "operation" : oper,
        "params" : {}
    }
    
    for key in json_data:
        objetoJson["params"][key] = json_data[key]
    
    return objetoJson