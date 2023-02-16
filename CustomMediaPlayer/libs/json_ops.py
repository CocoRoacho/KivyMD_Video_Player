import json

def write_json_file(filename, data_dict):
    """prepare(serialize) and write data to a json file

    Args:
        filename (Str): path + filename as string
        data_dict (dict): data saved to the json file prepared as dictionary
    """
    
    # Serializing json
    json_object = json.dumps(data_dict, indent=4)
    
    # Writing to sample.json
    with open(filename, "w") as outfile:
        outfile.write(json_object)

    
def open_json_file(filename):
    """loads a json-file specified with filename

    Args:
        filename (str): path + filename as string
    """

    # Opening JSON file
    with open(filename, 'r') as openfile:
 
        # Reading from json file
        json_object = json.load(openfile)
    
    ###print(json_object)
    ###print(type(json_object))

    return json_object