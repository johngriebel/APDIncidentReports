import { Component, OnInit, Input, OnChanges } from '@angular/core';
import { Location } from '@angular/common';
import { FormBuilder, FormGroup, FormArray } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import * as $ from 'jquery';
import { Incident, Suspect, Officer, Address, DateTime,
         states } from '../../data-model';
import { IncidentService } from '../../services/incident.service';

@Component({
    selector: 'app-suspect',
    templateUrl: './suspect.component.html',
    styleUrls: ['./suspect.component.css']
})
export class SuspectComponent implements OnInit, OnChanges {
    @Input() availableOfficers: Officer[];
    incidentId: number;
    suspectForm: FormGroup;
    states = states;
    @Input() suspects: Suspect[];

    constructor(private formBuilder: FormBuilder,
                private incidentService: IncidentService,
                private route: ActivatedRoute,
                private location: Location) {
        const id = +this.route.snapshot.paramMap.get("id");
        this.incidentId = id;
        this.createForm();
    }

    private createEmptySuspect() {
        return {id: 0,
            first_name: '',
            last_name: '',
            officer_signed: new Officer(),
            juvenile: false,
            home_address: {street_number: '',
                           route: '',
                           city: '',
                           state: '',
                           postal_code: ''},
            date_of_birth: new DateTime(),
            sex: '',
            race: '',
            height: 0,
            weight: 0,
            hair_color: '',
            eye_color: '',
            drivers_license: '',
            drivers_license_state: '',
            employer: '',
            employer_address: {street_number: '',
                               route: '',
                               city: '',
                               state: '',
                               postal_code: ''},
            build: '',
            tattoos: '',
            scars: '',
            hairstyle: ''};
    }

    ngOnInit() {
    }

    ngOnChanges() {
        this.rebuildForm();
    }

    rebuildForm() {
        this.suspectForm.reset({
            incident_id: this.incidentId
        });
        this.setSuspectsArray(this.suspects);
    }

    setSuspectsArray(suspects: Suspect[]) {
        const suspectFormGroups = suspects.map(suspect => this.formBuilder.group({
            id: suspect.id,
            first_name: suspect.first_name,
            last_name: suspect.last_name,
            officer_signed: suspect.officer_signed.id || suspect.officer_signed,
            home_address: this.formBuilder.group(suspect.home_address || 
                                                { street_number: '',
                                                  route: '',
                                                  locality: '',
                                                  postal_code: '',
                                                  state: ''}),
            juvenile: suspect.juvenile,
            date_of_birth: suspect.date_of_birth,
            sex: suspect.sex,
            race: suspect.race,
            height: suspect.height,
            weight: suspect.weight,
            drivers_license: suspect.drivers_license,
            drivers_license_state: suspect.drivers_license_state,
            employer: suspect.employer,
            employer_address: this.formBuilder.group(suspect.employer_address || 
                                                    { street_number: '',
                                                      route: '',
                                                      locality: '',
                                                      postal_code: '',
                                                      state: ''
                                                }),
            build: suspect.build,
            tattoos: suspect.tattoos,
            scars: suspect.scars,
            hairstyle: suspect.hairstyle
            })
        );
        const suspectsFormArray = this.formBuilder.array(suspectFormGroups);
        this.suspectForm.setControl('suspectsArray', suspectsFormArray);
    }

    get suspectsArray(): FormArray {
        return this.suspectForm.get('suspectsArray') as FormArray;
    }

    createForm() {
        this.suspectForm = this.formBuilder.group({
            incident_id: this.incidentId,
            suspectsArray: this.formBuilder.array([]),
        });
        console.log("form created");
    }

    prepareSaveSuspects(): Suspect[] {
        const formModel = this.suspectForm.value;
        
        const suspectsArrayCopy: Suspect[] = formModel.suspectsArray.map(
            (suspect: Suspect) => Object.assign({}, suspect)
        );
        console.log("suspects array copy");
        console.log(suspectsArrayCopy);
        return suspectsArrayCopy;

    }

    onSubmit(){
        this.suspects = this.prepareSaveSuspects();
        var count = 0;
        this.suspects.forEach(suspect => {
            count += 1;
            if (suspect.id === 0){
                console.log("in the create block");
                this.incidentService.addSuspect(this.incidentId, suspect).subscribe(
                    suspect => {
                        console.log("Created a new suspect");
                        this.suspects.push(suspect);
                    });
            }
            else {
                console.log("would be updating here");
                this.incidentService.updateSuspect(this.incidentId, suspect).subscribe(
                    suspect => {
                        console.log(`Successfully updated suspect: ${suspect}`);
                    });
                }
        });
        this.rebuildForm();
    }

    addSuspect() {
        this.suspects.push(new Suspect());
        console.log(this.suspectsArray);
        this.rebuildForm();
    }

    getFeet(suspect): number {
        var height = 0;
        if (suspect.value !== undefined) {
            height = suspect.value.height;
        }
        else {
            height = suspect.height
        }
        return Math.floor(height / 12);
    }

    getInches(suspect): number {
        console.log("in get Inches");
        var height = 0;
        if (suspect.value !== undefined) {
            height = suspect.value.height;
        }
        else {
            height = suspect.height;
        }
        return height % 12;
    }

    updateHeight(suspect, event) {
        const count = $(event.target).data("count");
        var feet = parseInt($(`#heightFeet${count}`)[0].value);
        var inches = parseInt($(`#heightInches${count}`)[0].value);
        const newHeight = (feet * 12) + inches;
        suspect.value.height = newHeight;

    }


}
