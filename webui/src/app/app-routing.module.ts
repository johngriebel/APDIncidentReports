import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { IncidentsComponent } from './incidents/incidents.component';
import { IncidentDetailComponent } from './incident-detail/incident-detail.component';

const routes: Routes = [
    {path: '', component: IncidentsComponent},
    {path: 'incidents/:id', component: IncidentDetailComponent}
];


@NgModule({
    exports: [RouterModule],
    imports: [
        RouterModule.forRoot(routes)
    ],
})
export class AppRoutingModule { }
