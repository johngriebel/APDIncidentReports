import { Component, Input, OnChanges } from '@angular/core';
import { FormBuilder, FormGroup, FormArray } from '@angular/forms';
import { Location } from '@angular/common';

import { Incident, Address, DateTime, Officer,
         Victim, Suspect, Offense } from '../data-model';
import { IncidentService } from '../incident.service';
import { OfficerService } from '../officer.service';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-incident-detail-reactive',
  templateUrl: './incident-detail-reactive.component.html',
  styleUrls: ['./incident-detail-reactive.component.css']
})
export class IncidentDetailReactiveComponent implements OnChanges{
    @Input() incident: Incident;
    availableOfficers: Officer[];
    availableOffenses: Offense[];
    incidentVictims: Victim[];
    incidentSuspects: Suspect[];

    incidentForm: FormGroup;

    dateString: String;
    timeString: String;

    constructor(private formBuilder: FormBuilder,
                private route: ActivatedRoute,
                private incidentService: IncidentService,
                private officerService: OfficerService,
                private ngLocation: Location
            ) {
                var today = new Date();
                var day = today.getDate();
                var month = today.getMonth() + 1;
                var year = today.getFullYear();

                var hours = today.getHours();
                var minutes = today.getMinutes();
                var timeString = hours.toString().padStart(2, "0") + ":" + minutes.toString().padStart(2, "0");

                this.dateString = year.toString() + "-" + month.toString().padStart(2, "0") + "-" + day.toString().padStart(2, "0");
                this.timeString = timeString;
                console.log(this.dateString);
                this.createForm();
            }

     createForm() {
        this.incidentService.getAllOffenses().subscribe(
            (availableOffenses) => {
                this.availableOffenses = availableOffenses;
                console.log(this.availableOffenses);
            }
        );

         this.incidentForm = this.formBuilder.group({
             incident_number: 'Incident number',
             location: this.formBuilder.group({
                 street_number: '',
                 route: '',
                 city: '',
                 postal_code: '',
                 state: ''
             }),
             report_datetime: this.formBuilder.group({
                 date: this.dateString,
                 time: this.timeString,
             }),
             reporting_officer: this.formBuilder.group({
                 id: '',
                 officer_number: '',
                 user: {}
             }),
             reviewed_datetime: this.formBuilder.group({
                date: this.dateString,
                time: this.timeString,
             }),
            reviewed_by_officer: this.formBuilder.group({
                id: '',
                officer_number: '',
                user: {}
            }),
            investigating_officer: this.formBuilder.group({
                id: '',
                officer_number: '',
                user: {}
            }),
            officer_making_report: this.formBuilder.group({
                id: '',
                officer_number: '',
                user: {}
            }),
            supervisor: this.formBuilder.group({
                id: '',
                officer_number: '',
                user: {}
            }),
            approved_datetime: this.formBuilder.group({
                date: this.dateString,
                time: this.timeString,
             }),
             earliest_occurrence_datetime: this.formBuilder.group({
                date: this.dateString,
                time: this.timeString,
             }),
             latest_occurrence_datetime: this.formBuilder.group({
                date: this.dateString,
                time: this.timeString,
             }),
             beat: 0,
             shift: "",
             damaged_amount: 0.0,
             stolen_amount: 0.0,
             offenses: this.availableOffenses,
             narrative: "",

             victims: this.formBuilder.array([]),
             suspects: this.formBuilder.array([]),

         })
     }

     setVictims(victims: Victim[]) {
        const victimFormGroups = victims.map(victim => this.formBuilder.group(victim));
        const victimFormArray = this.formBuilder.array(victimFormGroups);
        this.incidentForm.setControl('victims', victimFormArray);
     }

     setSuspects(suspects: Suspect[]) {
        const suspectFormGroups = suspects.map(suspect => this.formBuilder.group(suspect));
        const suspectFormArray = this.formBuilder.array(suspectFormGroups);
        this.incidentForm.setControl('suspects', suspectFormArray);
     }

