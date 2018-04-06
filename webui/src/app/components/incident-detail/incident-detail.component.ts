import { Component, Input, OnChanges, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormArray } from '@angular/forms';
import { Location } from '@angular/common';

import { Incident, Address, DateTime, Officer,
         Victim, Suspect, Offense, states, IncidentFile } from '../../data-model';
import { IncidentService } from '../../services/incident.service';
import { ActivatedRoute } from '@angular/router';
import { environment } from '../../../environments/environment';
import { HttpClient } from '@angular/common/http';

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
    incidentFiles: IncidentFile[];

    incidentForm: FormGroup;

    dateString: string;
    timeString: string;

    showSuccessAlert: boolean;
    now: DateTime;
    baseURL = environment.baseURL
    printURL: string;
    activeTab: string;

    states = states;

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
        var now = new DateTime(this.dateString,
                               this.timeString);
        this.now = now;
        this.activeTab = "incident";
    }
    
    ngOnInit() {
        this.getIncident();
    }
    getIncident(): void {
        console.log(this.route.snapshot);
        const id = +this.route.snapshot.paramMap.get("id");
        if (id !== 0) {
            this.incidentService.getIncident(id).subscribe(
                incident => {
                    this.incident = incident;
                    this.printURL = `${this.baseURL}/incidents/print/${this.incident.id}/`
                    this.createForm();
                }
            );
        }
        else {
            console.log("We must be creating a new incident");
            this.incident = new Incident();
            this.incident.location = new Address();
            this.incident.report_datetime = this.now;
            this.incident.reporting_officer = new Officer();
            this.incident.reviewed_datetime = this.now;
            this.incident.approved_datetime = this.now;
            this.incident.reviewed_by_officer = new Officer();
            this.incident.investigating_officer = new Officer();
            this.incident.officer_making_report = new Officer();
            this.incident.supervisor = new Officer();
            this.incident.earliest_occurrence_datetime = this.now;
            this.incident.latest_occurrence_datetime = this.now;
            this.createForm();
        }

        this.incidentService.getAllOffenses().subscribe(
            (availableOffenses) => {
                this.availableOffenses = availableOffenses;
            }
        );

        this.incidentService.getAllOfficers().subscribe(
            officers => {
                this.availableOfficers = officers;
            }
        );
    }

    private getLocation(): Address {
        if (this.incident !== undefined){
            return this.incident.location;
        }
        else {
            return new Address();
        }
    }

    getMyVictims() {
        this.incidentService.getVictims(this.incident.id).
            subscribe((victims) => {
                if (victims.length === 0){
                    console.log("length  was 0");
                    var fakeVictims = new Array<Victim>();
                    fakeVictims.push(new Victim());
                    console.log("fake victims");
                    console.log(fakeVictims);
                    this.incidentVictims = fakeVictims;
                }
                else {
                    this.incidentVictims = victims;
                }
                console.log(this.incidentVictims);
            });
    }

    getMySuspects() {
        this.incidentService.getSuspects(this.incident.id).
            subscribe((suspects) => {
                if (suspects.length === 0){
                    console.log("length  was 0");
                    var fakeSuspects = new Array<Suspect>();
                    fakeSuspects.push(new Suspect());
                    this.incidentSuspects = fakeSuspects;
                }
                else {
                    this.incidentSuspects = suspects;
                }
            });
    }

     createForm() {
        
        this.getMyVictims();
        this.getMySuspects();
        this.incidentService.getFiles(this.incident).subscribe((files) => {
            this.incidentFiles = files;
        });

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
         });
     }

     rebuildForm() {
        console.log("this.incident.reporting_officer")
        console.log(this.incident.reporting_officer);
                
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
            stolen_amount: this.incident.stolen_amount || 0.0,
        });
        this.incidentService.getVictims(this.incident.id).
        subscribe((victims) => {
            this.incidentVictims = victims;
            console.log(this.incidentVictims);
        });

        this.incidentService.getSuspects(this.incident.id).
        subscribe((suspects) => {
            this.incidentSuspects = suspects;
            console.log(this.incidentSuspects);
        });
     }
     /*
     addVictim() {
         this.victims.push(this.formBuilder.group(new Victim()));
     }
     */

     prepareSaveIncident(): Incident {
        const formModel = this.incidentForm.value;
        console.log("formModel.reporting_officer");
        console.log(formModel.reporting_officer);

        const saveIncident: Incident = {
            id: this.incident.id,
            incident_number: formModel.incident_number as string,
            location: formModel.location as Address,
            report_datetime: formModel.report_datetime as DateTime,
            reporting_officer: formModel.reporting_officer.id,
            reviewed_datetime: formModel.reviewed_datetime as DateTime,
            reviewed_by_officer: formModel.reviewed_by_officer.id,
            investigating_officer: formModel.investigating_officer.id,
            officer_making_report: formModel.officer_making_report.id,
            supervisor: formModel.supervisor.id,
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
        console.log("Print button clicked");
        const printURL = `${this.baseURL}/incidents/print/${this.incident.id}/`
        window.location.href = printURL;
     }

     goToVictims() {
        this.activeTab = "victims";
     }

     goToSuspects() {
        this.activeTab = "suspects";
     }

     goToFiles() {
        this.activeTab = "files";
     }

     goToIncident() {
       this.activeTab = "incident";
    }

}
