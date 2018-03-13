import re
import logging
import json
import pytz
from typing import Union, Tuple, Dict, List, Any
from datetime import datetime
from django.utils import timezone
from itertools import groupby
from rest_framework import status
from rest_framework.response import Response
from address.models import to_python
from cases.models import (Incident,
                          IncidentInvolvedParty,
                          Officer, IncidentFile,
                          Address, City, State)
from .constants import VICTIM, SUSPECT
date_format = re.compile("\d{4}-\d{2}-\d{2}")
logger = logging.getLogger('cases')


def convert_date_string_to_object(date_string: str) -> Union[datetime, None]:
    date_parts = None
    if date_string:
        parts = date_string.split()
        logger.debug(f"Parts: {parts}")
        date_portion = parts[0]
        if len(parts) > 1:
            time_portion = date_string.split()[-1]
        else:
            time_portion = None
        if time_portion:
            time_parts = time_portion.split(":")
            logger.debug(("time parts", time_parts))
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
            logger.debug((year, month, day, hours, minutes))
            date_object = datetime(year=year,
                                   month=month,
                                   day=day,
                                   hour=hours,
                                   minute=minutes)
            date_object = timezone.make_aware(date_object,
                                timezone=pytz.timezone("US/Eastern"))
            return date_object
        else:
            raise ValueError(f"Incorrectly formatted date string: {date_string}")
    else:
        return None


def handle_address(party_data: Dict[str, Any], key: str) -> Dict:
    address_dict = {addr_key.replace(f"{key}_", ""): party_data[addr_key]
                    for addr_key in party_data if f"{key}_" in addr_key}
    address_dict[f"raw"] = party_data[f"{key}_formatted"]
    address_object = to_python(address_dict)
    address_data = {f"{key}_raw": party_data[f"{key}_formatted"],
                    key: address_object}
    party_data.update(address_data)
    party_data = {nkey: value for nkey, value in party_data.items()
                  if f"{key}_" not in nkey}
    return party_data


def get_party_groups(data: dict) -> list:
    groups = []
    for k, g in groupby(data, lambda obj: obj.split("-")[:2]):
        if not ('INITIAL_FORMS' in k or 'MAX_NUM_FORMS' in k
                or 'MIN_NUM_FORMS' in k or 'TOTAL_FORMS' in k):
            groups.append(list(g))
    return groups


def get_display_sequence_from_group(key_str):
    return key_str.split("-")[1]


def handle_files(incident: Incident, files: List) -> List[IncidentFile]:
    inc_files = []
    for upload in files:
        incident_file = IncidentFile(incident=incident,
                                     file=upload)
        incident_file.save()
        inc_files.append(incident_file)
    return inc_files


def handle_officer_signed(party_data: Dict[str, Any], cache) -> Dict:
    officer_id = party_data['officer_signed']
    if officer_id in cache:
        party_data['officer_signed'] = cache[officer_id]
    else:
        officer = Officer.objects.get(id=officer_id)
        party_data['officer_signed'] = cache[officer_id] = officer
    return party_data


def handle_height_and_weight(party_data: Dict[str, Any]) -> Dict:
    if party_data['height'] == "":
        party_data['height'] = None
    if party_data['weight'] == "":
        party_data['weight'] = None
    return party_data


def init_indiv_data(data: Dict, group: List) -> Dict:
    display_seq = get_display_sequence_from_group(group[0])
    # Indexing to 10 will be a problem if there are ever double digits victims or suspects
    indiv_party_data = {key[10:].lstrip("-"): data[key] for key in group}
    indiv_party_data['display_sequence'] = display_seq
    return indiv_party_data


def handle_group(incident: Incident, data: Dict, group: List, officers_cache: Dict) -> Dict:
    indiv_party_data = init_indiv_data(data=data, group=group)
    if indiv_party_data.get('officer_signed', "") == "":
        # If we've gotten here, the form is valid, but a required field is missing, so this
        # must be an empty form. Skip it. this is a temporary hack
        return officers_cache

    converted_date = convert_date_string_to_object(indiv_party_data['date_of_birth'])
    indiv_party_data['date_of_birth'] = converted_date

    indiv_party_data = handle_address(party_data=indiv_party_data,
                                      key="home_address")
    indiv_party_data = handle_address(party_data=indiv_party_data,
                                      key="employer_address")
    indiv_party_data = handle_officer_signed(party_data=indiv_party_data,
                                             cache=officers_cache)
    indiv_party_data = handle_height_and_weight(party_data=indiv_party_data)

    party_type = SUSPECT if "suspect" in group[0].lower() else VICTIM

    obj, _ = IncidentInvolvedParty.objects.update_or_create(
        display_sequence=indiv_party_data['display_sequence'],
        incident=incident,
        party_type=party_type,
        defaults=indiv_party_data)
    obj.home_address = indiv_party_data['home_address']
    obj.save()

    return officers_cache


def cleanse_incident_party_data_and_create(incident: Incident, data: dict, groups: list):
    officers_cache = {}
    for group in groups:
        if len(group) > 1:
            handle_group(incident=incident,
                         data=data,
                         group=group,
                         officers_cache=officers_cache)


def parse_and_compile_incident_input_data(post_data) -> Tuple[Dict, List, List, Dict]:
    victim_data = [{key: post_data.get(key) for key in post_data if key.startswith("victims")}]
    suspect_data = [{key: post_data.get(key) for key in post_data if key.startswith("suspects")}]
    party_data = {}

    # Always guaranteed to have at least one victim and one suspect
    for vdata in victim_data:
        party_data.update(vdata)
    for sdata in suspect_data:
        party_data.update(sdata)

    incident_data = {key: post_data.get(key) for key in post_data
                     if isincident_field(key)}
    incident_data['offenses'] = post_data.getlist("offenses")
    incident_data['report_datetime'] = post_data.getlist("report_datetime")[0]

    return incident_data, victim_data, suspect_data, party_data


def isincident_field(field_name: str) -> bool:
    return (("victim" not in field_name) and ("suspect" not in field_name)
            and not field_name == "csrfmiddlewaretoken")


def isincidentparty_field(field_name: str) -> bool:
    return "suspect" in field_name or "victim" in field_name


def create_incident_involved_party(request, serializer_class,
                                   kwargs: Dict[str, Any]) -> Response:
    dirty_data = {key: value for key, value in request.data.items()}
    dirty_data['incident'] = kwargs.get('incidents_pk')
    dirty_data['party_type'] = kwargs['party_type']

    for addr in ["home_address", "employer_address"]:
        address_attrs = dirty_data.get(addr)
        if address_attrs is not None:
            dirty_data[addr] = json.loads(dirty_data[addr])
    serializer = serializer_class(data=dirty_data)
    valid = serializer.is_valid()

    if not valid:
        logger.debug(serializer.errors)
        resp_status = status.HTTP_400_BAD_REQUEST
        resp_data = serializer.errors
    else:
        serializer.create(validated_data=dirty_data)
        resp_status = status.HTTP_201_CREATED
        resp_data = serializer.data

    return Response(status=resp_status,
                    data=resp_data)


def parse_and_create_address(*, address_data: Dict[str, str]) -> Address:
    # TODO: Validation
    abbr = address_data.pop("state_abbreviation")
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
    validated_data['location'] = parse_and_create_address(address_data=validated_data['location'])

    return validated_data
