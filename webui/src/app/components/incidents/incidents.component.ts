import { Component, OnInit } from '@angular/core';
import { Incident } from '../../data-model';
import { IncidentService } from '../../services/incident.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-incidents',
  templateUrl: './incidents.component.html',
  styleUrls: ['./incidents.component.css']
})
export class IncidentsComponent implements OnInit {

    incidents: Incident[];
    constructor(private incidentService: IncidentService) {
    }

    ngOnInit() {
        this.getIncidents();
    }

    getIncidents(): void {
        this.incidentService.getIncidents().subscribe(incidents => 
            this.incidents = incidents);
    }

    newIncident() {
    }

}
