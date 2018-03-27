import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { AppComponent } from './app.component';
import { IncidentsComponent } from './components/incidents/incidents.component';
import { IncidentService } from './services/incident.service';
import { MessageService } from './services/message.service';
import { MessagesComponent } from './components/messages/messages.component';
import { HttpModule } from '@angular/http';
import { HttpClientModule } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { OfficerService } from './services/officer.service';
import { IncidentDetailComponent } from './components/incident-detail/incident-detail.component';
import { LandingPageComponent } from './components/landing-page/landing-page.component';
import { VictimComponent } from './components/victim/victim.component';


@NgModule({
  declarations: [
    AppComponent,
    IncidentsComponent,
    MessagesComponent,
    IncidentDetailComponent,
    LandingPageComponent,
    VictimComponent,
  ],
  imports: [
    BrowserModule,
    HttpModule,
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
