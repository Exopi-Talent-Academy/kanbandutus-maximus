import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddNewTask } from './add-new-task';

describe('AddNewTask', () => {
  let component: AddNewTask;
  let fixture: ComponentFixture<AddNewTask>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddNewTask],
    }).compileComponents();

    fixture = TestBed.createComponent(AddNewTask);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
