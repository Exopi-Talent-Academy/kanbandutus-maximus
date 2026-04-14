import { Component } from '@angular/core';
import { Container } from '../../shared/container/container';

@Component({
  selector: 'app-header',
  imports: [Container],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class Header {}
