# APD Incident Report Application

## Road Map
**Initial Target Completion Date:** March 5, 2018

This is very much a living document. Don't hesitate to ask questions.

### Software Agreement
- [x] Send consultation agreement to APD for approval and signing
    - Don't worry, it will be a very simple one

### Features
All of these are to be documented as they are completed
- [x] Authentication
    - Basic Authentication is done. No password reset or any thing like that
- [x] Define Database Schema
- [x] Create reports
    - [x] Define a ModelForm for relevant models
    - [x] Datetime widget
    - [x] Basic, manual version with separate page for each entity
    - [x] Single page, in-line creation of all entities
    - [x] Smart address lookup
    - [ ] Enter all Offense types into database with UCR and NGIC codes, create fixture file
    - [ ] File upload
- [x] Update Reports
    - Get this more or less for free once report creation is finished
- [ ] Approve reports
    - Will need more information surrounding this
- [x] Find a specific report (Search)
    - Search by the following fields:
        - [x] Incident Number
        - [x] Report Date and/or Time
        - [x] Reporting Officer
            - Last name implemented, add lookup by office id
        - [x] Possible Occurrence Range
        - [x] Location
        - [x] Beat?
        - [x] Shift?
        - [x] Offense Type(s)
        - The following attributes for both victims and suspects:
            - [x] Juvenile
            - [x] Date of Birth
            - [x] Sex
            - [x] Race
            - [x] Height
            - [x] Weight
            - [x] Build
            - [x] Tattoos
            - [x] Scars
            - [x] Hairstyle
            - [x] Hair Color
            - [x] Eye Color
            - Some of these may apply only to victims, or only to suspects, but the DB Schema makes
              it easier to enable it for both party types
    - Would be nice to allow per field options 
- [x] Ability to print a report
    - Record all print requests -> Who printed it and when
- [ ] Email/Share reports?
    - Probably privacy concerns
- [x] View the list of all reports
    - Trivial
    - [ ] Decide which fields should be displayed in table
- [ ] Cosmetics
    - Nice Nav Bar
    - Correct Color Scheme
- [ ] Unit Testing
- [ ] Code cleanup/refactor
- [ ] Logging

### Deployment
- [ ] Talk to APD, determine their hosting practices (Do they use AWS, 
Google Cloud, internal servers, etc)
- [ ] Script deployment so that stack can be brought up with one command
    - [ ] Django Server itself (EC2)
    - [ ] Database Instance (RDS)
    - [ ] File Upload Hosting (S3)
### Demo
- [ ] Have Kayla set something up
    - Maybe do a pre-demo demo with Kayla

### Hand Off to APD
- [ ] Assist APD with initial deployment, begin maintenance phase per consultation agreement
