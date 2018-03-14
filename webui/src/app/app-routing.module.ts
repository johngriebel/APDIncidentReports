import { NgModule } from '@angular/core';
import { RouterModule, Routes, CanActivate } from '@angular/router';
import { IncidentsComponent } from './incidents/incidents.component';
import { LoginComponent } from './login/login.component';

const routes: Routes = [
    {path: '', component: IncidentsComponent},
    {path: 'login', component: LoginComponent}
];


@NgModule({
    exports: [RouterModule],
    imports: [
        RouterModule.forRoot(routes)
    ]
})
export class AppRoutingModule { }
