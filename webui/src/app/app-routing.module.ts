import { NgModule } from '@angular/core';
import { RouterModule, Routes, CanActivate } from '@angular/router';
import { IncidentsComponent } from './components/incidents/incidents.component';
import { LoginComponent } from './components/login/login.component';

const routes: Routes = [
    {path: '', component: IncidentsComponent},
];


@NgModule({
    exports: [RouterModule],
    imports: [
        RouterModule.forRoot(routes)
    ]
})
export class AppRoutingModule { }
