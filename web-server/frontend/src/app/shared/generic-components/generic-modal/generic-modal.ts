import { Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'generic-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './generic-modal.html',
  styleUrl: './generic-modal.scss'
})
export class GenericModal {
  readonly isOpen = input<boolean>(false);
  readonly title = input<string>('Details');
  readonly closeOnBackdrop = input<boolean>(true);

  readonly onClose = output<void>();

  closeModal() {
    this.onClose.emit();
  }

  onBackdropClick(event: MouseEvent) {
    if (this.closeOnBackdrop() && (event.target as HTMLElement).classList.contains('gen-modal-overlay')) {
      this.closeModal();
    }
  }
}
