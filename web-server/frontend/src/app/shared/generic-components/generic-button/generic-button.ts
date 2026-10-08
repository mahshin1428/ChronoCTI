import { Component, input, output } from '@angular/core';
import { CommonModule, NgClass } from '@angular/common';

@Component({
  selector: 'generic-button',
  standalone: true,
  imports: [CommonModule, NgClass],
  templateUrl: './generic-button.html',
  styleUrl: './generic-button.scss'
})
export class GenericButton {
  // Inputs
  readonly id = input<string>('');
  readonly value = input<string>('');
  readonly cssClass = input<string>('');
  readonly styles = input<string>('');
  readonly enable = input<boolean>(true);
  readonly visible = input<boolean>(true);
  readonly label = input<string>('');
  readonly icon = input<string>('');

  // Outputs
  readonly valueChanged = output<string>();
  readonly onClick = output<MouseEvent>();

  get isDisabled(): boolean {
    return !this.enable();
  }

  get isHidden(): boolean {
    return !this.visible();
  }

  get buttonClasses(): string {
    const baseClasses = 'gen-btn ';
    const stateClasses = this.isDisabled ? 'gen-btn-disabled' : '';
    const customClasses = this.cssClass() || 'gen-btn-primary';
    return `${baseClasses} ${customClasses} ${stateClasses}`.trim();
  }

  onButtonClick(event: MouseEvent) {
    if (!this.isDisabled) {
      this.onClick.emit(event);
      this.valueChanged.emit(this.value());
    }
  }
}
