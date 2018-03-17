import { Component, OnInit } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { User } from '../data-model';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent  {

    user: User = new User();

    constructor(private authService: AuthService,
                private router: Router) { }

    onLogin(): void {
        this.authService.login(this.user).then((user) => {
            var officerObject = user.json().officer;
            console.log("INITIAL OFFICER OBJECT");
            console.log(officerObject)
            localStorage.setItem('token', user.json().token);
            localStorage.setItem('loggedIn', "true");
            localStorage.setItem('officer', JSON.stringify(officerObject));
            console.log(user.json());
            this.router.navigateByUrl('');
        })
        .catch((err) => {
          console.log(err);
        });
      }
}
