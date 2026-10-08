import os
import sys
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from .schemas import AnalyzeRequest, AnalyzeResponse, AttackFlowGraph
    from .pipeline import pipeline_instance
    from .attack_flow import attack_flow_engine
except ImportError:
    from schemas import AnalyzeRequest, AnalyzeResponse, AttackFlowGraph
    from pipeline import pipeline_instance
    from attack_flow import attack_flow_engine

app = FastAPI(
    title="ChronoCTI NetworkX Attack Flow Web API",
    description="Automated Cyber Threat Intelligence backend generating Attack Flow graphs using Python NetworkX.",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "static", "browser")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ChronoCTI Attack Flow API",
        "asset_models_loaded": pipeline_instance.asset_model is not None,
        "total_asset_classes": len(pipeline_instance.asset_tax),
        "total_technique_classes": len(pipeline_instance.technique_tax),
        "networkx_ready": True
    }

@app.get("/api/assets/taxonomy")
def get_asset_taxonomy():
    """Returns the complete list of MITRE ICS/IT Assets."""
    return pipeline_instance.asset_tax

@app.get("/api/techniques/taxonomy")
def get_technique_taxonomy():
    """Returns the list of MITRE ATT&CK techniques."""
    return pipeline_instance.technique_tax

@app.get("/api/scenarios")
def list_scenarios():
    """Returns list of available pre-built Attack Flow scenarios."""
    return [
        {
            "id": "equifax",
            "name": "Equifax Apache Struts Attack Flow (Showcase)",
            "description": "Exact reproduction of the multi-stage attack flow diagram with Blue Action blocks, Green Condition blocks with (T)/(F) badges, and Red AND gates."
        },
        {
            "id": "triton",
            "name": "TRITON / TRISIS Industrial Malware Flow",
            "description": "Techniques targeting PLCs, HMIs, Domain Controllers, and SIS controllers with simultaneous execution AND gates."
        }
    ]

@app.get("/api/scenarios/{scenario_id}")
def get_scenario(scenario_id: str):
    """Fetches a specific Attack Flow scenario."""
    if scenario_id == "equifax":
        return attack_flow_engine.get_equifax_showcase_scenario()
    elif scenario_id == "triton":
        return attack_flow_engine.get_triton_ics_scenario()
    else:
        raise HTTPException(status_code=404, detail="Scenario not found")

@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_report(payload: AnalyzeRequest):
    """
    Analyzes raw text from a CTI report and builds the NetworkX Attack Flow graph.
    """
    if not payload.text or len(payload.text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Report text must not be empty.")
    
    result = pipeline_instance.process_report(
        raw_text=payload.text,
        report_name=payload.report_name or "cti-report",
        asset_thresh=payload.asset_threshold if payload.asset_threshold is not None else 0.5,
        tech_thresh=payload.technique_threshold if payload.technique_threshold is not None else 0.5
    )
    return result

@app.post("/api/upload", response_model=AnalyzeResponse)
async def upload_and_analyze(
    file: UploadFile = File(...),
    asset_threshold: Optional[float] = Form(0.5),
    technique_threshold: Optional[float] = Form(0.5)
):
    """Accepts file upload (.txt, .md, .csv, .json) and executes full CTI analysis."""
    try:
        content_bytes = await file.read()
        raw_text = content_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
        
    if not raw_text or len(raw_text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
    result = pipeline_instance.process_report(
        raw_text=raw_text,
        report_name=file.filename,
        asset_thresh=asset_threshold,
        tech_thresh=technique_threshold
    )
    return result

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """Serves the interactive web dashboard."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h1>ChronoCTI Web Server</h1><p>API docs available at <a href='/docs'>/docs</a></p>")
