import logging
import json
import requests
import azure.functions as func
from datetime import date, timedelta

_API_ENDPOINT = "https://cdn-api.co-vin.in/api/{0}"


class District(object):
    def __init__(self, district_id, district_name, state_id) -> None:
        super().__init__()
        self.district_id = district_id
        self.district_name = district_name
        self.state_id = state_id
    
    def __repr__(self) -> str:
        return str(self.district_id) + ": " + \
            self.district_name + " | StateId: " + \
            str(self.state_id)


class AppointmentSlot(object):
    def __init__(self, slot) -> None:
        self.slot_time = slot
    
    def __repr__(self) -> str:
        return self.slot_time


class AppointmentSession(object):
    def __init__(self, session_id, date, available_capacity, min_age_limit, vaccine, slots) -> None:
        self.session_id = session_id
        self.date = date
        self.available_capacity = available_capacity
        self.min_age_limit = min_age_limit
        self.vaccine = vaccine
        self.slots = []
        for slot in slots:
            self.slots.append(AppointmentSlot(slot))


class Center(object):
    def __init__(self, center_info):
        self.center_id = center_info["center_id"]
        self.name = center_info["name"]
        self.state_name = center_info["state_name"]
        self.district_name = center_info["district_name"]
        self.block_name = center_info["block_name"]
        self.pincode = center_info["pincode"]
        self.lat = center_info["lat"]
        self.long = center_info["long"]
        self.from_time = center_info["from"]
        self.to_time = center_info["to"]
        self.fee_type = center_info["fee_type"]
        self.sessions = []
        for session in center_info["sessions"]:
            self.sessions.append(AppointmentSession(
                session["session_id"], 
                session["date"], 
                session["available_capacity"], 
                session["min_age_limit"], 
                session["vaccine"], 
                session["slots"])
            )


def _send_request(api_call, params, headers=None):
    if headers:
        return requests.get(api_call, 
                            params=params, 
                            headers=headers).json()
    else:
        return requests.get(api_call, 
                            params=params).json()


def _get_all_states_json():
    _API='v2/admin/location/states'
    return _send_request(_API_ENDPOINT.format(_API), None)


def _get_all_cities_for_state_json(state_id):
    _API=f'v2/admin/location/districts/{state_id}'
    return _send_request(_API_ENDPOINT.format(_API), None)


def get_vaccinations_calendar_data_for_district(district_id, date_to_start_looking):
    _API = f'v2/appointment/sessions/public/calendarByDistrict?district_id={district_id}&date={date_to_start_looking}'
    centers_json = _send_request(_API_ENDPOINT.format(_API), None, {"accept": "application/json"})

    logging.info("Centers check: {} - {} - {}".format("centers" in centers_json, district_id, date_to_start_looking))

    if "centers" in centers_json:
        center_data_by_district = {}
        for center_info in centers_json["centers"]:
            if center_info["district_name"] in center_data_by_district:
                center_data_by_district["district_name"].append(Center(center_info))
            else:
                center_data_by_district["district_name"] = []
                center_data_by_district["district_name"].append(Center(center_info))
        return center_data_by_district
    
    return None


def get_vaccinations_single_data_for_district(district_id, date_to_start_looking):
    _API=f'v2​/appointment​/sessions​/public​/findByDistrict?district_id={district_id}&date={date_to_start_looking}'
    centers_json = _send_request(_API_ENDPOINT.format(_API), None, {"accept": "application/json"})

    center_data_by_district = {}

    for center_info in centers_json["centers"]:
        if center_info["district_name"] in center_data_by_district:
            center_data_by_district["district_name"].append(Center(center_info))
        else:
            center_data_by_district["district_name"] = []
            center_data_by_district["district_name"].append(Center(center_info))

    return center_data_by_district


def get_all_vaccinations_calendar_data_for_districts(district_ids, date_to_start_looking):
    # states = {}
    # districts = {}
    # states_json = _get_all_states_json()

    # for state in states_json["states"]:
    #     states["state_id"] = state["state_name"]
    #     districts_json = _get_all_cities_for_state_json(state.state_id)
    #     for district in districts_json["districts"]:
    #         districts["district_id"] = District(district["district_id"], district["district_name"], state.state_id)

    center_data_for_district = {}

    for d_id in district_ids:
        center_data_for_district[d_id] = get_vaccinations_calendar_data_for_district(d_id, date_to_start_looking=date_to_start_looking)

    return center_data_for_district
