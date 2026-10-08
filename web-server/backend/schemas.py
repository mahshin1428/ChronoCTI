from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="Raw CTI report text")
    report_name: Optional[str] = Field("cti-report", description="Name or identifier of the report")
    asset_threshold: Optional[float] = Field(0.5, description="Classification confidence threshold for assets")
    technique_threshold: Optional[float] = Field(0.5, description="Classification confidence threshold for techniques")

class AssetDetail(BaseModel):
    id: str
    name: str
    confidence: float
    sentence_id: int
    sentence_text: str
    prediction_source: str = "classifier"

class UniqueAssetSummary(BaseModel):
    id: str
    name: str
    occurrence_count: int
    highest_confidence: float
    matched_sentences: List[int]

class TechniqueDetail(BaseModel):
    id: str
    name: str
    confidence: float
    sentence_id: int
    sentence_text: str
    prediction_source: str = "classifier"

class UniqueTechniqueSummary(BaseModel):
    id: str
    name: str
    occurrence_count: int
    highest_confidence: float
    matched_sentences: List[int]

class SentenceItem(BaseModel):
    sentence_id: int
    text: str
    assets: List[AssetDetail]
    techniques: List[TechniqueDetail]
    temporal_signals: List[str]

# --- Attack Flow Schemas (NetworkX powered) ---

class Evidence(BaseModel):
    sentence_id: int
    text: str

class AttackFlowNode(BaseModel):
    id: str
    type: str  # "technique", "asset", "logic_gate", "condition"
    raw_id: str
    label: str
    subtitle: Optional[str] = ""
    category: Optional[str] = ""
    confidence: float = 1.0
    occurrence_count: int = 1
    evidence: List[Evidence] = Field(default_factory=list)
    prediction_sources: List[str] = Field(default_factory=list)
    sentence_id: Optional[int] = None
    sentence_text: Optional[str] = ""
    x: float
    y: float
    width: float
    height: float
    branches: Optional[List[Dict[str, str]]] = None

class AttackFlowEdge(BaseModel):
    id: str
    source: str
    target: str
    relation: str  # "REPORT_ORDER" or "CO_MENTIONED"
    edge_type: str = "temporal"
    evidence: List[Evidence] = Field(default_factory=list)
    basis: str = ""
    label: Optional[str] = ""
    branch: Optional[str] = None
    start_point: Optional[List[float]] = None
    end_point: Optional[List[float]] = None
    path_points: Optional[List[List[float]]] = None

class AttackFlowMetrics(BaseModel):
    total_nodes: int
    total_edges: int
    is_dag: bool
    longest_attack_chain: int
    density: float

class AttackFlowGraph(BaseModel):
    title: Optional[str] = "ChronoCTI Attack Flow"
    description: Optional[str] = ""
    nodes: List[AttackFlowNode]
    edges: List[AttackFlowEdge]
    canvas_width: float = 1200
    canvas_height: float = 800
    metrics: AttackFlowMetrics

# --- Comprehensive API Response ---

class AnalyzeResponse(BaseModel):
    report_name: str
    total_sentences: int
    summary: Dict[str, Any]
    assets: List[UniqueAssetSummary]
    techniques: List[UniqueTechniqueSummary]
    sentences: List[SentenceItem]
    attack_flow: AttackFlowGraph
