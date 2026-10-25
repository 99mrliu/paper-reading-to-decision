#!/usr/bin/env python3
"""Independent paired-mean normal-approximation CI planning, not a power test."""
import argparse
import json
import math
from pathlib import Path
from statistics import NormalDist
from numeric import finite


def plan(sd,n,target,confidence=.95):
    sd=finite(sd);target=finite(target);confidence=finite(confidence)
    if sd<=0 or target<=0 or n<=1 or not 0<confidence<1:raise ValueError('invalid precision assumptions')
    z=NormalDist().inv_cdf((1+confidence)/2)
    return {'sd':sd,'n':n,'confidence':confidence,'approx_half_width':z*sd/math.sqrt(n),
            'target_half_width':target,'n_for_target_half_width':math.ceil((z*sd/target)**2),
            'scope':'Independent paired observations, normal approximation; estimated SD must match the actual comparison. Not a power calculation or guaranteed sample size.'}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--sd',type=float,required=True);ap.add_argument('--n',type=int,required=True)
    ap.add_argument('--half-width',type=float,required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    try:r={'status':'ok',**plan(a.sd,a.n,a.half_width)}
    except Exception as exc:r={'status':'error','error':str(exc)}
    Path(a.out).write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False))
    raise SystemExit(0 if r['status']=='ok' else 1)
