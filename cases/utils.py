import re
from typing import Union
from datetime import date
from itertools import groupby
from .models import (Address,
                     Incident,
                     IncidentInvolvedParty,
                     Officer)
from .constants import VICTIM, SUSPECT
date_format = re.compile("\d{4}-\d{2}-\d{2}")


def convert_date_string_to_object(date_string: str) -> Union[date, None]:
    date_parts = None
    if date_string:
        if "-" in date_string:
            date_parts = date_string.split("-")
            year = int(date_parts[0])
            month = int(date_parts[1])
            day = int(date_parts[2])
        elif "/" in date_string:
            date_parts = date_string.split("/")
            year = int(date_parts[2])
            month = int(date_parts[0])
            day = int(date_parts[1])

        if date_parts is not None and len(date_parts) == 3:
            print(("date parts", date_parts))
            date_object = date(year=year,
                               month=month,
                               day=day)
            return date_object
        else:
            raise ValueError(f"Incorrectly formatted date string: {date_string}")
    else:
        return None


def handle_address(address: str) -> Union[None, Address]:
    if address == "":
        ret_address = None
    else:
        ret_address = Address.objects.get(id=address)

    return ret_address


def get_party_groups(data: dict) -> list:
    groups = []
    for k, g in groupby(data, lambda obj: obj.split("-")[:2]):
        if not ('INITIAL_FORMS' in k or 'MAX_NUM_FORMS' in k
                or 'MIN_NUM_FORMS' in k or 'TOTAL_FORMS' in k):
            groups.append(list(g))
    return groups


def cleanse_incident_party_data(incident: Incident, data: dict, groups: list):
    officers_cache = {}
    parties_to_create = []
    for group in groups:
        if len(group) > 1:
            indiv_party_data = {key[10:]: data[key] for key in group}
            if indiv_party_data.get('officer_signed', "") == "":
                # If we've gotten here, the form is valid, but a required field is missing, so this
                # must be an empty form. Skip it. this is a temporary hack
                continue

            converted_date = convert_date_string_to_object(indiv_party_data['date_of_birth'])
            indiv_party_data['date_of_birth'] = converted_date

            officer_id = indiv_party_data['officer_signed']
            if officer_id in officers_cache:
                indiv_party_data['officer_signed'] = officers_cache[officer_id]
            else:
                officer = Officer.objects.get(id=officer_id)
                indiv_party_data['officer_signed'] = officers_cache[officer_id] = officer

            for key in ["home_address", "employer_address"]:
                indiv_party_data[key] = handle_address(indiv_party_data[key])

            if indiv_party_data['height'] == "":
                indiv_party_data['height'] = None
            if indiv_party_data['weight'] == "":
                indiv_party_data['weight'] = None

            party_type = SUSPECT if "suspect" in group[0].lower() else VICTIM
            indiv_party_data.update({'incident': incident, 'party_type': party_type})
            parties_to_create.append(IncidentInvolvedParty(**indiv_party_data))

    return parties_to_create
