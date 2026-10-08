import os
import re
import json
from typing import List, Dict, Tuple, Any
import spacy
from collections import defaultdict

try:
    from .attack_flow import attack_flow_engine
except ImportError:
    from attack_flow import attack_flow_engine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSET_TAXONOMY_PATH = os.path.join(BASE_DIR, "Datasets/Dataset/Sentence-to-asset-mappings/selected_assetsWName.json")
TECHNIQUE_TAXONOMY_PATH = os.path.join(BASE_DIR, "sentence_to_technique_classifier/selected_techniquesWName.json")
ASSET_MODEL_PATH = os.path.join(BASE_DIR, "sentence_to_asset_classifier/bagging_models/asset_classifier_model/model-best")
ASSET_FALLBACK_MODEL = os.path.join(BASE_DIR, "sentence_to_asset_classifier/bagging_models/lgAll-0/model-best")
TECHNIQUE_MODEL_PATH = os.path.join(BASE_DIR, "sentence_to_technique_classifier/bagging_models/robertaCtiAll-final/model-best")

TEMPORAL_PATTERNS = [
    (r"\b(first|initially|at first|prior to|before|earlier)\b", "BEFORE"),
    (r"\b(then|next|after|afterwards|subsequently|later|following this|minutes later|hours later|days later)\b", "AFTER"),
    (r"\b(meanwhile|simultaneously|at the same time|concurrently|while|during)\b", "OVERLAP"),
    (r"\b(finally|eventually|ultimately|in the end|at last)\b", "FINALLY"),
    (r"\b(on the \w+ day|day \d+|around \d+:\d+|\d+ hours? post|\d+ minutes?)\b", "TIME_ANCHOR")
]

ASSET_KEYWORDS = {
    "A0001": [r"\bworkstations?\b", r"\bbeachheads?\b", r"\bdesktops?\b", r"\blaptops?\b", r"\bclient machine\b", r"\bhost machine\b"],
    "A0002": [r"\bhmi\b", r"\bhuman[- ]machine interface\b", r"\boperator station\b", r"\bpatient monitor\b", r"\bc-more\b"],
    "A0003": [r"\bplc\b", r"\bprogrammable logic controller\b", r"\btriconex\b", r"\btricon\b", r"\bmicro800\b", r"\bm580\b", r"\brx3i\b"],
    "A0004": [r"\brtu\b", r"\bremote terminal unit\b", r"\btbox\b", r"\bmtu\b"],
    "A0005": [r"\bied\b", r"\bintelligent electronic device\b", r"\bprotective relay\b"],
    "A0006": [r"\bhistorians?\b", r"\bdata historian\b", r"\bproficy\b", r"\bhda\b", r"\bopc hda\b"],
    "A0007": [r"\bcontrol servers?\b", r"\bscada servers?\b", r"\bcms server\b", r"\bcentral server\b", r"\bsupervisory server\b"],
    "A0008": [r"\bdomain controllers?\b", r"\bservers?\b", r"\bfile servers?\b", r"\bbackup servers?\b", r"\bexchange\b", r"\bftp server\b", r"\bactive directory\b", r"\bdatabase servers?\b", r"\bdatabases?\b"],
    "A0009": [r"\bdata gateways?\b", r"\bopc gateways?\b", r"\bgateways?\b", r"\bsra gateway\b"],
    "A0010": [r"\bsafety controllers?\b", r"\bsis\b", r"\bsafety instrumented system\b", r"\bsil[- ]3\b"],
    "A0011": [r"\bvpn\b", r"\bvirtual private network\b", r"\bopenvpn\b", r"\becatcher\b", r"\banyconnect\b"],
    "A0012": [r"\bjump hosts?\b", r"\bjump box\b", r"\bbastion hosts?\b", r"\bjump servers?\b"],
    "A0013": [r"\bfield i/?o\b", r"\bsensors?\b", r"\bactuators?\b", r"\bvalves?\b", r"\bmotors?\b", r"\bfield devices?\b", r"\bio devices?\b"],
    "A0014": [r"\brouters?\b", r"\brax30\b", r"\bnetgear\b", r"\bedr-g902\b", r"\bedr-g903\b"],
    "A0015": [r"\bswitch\b", r"\bswitches\b", r"\bwgs-804hpt\b", r"\bnetwork switch\b"],
    "A0016": [r"\bfirewalls?\b", r"\bpacket filter\b", r"\bstateful inspection\b"],
    "A0017": [r"\bdcs\b", r"\bdistributed control system\b", r"\bmark vie\b", r"\bmarkvi\b", r"\b800xa\b"],
    "A0018": [r"\bpac\b", r"\bprogrammable automation controller\b", r"\bmodicon m340\b", r"\bpacsystems\b"]
}

