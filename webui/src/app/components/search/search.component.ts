import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import * as $ from 'jquery';
import { IncidentService } from '../../services/incident.service';
import { DateTime, Officer, Offense, Incident,
         eye_colors, states, hair_colors } from '../../data-model';

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
        this.incidentService.getAllOffenses().subscribe(offenses => {
            this.availableOffenses = offenses;
            this.createForm();
        });
    }

    onSubmit() {
        console.log("In the onSubmit method");
        console.log(this.searchForm.value);
        this.incidentService.searchIncidents(
            {incident_number: this.searchForm.value.incident_number}).subscribe(incidents => {
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
            min_report_datetime: this.formBuilder.group({date: '', time: ''}),
            max_report_datetime: this.formBuilder.group({date: '', time: ''}),
            reporting_officer: this.formBuilder.group({
                id: 0,
                officer_number: 0,
                user: {}
            }),
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
