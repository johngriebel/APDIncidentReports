import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';
import { Incident, Victim, Suspect, Offense } from './data-model';
import { MessageService } from './message.service';

const httpOptions = {
    headers: new HttpHeaders({'Content-Type': 'application/json'})
}

@Injectable()
export class IncidentService {
    private incidentsUrl = 'http://127.0.0.1:8000/api/incidents/'
    private offensesUrl = 'http://127.0.0.1:8000/api/offenses/'
    
    constructor(private messageService: MessageService,
                private http: HttpClient) { }

    public log(message: string) {
        this.messageService.add('IncidentService: ' + message);
    }

    getIncidents(): Observable<Incident[]> {
        return this.http.get<Incident[]>(this.incidentsUrl).pipe(
            tap(incidents => this.log(`fetched incidents`)),
            catchError(this.handleError('getIncidents', []))
        );
    }

    getAllOffenses(): Observable<Offense[]> {
        return this.http.get<Offense[]>(this.offensesUrl).pipe(
            tap(offenses => this.log(`fetched offenses`)),
            catchError(this.handleError('getOffenses', []))
        );
    }

    getIncident(id: number): Observable<Incident> {
        const url = `${this.incidentsUrl}${id}`;
        return this.http.get<Incident>(url).pipe(
            tap(_ => this.log(`fetched incident id=${id}`)),
            catchError(this.handleError<Incident>(`getIncident id=${id}`))
          );
    }

    getVictims(id: number): Observable<Victim[]> {
        const url = `${this.incidentsUrl}${id}/victims/`;
        return this.http.get<Victim[]>(url).pipe(
            tap(victims => this.log(`fetched victims`)),
            catchError(this.handleError('getVictims', []))
          );
    }

    getSuspects(id: number): Observable<Suspect[]> {
        const url = `${this.incidentsUrl}${id}/suspects/`;
        return this.http.get<Suspect[]>(url).pipe(
            tap(victims => this.log(`fetched suspects`)),
            catchError(this.handleError('getSuspects', []))
          );
    }

    updateIncident (incident: Incident): Observable<any> {
        // console.log(incident.location);
        console.log(incident.damaged_amount);
        return this.http.patch(this.incidentsUrl + incident.id + "/", incident, httpOptions).pipe(
            tap(_ => this.log(`updated incident id=${incident.id}`)),
            catchError(this.handleError<any>('updateIncident'))
          );
    }

    addIncident (incident: Incident): Observable<Incident> {
        console.log(incident);
        return this.http.post<Incident>(this.incidentsUrl, incident, httpOptions).pipe(
            tap((incident: Incident) => this.log(`added incident w/ id=${incident.id}`)),
            catchError(this.handleError<Incident>('addIncident'))
        );
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
