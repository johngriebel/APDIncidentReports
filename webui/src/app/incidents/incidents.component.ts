import { Component, OnInit } from '@angular/core';
import { Incident } from '../incident';
import { IncidentService } from '../incident.service';

@Component({
  selector: 'app-incidents',
  templateUrl: './incidents.component.html',
  styleUrls: ['./incidents.component.css']
})
export class IncidentsComponent implements OnInit {

    incidents: Incident[];

    constructor(private incidentService: IncidentService) {}

    ngOnInit() {
        this.getIncidents();
    }

    getIncidents(): void {
        this.incidentService.getIncidents().subscribe(incidents => this.incidents = incidents);
    }

}
