# ChronoCTI: Cyber Threat Intelligence Analysis and Attack-Flow Visualization

## Release details

**Title:** ChronoCTI: Cyber Threat Intelligence Analysis and Attack-Flow Visualization — Source Code Without Trained Models  
**Author:** Mahshin Islam  
**Affiliation:** University of Dhaka  
**Resource type:** Software  
**Snapshot date:** 2026-10-07

## Project description

ChronoCTI is a natural language processing and machine learning project for analyzing cyber threat intelligence reports and studying temporal relationships among cyberattack tactics, techniques, and procedures. The research code covers technique and asset classification, discourse and coreference analysis, temporal feature extraction, association-rule features, and temporal-relation learning. Its FastAPI and Angular web application visualizes detected MITRE ATT&CK techniques and asset categories with supporting report evidence.

This code-only release includes source code, configuration, dependency declarations, documentation, and taxonomies needed by the web application. Research datasets, trained models, checkpoints, pretrained embeddings, installed dependencies, and private environment files are excluded. The web application supports a keyword-based demonstration without trained weights. Its graph links represent co-occurrence and narrative mention order, rather than verified execution chronology or causality. Running the full trained research pipeline requires separately supplied data and separately obtained or retrained models.

## License and attribution

The root LICENSE contains Apache License 2.0. Included third-party components retain their own license and attribution notices. Existing source authorship and notices are preserved.

## Presentation

Suitable for source-code review and a local keyword-based demonstration. See web-server/README.md for application details. Create a Python environment and install fastapi, uvicorn, python-multipart, spacy, and networkx; install frontend dependencies using npm ci and build the frontend before starting web-server/run.py. No trained language-model download is required for the keyword fallback.

Department and ORCID were not provided. This archive has been prepared locally; it has not been uploaded or published to Zenodo.
