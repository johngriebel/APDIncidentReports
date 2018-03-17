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
    selectedIncident: Incident;
    loggedIn: boolean = false;
    constructor(private incidentService: IncidentService,
                private router: Router) {
        this.loggedIn = (localStorage.getItem('loggedIn') == "true");
    }

    ngOnInit() {
        if (!this.loggedIn){
            this.router.navigateByUrl("/login");
        }
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

    newIncident() {
        this.selectedIncident = new Incident();
        console.log(this.selectedIncident);
    }

}
