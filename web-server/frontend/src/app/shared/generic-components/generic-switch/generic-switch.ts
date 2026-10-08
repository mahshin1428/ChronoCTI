import { Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'generic-switch',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './generic-switch.html',
  styleUrl: './generic-switch.scss'
})
export class GenericSwitch {
  readonly id = input<string>('');
  readonly label = input<string>('');
  readonly isChecked = input<boolean>(false);
  readonly enable = input<boolean>(true);

  readonly onSwitchChanged = output<boolean>();

  toggle(event: Event) {
    if (this.enable()) {
      const checked = (event.target as HTMLInputElement).checked;
      this.onSwitchChanged.emit(checked);
    }
  }
}
