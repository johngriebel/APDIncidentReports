import re
import logging
import pytz

from typing import Optional, Dict, Any
from datetime import datetime
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from cases.models import (Officer, Address,
                          City, State)

date_format = re.compile(r"\d{4}-\d{2}-\d{2}")
logger = logging.getLogger('cases')


def convert_date_string_to_object(date_string: str) -> Optional[datetime, None]:
    date_parts = None
    if date_string.strip():
        parts = date_string.split()
        date_portion = parts[0]
        if len(parts) > 1:
            time_portion = date_string.split()[-1]
        else:
            time_portion = None
        if time_portion:
            time_parts = time_portion.split(":")
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
        else:
            hours = 0
            minutes = 0
        if "-" in date_portion:
            date_parts = date_portion.split("-")
            year = int(date_parts[0])
            month = int(date_parts[1])
            day = int(date_parts[2])
        elif "/" in date_string:
            date_parts = date_portion.split("/")
            year = int(date_parts[2])
            month = int(date_parts[0])
            day = int(date_parts[1])

        if date_parts is not None and len(date_parts) == 3:
            date_object = datetime(year=year,
                                   month=month,
                                   day=day,
                                   hour=hours,
                                   minute=minutes,
                                   tzinfo=pytz.timezone(settings.TIME_ZONE))
            return date_object
        else:
            raise ValueError(f"Incorrectly formatted date string: {date_string}")
    else:
        return None


def isincident_field(field_name: str) -> bool:
    return (("victim" not in field_name) and ("suspect" not in field_name)
            and not field_name == "csrfmiddlewaretoken")


def isincidentparty_field(field_name: str) -> bool:
    return "suspect" in field_name or "victim" in field_name


def create_incident_involved_party(request, serializer_class,
                                   kwargs: Dict[str, Any]) -> Response:
    dirty_data = {key: value for key, value in request.data.items()}
    logger.debug(f"Incident Involved Party Dirty Data: {dirty_data}")
    dirty_data['incident'] = kwargs.get('incidents_pk')

    serializer = serializer_class(data=dirty_data,
                                  context={'request': request})
    valid = serializer.is_valid()

    if not valid:
        logger.debug(serializer.errors)
        resp_status = status.HTTP_400_BAD_REQUEST
        resp_data = serializer.errors
    else:
        serializer.create(validated_data=serializer.validated_data, party_type=kwargs.get('party_type'))
        resp_status = status.HTTP_201_CREATED
        resp_data = serializer.data

    return Response(status=resp_status,
                    data=resp_data)


def parse_and_create_address(*, address_data: Dict[str, str]) -> Address:
    # TODO: Validation
    abbr = address_data.pop("state")
    address_data.pop("country", None)
    state, created = State.objects.get_or_create(abbreviation=abbr,
                                                 defaults={'name': address_data.get("state", ""),
                                                           'abbreviation': abbr})
    if created:
        logger.debug(f"Created new state: {state}")
    # state.save()
    city = City(name=address_data.pop("city"),
                state=state)
    city.save()
    address_data['city'] = city
    address = Address(**address_data)
    address.save()
    logger.debug(f"Address object: {address}")
    return address


def handle_incident_foreign_keys_for_creation(*, validated_data):
    for field in validated_data.keys():
        if "officer" in field or "supervisor" in field:
            validated_data[field] = Officer.objects.get(officer_number=validated_data[field])

    return validated_data
