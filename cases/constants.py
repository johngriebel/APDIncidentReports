GEORGIA = "GA"
STATE_CHOICES = [(GEORGIA, "Georgia")]

DAY = "D"
EVENING = "E"
NIGHT = "N"

SHIFT_CHOICES = [(DAY, "Day"),
                 (EVENING, "Evening"),
                 (NIGHT, "Night")]

VICTIM = "VICTIM"
SUSPECT = "SUSPECT"

PARTY_TYPE_CHOICES = [(VICTIM, "Victim"),
                (SUSPECT, "Suspect")]

MALE = "M"
FEMALE = "F"
SEX_CHOICES = [(MALE, "Male"),
               (FEMALE, "Female")]

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
                (OTHER, "Other")]

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
                     (EYE_UNKNOWN, "Unknown")]

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
                      (EYE_UNKNOWN, "Unknown")]
