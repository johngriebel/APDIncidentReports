import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'APD';
  loggedIn: boolean = false;
  constructor(private router: Router) {
      this.loggedIn = (localStorage.getItem('loggedIn') == "true");
      console.log("this.logged in");
      console.log(this.loggedIn);
  }

    login(){
        console.log("In login method");
        this.router.navigateByUrl("/login");
    }

    logout(){
        console.log("logout button clicked")
    }
}
