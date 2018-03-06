import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { catchError, map, tap } from 'rxjs/operators';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';
import { Incident } from './incident';
import { MessageService } from './message.service';

const httpOptions = {
    headers: new HttpHeaders({'Content-Type': 'application/json'})
}

@Injectable()
export class IncidentService {
    private incidentsUrl = 'http://127.0.0.1:8000/api/incidents/'
    
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

    getIncident(id: number): Observable<Incident> {
        const url = `${this.incidentsUrl}${id}`;
        return this.http.get<Incident>(url).pipe(
            tap(_ => this.log(`fetched incident id=${id}`)),
            catchError(this.handleError<Incident>(`getIncident id=${id}`))
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
