"""Create fresh inputs for a real AI reading; this never calls a model."""
from pathlib import Path
import argparse,shutil
p=argparse.ArgumentParser();p.add_argument('--destination',required=True);a=p.parse_args()
root=Path(__file__).resolve().parent;dest=Path(a.destination).resolve()
dest.mkdir(parents=True,exist_ok=False)
(dest/'INPUT/materials').mkdir(parents=True);(dest/'out').mkdir()
shutil.copy2(root/'materials/fusion-tax.pdf',dest/'INPUT/materials/fusion-tax.pdf')
shutil.copy2(root/'cases/A/task.md',dest/'INPUT/task.md')
shutil.copytree(root/'skill',dest/'skill',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copy2(root/'runs/A2-with/prompt.txt',dest/'prompt.txt')
print('Prepared fresh PDF/task/Skill/prompt. No AI called; no old answer copied. Directory:',dest)
