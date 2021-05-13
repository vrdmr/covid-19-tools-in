from datetime import datetime
import time
import logging
import json
import azure.functions as func

from shared.vaccine_utils import \
    get_vaccinations_calendar_data_for_district, \
    _get_all_states_json, _get_all_cities_for_state_json, \
    District


'''
states = []
districts = []
# states_json = _get_all_states_json()
for state in states_json["states"]:
    states.append(State(state["state_id"], state["state_name"]))
for state in states:
    # districts_json = _get_all_cities_for_state_json(state.state_id)
    for district in districts_json["districts"]:
        districts.append(District(district["district_id"], district["district_name"], state.state_id))
'''

def main(req: func.HttpRequest, district_id, mode) -> func.HttpResponse:
    # district_id = req.params.get('district_id')
    # pincode = req.params.get('pin')
    # date_str = req.params.get('date')  # datetime to date
    # mode = req.params.get('mode')      # single vs calendar
    # cache_reload = req.params.get('force_recaching')
    # min_age_limit = req.params.get('age_limit') # all, 45

    # if not district_id and not date_str and not pincode:
    #     return func.HttpResponse(json.dumps({"Error": "No district_id, date_str or pincode passed. Please pass at least one of the two, along with the date, as query"}), status_code=404)

    todays_date = datetime.strftime(datetime.today(), "%d-%m-%y")

    states = {}
    districts = {}
    states_json = _get_all_states_json()
    for state in states_json["states"]:
        states[state["state_id"]] = state["state_name"]

    logging.info('Python timer trigger function ran at %s', states.keys())

    with open('./GetVaccineSlots/districts.dat', 'w+') as districts_file:
        with open('./GetVaccineSlots/states.dat', 'w+') as state_file:
            for state_id in states.keys():
                state_file.write("{} - {}\n".format(state_id, states[state_id]))
                districts_json = _get_all_cities_for_state_json(state_id)
                
                for district in districts_json["districts"]:
                    districts["district_id"] = District(district["district_id"], district["district_name"], state_id)
                    districts_file.write("{} - {} - {}\n".format(district["district_id"], district["district_name"], state_id))

    for did in districts.keys():
        center_info = get_vaccinations_calendar_data_for_district(did, todays_date)

        if center_info:
            with open('./GetVaccineSlots/pin.dat', "w+") as pin_file:
                for center_name, centers in center_info.items():
                    for c in centers:
                        pin_file.write('{} - {} - {} - {} - {}\n'.format(center_name, c.state_name, c.district_name, c.block_name, c.pin))
        time.sleep(.1)

    return func.HttpResponse("This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.", status_code=200)
