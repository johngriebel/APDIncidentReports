import logging
from django.utils import timezone
from typing import Dict
from .models import Incident
from .utils import (isincident_field,
                    convert_date_string_to_object,
                    isincidentparty_field)
logger = logging.getLogger('cases')


def cleanse_filter_key(key: str) -> str:
    if "_min" in key:
        filter_key = key.replace("_min", "__gte")
    elif "_max" in key:
        filter_key = key.replace("_max", "__lte")
    elif "officer" in key or key == "supervisor":
        filter_key = key + "__id"
    elif "earliest_" in key:
        filter_key = key + "__gte"
    elif "latest" in key:
        filter_key = key + "__lte"
    elif "location" in key:
        filter_key = key.replace("location_", "location__") + "__icontains"
    elif key == "offenses":
        filter_key = key + "__id__in"
    elif key == "date_of_birth":
        filter_key = key
    else:
        filter_key = key + "__icontains"
    return filter_key


def cleanse_value(key: str, data: dict):
    if "date" in key:
        if isinstance(data[key], dict):
            date_str = f"{data[key]['date']} {data[key]['time']}"
        else:
            date_str = data[key]
        value = convert_date_string_to_object(date_str)
        if value and (not value.tzinfo):
            logger.info(f"Converted value was not timezone aware. Making it so.")
            value = timezone.make_aware(value)
    elif key == "offenses":
        if hasattr(data, "getlist"):
            value = data.getlist(key)
        else:
            value = data.get(key)
    elif key == "officer_signed":
        value = data[key]['id'] or None
    else:
        value = data[key]
    return value


def build_reverse_lookups(party_type: str, params: dict) -> Dict:
    involved_party_lookups = {'incidentinvolvedparty__party_type': party_type.upper()}
    for key in params:
        if "address" in key:
            location_filters = handle_location_filtering(location_data=params[key],
                                                         filter_prefix=key)
            if location_filters:
                involved_party_lookups.update(location)
            continue
        if params[key]:
            cleaned_sub_key = cleanse_filter_key(key)
            filter_key = f"incidentinvolvedparty__{cleaned_sub_key}"
            value = cleanse_value(key, data=params)
            if value:
                involved_party_lookups[filter_key] = value
    return involved_party_lookups


def handle_location_filtering(location_data: Dict, filter_prefix: str="location") -> Dict:
    location_filters = {}
    for key in ["street_number", "route", "postal_code"]:
        if key in location_data and location_data[key] != "":
            location_filters[f"{filter_prefix}__{key}__icontains"] = location_data[key]

    if "city" in location_data and location_data['city'] != "":
        location_filters[f"{filter_prefix}__city__name__icontains"] = location_data['city']

    if "state" in location_data and location_data['state'] != "":
        location_filters[f"{filter_prefix}__city__state__abbreviation"] = location_data['state']

    return location_filters


def get_search_results(*, params: dict):
    logger.info(f"Search parameters: {params}")
    filter_dict = {}
    for key in params:
        if "datetime" in key:
            params[key] = f"{params[key]['date']} {params[key]['time']}"
        if isincident_field(key):
            if key == "location":
                location_filters = handle_location_filtering(location_data=params[key])
                filter_dict.update(location_filters)
            else:
                filter_key = cleanse_filter_key(key)
                if params[key]:
                    filter_dict[filter_key] = cleanse_value(key, params)
        elif "victim" == key or "suspect" == key:
            reverse_lookups = build_reverse_lookups(key, params[key])
            filter_dict.update(reverse_lookups)
    logger.debug(f"Filter dict: {filter_dict}")
    incidents = Incident.objects.filter(**filter_dict)
    logger.info(f"Results: {incidents}")
    return incidents
