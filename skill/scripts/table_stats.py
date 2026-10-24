#!/usr/bin/env python3
"""Read one-line numeric table rows. Column labels are supplied from the header."""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import sys
from numeric import normalize


def extract(text,table,columns,count):
    lines=text.splitlines(); start=None; block=[]
    for line in lines:
        m=re.match(r'\s*TABLE\s+(\d+)\.',line,re.I)
        if m:
            if start is not None:break
            if int(m.group(1))==table:start=True
        elif start is not None:block.append(line)
    if start is None:raise ValueError('table caption not found')
    token=re.compile(r'[-+−]?\d+(?:\.\d+)?%?')
    rows=[]
    for raw in block:
        # Numeric grids have a textual row name, then whitespace-delimited cells.
        m=re.match(r'^\s*([A-Za-z][A-Za-z _/()\-]*?)\s+((?:[-+−]?\d+(?:\.\d+)?%?\s*)+)\s*$',raw)
        if not m:continue
        vals=token.findall(m.group(2))
        if len(vals)!=len(columns):raise ValueError('column mismatch on row '+m.group(1))
        rows.append({'label':m.group(1).strip(),'values':{c:str(Decimal(v.replace('−','-').rstrip('%'))) for c,v in zip(columns,vals)},'raw':raw})
    if len(rows)!=count:raise ValueError(f'expected {count} data rows, found {len(rows)}; inspect wrapped/merged rows')
    if len({r['label'] for r in rows})!=len(rows):raise ValueError('duplicate row labels')
    ranges={c:{'min':str(min(Decimal(r['values'][c]) for r in rows)),
               'max':str(max(Decimal(r['values'][c]) for r in rows))} for c in columns}
    return {'rows':rows,'ranges':ranges,'table':table,'n_rows':len(rows),'warning':'Column order/meaning supplied by reader; verify original header. No semantic certification.'}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--layout',required=True);ap.add_argument('--table',type=int,required=True)
    ap.add_argument('--columns',required=True);ap.add_argument('--rows',type=int,required=True)
    ap.add_argument('--diff');ap.add_argument('--out',required=True);a=ap.parse_args()
    try:
        p=Path(a.layout);data=p.read_bytes();columns=a.columns.split(',')
        if len(set(columns))!=len(columns):raise ValueError('duplicate columns')
        result=extract(data.decode(),a.table,columns,a.rows);result['source_sha256']=hashlib.sha256(data).hexdigest()
        if a.diff:
            left,right=a.diff.split(':');ds=[Decimal(r['values'][left])-Decimal(r['values'][right]) for r in result['rows']]
            result['difference']={'left':left,'right':right,'by_row':{r['label']:str(v) for r,v in zip(result['rows'],ds)},'min':str(min(ds)),'max':str(max(ds))}
        result['status']='ok'
    except Exception as exc:result={'status':'error','error':str(exc)[:300]}
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
    return 0 if result['status']=='ok' else 1

if __name__=='__main__':sys.exit(main())