TECHNIQUE_KEYWORDS = {
    "T1059": [r"\bcommand and script\b", r"\bpowershell\b", r"\bbatch script\b", r"\bcmd\.exe\b", r"\bwmic\b", r"\bvbs\b", r"\b165\.bat\b", r"\bfind\.bat\b"],
    "T1078": [r"\bvalid accounts?\b", r"\bdomain admin\b", r"\blocal administrator\b", r"\bcreated a user\b", r"\badmin account\b"],
    "T1003": [r"\bdump lsass\b", r"\blsass\b", r"\bprocdump\b", r"\bmimikatz\b", r"\bntds\.dit\b", r"\bpass[- ]the[- ]hash\b", r"\bcredential dumping\b", r"\bcredentials?\b"],
    "T1021": [r"\brdp\b", r"\bremote desktop\b", r"\bsmb\b", r"\bssh tunnel\b", r"\bwmiexec\b", r"\batexec\b", r"\bvnc\b"],
    "T1053": [r"\bscheduled tasks?\b", r"\bschtasks\b", r"\bcron\b"],
    "T1562": [r"\bdisable windows defender\b", r"\bdisabled windows defender\b", r"\bkill antivirus\b", r"\bset-mppreference\b", r"\bimpair defenses\b"],
    "T1055": [r"\bprocess injection\b", r"\binjected svchost\b", r"\binjected process\b", r"\bwuauclt\b", r"\bmemory injection\b"],
    "T1105": [r"\bingress tool transfer\b", r"\bdownloaded\b", r"\btransferred\b", r"\bdropmefiles\b", r"\bpulled down\b"],
    "T1070": [r"\bindicator removal\b", r"\bcleared logs\b", r"\bdeleted logs\b", r"\bdeleted installer\b", r"\bclear windows event logs\b", r"\bfile deletion\b"],
    "T1486": [r"\bdata encrypted for impact\b", r"\bransomware\b", r"\bbitlocker\b", r"\bdiskcryptor\b", r"\blockbit\b", r"\bnokoyawa\b"],
    "T1046": [r"\bnetwork service discovery\b", r"\bport scanning\b", r"\badvanced ip scanner\b", r"\bsoftperfect\b", r"\bvulnerability scanning\b"],
    "T1018": [r"\bremote system discovery\b", r"\badfind\b", r"\bping utility\b", r"\bnetlogon\b", r"\bgather victim network\b"],
    "T1087": [r"\baccount discovery\b", r"\bquery user\b", r"\bnet user\b", r"\bdomain trusts\b"],
    "T1190": [r"\bexploit public[- ]facing\b", r"\bzerologon\b", r"\bcve-2020-1472\b", r"\bcve-2020-14882\b", r"\bconfluence rce\b", r"\bstruts\b", r"\bcve-2017-5638\b"],
    "T1071": [r"\bapplication layer protocol\b", r"\bcobalt strike\b", r"\bbeacon\b", r"\bicedid\b", r"\bqbot\b", r"\bbumblebee\b", r"\bflawedgrace\b", r"\bencrypted channel\b"],
    "T1567": [r"\bexfiltration over web service\b", r"\brclone\b", r"\bmega\.io\b", r"\bmega\.nz\b", r"\bexfiltrat\b", r"\bexfiltration\b"],
    "T1505": [r"\bweb shell\b", r"\bchina chopper\b", r"\bwebshell\b"],
    "T1560": [r"\barchive collected data\b", r"\bzip archive\b", r"\bcompressed data\b"],
    "T1140": [r"\bdeobfuscate\b", r"\bdecode files\b", r"\bbase64 decode\b"],
    "T1090": [r"\bmulti[- ]hop proxy\b", r"\bproxy chain\b", r"\btor proxy\b"]
}

