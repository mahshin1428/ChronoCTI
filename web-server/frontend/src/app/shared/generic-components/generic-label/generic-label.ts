import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'generic-label',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './generic-label.html',
  styleUrl: './generic-label.scss'
})
export class GenericLabel {
  readonly text = input<string>('');
  readonly color = input<'blue' | 'green' | 'red' | 'amber' | 'gray'>('blue');
  readonly icon = input<string>('');

  get badgeClasses(): string {
    return `gen-badge gen-badge-${this.color()}`;
  }
}
