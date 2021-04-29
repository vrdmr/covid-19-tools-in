import logging

from azure.functions import HttpRequest, HttpResponse
import re
import json
from shared.image_processor import process_image_url_to_get_text

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


def parse_tweet_url_from_body(request_body):
    regex = r"TWEET:(\n*\s*.*)\|\|\|\|\|\|\|\|\|?\|?\|?IMAGEURL:(.*)"
    matches = re.findall(regex, request_body, re.MULTILINE | re.IGNORECASE | re.DOTALL)
    return matches[0][0], matches[0][1]


def _is_valid_url(url):
    regex = ("((http|https)://)(www.)?" +
             "[a-zA-Z0-9@:%._\\+~#?&//=]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")

    # Compile the ReGex
    p = re.compile(regex)
 
    # If the string is empty
    # return false
    if (url == None):
        return False
 
    # Return if the string
    # matched the ReGex
    if(re.search(p, url)):
        return True
    else:
        return False

def main(req: HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request to parse text for relevent information.')
    body_to_return = {}
    text_from_image = None

    try:
        req_body = req.get_body()

        if req_body is None or req_body==b'':
            raise ValueError()
    except ValueError:
        return HttpResponse(json.dumps({"Error": "No body"}), status_code=404)
    else:
        try:
            tweet, image_url = parse_tweet_url_from_body(req_body.decode('utf-8'))
            cities_referenced = fetch_city_info(tweet)
            resources_referenced = fetch_resources_info(tweet)
            contact_details = fetch_contact_info(tweet)

            if image_url is not None and _is_valid_url(image_url):
                text_from_image = process_image_url_to_get_text(image_url=image_url)
                cities_referenced_in_image = fetch_city_info(' '.join(text_from_image))
                resources_referenced_in_image = fetch_resources_info(' '.join(text_from_image))
                contact_details_in_image = fetch_contact_info(' '.join(text_from_image))

        except Exception as e:
            logging.error(e)
            return HttpResponse(json.dumps({"Error": "No tweet"}), status_code=404)

    
    body_to_return = {
        "cities": str(cities_referenced),
        "resources_referenced": str (resources_referenced),
        "contact_details": str(contact_details),
        "text_from_image": text_from_image if text_from_image else "",
        "cities_from_image": cities_referenced_in_image if text_from_image else "",
        "resources_referenced_from_image": resources_referenced_in_image if text_from_image else "",
        "contact_details_from_image": contact_details_in_image if text_from_image else ""
    }

    return HttpResponse(json.dumps(body_to_return), status_code=200)
