import { NgModule } from '@angular/core';
import { RouterModule, Routes, CanActivate } from '@angular/router';
import { LandingPageComponent } from './components/landing-page/landing-page.component';
import { IncidentsComponent } from './components/incidents/incidents.component';
import { IncidentDetailComponent } from './components/incident-detail/incident-detail.component';

const routes: Routes = [
    {path: '', redirectTo: 'dashboard', pathMatch: 'full'},
    {path: 'dashboard', component: LandingPageComponent},
    {path: 'incidents', component: IncidentsComponent},
    {path: 'incidents/:id', component: IncidentDetailComponent},
    {path: 'create-incident', component: IncidentDetailComponent}
];


@NgModule({
    exports: [RouterModule],
    imports: [
        RouterModule.forRoot(routes)
    ]
})
export class AppRoutingModule { }
