import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';
import { Incident } from '../incident';
import { IncidentService } from '../incident.service';
import * as moment from 'moment';

@Component({
  selector: 'app-incident-detail',
  templateUrl: './incident-detail.component.html',
  styleUrls: ['./incident-detail.component.css']
})
export class IncidentDetailComponent implements OnInit {

    incident: Incident;
    constructor(private route: ActivatedRoute,
                private incidentService: IncidentService,
                private location: Location) { }

    ngOnInit(): void {
        this.getIncident();
    }

    getIncident(): void {
        const id = +this.route.snapshot.paramMap.get('id');
        this.incidentService.getIncident(id)
        .subscribe((incident) => {this.incident = incident; console.log(this.incident)});
    }

    save(): void {
        this.incidentService.updateIncident(this.incident).subscribe();
    }

}
