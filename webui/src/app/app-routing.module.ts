import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { IncidentsComponent } from './incidents/incidents.component';
import { IncidentDetailComponent } from './incident-detail/incident-detail.component';
import { IncidentDetailReactiveComponent } from './incident-detail-reactive/incident-detail-reactive.component';

const routes: Routes = [
    {path: '', component: IncidentsComponent},
    {path: 'incidents/:id', component: IncidentDetailComponent},
    {path: 'incidents-reactive/:id', component: IncidentDetailReactiveComponent}
];


@NgModule({
    exports: [RouterModule],
    imports: [
        RouterModule.forRoot(routes)
    ],
})
export class AppRoutingModule { }
