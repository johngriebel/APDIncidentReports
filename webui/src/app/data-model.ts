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
    street_number: "";
    route: "";
    city: "";
    state: "";
    postal_code: "";

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
    date: "";
    time: "";
}

// TODO: Can Suspect and Victim be merged?
export class Suspect {
    first_name: '';
    last_name: '';
    officer_signed: Officer;
    juvenile: false;
    home_address: Address;
    date_of_birth: '';
    sex: '';
    race: '';
    height: 0;
    weight: 0;
    hair_color: '';
    eye_color: '';
    drivers_license: '';
    drivers_license_state: '';
    employer: ''
    employer_address: Address;
    build: '';
    tattoos: '';
    scars: '';
    hairstyle: '';
}

export class Victim {
    first_name: '';
    last_name: '';
    officer_signed: Officer;
    juvenile: false;
    home_address: Address;
    date_of_birth: '';
    sex: '';
    race: '';
    height: 0;
    weight: 0;
    hair_color: '';
    eye_color: '';
    drivers_license: '';
    drivers_license_state: '';
    employer: '';
    employer_address: Address;
    build: '';
    tattoos: '';
    scars: '';
    hairstyle: '';
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
