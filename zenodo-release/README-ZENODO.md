# ChronoCTI model-free source and dataset release

**Author:** Mahshin Islam  
**Affiliation:** University of Dhaka

This archive is a locally prepared review candidate. It has not been uploaded or published. Consult ZENODO-METADATA.md for the project description, dataset scope, licenses, and unresolved publication details.

Extract the ZIP to obtain the ChronoCTI directory. Original source files and dataset paths are preserved. The release directory contains metadata, a SHA-256 manifest, exclusions, and the packaging script. Original working files were not modified.

## Included

Research and web application source, dependency declarations, configuration, project documentation, available readable datasets, annotations, feature tables, prediction outputs, graph exports, and existing license notices. Derived features/predictions are research data, not trained model weights. The source includes third-party TimeML/Mallet code with its notices.

## Excluded

Identified trained/pretrained model directories, checkpoints and optimizer states, spaCy model distributions, embeddings (including text vectors), downloaded model caches, binary/serialized artifacts, bundled archives and dependencies, statistical NLP parameters, environment files, and logs/caches. Conservative filtering omits some regenerable serialized datasets and third-party runtime resources too. See EXCLUSIONS.csv. This is not a complete preconfigured offline training environment.

## Demonstration without trained weights

The web backend falls back to a blank English spaCy pipeline and keyword rules when trained models are absent. No language-model download is needed for that mode. Trained classification and the full offline temporal learner are not part of this demonstration. Graph links indicate co-mention and narrative order, not verified execution chronology or causality.

From the extracted ChronoCTI directory, with Python 3.11 and Node/npm available:

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install fastapi uvicorn python-multipart spacy networkx
npm ci --prefix web-server/frontend
npm run build --prefix web-server/frontend
python web-server/run.py
```

Open http://localhost:8000, use the report input, and try:

> The attacker used PowerShell on a workstation. Then they used RDP to access a server. Finally ransomware encrypted the server.

The example is synthetic. Dependencies must be installed separately; these commands are a minimal setup recipe, not a tested clean-environment dependency lock. Existing research Pipfiles/requirements are preserved for their respective pipeline modules. Historical project documentation may describe trained artifacts that are intentionally absent from this release.

## Reproduction and audit

MANIFEST.csv lists each original included file, its size, and SHA-256. EXCLUSIONS.csv records excluded paths (directory exclusions cover descendants). SHA256SUMS.txt alongside the ZIP checks the entire archive. ZIP integrity and packaging rules are checked by prepare_release.py. Secret scanning uses common credential patterns and excludes environment files; this does not certify the privacy or redistribution rights of dataset contents.

## Upload steps

Sign into https://zenodo.org/ and create a new upload. Attach the ZIP and optionally the external metadata and checksum files. Use the description in ZENODO-METADATA.md, add confirmed authors/affiliations and appropriate license information, and save a draft. Review the dataset permissions and record contents before publication. A DOI exists only after one is reserved or the record is published; none has been created by this packaging task.

Credential-pattern filtering also omits any selected small text/source files containing common API-key or private-key patterns, including potentially quoted samples in CTI reports. Omitted files are recorded in EXCLUSIONS.csv; credential values are never printed. This does not imply those samples are active credentials.
