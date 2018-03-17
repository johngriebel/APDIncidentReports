import logging
from django.utils import timezone
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
    elif key == "reporting_officer":
        filter_key = key + "__user__last_name__iexact"
    elif "earliest_" in key:
        filter_key = key + "__gte"
    elif "latest" in key:
        filter_key = key + "__lte"
    elif "location" in key:
        filter_key = key.replace("location_", "location__") + "__icontains"
    elif key == "offenses":
        filter_key = key + "__in"
    else:
        filter_key = key + "__icontains"
    return filter_key


def cleanse_value(key: str, data: dict):
    if "date" in key:
        value = convert_date_string_to_object(data[key])
        if not value.tzinfo:
            logger.info(f"Converted value was not timezone aware. Making it so.")
            value = timezone.make_aware(value)
    elif key == "offenses":
        value = data.getlist(key)
    elif key == "juvenile":
        value = {'2': True, '3': False}[data[key]]
    else:
        value = data[key]
    return value


def build_reverse_lookups(key: str, params: dict):
    if params[key]:
        if "juvenile" in key:
            if params[key] == "1":
                # A value of "1" here corresponds to either "I don't know" or either
                return {}
        party_type = key.split("_")[0]
        filter_key = key.replace(party_type, "incidentinvolvedparty_")
        filter_key_parts = filter_key.split("__")
        filter_key = filter_key_parts[0] + "__" + cleanse_filter_key(filter_key_parts[1])
        value = cleanse_value(key, data=params)
        return {filter_key: value, 'incidentinvolvedparty__party_type': party_type.upper()}
    else:
        return {}


def get_search_results(*, params: dict):
    logger.info(f"Search parameters: {params}")
    filter_dict = {}
    for key in params:
        if isincident_field(key):
            filter_key = cleanse_filter_key(key)
            if params[key]:
                filter_dict[filter_key] = cleanse_value(key, params)
        elif isincidentparty_field(key):
            reverse_lookups = build_reverse_lookups(key, params)
            filter_dict.update(reverse_lookups)
    incidents = Incident.objects.filter(**filter_dict)
    logger.info(f"Results: {incidents}")
    return incidents
