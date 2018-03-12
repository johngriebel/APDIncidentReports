import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { IncidentDetailReactiveComponent } from './incident-detail-reactive.component';

describe('IncidentDetailReactiveComponent', () => {
  let component: IncidentDetailReactiveComponent;
  let fixture: ComponentFixture<IncidentDetailReactiveComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ IncidentDetailReactiveComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(IncidentDetailReactiveComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
