import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs/Observable';
import { JwtHelperService } from '@auth0/angular-jwt';
import { LogIn } from '../data-model';
import { Router } from '@angular/router';

@Injectable()
export class AuthService {

    private baseURL = `${environment.baseURL}/auth/`
    isLoggedIn = false;

    constructor(private http: HttpClient,
                public router: Router) { }

    public getHeaders(): HttpHeaders {
        let headers = new HttpHeaders({'Content-Type': 'application/json'});
        return headers;
    }

    acquireToken(logInData: LogIn): Observable<any> {
        const fullURL = `${this.baseURL}token-auth/`
        return this.http.post(fullURL, logInData,
                              {headers: this.getHeaders()});
    }

    setUpSession(authResult) {
        localStorage.setItem('loggedInOfficer', JSON.stringify(authResult.officer));
        localStorage.setItem('token', authResult.token);
        const helper = new JwtHelperService();
        const decodedToken = helper.decodeToken(authResult.token);
        localStorage.setItem('tokenExpiry', decodedToken.exp);
        this.isLoggedIn = true;
        console.log("Successfully set up session");
    }

    private logOut(){
        localStorage.setItem('loggedInOfficer', null);
        localStorage.setItem('token', null);
        localStorage.setItem('tokenExpiry', null);
        this.router.navigateByUrl("/landing-page");

    }

    private checkLoggedIn(): boolean {
        var token = localStorage.getItem('token');
        var tokenExpiry = parseInt(localStorage.getItem('tokenExpiry'));
        const now = Date.now();

        if (now < tokenExpiry && token != undefined){
            return true;
        }
        else{
            console.log("Either token has expired or the officer was never logged in. Resetting session");
            this.logOut();
            return false;
        }

    }

}
