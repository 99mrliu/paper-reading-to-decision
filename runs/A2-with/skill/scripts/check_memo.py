#!/usr/bin/env python3
"""Verify every numeric segment's references; never certify semantic support."""
import argparse
import json
from pathlib import Path
import re
import sys
from decimal import Decimal
from numeric import normalize, numbers, finite

TAG=re.compile(r'\[(C\d+|context)\]')
LABEL=re.compile(r'(?:nDCG@\d+|p(?:50|95|99)\b|BM25|BGE[-\w.]*|Qwen[\w.\-]*|MOMENT[-\w]*|v\d+(?:\.\d+)*|(?:Table|Fig(?:ure)?\.?|Section|Eq\.?|p\.)\s*\d+(?:\.\d+)*)',re.I)


def values(text):
    text=LABEL.sub(' ',text)
    text=re.sub(r'(?<![\d.])(?:19|20)\d{2}(?![\d.])',' ',text)
    text=re.sub(r'^\s*(?:#+\s*)?(?:\d+[.)、]\s+)','',text)
    return numbers(text)


def check(memo,ledger,context):
    claims={c['id']:c for c in ledger.get('claims',[])}
    ctx=[Decimal(str(finite(v))) for v in context.get('numbers',[])]
    errors=[];used=set()
    for line_no,line in enumerate(memo.splitlines(),1):
        if not line.strip() or re.fullmatch(r'\s*[|:\- ]+\s*',line):continue
        pos=0
        for m in TAG.finditer(line):
            tag=m.group(1); segment=line[pos:m.start()];pos=m.end()
            if tag=='context':allowed=ctx
            elif tag not in claims:
                errors.append({'line':line_no,'error':'undefined reference '+tag});continue
            else:
                used.add(tag);c=claims[tag]
                allowed=[Decimal(str(finite(v))) for v in c.get('numbers',[])]
                if c.get('derived'):allowed.append(Decimal(str(finite(c['derived']['result']))))
            for v in values(segment):
                if v not in allowed:errors.append({'line':line_no,'error':f'{v} absent from {tag}'})
        if values(line[pos:]):errors.append({'line':line_no,'error':'untagged numeric segment','text':line[pos:][:130]})
    return {'status':'fail' if errors else 'pass','violations':errors,'used_claims':sorted(used),
            'scope':'numeric references only; source meaning and table alignment require review'}


def main():
    ap=argparse.ArgumentParser()
    for x in ['memo','ledger','context','out']:ap.add_argument('--'+x,required=True)
    a=ap.parse_args()
    try:result=check(Path(a.memo).read_text(),json.loads(Path(a.ledger).read_text()),json.loads(Path(a.context).read_text()))
    except Exception as exc:result={'status':'bad_input','error':str(exc)[:300]}
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
    return 0 if result['status']=='pass' else 1

if __name__=='__main__':sys.exit(main())
