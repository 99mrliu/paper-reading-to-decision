"""Fresh equal-budget CLI sessions; capture the matching native session by ID."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT=Path(__file__).resolve().parent
BIN='/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin'
APP='/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS'

def tree_sha(path):
    h=hashlib.sha256()
    for p in sorted(path.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            h.update(str(p.relative_to(path)).encode());h.update(p.read_bytes())
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',choices=['A','B','C'],required=True)
    ap.add_argument('--run',required=True);ap.add_argument('--with-skill',action='store_true');a=ap.parse_args()
    d=ROOT/'runs'/a.run;d.mkdir(parents=True,exist_ok=False)
    (d/'out').mkdir();(d/'INPUT/materials').mkdir(parents=True)
    shutil.copy2(ROOT/'cases'/a.case/'task.md',d/'INPUT/task.md')
    material={'A':'fusion-tax.pdf','B':'tsbase.pdf','C':'synthetic-scan-fusion-p1-3.pdf'}[a.case]
    shutil.copy2(ROOT/'materials'/material,d/'INPUT/materials'/material)
    if a.with_skill:shutil.copytree(ROOT/'skill',d/'skill',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    prompt=('Complete one independent paper-reading task. Read INPUT/task.md and original INPUT materials. '
            'Use only this working directory and ordinary installed executables/libraries. Do not inspect parent directories, '
            'other sessions, global skills, credentials, history, or evaluation criteria. No network, delegation, publishing or uploading. '
            'Do not alter INPUT or supplied skill files. Write artifacts only under out/. Work independently, no questions. '
            'Budget: 30 visible command/tool operations, 900 seconds. The Chinese memo out/report.md must be at most 12000 characters. '
            'Do not repeat it in the final message; final message at most 120 words. Preserve failed checks before fixes. '
            'State limitations if material or budget is insufficient. Do not claim a literal number check proves scientific meaning.\n')
    prompt+=('Use the supplied skill/SKILL.md and its helpers.\n' if a.with_skill else 'Use your ordinary reading approach with the available base tools; no skill is supplied.\n')
    (d/'prompt.txt').write_text(prompt)
    env=dict(os.environ,PATH=f'{BIN}:{APP}:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin',NO_PROXY='*',no_proxy='*',PYTHONDONTWRITEBYTECODE='1')
    # Rust env::vars() panics on an inherited non-Unicode value. Remove invalid
    # process-environment entries symmetrically; never mutate the user's settings.
    removed_invalid=[]
    for k,v in list(env.items()):
        try:k.encode('utf-8');v.encode('utf-8')
        except UnicodeEncodeError:removed_invalid.append(k);env.pop(k,None)
    for k in list(env):
        if any(s in k.upper() for s in ['PLAYGROUND','BOHR','MINERU','LARK','GMAIL','AWS_','OPENAI_API_KEY','ANTHROPIC']):env.pop(k,None)
    command=[f'{BIN}/codex','--no-daemon','exec','--ignore-user-config','--skip-git-repo-check','--sandbox','danger-full-access','-c','approval_policy="never"','--json','-C',str(d),'-o',str(d/'out/assistant_final.md'),'-']
    t=time.monotonic();start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (d/'events.jsonl').open('w') as out,(d/'stderr.log').open('w') as err:
        p=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=out,stderr=err,text=True,env=env,start_new_session=True)
        timeout=False
        try:p.communicate(prompt,timeout=900)
        except subprocess.TimeoutExpired:
            timeout=True
            import signal
            os.killpg(p.pid,signal.SIGTERM)
            try:p.wait(timeout=10)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
    rows=[]
    for line in (d/'events.jsonl').read_text().splitlines():
        try:rows.append(json.loads(line))
        except ValueError:pass
    thread=next((r.get('thread_id') for r in rows if r.get('type')=='thread.started'),None)
    candidates=list((Path.home()/'.codex/sessions').rglob('*'+thread+'*.jsonl')) if thread else []
    # A concurrent desktop session must never be mistaken for this run.
    native=None
    for c in candidates:
        try:first=json.loads(c.open().readline());payload=first.get('payload',{})
        except Exception:continue
        if payload.get('id')==thread and payload.get('cwd')==str(d):
            shutil.copy2(c,d/'session_native.jsonl');native=d/'session_native.jsonl';break
    completions=[r for r in rows if r.get('type')=='turn.completed']
    visible=[r for r in rows if r.get('type')=='item.started' and r.get('item',{}).get('type') in ['command_execution','mcp_tool_call','web_search']]
    model='Configured CLI default; exact service snapshot unavailable'
    if native:
        for line in native.read_text().splitlines():
            try:r=json.loads(line)
            except ValueError:continue
            if r.get('type')=='turn_context' and r.get('payload',{}).get('model'):model=r['payload']['model'];break
    meta={'run':a.run,'case':a.case,'condition':'with_skill' if a.with_skill else 'without_skill','started_at':start,
          'duration_seconds':round(time.monotonic()-t,3),'exit_code':p.returncode,'timed_out':timeout,'thread_id':thread,
          'native_session_captured':bool(native),'model':model,'model_version':'exact service snapshot unavailable',
          'harness':subprocess.check_output([f'{BIN}/codex','--version'],text=True).strip(),'independent_session':True,
          'tool_calls_visible':len(visible),'operation_budget_note':'30-operation instruction; visible JSONL is a lower bound, not hard-enforced. Wall-time timeout enforced.',
          'usage':completions[-1].get('usage') if completions else None,'cost':None,'cost_note':'No billed amount exposed',
          'report_exists':(d/'out/report.md').exists(),'human_steps':[],
          'invalid_environment_keys_removed':removed_invalid,
          'skill_tree_sha256':tree_sha(ROOT/'skill') if a.with_skill else None,
          'task_sha256':hashlib.sha256((d/'INPUT/task.md').read_bytes()).hexdigest(),
          'input_sha256':hashlib.sha256((d/'INPUT/materials'/material).read_bytes()).hexdigest()}
    (d/'session.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(json.dumps(meta,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
