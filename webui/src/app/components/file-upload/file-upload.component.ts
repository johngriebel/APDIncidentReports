import { Component, OnInit, Input, OnChanges } from '@angular/core';
import { RequestOptions } from '@angular/http';
import * as $ from 'jquery';
import { Incident, IncidentFile } from '../../data-model';
import {IncidentService} from '../../services/incident.service';
import { FormGroup, FormBuilder } from '@angular/forms';

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css']
})
export class FileUploadComponent implements OnInit, OnChanges {
    @Input() incident: Incident;
    @Input() existingFiles: IncidentFile[];
    fileUploadForm: FormGroup;
    files: FileList;
    constructor(private incidentService: IncidentService,
                private formBuilder: FormBuilder) {
        this.createForm();
    }

    ngOnInit() {
        console.log("existingFiles");
        console.log(this.existingFiles);
    }

    ngOnChanges() {
        this.rebuildForm();
    }

    createForm(){
        console.log("In create form");
        this.fileUploadForm = this.formBuilder.group({
            files: []
        });
    }

    rebuildForm() {
        this.fileUploadForm.reset({
            files: this.files
        });
    }

    fileChange(event) {
        console.log("in file change methd");
        console.log("event");
        console.log($(event.target));
        let fileList: FileList = $(event.target)[0].files;
        console.log(fileList);
        // this.incidentService.uploadFile(this.incident, fileList);
    }

    deleteFiles(){
        console.log("delete files button clicked");
        var deleteCheckboxes = $('.delete-file-check').toArray();
        console.log(deleteCheckboxes);
    }

}
