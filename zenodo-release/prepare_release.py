"""Build a conservative, model-free review archive; never modify original files."""
from pathlib import Path
import os, json, re, csv, hashlib, zipfile
ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
SKIP={'venv','.venv','node_modules','.git','__pycache__','.angular','zenodo-release','.cache','cache_dir','wandb','bagging_models','packages','model-best','model-last','roberta-cti','cti-roberta','cti_w2v_v2','cti-w2v_v2','discourse_model_output','discourse_coref_model_output'}
ALLOWED={'.py','.ts','.js','.html','.css','.scss','.java','.sh','.pl','.pm','.perl','.bat','.md','.txt','.json','.jsonl','.csv','.xlsx','.xml','.gexf','.cfg','.yml','.yaml','.toml','.lock','.xsd','.dtd','.properties','.rules','.in','.script','.tex','.bib','.png','.jpg','.jpeg','.gif','.svg','.pdf','.rst'}
NAMES={'license','licenses','notice','authors','copying','pipfile','makefile','dockerfile','.gitignore'}
SECRET=re.compile(rb'(?:sk-(?:proj-)?[A-Za-z0-9_-]{32,}|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
def reason(p):
 parts=p.parts; low=p.as_posix().lower(); name=p.name.lower()
 if any(x.lower() in SKIP or x.lower().startswith('checkpoint-') for x in parts):return 'model, dependency, cache, or generated release directory'
 if name.startswith('.env') or name in {'.ds_store'} or any(x.startswith('.') and x!='.gitignore' for x in parts):return 'private/environment/hidden file'
 if 'w2v_cti_reports' in low:return 'trained word embeddings (including text vectors)'
 if low.startswith('timeml/treetagger/lib/') or low.startswith('timeml/library/evita/dictionaries/'):return 'third-party NLP parameters/statistical resources'
 if any(x in parts for x in ['logs','tmp']):return 'temporary files or logs'
 if p.suffix.lower() not in ALLOWED and name not in NAMES:return 'binary/serialized/archived artifact or unreviewed file type'
 return ''
files=[];excluded=[]
for base,dirs,names in os.walk(ROOT):
 for d in list(dirs):
  rel=(Path(base)/d).relative_to(ROOT)
  if d.lower() in SKIP or d.startswith('.') or d.lower().startswith('checkpoint-'):
   excluded.append((rel.as_posix()+'/', 'directory excluded: models, dependencies, caches, hidden files, or release output'))
   dirs.remove(d)
 for n in names:
  f=Path(base)/n; p=f.relative_to(ROOT)
  why='symbolic link' if f.is_symlink() else reason(p)
  if why:excluded.append((p.as_posix(),why));continue
  # Model JSON detection and credential scan: stream to avoid loading huge datasets.
  with f.open('rb') as h:
   first=h.read(65536)
   if p.suffix=='.json' and (b'"learner_model_param"' in first or b'"gradient_booster"' in first):
    excluded.append((p.as_posix(),'serialized trained model JSON'));continue
  files.append((f,p))
# Scan source/config/documentation for common real credential formats, without printing values.
clean_files=[]
for f,p in files:
 if f.stat().st_size<10_000_000 and p.suffix.lower() not in {'.xlsx','.png','.jpg','.jpeg','.gif','.pdf'}:
  if SECRET.search(f.read_bytes()):
   excluded.append((p.as_posix(),'credential-like content detected; omitted pending review (may be a quoted CTI sample)'));continue
 clean_files.append((f,p))
files=clean_files
with (OUT/'EXCLUSIONS.csv').open('w') as h:
 w=csv.writer(h);w.writerow(['path','reason']);w.writerows(sorted(excluded))
print('Selected',len(files),'files;',round(sum(f.stat().st_size for f,p in files)/1e9,3),'GB uncompressed',flush=True)
archive=OUT/'ChronoCTI-code-and-datasets-no-models.zip'
rows=[]
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
 for f,p in sorted(files,key=lambda x:str(x[1])):
  digest=hashlib.sha256()
  with f.open('rb') as src,z.open('ChronoCTI/'+p.as_posix(),'w',force_zip64=True) as dst:
   while chunk:=src.read(1024*1024):digest.update(chunk);dst.write(chunk)
  rows.append((p.as_posix(),f.stat().st_size,digest.hexdigest()))
 for name in ['README-ZENODO.md','ZENODO-METADATA.md','EXCLUSIONS.csv','prepare_release.py']:
  z.write(OUT/name,'ChronoCTI/release/'+name)
 with (OUT/'MANIFEST.csv').open('w') as h:
  w=csv.writer(h);w.writerow(['path','bytes','sha256']);w.writerows(rows)
 z.write(OUT/'MANIFEST.csv','ChronoCTI/release/MANIFEST.csv')
print('Archive written; verifying CRCs...',flush=True)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 assert all(not reason(Path(n).relative_to('ChronoCTI')) for n in z.namelist() if not n.startswith('ChronoCTI/release/'))
h=hashlib.sha256()
with archive.open('rb') as f:
 while chunk:=f.read(1024*1024):h.update(chunk)
(OUT/'SHA256SUMS.txt').write_text(h.hexdigest()+'  '+archive.name+'\n')
print(json.dumps({'files':len(rows),'archive_bytes':archive.stat().st_size,'crc_check':'passed','sha256':h.hexdigest()}),flush=True)
