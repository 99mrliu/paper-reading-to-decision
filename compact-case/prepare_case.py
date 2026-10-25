from pathlib import Path
import argparse,shutil
p=argparse.ArgumentParser();p.add_argument('--destination',required=True);a=p.parse_args()
r=Path(__file__).resolve().parent;d=Path(a.destination).resolve();d.mkdir(parents=True,exist_ok=False)
(d/'INPUT').mkdir();(d/'out').mkdir()
shutil.copy2(r/'evidence/task.md',d/'INPUT/task.md')
shutil.copytree(r/'sources',d/'INPUT/sources')
shutil.copytree(r/'skill',d/'skill',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copy2(r/'rerun_prompt.txt',d/'prompt.txt')
print('Prepared excerpt-based inputs only. No model called and no old answer copied.')
