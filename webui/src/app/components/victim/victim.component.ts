import { Component, OnInit, Input } from '@angular/core';
import { Location } from '@angular/common';
import { FormBuilder, FormGroup, FormArray } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';

import { Incident, Victim, Officer, Address, DateTime,
         states } from '../../data-model';
import { IncidentService } from '../../services/incident.service';

@Component({
    selector: 'app-victim',
    templateUrl: './victim.component.html',
    styleUrls: ['./victim.component.css']
})
export class VictimComponent implements OnInit {
    @Input() victims: Victim[];
    availableOfficers: Officer[];
    incidentId: Number;
    victimForm: FormGroup;
    states = states;

    constructor(private formBuilder: FormBuilder,
                private incidentService: IncidentService,
                private route: ActivatedRoute,
                private location: Location) { }

    ngOnInit() {
        this.getVictims();
    }

    getVictims() {
        const incidentId = +this.route.snapshot.paramMap.get('id');
        this.incidentId = incidentId;
        this.incidentService.getVictims(incidentId).subscribe(
            victims => {
                this.victims = victims;
                console.log(this.victims);
                this.createForm();
            }
        );

        this.incidentService.getAllOfficers().subscribe(
            officers => {
                this.availableOfficers = officers;
            }
        );
    }

    createForm() {
        this.victimForm = this.formBuilder.group({
            first_name: this.victims[0].first_name,
            last_name: this.victims[0].last_name,
            officer_signed: this.formBuilder.group(this.victims[0].officer_signed),
            home_address: this.formBuilder.group(this.victims[0].home_address || 
                                                {street_number: '',
                                                 route: '',
                                                 locality: '',
                                                 postal_code: '',
                                                 state: '',
                                                 country: ''}),
            juvenile: this.victims[0].juvenile,
            date_of_birth: this.victims[0].date_of_birth,
            sex: this.victims[0].sex,
            race: this.victims[0].race,
            height: this.victims[0].height,
            weight: this.victims[0].weight,
            drivers_license: this.victims[0].drivers_license,
            drivers_license_state: this.victims[0].drivers_license_state,
            employer: this.victims[0].employer,
            employer_address: this.formBuilder.group(this.victims[0].employer_address || 
                                                    {street_number: '',
                                                    route: '',
                                                    locality: '',
                                                    postal_code: '',
                                                    state: '',
                                                    country: ''}),
            build: this.victims[0].build,
            tattoos: this.victims[0].tattoos,
            scars: this.victims[0].scars,
            hairstyle: this.victims[0].hairstyle
        });
    }


}
