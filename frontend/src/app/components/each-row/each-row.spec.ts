import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EachRow } from './each-row';

describe('EachRow', () => {
  let component: EachRow;
  let fixture: ComponentFixture<EachRow>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EachRow],
    }).compileComponents();

    fixture = TestBed.createComponent(EachRow);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
