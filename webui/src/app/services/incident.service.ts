import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';
import { Incident, Victim, Suspect, Offense, Officer } from '../data-model';
import { environment } from '../../environments/environment';


@Injectable()
export class IncidentService {
    private incidentsUrl = `${environment.baseURL}/incidents/`;
    private offensesUrl = `${environment.baseURL}/offenses/`
    private officersUrl = `${environment.baseURL}/officers/`
    
    constructor(private http: HttpClient) { 
                
            }

    public log(message: string) {
        console.log('IncidentService: ' + message);
    }

    public getHeaders(): HttpHeaders {
        let headers = new HttpHeaders({'Content-Type': 'application/json'});
        return headers;
    }

    getIncidents(): Observable<Incident[]> {
        let headers = new HttpHeaders({'Content-Type': 'application/json'});
        return this.http.get<Incident[]>(this.incidentsUrl, { headers: headers }).pipe(
            tap(incidents => this.log(`fetched incidents`)),
            catchError(this.handleError('getIncidents', []))
        );
    }

    getAllOffenses(): Observable<Offense[]> {
        let headers = new HttpHeaders({'Content-Type': 'application/json'});
        return this.http.get<Offense[]>(this.offensesUrl, {headers: headers}).pipe(
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
        let headers = new HttpHeaders({'Content-Type': 'application/json'});
        const url = `${this.incidentsUrl}${id}`;
        return this.http.get<Incident>(url, {headers: headers}).pipe(
            tap(_ => this.log(`fetched incident id=${id}`)),
            catchError(this.handleError<Incident>(`getIncident id=${id}`))
          );
    }

    getVictims(id: number): Observable<Victim[]> {
        let headers = new HttpHeaders({'Content-Type': 'application/json'});
        const url = `${this.incidentsUrl}${id}/victims/`;
        return this.http.get<Victim[]>(url, {headers: headers}).pipe(
            tap(victims => this.log(`fetched victims`)),
            catchError(this.handleError('getVictims', []))
          );
    }

    updateVictim(incidentId: number, victim: Victim): Observable<any> {
        const fullURL = `${this.incidentsUrl}${incidentId}/victims/${victim.id}/`
        return this.http.patch(fullURL, victim, {headers: this.getHeaders()}).pipe(
            tap(_ => this.log(`updated victim id=${victim.id}`)),
            catchError(this.handleError<Victim>('updateVictim'))
        );
    }

    getSuspects(id: number): Observable<Suspect[]> {
        let headers = new HttpHeaders({'Content-Type': 'application/json'});
        const url = `${this.incidentsUrl}${id}/suspects/`;
        return this.http.get<Suspect[]>(url, {headers: headers}).pipe(
            tap(victims => this.log(`fetched suspects`)),
            catchError(this.handleError('getSuspects', []))
          );
    }

    updateIncident (incident: Incident): Observable<any> {
        let headers = new HttpHeaders({'Content-Type': 'application/json'});
        return this.http.patch(this.incidentsUrl + incident.id + "/", incident, {headers: headers}).pipe(
            tap(_ => this.log(`updated incident id=${incident.id}`)),
            catchError(this.handleError<any>('updateIncident'))
          );
    }

    addIncident (incident: Incident): Observable<Incident> {
        let headers = new HttpHeaders({'Content-Type': 'application/json'});
        return this.http.post<Incident>(this.incidentsUrl, incident, {headers: headers}).pipe(
            tap((incident: Incident) => this.log(`added incident w/ id=${incident.id}`)),
            catchError(this.handleError<Incident>('addIncident'))
        );
    }

    printIncident(incident: Incident): Observable<Incident> {
        const printURL = `${this.incidentsUrl}print/${incident.id}/`
        console.log(printURL);
        return this.http.get<Incident>(printURL, {headers: this.getHeaders()});
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
