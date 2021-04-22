import logging

import azure.functions as func

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

import urllib.parse
import os
import time

'''
Authenticate
Authenticates your credentials and creates a client.
'''

subscription_key = os.getenv("CV_RESOURCE_SUB_KEY")
endpoint =  os.getenv("CV_RESOURCE_SUB_ENDPOINT")
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

def _process_image_url_to_get_text(image_url):
    # Call API with URL and raw response (allows you to get the operation location)
    recognize_results = computervision_client.read(image_url,  raw=True)
    # Get the operation location (URL with an ID at the end) from the response
    operation_location_remote = recognize_results.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = operation_location_remote.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results
    while True:
        get_handw_text_results = computervision_client.get_read_result(operation_id)
        if get_handw_text_results.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Return the detected text
    result = []
    if get_handw_text_results.status == OperationStatusCodes.succeeded:
        for text_result in get_handw_text_results.analyze_result.read_results:
            for line in text_result.lines:
                result.append(line.text)
        return result


def main(req: func.HttpRequest) -> func.HttpResponse:
    mode = str(req.params.get('mode'))
    logging.info(f'Python HTTP trigger function got a new {mode} request.')

    try:
        if mode.upper() == "URL":
            encoded_image_url = urllib.parse.unquote(str(req.params.get('url')))
            parsed_text=_process_image_url_to_get_text(image_url=encoded_image_url)
        else:
            return func.HttpResponse("Incorrect Mode", status_code=404)
    except Exception as e:
        print("Exception: ", e)
        return func.HttpResponse("Internal Service Error", status_code=400)

    return func.HttpResponse(str(parsed_text), status_code=200)
