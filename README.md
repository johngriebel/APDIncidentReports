# APD Incident Report Application

## Road Map
**Initial Target Completion Date:** March 5, 2018

### Software Agreement
- Send consultation agreement to APD for approval and signing
    - Don't worry, it will be a very simple one

### Features
All of these are to be documented as they are completed
- Authentication
    - Sign up or invite?
    - Use a third party authentication service such as Auth0?
- Define Database Schema
    - Approximately 80% complete. Just need a few details
- Create reports
    - Define a ModelForm for incidents
    - Enter all Offense types into database with UCR and NGIC codes, create fixture file
    - File upload
- Update Reports
    - Get this more or less for free once report creation is finished
- Approve reports
    - Will need more information surrounding this
- Find a specific report (Search)
    - Search by the following fields:
        - Incident Number
        - Report Date and/or Time
        - Reporting Officer
        - Possible Occurrence Range
        - Location
        - Beat?
        - Shift?
        - Offense Type(s)
        - The following attributes for both victims and suspects:
            - Juvenile
            - Date of Birth
            - Sex
            - Race
            - Height
            - Weight
            - Build
            - Tattoos
            - Scars
            - Hairstyle
            - Hair Color
            - Eye Color
            - Some of these may apply only to victims, or only to suspects, but the DB Schema makes
              it easier to enable it for both party types
- Ability to print a report
    - Record all print requests -> Who printed it and when
- Email/Share reports?
    - Probably privacy concerns
- View the list of all reports
    - Trivial

### Deployment
- Talk to APD, determine their hosting practices (Do they use AWS, 
Google Cloud, internal servers, etc)
- Script deployment so that stack can be brought up with one command
    - Django Server itself (EC2)
    - Database Instance (RDS)
    - File Upload Hosting (S3)
### Demo
- Have Kayla set something up
    - Maybe do a pre-demo demo with Kayla

### Hand Off to APD
- Assist APD with initial deployment, begin maintenance phase per consultation agreement
