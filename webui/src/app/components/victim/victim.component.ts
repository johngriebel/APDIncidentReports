import { Component, OnInit, Input, OnChanges } from '@angular/core';
import { Location } from '@angular/common';
import { FormBuilder, FormGroup, FormArray } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import * as $ from 'jquery';
import { Incident, Victim, Officer, Address, DateTime,
         states, 
         AddressTwo} from '../../data-model';
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

    private createEmptyVictim() {
        return new Victim();
    }

    ngOnInit() {
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
            officer_signed: victim.officer_signed.id || victim.officer_signed,
            home_address: this.formBuilder.group(victim.home_address || 
                                                { street_number: '',
                                                  route: '',
                                                  city: '',
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
        console.log("form created");
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
        this.victims = this.prepareSaveVictims();
        var count = 0;
        this.victims.forEach(victim => {
            count += 1;
            if (victim.id === 0){
                console.log("in the create block");
                this.incidentService.addVictim(this.incidentId, victim).subscribe(
                    victim => {
                        console.log("Created a new victim");
                        this.victims.push(victim);
                    });
            }
            else {
                console.log("would be updating here");
                this.incidentService.updateVictim(this.incidentId, victim).subscribe(
                    victim => {
                        console.log(`Successfully updated victim: ${victim}`);
                    });
                }
        });
        this.rebuildForm();
    }

    addVictim() {
        this.victims.push(this.createEmptyVictim());
        console.log(this.victimsArray);
        this.rebuildForm();
    }

    getFeet(victim): number {
        var height = 0;
        if (victim.value !== undefined) {
            height = victim.value.height;
        }
        else {
            height = victim.height
        }
        return Math.floor(height / 12);
    }

    getInches(victim): number {
        console.log("in get Inches");
        var height = 0;
        if (victim.value !== undefined) {
            height = victim.value.height;
        }
        else {
            height = victim.height;
        }
        return height % 12;
    }

    updateHeight(victim, event) {
        const count = $(event.target).data("count");
        var feet = parseInt($(`#heightFeet${count}`)[0].value);
        var inches = parseInt($(`#heightInches${count}`)[0].value);
        const newHeight = (feet * 12) + inches;
        victim.value.height = newHeight;

    }


}
