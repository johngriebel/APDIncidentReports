from reportlab.rl_config import defaultPageSize


EMPTY_CHOICE = ("", "-------")

STATES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AS": "American Samoa",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District Of Columbia",
    "FM": "Federated States Of Micronesia",
    "FL": "Florida",
    "GA": "Georgia",
    "GU": "Guam",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MH": "Marshall Islands",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "MP": "Northern Mariana Islands",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PW": "Palau",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VI": "Virgin Islands",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}
STATE_CHOICES = [(abbrev, full) for abbrev, full in STATES.items()]

DAY = "D"
EVENING = "E"
NIGHT = "N"

SHIFT_CHOICES = [(DAY, "Day"),
                 (EVENING, "Evening"),
                 (NIGHT, "Night"),
                 EMPTY_CHOICE]

VICTIM = "VICTIM"
SUSPECT = "SUSPECT"

PARTY_TYPE_CHOICES = [(VICTIM, "Victim"),
                      (SUSPECT, "Suspect"),
                      EMPTY_CHOICE]

MALE = "M"
FEMALE = "F"
SEX_CHOICES = [(MALE, "Male"),
               (FEMALE, "Female"),
               EMPTY_CHOICE]

# TODO: Hispanic?
ASIAN = "ASIAN"
BLACK = "BLACK"
NATIVE = "NATIVE"
PAC_ISLANDER = "HAWAIIAN/PACIFIC_ISLANDER"
WHITE = "WHITE"
OTHER = "OTHER"

RACE_CHOICES = [(ASIAN, "Asian"),
                (BLACK, "Black/African American"),
                (NATIVE, "Native American"),
                (PAC_ISLANDER, "Native Hawaiian/Pacific Islander"),
                (WHITE, "White"),
                (OTHER, "Other"),
                EMPTY_CHOICE]

# Eye Colors
EYE_BLACK = "BLK"
EYE_BROWN = "BRO"
EYE_GREEN = "GRN"
EYE_MAROON = "MAR"
EYE_PINK = "PNK"
EYE_BLUE = "BLU"
EYE_GRAY = "GRY"
EYE_HAZEL = "HAZ"
EYE_MULTI = "MUL"
EYE_UNKNOWN = "XXX"

# From https://nief.org/attribute-registry/codesets/NCICEyeColorCode/
EYE_COLOR_CHOICES = [(EYE_BLACK, "Black"),
                     (EYE_BROWN, "Brown"),
                     (EYE_GREEN, "Green"),
                     (EYE_MAROON, "Maroon"),
                     (EYE_PINK, "Pink"),
                     (EYE_BLUE, "Blue"),
                     (EYE_GRAY, "Gray"),
                     (EYE_HAZEL, "Hazel"),
                     (EYE_MULTI, "MUL"),
                     (EYE_UNKNOWN, "Unknown"),
                     EMPTY_CHOICE]

BALD = "BLD"
BLOND = "BLN"
ORANGE = "ONG"
PURPLE = "PLE"
RED = "RED"
SANDY = "SDY"
WHITE = "WHI"

# From: https://nief.org/attribute-registry/codesets/NCICHairColorCode/
HAIR_COLOR_CHOICES = [(BALD, "Bald"),
                      (EYE_BLACK, "Black"),
                      (BLOND, "Blond or Strawberry"),
                      (EYE_BLUE, "Blue"),
                      (EYE_BROWN, "Brown"),
                      (EYE_GRAY, "Gray or Partially Gray"),
                      (EYE_GREEN, "Green"),
                      (ORANGE, "Orange"),
                      (EYE_PINK, "Pink"),
                      (PURPLE, "Purple"),
                      (RED, "Red or Auburn"),
                      (SANDY, "Sandy"),
                      (WHITE, "White"),
                      (EYE_UNKNOWN, "Unknown"),
                      EMPTY_CHOICE]


PAGE_WIDTH = defaultPageSize[0]
PAGE_HEIGHT = defaultPageSize[1]
PAGE_CENTER_X = PAGE_WIDTH / 2.0

COLUMN_X_POSITION_MAP = {
    1: 100,
    2: 200,
    3: 300,
    4: 400
}

LEFT_ALIGN_X = 25
TOP_ALIGN_Y = 800

MAX_TEXT_LINE_WIDTH = 90
# i.e. the lowest point on a page that we want a line of text to be drawn
MIN_Y_POSITION = PAGE_HEIGHT - TOP_ALIGN_Y
COLOR_RGB_VALUES = {'red': (255, 0, 0),
                    'blue': (0, 38, 150),
                    'black': (0, 0, 0)}