import { Component, Input, OnChanges } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Location } from '@angular/common';

import { Incident, Address, DateTime, Officer,
         Victim, Suspect } from '../data-model';
import { IncidentService } from '../incident.service';
import { OfficerService } from '../officer.service';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-incident-detail-reactive',
  templateUrl: './incident-detail-reactive.component.html',
  styleUrls: ['./incident-detail-reactive.component.css']
})
export class IncidentDetailReactiveComponent implements OnChanges{
    @Input() incident: Incident;
    availableOfficers: Officer[];
    victims: Victim[];
    suspects: Suspect[];

    incidentForm: FormGroup;

    constructor(private formBuilder: FormBuilder,
                private route: ActivatedRoute,
                private incidentService: IncidentService,
                private officerService: OfficerService,
                private ngLocation: Location
            ) {
                this.officerService.getOfficers().
                subscribe((availableOfficers) => 
                {this.availableOfficers = availableOfficers; 
                    console.log(this.availableOfficers)
                });                
        this.createForm();
     }

     createForm() {
         this.incidentForm = this.formBuilder.group({
             incident_number: 'Incident number',
             location: this.formBuilder.group({
                 street_number: '',
                 route: '',
                 locality: '',
                 postal_code: '',
                 state: '',
                 country: '',
             }),
             report_datetime: this.formBuilder.group({
                 date: '',
                 time: ''
             }),
             reporting_officer: this.formBuilder.group({
                 id: '',
                 officer_number: '',
                 user: {}
             }),
             beat: 0,
             shift: "",
             damaged_amount: 0.0,
             stolen_amount: 0.0,
             narrative: ""
         })
     }

     rebuildForm() {
         console.log("this.incident.reporting_officer")
         console.log(this.incident.reporting_officer);
         this.incidentForm.reset({
             incident_number: this.incident.incident_number,
             location: this.incident.location,
             report_datetime: this.incident.report_datetime,
             reporting_officer: this.incident.reporting_officer
         })
     }

     ngOnChanges(){
         this.rebuildForm();
     }

}
