import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { VictimComponent } from './victim.component';

describe('VictimComponent', () => {
  let component: VictimComponent;
  let fixture: ComponentFixture<VictimComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ VictimComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(VictimComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
