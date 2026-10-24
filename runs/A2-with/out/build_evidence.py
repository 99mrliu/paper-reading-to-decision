import json,re,sys
from pathlib import Path
sys.path.insert(0,'skill/scripts')
from numeric import numbers
p=Path('out/triage')
text=(p/'tables/p09.txt').read_text()
block=text.split('TABLE 8.')[1].split('base, large:')[0]
rows=[]
for l in block.splitlines():
 if re.match(r'\s*(SciFact|FiQA|NFCorpus|ArguAna|SciDocs|TREC-COVID|Quora)\s+[-+\d]',l): rows.append(l)
assert len(rows)==14
for name,rs in [('interp',rows[:7]),('rrf',rows[7:])]:
 Path(f'out/table8_{name}_layout.txt').write_text('TABLE 8. Extracted '+name+' block; column order retained\n'+'\n'.join(rs))
claims=[]
def add(cid,statement,page,unit,quotes,typ='reported',derived=None):
 if isinstance(quotes,str):quotes=[quotes]
 c=dict(id=cid,type=typ,statement=statement,verdict='conditional',condition='仅限论文所测模型、语料、候选深度与硬件；不得直接外推生产管线',evidence=[dict(page=page,unit=unit,quote=q) for q in quotes],numbers=sorted(set(float(x) for q in quotes for x in numbers(q))))
 if derived:c['derived']=derived
 claims.append(c)
def excerpt(page,start,end):
 t=(p/'pages'/f'p{page:02d}.txt').read_text();a=t.index(start);return t[a:t.index(end,a)+len(end)]
add('C1','首阶段比较完整插值块：相对always-dense的收益与损失，另列oracle',9,'Table 8, Interp(0.7), all seven rows',rows[:7])
add('C2','RRF完整块包含负收益，不采用正文四舍五入范围替代表格',9,'Table 8, RRF, all seven rows',rows[7:])
add('C3','融合公式、归一化、固定权重和检索深度',5,'IV-B',excerpt(5,'Fusion. RRF','deterministic.'))
add('C4','重排比较为候选源各自top30，使用同一重排器',5,'IV-C',excerpt(5,'To measure how much','for cost.'))
t13=json.loads(Path('out/table13.json').read_text());qr=[r['raw'] for r in t13['rows']]
add('C5','重排全表完整范围及各语料结果',14,'Table 13, all seven rows',qr)
add('C6','重排插值减重排dense最小值',14,'Table 13, all seven rows',qr,'derived',dict(formula='min(a-b,c-d,e-f,g-h,i-j,k-l,m-n)',inputs=dict(zip('abcdefghijklmn',[v for r in t13['rows'] for v in [float(r['values']['RerankInterp']),float(r['values']['RerankDense'])]])),result=-.001))
add('C7','重排插值减重排dense最大值',14,'Table 13, all seven rows',qr,'derived',dict(formula='max(a-b,c-d,e-f,g-h,i-j,k-l,m-n)',inputs=dict(zip('abcdefghijklmn',[v for r in t13['rows'] for v in [float(r['values']['RerankInterp']),float(r['values']['RerankDense'])]])),result=.018))
add('C8','重排会新增受损查询，不能把净受损比例下降当作全部修复',12,'V-H',excerpt(12,'These are\nnet changes','Supplementary Table S12)'))
add('C9','接近目标文档量的FiQA成本实例',14,'Table 14, FiQA complete row',[l for l in (p/'tables/p14.txt').read_text().splitlines() if re.match(r'\s*FiQA\s+58k',l)][0])
add('C10','硬件、缓存及采样条件',5,'IV-C',excerpt(5,'Efficiency is measured','(dense).'))
add('C11','风险厌恶检验仅相对always-dense',8,'V-D',excerpt(8,'Risk-sensitive significance.','risk-robust.'))
add('C12','候选权重留出选择及风险',7,'Table 4, all seven rows',[l for l in (p/'tables/p07.txt').read_text().split('TABLE 4.')[1].split('TABLE 5.')[0].splitlines() if re.match(r'\s*(SciFact|FiQA|NFCorpus|ArguAna|SciDocs|TREC-COVID|Quora)\s+\d',l)])
add('C13','重排和生产延迟外推局限',15,'VI-G',excerpt(15,'(1) We evaluate','not Lucene;'))
add('C14','路由负结果有方法边界',12,'V-G',excerpt(12,'Trained on the six','signals we tested.'))
add('C15','排名与覆盖不能等同，聚合召回掩盖个体损失',8,'V-D',excerpt(8,'Mostly ranking, not coverage.','second stage removes.'))
add('C16','精度计划需pilot；不是新管线方差估计',15,'VI-D',excerpt(15,'As\na planning illustration','overlapping zero does not establish equivalence.'))
add('C17','平衡语料可偏好rank fusion',7,'Table 5, NFCorpus and TREC-COVID complete rows',[r['raw'] for r in json.loads(Path('out/table5.json').read_text())['rows'] if r['label'] in ['NFCorpus','TREC-COVID']])
Path('out/ledger.json').write_text(json.dumps({'claims':claims},ensure_ascii=False,indent=2))
Path('out/context.json').write_text(json.dumps({'numbers':[30,10,100,50000,.6,.7,.5,0,1,60,200,400,.20,.005,.01,.05,5,95,6147,.0196,1000], 'rationale':'任务部署约束：50000篇、CPU首阶段p95 100ms、固定top30 reranker、用户阅读top10。建议探索权重0/0.5/0.6/0.7/1（dense权重），RRF k60为论文候选。自定门槛：平均最终nDCG增益至少0.01且95%CI下界>0；实质退步定义低于基线0.05，比例95%上界≤5%；关键分层平均差95%下界≥-0.005。pilot 200个独立意图簇，400只是精度反例；假设SD0.20时半宽0.0196，目标0.005需6147，仅为独立均值精度情景，非实际方差、非功效保证。1000为报告字符上限说明不使用；0为零差/端点。'},ensure_ascii=False,indent=2))
