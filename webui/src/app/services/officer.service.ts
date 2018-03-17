import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { catchError, map, tap } from 'rxjs/operators';
import { MessageService } from './message.service';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';
import { Officer } from '../data-model';

@Injectable()
export class OfficerService {
    private officersUrl = 'http://127.0.0.1:8000/api/officers/'
    constructor(private messageService: MessageService,
        private http: HttpClient) { }

    public log(message: string) {
        this.messageService.add('OfficerService: ' + message);
    }

    getOfficers(): Observable<Officer[]> {
        let headers = new HttpHeaders({'Content-Type': 'application/json',
                                            'Authorization': `Bearer ${localStorage.getItem('token')}`});
        return this.http.get<Officer[]>(this.officersUrl, {headers: headers}).pipe(
            tap(officers => this.log(`fetched officers`)),
            catchError(this.handleError('getOfficers', []))
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
