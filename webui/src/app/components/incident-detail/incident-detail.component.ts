import { Component, Input, OnChanges, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormArray } from '@angular/forms';
import { Location } from '@angular/common';

import { Incident, Address, DateTime, Officer,
         Victim, Suspect, Offense } from '../../data-model';
import { IncidentService } from '../../services/incident.service';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-incident-detail',
  templateUrl: './incident-detail.component.html',
  styleUrls: ['./incident-detail.component.css']
})


export class IncidentDetailComponent implements OnInit {
    @Input() incident: Incident;
    availableOfficers: Officer[];
    availableOffenses: Offense[];
    incidentVictims: Victim[];
    incidentSuspects: Suspect[];

    incidentForm: FormGroup;

    dateString: string;
    timeString: string;

    showSuccessAlert: boolean;

    constructor(private formBuilder: FormBuilder,
                private route: ActivatedRoute,
                private incidentService: IncidentService,
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
        this.showSuccessAlert = false;
    }
    
    ngOnInit() {
        this.getIncident();
    }

    getIncident(): void {
        const id = +this.route.snapshot.paramMap.get("id");
        console.log("incident id");
        console.log(id);
        if (id !== 0) {
            this.incidentService.getIncident(id).subscribe(
                incident => {
                    this.incident = incident;
                    this.createForm();
                }
            );
        }
        else {
            console.log("We must be creating a new incident");
            var now: DateTime = {
                date: this.dateString,
                time: this.timeString
            }
            this.incident = new Incident();
            this.incident.location = new Address();
            this.incident.report_datetime = now;
            this.incident.reporting_officer = new Officer();
            this.incident.reviewed_datetime = now;
            this.incident.approved_datetime = now;
            this.incident.reviewed_by_officer = new Officer();
            this.incident.investigating_officer = new Officer();
            this.incident.officer_making_report = new Officer();
            this.incident.supervisor = new Officer();
            this.incident.earliest_occurrence_datetime = now;
            this.incident.latest_occurrence_datetime = now;
            this.createForm();
        }

        this.incidentService.getAllOffenses().subscribe(
            (availableOffenses) => {
                this.availableOffenses = availableOffenses;
                console.log(this.availableOffenses);
            }
        );

        this.incidentService.getAllOfficers().subscribe(
            officers => {
                this.availableOfficers = officers;
                console.log("Got officers");
                console.log(this.availableOfficers);
            }
        );
    }

    get dataIsReady(): boolean {
        return (this.incident !== undefined && this.availableOfficers !== undefined && this.availableOffenses !== undefined);
    }


    private getLocation(): Address {
        if (this.incident !== undefined){
            return this.incident.location;
        }
        else {
            return new Address();
        }
    }

     createForm() {

         this.incidentForm = this.formBuilder.group({
             incident_number: this.incident.incident_number,
             location: this.formBuilder.group({
                 street_number: this.incident.location.street_number,
                 route: this.incident.location.route,
                 city: this.incident.location.city,
                 postal_code: this.incident.location.postal_code,
                 state: this.incident.location.state
             }),
             report_datetime: this.formBuilder.group({
                 date: this.incident.report_datetime.date,
                 time: this.incident.report_datetime.time,
             }),
             reporting_officer: this.formBuilder.group({
                 id: this.incident.reporting_officer.id,
                 officer_number: this.incident.reporting_officer.officer_number,
                 user: this.incident.reporting_officer.user
             }),
             reviewed_datetime: this.formBuilder.group({
                date: this.incident.reviewed_datetime.date,
                time: this.incident.reviewed_datetime.time,
             }),
            reviewed_by_officer: this.formBuilder.group({
                id: this.incident.reviewed_by_officer.id,
                 officer_number: this.incident.reviewed_by_officer.officer_number,
                 user: this.incident.reviewed_by_officer.user
            }),
            investigating_officer: this.formBuilder.group({
                id: this.incident.investigating_officer.id,
                 officer_number: this.incident.investigating_officer.officer_number,
                 user: this.incident.investigating_officer.user
            }),
            officer_making_report: this.formBuilder.group({
                id: this.incident.officer_making_report.id,
                 officer_number: this.incident.officer_making_report.officer_number,
                 user: this.incident.officer_making_report.user
            }),
            supervisor: this.formBuilder.group({
                id: this.incident.supervisor.id,
                 officer_number: this.incident.supervisor.officer_number,
                 user: this.incident.supervisor.user
            }),
            approved_datetime: this.formBuilder.group({
                date: this.incident.approved_datetime.date,
                time: this.incident.approved_datetime.time,
             }),
             earliest_occurrence_datetime: this.formBuilder.group({
                date: this.incident.earliest_occurrence_datetime.date,
                time: this.incident.earliest_occurrence_datetime.time,
             }),
             latest_occurrence_datetime: this.formBuilder.group({
                date: this.incident.latest_occurrence_datetime.date,
                time: this.incident.latest_occurrence_datetime.time,
             }),
             beat: this.incident.beat,
             shift: this.incident.shift,
             damaged_amount: this.incident.damaged_amount,
             stolen_amount: this.incident.stolen_amount,
             offenses: this.availableOffenses,
             narrative: this.incident.narrative,

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
        console.log("this.incident.reporting_officer")
        console.log(this.incident.reporting_officer);
        

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

     addVictim() {
         this.victims.push(this.formBuilder.group(new Victim()));
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
         this.incident = this.prepareSaveIncident();
         console.log(this.incident.location);
         if (this.incident.id != 0){
            this.incidentService.updateIncident(this.incident).subscribe();
            this.showSuccessAlert = true;
         }
         else {
             this.incidentService.addIncident(this.incident).subscribe(incident => {
                 console.log(incident);
                 this.showSuccessAlert = true;
             });
         }
         this.rebuildForm();
     }

     print(){
         console.log("Print button clicked")
     }

}
