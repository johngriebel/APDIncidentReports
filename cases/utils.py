import re
from typing import Union
from datetime import date
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


def cleanse_incident_party_data(incident: Incident, data: dict, groups: list, officers_cache=dict):
    parties_to_create = []
    for group in groups:
        if len(group) > 1:
            print(("group", group))
            indiv_party_data = {key[10:]: data[key] for key in group}
            if indiv_party_data.get('officer_signed', "") == "":
                # If we've gotten here, the form is valid, but a required field is missing, so this
                # must be an empty form. Skip it. this is a temporary hack
                continue
            print(f"Indiv victim data: {indiv_party_data}")
            officer_id = indiv_party_data['officer_signed']

            converted_date = convert_date_string_to_object(indiv_party_data['date_of_birth'])

            indiv_party_data['date_of_birth'] = converted_date

            if officer_id in officers_cache:
                indiv_party_data['officer_signed'] = officers_cache[officer_id]
            else:
                officer = Officer.objects.get(id=officer_id)
                indiv_party_data['officer_signed'] = officers_cache[officer_id] = officer

            home_address_id = indiv_party_data['home_address']
            if indiv_party_data['home_address'] == "":
                indiv_party_data['home_address'] = None
            else:
                indiv_party_data['home_address'] = Address.objects.get(id=home_address_id)

            employer_address_id = indiv_party_data['employer_address']
            if employer_address_id == "":
                indiv_party_data['employer_address'] = None
            else:
                indiv_party_data['employer_address'] = Address.objects.get(id=home_address_id)

            if indiv_party_data['height'] == "":
                indiv_party_data['height'] = None
            if indiv_party_data['weight'] == "":
                indiv_party_data['weight'] = None

            party_type = SUSPECT if "suspect" in group[0].lower() else VICTIM
            indiv_party_data.update({'incident': incident, 'party_type': party_type})
            parties_to_create.append(IncidentInvolvedParty(**indiv_party_data))

    return parties_to_create
