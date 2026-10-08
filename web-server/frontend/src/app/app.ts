import { Component, HostListener, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { AnalyzeResponse, AttackFlowGraph } from './models/attack-flow.model';
import { AttackFlowCanvasComponent } from './components/attack-flow-canvas/attack-flow-canvas';
import { ReportAnalyzerComponent } from './components/report-analyzer/report-analyzer';

@Component({selector: 'app-root', standalone: true,
  imports: [CommonModule, HttpClientModule, AttackFlowCanvasComponent, ReportAnalyzerComponent],
  templateUrl: './app.html', styleUrl: './app.scss'})
export class AppComponent {
  currentGraph = signal<AttackFlowGraph | null>(null);
  result = signal<AnalyzeResponse | null>(null);
  isAnalyzing = signal(false);
  sidebarWidth = signal(340);
  isDraggingSidebar = signal(false);
  isSidebarCollapsed = signal(false);
  onAnalysisResult(result: AnalyzeResponse) { this.result.set(result); this.currentGraph.set(result.attack_flow); }
  onResizerMouseDown(event: MouseEvent) { event.preventDefault(); this.isDraggingSidebar.set(true); }
  @HostListener('window:mousemove', ['$event'])
  onWindowMouseMove(event: MouseEvent) {
    if (this.isDraggingSidebar()) this.sidebarWidth.set(Math.max(280, Math.min(event.clientX, Math.min(550, window.innerWidth - 400))));
  }
  @HostListener('window:mouseup') onWindowMouseUp() { this.isDraggingSidebar.set(false); }
  toggleSidebar() { this.isSidebarCollapsed.update(value => !value); }
}
