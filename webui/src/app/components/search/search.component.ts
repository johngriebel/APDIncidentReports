import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import * as $ from 'jquery';
import { IncidentService } from '../../services/incident.service';
import { DateTime, Officer, Offense, Incident,
         eye_colors, states, hair_colors, blankSearchCriteria,
        AddressTwo } from '../../data-model';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent implements OnInit {

    searchForm: FormGroup;

    availableOfficers: Officer[];
    availableOffenses: Offense[];
    searchResults: Incident[];


    states = states;
    eyeColors = eye_colors;
    hairColors = hair_colors;

    constructor(private formBuilder: FormBuilder,
                private incidentService: IncidentService) { }

    ngOnInit() {
        this.incidentService.getAllOfficers().subscribe(officers => {
            this.availableOfficers = officers;
        });
        this.incidentService.getAllOffenses().subscribe(offenses => {
            this.availableOffenses = offenses;
            this.createForm();
        });
    }

    private shouldParamBeSent(name, value): boolean {
        let blankValue = blankSearchCriteria[name];

        if (name === "victim"){
            return false;
        }
        else if (blankValue instanceof Object){
            return !blankValue.equals(value);
        }
        else{
            return blankSearchCriteria[name] != value;
        }
    }


    prepareSearchParams(rawParams) {
        var cleanedParams = {};
        
        Object.keys(rawParams).forEach(param => {
            let value = rawParams[param]
            if (this.shouldParamBeSent(param, rawParams[param])){
                if (rawParams[param] instanceof Object){
                    if (param == "reporting_officer"){
                        cleanedParams[param] = rawParams[param].id;
                    }
                    else{
                        cleanedParams[param] = rawParams[param];
                    }
                }
                else{
                    cleanedParams[param] = rawParams[param];
                }
            }
        });
        return cleanedParams
    }

    onSubmit() {
        const searchParams = this.prepareSearchParams(this.searchForm.value);
        this.incidentService.searchIncidents(searchParams).subscribe(
            incidents => {
                console.log("Found incidents");
                console.log(incidents);
                this.searchResults = incidents;
            });
    }

    createForm() {
        this.searchForm = this.formBuilder.group({
            incident_number: '',
            location: this.formBuilder.group({
                street_number: '',
                route: '',
                city: '',
                postal_code: '',
                state: '',
            }),
            report_datetime_min: this.formBuilder.group({date: '', time: ''}),
            report_datetime_max: this.formBuilder.group({date: '', time: ''}),
            reporting_officer: this.formBuilder.group(new Officer()),
            earliest_occurrence_datetime: this.formBuilder.group({date: '', time: ''}),
            latest_occurrence_datetime: this.formBuilder.group({date: '', time: ''}),
            beat: 0,
            shift: '',
            offenses: [],
            victim: this.formBuilder.group({
                first_name: '',
                last_name: '',
                //juvenile: false,
                min_date_of_birth: this.formBuilder.group({date: '', time: ''}),
                max_date_of_birth: this.formBuilder.group({date: '', time: ''}),
                sex: '',
                race: '',
                min_height: 0,
                max_height: 0,
                min_weight: 0,
                max_weight: 0,
                build: '',
                tattoos: '',
                scars: '',
                hairstyle: '',
                hair_color: '',
                eye_color: ''
            })
        });
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
