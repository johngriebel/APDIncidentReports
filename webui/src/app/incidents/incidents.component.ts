import { Component, OnInit } from '@angular/core';
import { Incident } from '../data-model';
import { IncidentService } from '../incident.service';

@Component({
  selector: 'app-incidents',
  templateUrl: './incidents.component.html',
  styleUrls: ['./incidents.component.css']
})
export class IncidentsComponent implements OnInit {

    incidents: Incident[];
    selectedIncident: Incident;

    constructor(private incidentService: IncidentService) {}

    ngOnInit() {
        this.getIncidents();
    }

    getIncidents(): void {
        this.incidentService.getIncidents().subscribe(incidents => this.incidents = incidents);
        this.selectedIncident = undefined;
    }

    select(incident: Incident) {
        this.selectedIncident = incident;
        console.log(this.selectedIncident);
    }

}
