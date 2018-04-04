export class User {
    constructor(username?: string, password?: string) {}
}


export class Officer {
    constructor(public id: number = 0,
                public officer_number: number = 0,
                public user: object = {}){}

    equals(other) {
        return (other.id === this.id &&
                other.officer_number === this.officer_number);
    }

    getValue() {
        return this.id;
    }
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

export class AddressTwo {
    constructor (public street_number: string = "",
                 public route: string = "",
                 public city: string = "",
                 public state: string = "",
                 public postal_code: string = ""){
                 }
    equals(other){
        return (other.street_number === this.street_number &&
                other.route === this.route &&
                other.city === this.city &&
                other.state === this.state &&
                other.postal_code === this.postal_code)
    }

    getValue(){
        return this;
    }
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

    constructor(public date: string = "",
                public time: string = ""){}

    equals(other) {
        console.log("In the custom .equals method");
        return (other.date == this.date &&
                other.time == this.time);
    }

    getValue() {
        return this;
    }
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
    constructor(
    public id: number = 0,
    public first_name: string = "",
    public last_name: string = "",
    public officer_signed: Officer = new Officer(),
    public juvenile: boolean = false,
    public home_address: AddressTwo = new AddressTwo(),
    public date_of_birth: DateTime = new DateTime(),
    public sex: string = "",
    public race: string = "",
    public height: number = 0,
    public weight: number = 0,
    public hair_color: string = "",
    public eye_color: string = "",
    public drivers_license: string = "",
    public drivers_license_state: string = "",
    public employer: string = "",
    public employer_address: AddressTwo = new AddressTwo(),
    public build: string = "",
    public tattoos: string = "",
    public scars: string = "",
    public hairstyle: string = ""){}

    equals(other){
        return (other.id === this.id &&
                other.first_name === this.first_name &&
                other.last_name === this.last_name &&
                this.officer_signed.equals(other.officer_signed) &&
                other.juvenile === this.juvenile &&
                this.home_address.equals(other.home_address) &&
                this.date_of_birth.equals(other.date_of_birth) &&
                other.sex === this.sex &&
                other.race === this.race &&
                other.height === this.height &&
                other.weight === this.weight &&
                other.hair_color === this.hair_color &&
                other.drivers_license === this.drivers_license &&
                other.drivers_license_state === this.drivers_license_state &&
                other.employer === this.employer &&
                this.employer_address.equals(other.employer_address) &&
                other.build === this.build &&
                other.tattoos === this.build &&
                other.scars === this.scars &&
                other.hairstyle === this.hairstyle
            )
    }
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

export const blankSearchCriteria = {
    incident_number: '',
    location: new AddressTwo(),
    report_datetime_min: new DateTime(),
    report_datetime_max: new DateTime(),
    reporting_officer: new Officer(),
    earliest_occurrence_datetime: new DateTime(),
    latest_occurrence_datetime: new DateTime(),
    beat: 0,
    shift: '',
    offenses: null,
    victim: new Victim()
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

export const eye_colors = [
    {abbreviation: "BLK", display: "Black"}
]

export const hair_colors = [
    {abbreviation: "BLD", display: "Bald"}
]

