import { Injectable } from '@angular/core';
import { Headers, Http } from '@angular/http';
import { User } from '../data-model';
import 'rxjs/add/operator/toPromise';

@Injectable()
export class AuthService {
    private BASE_URL: string = 'http://localhost:8000/';
    private headers: Headers = new Headers({'Content-Type': 'application/json'});

    constructor(private http: Http) {}

    login(user: User): Promise<any> {
        let url: string = `${this.BASE_URL}api-token-auth/`;
        return this.http.post(url, user, {headers: this.headers}).toPromise();
    }

    test(): string {
        return 'working';
    }

}
