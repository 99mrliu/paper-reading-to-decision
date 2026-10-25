from pathlib import Path
import hashlib,json,math,subprocess,sys,tempfile
r=Path(__file__).resolve().parent;p=json.loads((r/'provenance.json').read_text())
for name,item in p['files'].items():
    assert hashlib.sha256((r/name).read_bytes()).hexdigest()==item['packaged_sha256'],name
assert hashlib.sha256((r/'evidence/selected-operations.jsonl').read_bytes()).hexdigest()==p['selected_operations']['packaged_sha256']
with tempfile.TemporaryDirectory() as tmp:
    tmp=Path(tmp)
    def call(script,args,out):
        q=subprocess.run([sys.executable,str(r/'skill/scripts'/script),*map(str,args),'--out',str(tmp/out)],capture_output=True,text=True)
        if q.returncode:raise RuntimeError(q.stdout+q.stderr)
        return json.loads((tmp/out).read_text())
    t=call('table_stats.py',['--layout',r/'sources/tables/p14.txt','--table','13','--columns','FirstDense,FirstInterp,RerankDense,RerankInterp,RerankRRF,InterpBefore,InterpAfter,InterpNet,RRFBefore,RRFAfter,RRFNet','--rows','7','--diff','RerankInterp:RerankDense'],'table.json')
    assert t['difference']==json.loads((r/'evidence/table13.json').read_text())['difference']
    c=call('check_ledger.py',['--ledger',r/'evidence/ledger.json','--triage',r/'sources'],'claims.json')
    m=call('check_memo.py',['--memo',r/'evidence/report.md','--ledger',r/'evidence/ledger.json','--context',r/'evidence/context.json'],'memo.json')
    a=call('precision.py',['--sd','.20','--n','400','--half-width','.005'],'precision.json')
    assert a['n_for_target_half_width']==6147 and math.isclose(a['approx_half_width'],.019599639845400536)
    print(json.dumps({'status':'passed','source_pages':7,'literal_claims':len(c['claims']),'table_rows':t['n_rows'],'table_difference':t['difference'],'memo':m['status'],'scope':'Hash, literal excerpts and arithmetic only; no new AI run or scientific certification.'},ensure_ascii=False,indent=2))
