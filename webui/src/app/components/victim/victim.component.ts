import { Component, OnInit, Input, OnChanges } from '@angular/core';
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
export class VictimComponent implements OnInit, OnChanges {
    @Input() availableOfficers: Officer[];
    incidentId: number;
    victimForm: FormGroup;
    states = states;
    @Input() victims: Victim[];

    constructor(private formBuilder: FormBuilder,
                private incidentService: IncidentService,
                private route: ActivatedRoute,
                private location: Location) {
        const id = +this.route.snapshot.paramMap.get("id");
        this.incidentId = id;
        this.createForm();
    }

    ngOnInit() {
        console.log(this.victims);
        console.log("available officers");
        console.log(this.availableOfficers);
    }

    ngOnChanges() {
        this.rebuildForm();
    }

    rebuildForm() {
        this.victimForm.reset({
            incident_id: this.incidentId
        });
        this.setVictimsArray(this.victims);
    }

    setVictimsArray(victims: Victim[]) {
        const victimFormGroups = victims.map(victim => this.formBuilder.group({
            id: victim.id,
            first_name: victim.first_name,
            last_name: victim.last_name,
            officer_signed: this.formBuilder.group(victim.officer_signed),
            home_address: this.formBuilder.group(victim.home_address || 
                                                { street_number: '',
                                                  route: '',
                                                  locality: '',
                                                  postal_code: '',
                                                  state: ''}),
            juvenile: victim.juvenile,
            date_of_birth: victim.date_of_birth,
            sex: victim.sex,
            race: victim.race,
            height: victim.height,
            weight: victim.weight,
            drivers_license: victim.drivers_license,
            drivers_license_state: victim.drivers_license_state,
            employer: victim.employer,
            employer_address: this.formBuilder.group(victim.employer_address || 
                                                    { street_number: '',
                                                      route: '',
                                                      locality: '',
                                                      postal_code: '',
                                                      state: ''
                                                }),
            build: victim.build,
            tattoos: victim.tattoos,
            scars: victim.scars,
            hairstyle: victim.hairstyle
            })
        );
        const victimsFormArray = this.formBuilder.array(victimFormGroups);
        this.victimForm.setControl('victimsArray', victimsFormArray);
    }

    get victimsArray(): FormArray {
        return this.victimForm.get('victimsArray') as FormArray;
    }

    createForm() {
        this.victimForm = this.formBuilder.group({
            incident_id: this.incidentId,
            victimsArray: this.formBuilder.array([]),
        });
    }

    prepareSaveVictims(): Victim[] {
        const formModel = this.victimForm.value;
        
        const victimsArrayCopy: Victim[] = formModel.victimsArray.map(
            (victim: Victim) => Object.assign({}, victim)
        );
        console.log("victims array copy");
        console.log(victimsArrayCopy);
        return victimsArrayCopy;

    }

    onSubmit(){
        console.log("submit button clicked");
        this.victims = this.prepareSaveVictims();
        this.victims.forEach(victim => {
            console.log("Updating victim:");
            console.log(victim.id);
            this.incidentService.updateVictim(this.incidentId, victim).subscribe(
                victim => {
                    console.log("Successfully updated victim");
                }
            );
        });
        this.rebuildForm();
    }


}
