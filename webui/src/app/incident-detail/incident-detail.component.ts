import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';
import { Incident } from '../incident';
import { IncidentService } from '../incident.service';

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
        this.getHero();
    }

    getHero(): void {
        const id = +this.route.snapshot.paramMap.get('id');
        this.incidentService.getIncident(id)
        .subscribe(incident => this.incident = incident);
    }

}
