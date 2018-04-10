import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { LogIn } from '../../data-model';

@Component({
  selector: 'app-landing-page',
  templateUrl: './landing-page.component.html',
  styleUrls: ['./landing-page.component.css']
})
export class LandingPageComponent implements OnInit {

    loginForm: FormGroup;

    constructor(private formBuilder: FormBuilder,
                private authService: AuthService) { }

    createForm(){
        this.loginForm = this.formBuilder.group({
            username: '',
            password: ''
        });
    }

    ngOnInit() {
        this.createForm();
    }

    login() {
        console.log("called the login method");
        console.log(`Username: ${this.loginForm.value.username}`);
        console.log(`Password: ${this.loginForm.value.password}`);
        this.authService.acquireToken(this.loginForm.value as LogIn).
            subscribe(result => {
                console.log("result from auth call");
                console.log(result);
                this.authService.setUpSession(result);
                this.authService.router.navigateByUrl("/incidents");
            });
    }

}
