import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface GenericTableColumn {
  key: string;
  label: string;
  width?: string;
  type?: 'text' | 'badge' | 'number';
  badgeColor?: (val: any) => string;
}

@Component({
  selector: 'generic-table',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './generic-table.html',
  styleUrl: './generic-table.scss'
})
export class GenericTable {
  readonly columns = input<GenericTableColumn[]>([]);
  readonly data = input<any[]>([]);
  readonly title = input<string>('');
  readonly emptyMessage = input<string>('No data available');

  formatValue(col: GenericTableColumn, row: any): any {
    const val = row[col.key];
    return val !== undefined && val !== null ? val : '-';
  }

  getBadgeClass(col: GenericTableColumn, row: any): string {
    if (col.badgeColor) {
      return col.badgeColor(row[col.key]);
    }
    return 'badge-blue';
  }
}