class ChronoCTIPipeline:
    def __init__(self):
        print("Initializing ChronoCTI Backend Pipeline with NetworkX...")
        self.load_taxonomies()
        self.load_nlp_models()
        print("ChronoCTI Backend Pipeline Ready.")

    def load_taxonomies(self):
        if os.path.exists(ASSET_TAXONOMY_PATH):
            with open(ASSET_TAXONOMY_PATH, "r", encoding="utf-8") as f:
                self.asset_tax = json.load(f)
        else:
            self.asset_tax = []
        self.asset_map = {x["id"]: x["name"] for x in self.asset_tax}

        if os.path.exists(TECHNIQUE_TAXONOMY_PATH):
            with open(TECHNIQUE_TAXONOMY_PATH, "r", encoding="utf-8") as f:
                self.technique_tax = json.load(f)
        else:
            self.technique_tax = []
        self.technique_map = {x["id"]: x["name"] for x in self.technique_tax}

    def load_nlp_models(self):
        try:
            self.nlp_base = spacy.load("en_core_web_sm")
        except Exception:
            try:
                self.nlp_base = spacy.load("en_core_web_lg")
            except Exception:
                self.nlp_base = spacy.blank("en")
                self.nlp_base.add_pipe("sentencizer")

        self.asset_model = None
        for path in [ASSET_MODEL_PATH, ASSET_FALLBACK_MODEL]:
            if os.path.exists(path):
                try:
                    self.asset_model = spacy.load(path)
                    print(f"Loaded Asset Classifier from {path}")
                    break
                except Exception as e:
                    print(f"Warning: Could not load asset model: {e}")

        self.technique_model = None
        if os.path.exists(TECHNIQUE_MODEL_PATH):
            try:
                self.technique_model = spacy.load(TECHNIQUE_MODEL_PATH)
                print(f"Loaded Technique Classifier from {TECHNIQUE_MODEL_PATH}")
            except Exception as e:
                print(f"Technique model not loaded directly: {e}")

    def split_sentences(self, raw_text: str) -> List[str]:
        cleaned = re.sub(r'[\r\n]+', ' ', raw_text)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        doc = self.nlp_base(cleaned)
        sentences = [s.text.strip() for s in doc.sents if len(s.text.strip()) > 5]
        if not sentences:
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', raw_text) if len(s.strip()) > 5]
        return sentences

    def extract_temporal_signals(self, text: str) -> List[str]:
        signals = []
        text_lower = text.lower()
        for pattern, tag in TEMPORAL_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                signals.append(tag)
        return list(set(signals))

    def predict_assets(self, text: str, threshold: float = 0.5) -> List[Tuple[str, float, str]]:
        predictions = []
        text_lower = text.lower()

        if self.asset_model:
            try:
                doc = self.asset_model(text)
                for cat, score in doc.cats.items():
                    if score >= threshold:
                        predictions.append((cat, float(score), "classifier"))
            except Exception:
                pass

        for aid, patterns in ASSET_KEYWORDS.items():
            for pat in patterns:
                if re.search(pat, text_lower):
                    if 0.95 >= threshold and not any(p[0] == aid for p in predictions):
                        predictions.append((aid, 0.95, "keyword"))
                    break

        return sorted(predictions, key=lambda x: x[1], reverse=True)

    def predict_techniques(self, text: str, threshold: float = 0.5) -> List[Tuple[str, float, str]]:
        predictions = []
        text_lower = text.lower()

        if self.technique_model:
            try:
                doc = self.technique_model(text)
                for cat, score in doc.cats.items():
                    if score >= threshold:
                        predictions.append((cat, float(score), "classifier"))
            except Exception:
                pass

        for tid, patterns in TECHNIQUE_KEYWORDS.items():
            for pat in patterns:
                if re.search(pat, text_lower):
                    if 0.92 >= threshold and not any(p[0] == tid for p in predictions):
                        predictions.append((tid, 0.92, "keyword"))
                    break

        return sorted(predictions, key=lambda x: x[1], reverse=True)

    def process_report(self, raw_text: str, report_name: str = "report", asset_thresh: float = 0.5, tech_thresh: float = 0.5) -> Dict[str, Any]:
        sentences = self.split_sentences(raw_text)
        
        sentence_items = []
        unique_assets = defaultdict(lambda: {"count": 0, "highest_conf": 0.0, "sentences": []})
        unique_techniques = defaultdict(lambda: {"count": 0, "highest_conf": 0.0, "sentences": []})
        
        for idx, sent_text in enumerate(sentences):
            t_signals = self.extract_temporal_signals(sent_text)
            
            asset_preds = self.predict_assets(sent_text, threshold=asset_thresh)
            matched_assets = []
            for aid, conf, source in asset_preds:
                aname = self.asset_map.get(aid, aid)
                matched_assets.append({
                    "id": aid,
                    "name": aname,
                    "confidence": round(conf, 4),
                    "prediction_source": source,
                    "sentence_id": idx,
                    "sentence_text": sent_text
                })
                unique_assets[aid]["count"] += 1
                unique_assets[aid]["highest_conf"] = max(unique_assets[aid]["highest_conf"], conf)
                unique_assets[aid]["sentences"].append(idx)

            tech_preds = self.predict_techniques(sent_text, threshold=tech_thresh)
            matched_techniques = []
            for tid, conf, source in tech_preds:
                tname = self.technique_map.get(tid, tid)
                matched_techniques.append({
                    "id": tid,
                    "name": tname,
                    "confidence": round(conf, 4),
                    "prediction_source": source,
                    "sentence_id": idx,
                    "sentence_text": sent_text
                })
                unique_techniques[tid]["count"] += 1
                unique_techniques[tid]["highest_conf"] = max(unique_techniques[tid]["highest_conf"], conf)
                unique_techniques[tid]["sentences"].append(idx)

            sentence_items.append({
                "sentence_id": idx,
                "text": sent_text,
                "assets": matched_assets,
                "techniques": matched_techniques,
                "temporal_signals": t_signals
            })

        asset_summary_list = []
        for aid, data in unique_assets.items():
            asset_summary_list.append({
                "id": aid,
                "name": self.asset_map.get(aid, aid),
                "occurrence_count": data["count"],
                "highest_confidence": round(data["highest_conf"], 4),
                "matched_sentences": sorted(list(set(data["sentences"])))
            })
        asset_summary_list.sort(key=lambda x: x["occurrence_count"], reverse=True)

        tech_summary_list = []
        for tid, data in unique_techniques.items():
            tech_summary_list.append({
                "id": tid,
                "name": self.technique_map.get(tid, tid),
                "occurrence_count": data["count"],
                "highest_confidence": round(data["highest_conf"], 4),
                "matched_sentences": sorted(list(set(data["sentences"])))
            })
        tech_summary_list.sort(key=lambda x: x["occurrence_count"], reverse=True)

        attack_flow_graph = attack_flow_engine.build_attack_flow_from_chrono_data(
            sentences=sentence_items,
            asset_map=self.asset_map,
            technique_map=self.technique_map
        )
        attack_flow_graph["title"] = f"Attack Flow: {report_name}"
        attack_flow_graph["description"] = f"Entity associations and narrative order from {len(sentences)} report sentences."

        return {
            "report_name": report_name,
            "total_sentences": len(sentences),
            "summary": {
                "total_unique_assets": len(asset_summary_list),
                "total_unique_techniques": len(tech_summary_list),
                "total_graph_nodes": len(attack_flow_graph["nodes"]),
                "total_graph_edges": len(attack_flow_graph["edges"]),
                "longest_attack_chain": attack_flow_graph["metrics"]["longest_attack_chain"]
            },
            "assets": asset_summary_list,
            "techniques": tech_summary_list,
            "sentences": sentence_items,
            "attack_flow": attack_flow_graph
        }

pipeline_instance = ChronoCTIPipeline()
