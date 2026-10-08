# Zenodo metadata draft

Status: prepared locally; not uploaded or published. Author and affiliation supplied by the depositor. Dataset redistribution scope remains to be confirmed.

## Project title and authors

Suggested title: **ChronoCTI: Cyber Threat Intelligence Analysis, Temporal TTP Learning, and Attack-Flow Visualization — Source Code and Datasets (Without Trained Models)**

**Author:** Mahshin Islam  
**Affiliation:** University of Dhaka

Department and ORCID were not provided. Existing source and third-party attribution notices are preserved.

Suggested resource type: Software (accompanying datasets included).
Suggested snapshot version: 2026-10-07 (packaging date, not an upstream software version).
Keywords: ChronoCTI; cyber threat intelligence; MITRE ATT&CK; temporal relation extraction; natural language processing; attack-flow visualization; datasets.

## Dataset scope

Include the project's readable source datasets and available derived results: CTI report corpora; sentence-to-technique and sentence-to-asset mappings; relevance classification sentences; discourse and temporal-relation spreadsheets; training/evaluation splits; derived JSON/CSV features, predictions, and graph exports. Preserve original relative paths, including duplicate inputs used by different pipeline stages. MANIFEST.csv is the exact file list.

Exclude all identified trained model directories, checkpoints, optimizer states, spaCy model packages, pretrained caches, Word2Vec embeddings (including .txt vectors), and third-party statistical NLP parameters. Also exclude binary/serialized artifacts such as .pkl, .pickle, .spacy, .npy and bundled archives; some of these are regenerable training data rather than models. In particular dataset_df_threshold_95.pkl is omitted conservatively; readable feature JSON and generation scripts remain. EXCLUSIONS.csv records paths and reasons. Environments, credentials files, dependency installations, and caches are excluded.

The repository includes copies of external CTI reports and derived text. Public availability is not proof of redistribution permission. No complete provenance/permissions register or privacy clearance was established. The depositor must identify any restricted material before publication; this locally prepared archive is a review candidate, not a declaration of rights clearance.

## Project description (paste into Zenodo)

ChronoCTI is a natural language processing and machine learning project for analyzing cyber threat intelligence reports and studying temporal relationships among cyberattack tactics, techniques, and procedures. Its offline research pipeline includes sentence-to-technique and asset classification, discourse and coreference analysis, temporal feature extraction, association-rule features, and temporal-relation learning. A FastAPI and Angular report explorer visualizes detected MITRE ATT&CK techniques and asset categories with supporting report evidence. The web explorer displays sentence co-occurrence and narrative mention order; it does not execute the complete offline temporal-learning pipeline or establish attack causality. This release provides source code, configuration, available datasets and derived results, and documentation. Trained model weights, checkpoints, pretrained embeddings, environments, and private configuration files are excluded. A keyword-based demonstration is supported by the web code; reproducing trained-model inference requires separately obtained or retrained models.

## License information

The repository root LICENSE contains Apache License 2.0. Preserve this and third-party license notices; do not reassign authorship of existing code.

CC BY-SA 4.0 license texts are present in:
- Datasets/Dataset/Sentence-to-technique-mappings/CC_BY-SA-4.0.txt
- sentence_to_technique_classifier/assets/CC_BY-SA-4.0.txt

These files are evidence of a license supplied with those subsets, not proof that all reports, annotations, and derived data share that license. Dataset-wide licensing and attribution remain unverified. Do not label the entire combined release as exclusively Apache 2.0 or assign a new blanket data license. Complete the license/provenance review before publishing; separate software and dataset records can be used if needed.

## Presentation needs

Proposed presentation: source-code and dataset review plus a local keyword-based web demonstration, with no trained models distributed. This is a recommendation based on the user's teaching/demo purpose, not a confirmed teacher requirement. The dashboard illustrates extracted techniques, asset categories, evidence, and graph exports. It does not reproduce learned classifier accuracy or offline temporal-model results without trained artifacts. See README-ZENODO.md for setup and validation limitations.

## Outstanding publication details

- Optional department and ORCID, if the author wishes to provide them.
- Permission and intended public/private scope for external reports and all dataset subsets.
- Authenticated access to the depositor's Zenodo account. No Zenodo integration was found; nothing was uploaded.

Credential-pattern filtering also omits any selected small text/source files containing common API-key or private-key patterns, including potentially quoted samples in CTI reports. Omitted files are recorded in EXCLUSIONS.csv; credential values are never printed. This does not imply those samples are active credentials.
