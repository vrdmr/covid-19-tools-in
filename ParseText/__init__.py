import logging

from azure.functions import HttpRequest, HttpResponse
import re
import json

list_of_cities = set()
list_of_resources = set()

cities = open('./ParseText/cities.dat')
for i in cities:
    list_of_cities.add(i.strip().lower())

resources = open('./ParseText/resources.dat')

for i in resources:
    list_of_resources.add(i.strip().lower())


def fetch_city_info(tweet):
    regex = "(" + '|'.join(list(list_of_cities)) + ")"
    matches = re.finditer(regex, tweet, re.MULTILINE | re.IGNORECASE)
    cities = []
    for i in matches:
        cities.append(i.groups()[0])
    return cities

def fetch_resources_info(tweet):
    regex = "(" + '|'.join(list(list_of_resources)) + ")"
    matches = re.finditer(regex, tweet, re.MULTILINE | re.IGNORECASE)
    resources = []
    for i in matches:
        resources.append(i.groups()[0])
    return resources

def fetch_contact_info(tweet):
    phone_regex = r"(?:\s+|)((0|(?:(\+|)91))(?:\s|-)*(?:(?:\d(?:\s|-)*\d{9})|(?:\d{2}(?:\s|-)*\d{8})|(?:\d{3}(?:\s|-)*\d{7}))|\d{10}|\d{5}\ \d{5})(?:\s+|)"
    matches = re.finditer(phone_regex, tweet, re.MULTILINE | re.IGNORECASE)
    numbers = []
    for i in matches:
        numbers.append(i.groups()[0])
    return numbers


def main(req: HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request to parse text for relevent information.')
    body_to_return = {}

    try:
        req_body = req.get_body()
    except ValueError:
        return HttpResponse(json.dumps({"Error": "No body"}), status_code=404)
    else:
        try:
            tweet = req_body.decode('utf-8')
            cities_referenced = fetch_city_info(tweet)
            resources_referenced = fetch_resources_info(tweet)
            contact_details = fetch_contact_info(tweet) # TODO implement
        except Exception as e:
            print (e)
            return HttpResponse(json.dumps({"Error": "No tweet"}), status_code=404)

    
    body_to_return = {
        "cities": str(cities_referenced),
        "resources_referenced": str (resources_referenced),
        "contact_details": str(contact_details)
    }

    return HttpResponse(json.dumps(body_to_return), status_code=200)
