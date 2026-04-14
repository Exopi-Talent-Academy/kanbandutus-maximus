import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EachColumn } from './each-column';

describe('EachColumn', () => {
  let component: EachColumn;
  let fixture: ComponentFixture<EachColumn>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EachColumn],
    }).compileComponents();

    fixture = TestBed.createComponent(EachColumn);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
