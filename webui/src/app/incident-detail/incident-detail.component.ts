import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';
import { Incident, Officer } from '../data-model';
import { IncidentService } from '../incident.service';
import { OfficerService } from '../officer.service';
import * as moment from 'moment';

@Component({
  selector: 'app-incident-detail',
  templateUrl: './incident-detail.component.html',
  styleUrls: ['./incident-detail.component.css']
})
export class IncidentDetailComponent implements OnInit {

    incident: Incident;
    availableOfficers: Officer[];
    constructor(private route: ActivatedRoute,
                private incidentService: IncidentService,
                private officerService: OfficerService,
                private location: Location) { }

    ngOnInit(): void {
        this.getIncident();
    }

    getIncident(): void {
        const id = +this.route.snapshot.paramMap.get('id');
        this.incidentService.getIncident(id)
        .subscribe((incident) => {this.incident = incident; console.log(this.incident)});
        this.officerService.getOfficers().
        subscribe((availableOfficers) => {this.availableOfficers = availableOfficers; console.log(this.availableOfficers)});
    }

    save(): void {
        this.incidentService.updateIncident(this.incident).subscribe();
    }
}