     get victims(): FormArray {
         return this.incidentForm.get('victims') as FormArray;
     }

     get suspects(): FormArray {
        return this.incidentForm.get('suspects') as FormArray;
    }

     rebuildForm() {
         if (this.incident !== undefined) {
            console.log("this.incident.reporting_officer")
            console.log(this.incident.reporting_officer);

            this.officerService.getOfficers().subscribe(
                (availableOfficers) => {
                    this.availableOfficers = availableOfficers;
                    console.log(this.availableOfficers);
                }
            );

            

            this.incidentService.getVictims(this.incident.id).
            subscribe((victims) => {
                this.incidentVictims = victims;
                console.log(this.incidentVictims);
                this.setVictims(this.incidentVictims);
            });

            this.incidentService.getSuspects(this.incident.id).
            subscribe((suspects) => {
                this.incidentSuspects = suspects;
                console.log(this.incidentSuspects);
                this.setSuspects(this.incidentSuspects);
            });
            
            this.incidentForm.reset({
                incident_number: this.incident.incident_number,
                location: this.incident.location,
                report_datetime: this.incident.report_datetime,
                reporting_officer: this.incident.reporting_officer,
                reviewed_datetime: this.incident.reviewed_datetime,
                reviewed_by_officer: this.incident.reviewed_by_officer,
                investigating_officer: this.incident.investigating_officer,
                officer_making_report: this.incident.officer_making_report,
                supervisor: this.incident.supervisor,
                approved_datetime: this.incident.approved_datetime,
                earliest_occurrence_datetime: this.incident.earliest_occurrence_datetime,
                latest_occurrence_datetime: this.incident.latest_occurrence_datetime,
                beat: this.incident.beat,
                shift: this.incident.shift,
                offenses: this.incident.offenses,
                narrative: this.incident.narrative,
                damaged_amount: this.incident.damaged_amount || 0.0,
                stolen_amount: this.incident.stolen_amount || 0.0
            });
        }
     }

     addVictim() {
         this.victims.push(this.formBuilder.group(new Victim()));
     }

     ngOnChanges(){
         if (this.incident.id !== 0){
            this.rebuildForm();
         }
     }

     prepareSaveIncident(): Incident {
        const formModel = this.incidentForm.value;
        console.log(this.incident.offenses);
        console.log(formModel.offenses);

        const saveIncident: Incident = {
            id: this.incident.id,
            incident_number: formModel.incident_number as string,
            location: formModel.location as Address,
            report_datetime: formModel.report_datetime as DateTime,
            reporting_officer: formModel.reporting_officer as Officer,
            reviewed_datetime: formModel.reviewed_datetime as DateTime,
            reviewed_by_officer: formModel.reviewed_by_officer as Officer,
            investigating_officer: formModel.investigating_officer as Officer,
            officer_making_report: formModel.officer_making_report as Officer,
            supervisor: formModel.supervisor as Officer,
            approved_datetime: formModel.approved_datetime as DateTime,
            earliest_occurrence_datetime: formModel.earliest_occurrence_datetime as DateTime,
            latest_occurrence_datetime: formModel.latest_occurrence_datetime as DateTime,
            beat: formModel.beat as number,
            shift: formModel.shift as string,
            offenses: formModel.offenses,
            narrative: formModel.narrative as string,
            damaged_amount: formModel.damaged_amount as number,
            stolen_amount: formModel.stolen_amount as number,
        };
        return saveIncident
     }

     onSubmit() {
         console.log("save button clicked");
         this.incident = this.prepareSaveIncident();
         console.log("BADGER")
         console.log(this.incident.location);
         if (this.incident.id != 0){
            this.incidentService.updateIncident(this.incident).subscribe();
         }
         else {
             this.incidentService.addIncident(this.incident).subscribe();
         }
         this.rebuildForm();
     }

}
