export interface Evidence { sentence_id: number; text: string; }

export interface AttackFlowNode {
  id: string;
  type: 'technique' | 'asset' | 'logic_gate' | 'condition';
  raw_id: string;
  label: string;
  subtitle?: string;
  category?: string;
  confidence: number;
  sentence_id?: number;
  sentence_text?: string;
  occurrence_count?: number;
  evidence?: Evidence[];
  prediction_sources?: string[];
  x: number;
  y: number;
  width: number;
  height: number;
  branches?: Array<{ type: string; label: string }>;
}

export interface AttackFlowEdge {
  id: string;
  source: string;
  target: string;
  relation: string;
  edge_type: string;
  evidence?: Evidence[];
  basis?: string;
  label?: string;
  branch?: string;
  start_point?: [number, number];
  end_point?: [number, number];
  path_points?: Array<[number, number]>;
}

export interface AttackFlowMetrics {
  total_nodes: number;
  total_edges: number;
  is_dag: boolean;
  longest_attack_chain: number;
  density: number;
}

export interface AttackFlowGraph {
  title?: string;
  description?: string;
  nodes: AttackFlowNode[];
  edges: AttackFlowEdge[];
  canvas_width: number;
  canvas_height: number;
  metrics: AttackFlowMetrics;
}

export interface UniqueAssetSummary {
  id: string;
  name: string;
  occurrence_count: number;
  highest_confidence: number;
  matched_sentences: number[];
}

export interface UniqueTechniqueSummary {
  id: string;
  name: string;
  occurrence_count: number;
  highest_confidence: number;
  matched_sentences: number[];
}

export interface AnalyzeResponse {
  report_name: string;
  total_sentences: number;
  summary: {
    total_unique_assets: number;
    total_unique_techniques: number;
    total_graph_nodes: number;
    total_graph_edges: number;
    longest_attack_chain: number;
  };
  assets: UniqueAssetSummary[];
  techniques: UniqueTechniqueSummary[];
  sentences: any[];
  attack_flow: AttackFlowGraph;
}

export interface ScenarioPreset {
  id: string;
  name: string;
  description: string;
}
