# 关键证据格式

`out/ledger.json`：

```json
{"claims":[{"id":"C1","type":"reported","statement":"原文事实及其比较对象、单位和条件","verdict":"conditional","condition":"原论文的设置","evidence":[{"page":4,"unit":"Table 2, row A","quote":"完整原文句或表格行，至少12字符"}],"numbers":[0.8,0.7]}]}
```

原文数字必须出现在本 claim 的 evidence 引文集合内，不能只在同页任意地方存在。引用表格时保留行名和完整数据；范围可引用多行。引用不等于语义正确，必须人工/Agent 对照表头核查。

`type`: reported / derived / assumed。`verdict`: supported / conditional / contradicted / unknown。
`condition` 必填。unknown 需要 `missing`、`next_step`，可以没有引文，不能填未核数字。assumed 放自行设定的假设，必须 conditional，不能伪装原文结论。

派生值填 `derived: {"formula":"a-b","inputs":{"a":0.8,"b":0.7},"result":0.1}`，输入必须来自同 claim 引文。支持 + - * / ** % 及 max/min/abs/round/sqrt；结果必须有限，误差至多 1e-6。做区间、样本量或需要复杂计算时使用附带脚本并保留输入/输出，再解释。

禁止 `extra_numbers`。符号中的数字不是测量值（如 nDCG@10）；memo 检查器会忽略常见指标/型号的数字，其他名称解析失败时明确在上下文登记并保留说明，不能把没证据的结果列入上下文。

`out/context.json`: `{"numbers":[100,50000],"rationale":"这些来自任务部署约束；自行提出的门槛逐一说明理由"}`。

表格范围 helper：

```sh
python3 skill/scripts/table_stats.py --layout out/triage/tables/pNN.txt --table <编号> --columns <按表头顺序的逗号分隔列名> --rows <表的数据行数> --out out/table.json
# 可加 --diff <候选列名>:<基线列名>，输出逐行差值及完整 min/max。
python3 skill/scripts/precision.py --sd <配对差标准差> --n <样本数> --half-width <所需半宽> --out out/precision.json
```

表格脚本是单行数字网格解析器：保留原行、拒绝列数不合/不满足行数；不支持任意合并单元格。不能靠调行数掩盖缺行。精度计算是正态近似，聚类/时序数据需另设方案。
