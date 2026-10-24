"""Recompute saved evidence with the original tools, offline, without a model."""
from pathlib import Path
import hashlib,json,math,subprocess,sys,tempfile
root=Path(__file__).resolve().parent
mapping=json.loads((root/'provenance/source-map.json').read_text())
for name,item in mapping['unchanged_original_files'].items():
    assert hashlib.sha256((root/item.get('raw_copy',name)).read_bytes()).hexdigest()==item['sha256'],name
    if 'published_sha256' in item:assert hashlib.sha256((root/name).read_bytes()).hexdigest()==item['published_sha256'],name
run=root/'runs/A2-with/out';scripts=root/'skill/scripts'
with tempfile.TemporaryDirectory() as tmp:
    tmp=Path(tmp)
    def call(script,args,name):
        p=subprocess.run([sys.executable,str(scripts/script),*map(str,args),'--out',str(tmp/name)],capture_output=True,text=True)
        if p.returncode:raise RuntimeError(p.stdout+p.stderr)
        return json.loads((tmp/name).read_text())
    table=call('table_stats.py',['--layout',run/'triage/tables/p14.txt','--table','13',
        '--columns','FirstDense,FirstInterp,RerankDense,RerankInterp,RerankRRF,InterpBefore,InterpAfter,InterpNet,RRFBefore,RRFAfter,RRFNet',
        '--rows','7','--diff','RerankInterp:RerankDense'],'table.json')
    assert table['difference']==json.loads((run/'table13.json').read_text())['difference']
    ledger=call('check_ledger.py',['--ledger',run/'ledger.json','--triage',run/'triage'],'ledger.json')
    memo=call('check_memo.py',['--memo',run/'report.md','--ledger',run/'ledger.json','--context',run/'context.json'],'memo.json')
    precision=call('precision.py',['--sd','.20','--n','400','--half-width','.005'],'precision.json')
    assert precision['n_for_target_half_width']==6147
    assert math.isclose(precision['approx_half_width'],.019599639845400536)
    assert table['difference']['min']=='-0.001' and table['difference']['max']=='0.018'
    print(json.dumps({'status':'passed','verified_original_files':len(mapping['unchanged_original_files']),
        'table13_rows':table['n_rows'],'table13_difference':table['difference'],
        'literal_ledger_status':ledger['status'],'memo_check_status':memo['status'],
        'assumed_sd_precision':precision,'scope':'Saved-file integrity, literal quotes, table arithmetic and hypothetical precision only. Not new AI reading, semantic certification, production validation or power analysis.'},ensure_ascii=False,indent=2))
