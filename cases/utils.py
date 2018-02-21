import re
from typing import Union, Tuple
from datetime import datetime
from itertools import groupby
from .models import (Incident,
                     IncidentInvolvedParty,
                     Officer)
from .constants import VICTIM, SUSPECT
date_format = re.compile("\d{4}-\d{2}-\d{2}")


def convert_date_string_to_object(date_string: str) -> Union[datetime, None]:
    date_parts = None
    if date_string:
        date_portion = date_string.split()[0]
        time_portion = date_string.split()[-1]
        if time_portion:
            hours = int(time_portion[0])
            minutes = int(time_portion[1])
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
            print(("date parts", date_parts))
            date_object = datetime(year=year,
                                   month=month,
                                   day=day,
                                   hour=hours,
                                   minute=minutes)
            return date_object
        else:
            raise ValueError(f"Incorrectly formatted date string: {date_string}")
    else:
        return None


def handle_address(address: str):
    return None


def get_party_groups(data: dict) -> list:
    groups = []
    for k, g in groupby(data, lambda obj: obj.split("-")[:2]):
        if not ('INITIAL_FORMS' in k or 'MAX_NUM_FORMS' in k
                or 'MIN_NUM_FORMS' in k or 'TOTAL_FORMS' in k):
            groups.append(list(g))
    return groups


def cleanse_incident_party_data_and_create(incident: Incident, data: dict, groups: list):
    officers_cache = {}
    print(("data", data))
    for group in groups:
        print(("Group", group))
        print(len(group))
        if len(group) > 1:
            # TODO: Indexing to 10 will be a problem if there are ever double digits victims or suspects
            indiv_party_data = {key[10:].lstrip("-"): data[key] for key in group}
            print(("indiv party data", indiv_party_data))
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
            print(("group[0].lower()", group[0].lower()))
            party_type = SUSPECT if "suspect" in group[0].lower() else VICTIM
            indiv_party_data.update({'incident': incident, 'party_type': party_type})
            party_id = indiv_party_data.get('id') or None
            print(f"Incident involved party id: {party_id}")
            IncidentInvolvedParty.objects.update_or_create(id=party_id,
                                                           defaults=indiv_party_data)


def parse_and_compile_incident_input_data(post_data: dict) -> Tuple:
    victim_data = {key: post_data.get(key) for key in post_data if key.startswith("victims")}
    suspect_data = {key: post_data.get(key) for key in post_data if key.startswith("suspects")}
    party_data = {**victim_data, **suspect_data}

    incident_data = {key: post_data.get(key) for key in post_data
                     if (key not in victim_data and key not in suspect_data
                         and key not in ["offenses", "report_datetime"])}
    incident_data['offenses'] = post_data.getlist("offenses")
    incident_data['report_datetime'] = post_data.getlist("report_datetime")[0]

    return incident_data, victim_data, suspect_data, party_data


def isincident_field(field_name: str) -> bool:
    return ((not "location" in field_name) and ("victim" not in field_name)
            and ("suspect" not in field_name) and not field_name == "csrfmiddlewaretoken")


def isincidentparty_field(field_name: str) -> bool:
    return "suspect" in field_name or "victim" in field_name
