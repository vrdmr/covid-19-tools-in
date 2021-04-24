import logging

import azure.functions as func
from shared.image_processor import process_image_url_to_get_text

import urllib.parse

'''
Authenticate
Authenticates your credentials and creates a client.
'''

def main(req: func.HttpRequest) -> func.HttpResponse:
    mode = str(req.params.get('mode'))
    logging.info(f'Python HTTP trigger function got a new {mode} request.')

    try:
        if mode.upper() == "URL":
            encoded_image_url = urllib.parse.unquote(str(req.params.get('url')))
            parsed_text=process_image_url_to_get_text(image_url=encoded_image_url)
        else:
            return func.HttpResponse("Incorrect Mode", status_code=404)
    except Exception as e:
        print("Exception: ", e)
        return func.HttpResponse("Internal Service Error", status_code=400)

    return func.HttpResponse(str(parsed_text), status_code=200)
