import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { AppComponent } from './app.component';
import { IncidentsComponent } from './incidents/incidents.component';
import { IncidentDetailComponent } from './incident-detail/incident-detail.component';
import { IncidentService } from './incident.service';
import { MessageService } from './message.service';
import { MessagesComponent } from './messages/messages.component';
import { HttpClientModule } from '@angular/common/http';
import { AppRoutingModule } from './/app-routing.module';
import { OfficerService } from './officer.service';
import { IncidentDetailReactiveComponent } from './incident-detail-reactive/incident-detail-reactive.component';


@NgModule({
  declarations: [
    AppComponent,
    IncidentsComponent,
    IncidentDetailComponent,
    MessagesComponent,
    IncidentDetailReactiveComponent,
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    AppRoutingModule,
    FormsModule,
    ReactiveFormsModule
  ],
  providers: [IncidentService, 
              MessageService, 
              OfficerService],
  bootstrap: [AppComponent]
})
export class AppModule { }
