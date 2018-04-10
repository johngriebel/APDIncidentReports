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
    files: IncidentFile[];
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
        console.log("Uploading files.");
        console.log(event);
        let fileList: FileList = $(event.target)[0].files;
        this.incidentService.uploadFile(this.incident, fileList).subscribe(files => {
            files.forEach(file => {
                this.existingFiles.push(file);
            });
            console.log("Successfully uploaded all files");
            console.log(this.existingFiles);
        });
    }

    private updateFilesAfterDelete(){
        this.incidentService.getFiles(this.incident).subscribe(existingFiles => {
            this.existingFiles = existingFiles;
            this.files = this.existingFiles;

        });
    }

    deleteFiles(){
        console.log("delete files button clicked");
        var deleteCheckboxes = $('.delete-file-check').toArray();
        deleteCheckboxes.forEach(checkBox => {
            const fileId = $(checkBox).data("file-id");
            if ($(checkBox)[0].checked){
                console.log(`About to delete file with ID=${fileId}`);
                this.incidentService.deleteFile(this.incident, fileId).subscribe(data => {
                    console.log("deleted file");
                    this.updateFilesAfterDelete();
                });
            }
        });
        
        this.rebuildForm();
    }

}
