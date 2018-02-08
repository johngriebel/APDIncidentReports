from django.utils import timezone
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
                filter_key = key
            if params[key]:
                if "datetime" in key:
                    value = convert_date_string_to_object(params[key])
                    value = timezone.make_aware(value)
                elif key == "offenses":
                    value = params.getlist(key)
                else:
                    value = params[key]
                filter_dict[filter_key] = value
    print(f"Filter Dict: {filter_dict}")
    incidents = Incident.objects.filter(**filter_dict)
    print(f"Incidents: {incidents}")
    return incidents
