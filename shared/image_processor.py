import os
import time

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

subscription_key = os.getenv("CV_RESOURCE_SUB_KEY")
endpoint =  os.getenv("CV_RESOURCE_SUB_ENDPOINT")
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

def process_image_url_to_get_text(image_url):
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