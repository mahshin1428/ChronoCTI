import { Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ScenarioPreset } from '../../models/attack-flow.model';

@Component({
  selector: 'app-scenario-selector',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './scenario-selector.html',
  styleUrl: './scenario-selector.scss'
})
export class ScenarioSelectorComponent {
  readonly scenarios = input<ScenarioPreset[]>([]);
  readonly activeScenarioId = input<string>('equifax');
  readonly onScenarioChange = output<string>();

  selectScenario(id: string) {
    this.onScenarioChange.emit(id);
  }
}
