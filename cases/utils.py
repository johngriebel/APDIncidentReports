from typing import Union
from datetime import date


def convert_slash_date_to_iso(date_string: str) -> Union[date, None]:
    date_parts = date_string.split("/")
    if len(date_parts) == 3:
        date_object = date(year=int(date_parts[2]),
                           month=int(date_parts[0]),
                           day=int(date_parts[1]))
        return date_object
    elif date_string == "":
        return None
    else:
        raise ValueError("Incorrectly formatted date string")
