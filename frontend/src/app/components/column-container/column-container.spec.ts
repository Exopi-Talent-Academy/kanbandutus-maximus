import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ColumnContainer } from './column-container';

describe('ColumnContainer', () => {
  let component: ColumnContainer;
  let fixture: ComponentFixture<ColumnContainer>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ColumnContainer],
    }).compileComponents();

    fixture = TestBed.createComponent(ColumnContainer);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
