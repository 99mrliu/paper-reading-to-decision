#!/usr/bin/env python3
"""Check literal evidence and finite arithmetic, not scientific meaning."""
import argparse
import json
from pathlib import Path
import re
import sys
from numeric import normalize, numbers, contains, evaluate, finite


def check(ledger, triage):
    index=json.loads((triage/'index.json').read_text())
    out=[]; seen=set()
    for c in ledger.get('claims',[]):
        errs=[]; cid=c.get('id','')
        if not re.fullmatch(r'C\d+',cid) or cid in seen:errs.append('invalid or duplicate id')
        seen.add(cid)
        if c.get('type') not in ['reported','derived','assumed']:errs.append('invalid type')
        if c.get('verdict') not in ['supported','conditional','contradicted','unknown']:errs.append('invalid verdict')
        if not c.get('statement') or not c.get('condition'):errs.append('statement and condition required')
        if 'extra_numbers' in c:errs.append('extra_numbers is not evidence')
        unknown=c.get('verdict')=='unknown'; assumed=c.get('type')=='assumed'
        if unknown and (not c.get('missing') or not c.get('next_step')):errs.append('unknown needs missing and next_step')
        if assumed and c.get('verdict')!='conditional':errs.append('assumption must be conditional')
        evidence=c.get('evidence',[])
        if not evidence and not (unknown or assumed):errs.append('evidence required')
        observed=[]
        for e in evidence:
            page=e.get('page'); quote=e.get('quote','')
            if not isinstance(page,int) or isinstance(page,bool) or not 1<=page<=index['pages']:
                errs.append('invalid page');continue
            chunks=[]
            for folder in ['pages','tables']:
                f=triage/folder/f'p{page:02d}.txt'
                if f.exists():chunks.append(f.read_text())
            if len(normalize(quote))<12 or not e.get('unit'):errs.append('quote/unit insufficient')
            elif not any(normalize(quote) in normalize(x) for x in chunks):errs.append('quote not found on cited page')
            observed.extend(numbers(quote))
        for v in c.get('numbers',[]):
            try:
                if not contains(v,observed):errs.append(f'{v} absent from this claim evidence')
            except (ValueError,TypeError,OverflowError):errs.append('nonfinite/invalid evidence number')
        if unknown and c.get('numbers'):errs.append('unknown cannot claim verified numbers')
        d=c.get('derived')
        if c.get('type')=='derived' and not d:errs.append('derived computation required')
        if d:
            try:
                for v in d['inputs'].values():
                    if not contains(v,observed):errs.append('derived input absent from evidence')
                actual=evaluate(d['formula'],d['inputs']); target=finite(d['result'])
                if abs(actual-target)>1e-6:errs.append(f'formula mismatch: computed {actual}, reported {target}')
            except Exception as exc:errs.append('invalid calculation: '+str(exc)[:180])
        out.append({'id':cid,'pass':not errs,'errors':errs})
    if not out:out=[{'id':'-','pass':False,'errors':['empty ledger']}]
    return {'status':'pass' if all(x['pass'] for x in out) else 'fail','claims':out,
            'scope':'literal quoted evidence and finite arithmetic only; comparator/table semantics require review'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ledger',required=True);ap.add_argument('--triage',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    try:result=check(json.loads(Path(a.ledger).read_text()),Path(a.triage))
    except Exception as exc:result={'status':'bad_input','error':str(exc)[:300]}
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
    return 0 if result['status']=='pass' else 1

if __name__=='__main__':sys.exit(main())
