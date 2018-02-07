from .models import Incident
from .utils import isincident_field, convert_date_string_to_object


def get_search_results(params: dict):
    filter_dict = {}
    for key in params:
        if isincident_field(key):
            if "_min" in key:
                filter_key = key.replace("_min", "__gte")
            elif "_max" in key:
                filter_key = key.replace("_max", "__lte")
            else:
                filter_key = key
            if params[key]:
                if "datetime" in key:
                    value = convert_date_string_to_object(params[key])
                else:
                    value = params[key]
                filter_dict[filter_key] = value
    print(f"Filter Dict: {filter_dict}")
    incidents = Incident.objects.filter(**filter_dict)
    print(f"Incidents: {incidents}")
    return incidents
