import { Component, output, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CtiApiService } from '../../services/cti-api.service';
import { AnalyzeResponse } from '../../models/attack-flow.model';

@Component({selector: 'app-report-analyzer', standalone: true, imports: [CommonModule, FormsModule],
  templateUrl: './report-analyzer.html', styleUrl: './report-analyzer.scss'})
export class ReportAnalyzerComponent {
  readonly onAnalysisComplete = output<AnalyzeResponse>();
  readonly busyChange = output<boolean>();
  reportText = '';
  reportName = '';
  isAnalyzing = signal(false);
  errorMessage = signal('');
  constructor(private ctiApi: CtiApiService) {}
  loadExample() {
    this.reportName = 'Example · Remote access intrusion';
    this.reportText = 'The attacker used valid accounts to access the VPN.\nThe attacker then used PowerShell on the workstation to execute a script.\nThe script downloaded additional tools onto the workstation.\nNext, the attacker used RDP to access the server.\nThe attacker used credential dumping on the server to obtain more credentials.\nFinally, ransomware encrypted files on the server and the workstation.';
    this.errorMessage.set('');
  }
  runAnalysis() {
    if (this.isAnalyzing()) return;
    if (this.reportText.trim().length < 5) { this.errorMessage.set('Add a report with at least five characters.'); return; }
    this.isAnalyzing.set(true); this.busyChange.emit(true); this.errorMessage.set('');
    this.ctiApi.analyzeReport(this.reportText, this.reportName.trim() || 'Untitled report').subscribe({
      next: result => { this.isAnalyzing.set(false); this.busyChange.emit(false); this.onAnalysisComplete.emit(result); },
      error: error => { this.isAnalyzing.set(false); this.busyChange.emit(false); this.errorMessage.set(typeof error.error?.detail === 'string' ? error.error.detail : 'Could not analyze this report. Check that the server is running and try again.'); }
    });
  }
  async onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement, file = input.files?.[0];
    if (!file || this.isAnalyzing()) return;
    input.value = '';
    if (file.size > 5 * 1024 * 1024) { this.errorMessage.set('Please use a text report smaller than 5 MB.'); return; }
    try {
      this.reportText = await file.text(); this.reportName = file.name; this.errorMessage.set('');
    } catch { this.errorMessage.set('Could not read this file. Please paste the report text instead.'); }
  }
}
