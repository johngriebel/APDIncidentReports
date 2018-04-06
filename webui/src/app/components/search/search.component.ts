import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import * as $ from 'jquery';
import { IncidentService } from '../../services/incident.service';
import { DateTime, Officer, Offense, Incident,
         eye_colors, states, hair_colors, blankSearchCriteria,
        AddressTwo, 
        Victim,
        Suspect} from '../../data-model';

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
        if (blankValue instanceof Object){
            return !blankValue.equals(value);
        }
        else{
            return blankSearchCriteria[name] != value;
        }
    }


    prepareSearchParams(rawParams) {
        
        var cleanedParams = {};
        
        Object.keys(rawParams).forEach(param => {
            let value = rawParams[param];
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
        console.log("submit button clicked");
        console.log(this.searchForm.value);
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
            height_feet: 0,
            height_inches: 0,
            reporting_officer: this.formBuilder.group(new Officer()),
            earliest_occurrence_datetime: this.formBuilder.group({date: '', time: ''}),
            latest_occurrence_datetime: this.formBuilder.group({date: '', time: ''}),
            beat: 0,
            shift: '',
            offenses: [],
            victim: this.formBuilder.group(new Victim()),
            suspect: this.formBuilder.group(new Suspect())
        });
    }

    updateVictimHeight(event){
        let currentHeight = this.searchForm.value.victim.height;
        let currentFeet = Math.floor(currentHeight / 12);
        let currentInches = currentHeight % 12;
        let eventValue = parseInt(event.target.value);

        var newHeight = 0;

        if (event.target.id == "heightFeet"){
            newHeight = (eventValue * 12) + currentInches;
        }
        else {
            newHeight = currentHeight + eventValue;
        }
        this.searchForm.value.victim.height = newHeight;
    }

    updateSuspectHeight(event){
        let currentHeight = this.searchForm.value.suspect.height;
        let currentFeet = Math.floor(currentHeight / 12);
        let currentInches = currentHeight % 12;
        let eventValue = parseInt(event.target.value);

        var newHeight = 0;

        if (event.target.id == "heightFeet"){
            newHeight = (eventValue * 12) + currentInches;
        }
        else {
            newHeight = currentHeight + eventValue;
        }
        this.searchForm.value.suspect.height = newHeight;
    }

}
