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
            localStorage.setItem('token', user.json().token);
            localStorage.setItem('loggedIn', "true");
            this.router.navigateByUrl('');
        })
        .catch((err) => {
          console.log(err);
        });
      }
}
