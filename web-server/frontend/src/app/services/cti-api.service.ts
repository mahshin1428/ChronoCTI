import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AnalyzeResponse, AttackFlowGraph, ScenarioPreset } from '../models/attack-flow.model';

@Injectable({
  providedIn: 'root'
})
export class CtiApiService {
  private readonly baseUrl = '';

  constructor(private http: HttpClient) {}

  getHealth(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/api/health`);
  }

  getScenarios(): Observable<ScenarioPreset[]> {
    return this.http.get<ScenarioPreset[]>(`${this.baseUrl}/api/scenarios`);
  }

  getScenarioById(id: string): Observable<AttackFlowGraph> {
    return this.http.get<AttackFlowGraph>(`${this.baseUrl}/api/scenarios/${id}`);
  }

  analyzeReport(text: string, reportName: string = 'cti-report'): Observable<AnalyzeResponse> {
    return this.http.post<AnalyzeResponse>(`${this.baseUrl}/api/analyze`, {
      text,
      report_name: reportName,
      asset_threshold: 0.5,
      technique_threshold: 0.5
    });
  }

  uploadFile(file: File): Observable<AnalyzeResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('asset_threshold', '0.5');
    formData.append('technique_threshold', '0.5');
    return this.http.post<AnalyzeResponse>(`${this.baseUrl}/api/upload`, formData);
  }
}
