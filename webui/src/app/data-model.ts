export class User {
    constructor(username?: string, password?: string) {}
}


export class Officer {
    id: number;
    officer_number: number;
    user: object;
}

export class State {
    name: '';
    abbreviation: '';
}

export class City {
    name: '';
    state: State
}

export class Address {
    street_number: string;
    route: string;
    city: string;
    state: string;
    postal_code: string;

}

export class Incident {
    id = 0;
    incident_number = "";
    location: Address;
    report_datetime: DateTime;
    reviewed_datetime: DateTime;
    reporting_officer: Officer;
    reviewed_by_officer: Officer;
    investigating_officer: Officer;
    officer_making_report: Officer;
    supervisor: Officer;
    approved_datetime: DateTime;
    earliest_occurrence_datetime: DateTime;
    latest_occurrence_datetime: DateTime;
    beat = 0;
    shift = "";
    damaged_amount = 0.0;
    stolen_amount = 0.0;
    offenses: Offense[];
    narrative = "";

}

export class DateTime {
    date: string;
    time: string;
}

// TODO: Can Suspect and Victim be merged?
export class Suspect {
    id: number;
    first_name: string;
    last_name: string;
    officer_signed: Officer;
    juvenile: boolean;
    home_address: Address;
    date_of_birth: DateTime;
    sex: string;
    race: string;
    height: number;
    weight: number;
    hair_color: string;
    eye_color: string;
    drivers_license: string;
    drivers_license_state: string;
    employer: string;
    employer_address: Address;
    build: string;
    tattoos: string;
    scars: string;
    hairstyle: string;
}

export class Victim {
    id: number;
    first_name: string;
    last_name: string;
    officer_signed: Officer;
    juvenile: boolean;
    home_address: Address;
    date_of_birth: DateTime;
    sex: string;
    race: string;
    height: number;
    weight: number;
    hair_color: string;
    eye_color: string;
    drivers_license: string;
    drivers_license_state: string;
    employer: string;
    employer_address: Address;
    build: string;
    tattoos: string;
    scars: string;
    hairstyle: string;
}

export class Offense {
    id: 0;
    ucr_name_classification: '';
    ucr_subclass_description: '';
    gcic_code: '';
    ucr_code: '';
    ucr_rank: '';
    code_group: '';
    ucr_alpha: '';
}

export class IncidentFile {
    incident: number;
    file: string;
    file_name: string;
}

export const states = [
    "AL",
    "AK",
    "AS",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FM",
    "FL",
    "GA",
    "GU",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MH",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "MP",
    "OH",
    "OK",
    "OR",
    "PW",
    "PA",
    "PR",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VI",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
]