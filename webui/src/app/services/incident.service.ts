import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';
import { Incident, Victim, Suspect, 
         Offense, Officer, IncidentFile } from '../data-model';
import { environment } from '../../environments/environment';
import { RequestOptions } from '@angular/http';
import { Router } from '@angular/router';


@Injectable()
export class IncidentService {
    private incidentsUrl = `${environment.baseURL}/incidents/`;
    private offensesUrl = `${environment.baseURL}/offenses/`
    private officersUrl = `${environment.baseURL}/officers/`
    
    constructor(private http: HttpClient,
                private router: Router) { 
                
            }

    public log(message: string) {
        // console.log('IncidentService: ' + message);
    }

    public getHeaders(): HttpHeaders {
        let accessToken = localStorage.getItem('token')
        let headers = new HttpHeaders({'Content-Type': 'application/json',
                                        'Authorization': `Bearer ${accessToken}`});
        return headers;
    }

    getIncidents(): Observable<Incident[]> {
        return this.http.get<Incident[]>(this.incidentsUrl, { headers: this.getHeaders() }).pipe(
            tap(incidents => this.log(`fetched incidents`)),
            catchError(this.handleError('getIncidents', []))
        );
    }

    getAllOffenses(): Observable<Offense[]> {
        return this.http.get<Offense[]>(this.offensesUrl, {headers: this.getHeaders()}).pipe(
            tap(offenses => this.log(`fetched offenses`)),
            catchError(this.handleError('getOffenses', []))
        );
    }

    getAllOfficers(): Observable<Officer[]> {
        return this.http.get<Officer[]>(this.officersUrl, {headers: this.getHeaders()}).pipe(
            tap(offenses => this.log(`fetched offenses`)),
            catchError(this.handleError('getOffenses', []))
        );
    }

    getIncident(id: number): Observable<Incident> {
        const url = `${this.incidentsUrl}${id}/`;
        return this.http.get<Incident>(url, {headers: this.getHeaders()}).pipe(
            tap(_ => this.log(`fetched incident id=${id}`)),
            catchError(this.handleError<Incident>(`getIncident id=${id}`))
          );
    }

    getVictims(id: number): Observable<Victim[]> {
        const url = `${this.incidentsUrl}${id}/victims/`;
        return this.http.get<Victim[]>(url, {headers: this.getHeaders()}).pipe(
            tap(victims => this.log(`fetched victims`)),
            catchError(this.handleError('getVictims', []))
          );
    }

    addVictim (incidentId: number, victim: Victim): Observable<Victim> {
        const fullURL = `${this.incidentsUrl}${incidentId}/victims/`;
        return this.http.post<Victim>(fullURL, victim, {headers: this.getHeaders()}).pipe(
            tap((victim: Victim) => this.log(`added victim w/ id=${victim.id}`)),
            catchError(this.handleError<Victim>('addIncident'))
        );
    }

    updateVictim(incidentId: number, victim: Victim): Observable<any> {
        const fullURL = `${this.incidentsUrl}${incidentId}/victims/${victim.id}/`
        return this.http.patch(fullURL, victim, {headers: this.getHeaders()}).pipe(
            tap(_ => this.log(`updated victim id=${victim.id}`)),
            catchError(this.handleError<Victim>('updateVictim'))
        );
    }

    addSuspect(incidentId: number, suspect: Suspect): Observable<Suspect> {
        const fullURL = `${this.incidentsUrl}${incidentId}/suspects/`;
        return this.http.post<Suspect>(fullURL, suspect, {headers: this.getHeaders()}).pipe(
            tap((suspect: Suspect) => this.log(`added victim w/ id=${suspect.id}`)),
            catchError(this.handleError<Suspect>('addSuspect'))
        );
    }

    updateSuspect(incidentId: number, suspect: Suspect): Observable<any> {
        const fullURL = `${this.incidentsUrl}${incidentId}/suspects/${suspect.id}/`
        return this.http.patch(fullURL, suspect, {headers: this.getHeaders()}).pipe(
            tap(_ => this.log(`updated suspect id=${suspect.id}`)),
            catchError(this.handleError<Suspect>('updateSuspect'))
        );
    }

    getSuspects(id: number): Observable<Suspect[]> {
        const url = `${this.incidentsUrl}${id}/suspects/`;
        return this.http.get<Suspect[]>(url, {headers: this.getHeaders()}).pipe(
            tap(victims => this.log(`fetched suspects`)),
            catchError(this.handleError('getSuspects', []))
          );
    }

    updateIncident (incident: Incident): Observable<any> {
        return this.http.patch(this.incidentsUrl + incident.id + "/", incident, 
                                {headers: this.getHeaders()}).pipe(
            tap(_ => this.log(`updated incident id=${incident.id}`)),
            catchError(this.handleError<any>('updateIncident'))
          );
    }

    addIncident (incident: Incident): Observable<Incident> {
        return this.http.post<Incident>(this.incidentsUrl, incident, {headers: this.getHeaders()}).pipe(
            tap((incident: Incident) => this.log(`added incident w/ id=${incident.id}`)),
            catchError(this.handleError<Incident>('addIncident'))
        );
    }

    printIncident(incident: Incident) {
        let accessToken = localStorage.getItem('token');
        let headers = new HttpHeaders({'Authorization': `Bearer ${accessToken}`})
        const printURL = `${this.incidentsUrl}print/${incident.id}/`;
        return this.http.get(printURL, {headers: headers, 
                                        responseType: 'blob'});
    }

    getFiles(incident): Observable<IncidentFile[]> {
        const filesURL = `${this.incidentsUrl}${incident.id}/files/`;
        return this.http.get<IncidentFile[]>(filesURL, {headers: this.getHeaders()}).pipe(
            tap(files => this.log("Fetched files")),
            catchError(this.handleError('getFiles', []))
        );
    }

    uploadFile(incident, fileList): Observable<IncidentFile[]> {
        if(fileList.length > 0) {
            
            let accessToken = localStorage.getItem('token');
            let headers = new HttpHeaders({'Accept': "application/json",
                                           'Authorization': `Bearer ${accessToken}`});

            let formData = new FormData();
            for (var i = 0; i < fileList.length; i++){
                const file = fileList[i];
                formData.append('files', file);
            };
            const fullURL = `${this.incidentsUrl}${incident.id}/files/`
            return this.http.post<IncidentFile[]>(`${fullURL}`, formData, {headers: headers}).pipe(
                tap((files: IncidentFile[]) => this.log("Fetched files")),
                catchError(this.handleError('getFiles', []))
            );
        }
    }

    deleteFile(incident, fileId) {
        const fileURL = `${this.incidentsUrl}${incident.id}/files/${fileId}/`;
        return this.http.delete(fileURL, {headers: this.getHeaders()}).pipe(
            tap(data => console.log("deleted the file")),
            catchError(this.handleError('delete file'))
        );
    }

    searchIncidents(searchParams): Observable<any> {
        const searchURL = `${this.incidentsUrl}search/`;
        return this.http.post(searchURL, searchParams, 
                                {headers: this.getHeaders()}).pipe(
            tap(incidents => this.log("searched incidents")),
            catchError(this.handleError('searchIncidents', []))
        )
    }

    private handleError<T> (operation = 'operation', result?: T) {
        return (error: any): Observable<T> => {

            // TODO: send the error to remote logging infrastructure
            console.error(error); // log to console instead
            // TODO: better job of transforming error for user consumption
            this.log(`${operation} failed: ${error.message}`);

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
}

}
