---
name: adoption-review
description: Evaluate whether a quantitative methods paper supports changing an existing system. Reconcile the paper's actual comparators, full table ranges, downstream stages and measurement precision into a short, source-linked adoption decision.
metadata:
  version: "1.1.0"
---

# 方法采纳评审

输入是论文 PDF、待决策的问题和现有系统约束。交付可用于评审的中文备忘录与可核查的关键证据。重点处理“论文中的比较是否回答我们的决策”，按需要取证，不替用户执行论文方法或上线。

## 阅读与判断

1. `python3 skill/scripts/triage.py INPUT/materials/<paper.pdf> --out out/triage`。先看 map，再按决策选页。没有固定八页上限；定义、表格或下游结论缺上下文时继续查相邻页。图表文字无法确定列归属时看原页，不从被打乱的文本猜列。
2. 明确三个对象：现有系统、论文实际基线、候选系统。逐条区分原文观测、计算、作者解释、我们的建议。没有直接比较臂时写“未直接测量”，不把其他基线上的增益当作我们的上界。下游重排、缓存或审核存在时，查其独立实验。
3. 只登记会影响建议的证据，格式见 [ledger.md](references/ledger.md)。原文数字保留比较对象、单位、条件；尾部风险必须写清相对哪个参照。不要为了有账本收集所有数字。
4. **表格范围需要完整行集合。** 算 min/max 时写出涵盖和排除的行；不能丢掉零值、负值或小数位较多的端点。可用 `table_stats.py` 从布局文本提取全表、算范围与列差，按表头确认列顺序，异常就回原页。备忘录中的范围必须与表格结果一致。
5. **测量计划按要区分的量设计。** 先说明比较对象、独立抽样单位、变异来源、效应或精度目标。`precision.py` 只算独立配对均值的近似 CI 半宽，不是功效分析。论文中 A−B 的方差不能冒充新管线 C−D 的方差；先 pilot 估计。不能由区间跨零推出等效，也不能用比目标效应还宽的区间保证能分辨。

## 输出与机械检查

`out/report.md` 包括：建议与成立条件、关键证据与解释、适用边界、成本、未知项、下一步测量。篇幅服从用户约束。每个定量句附 `[C#]`；部署约束或自行提出的门槛放在 `out/context.json` 并标 `[context]`。门槛不是论文事实。

```sh
python3 skill/scripts/check_ledger.py --ledger out/ledger.json --triage out/triage --out out/check.json
python3 skill/scripts/check_memo.py --memo out/report.md --ledger out/ledger.json --context out/context.json --out out/memo_check.json
```

先保留失败文件再修正。机械通过只证明文本/数字与算术约束通过，不能证明分组、表头、科学意义或结论正确。最后单独核查：比较臂有无偷换、统计单位是否独立、完整范围与单位、未知是否影响建议。无需宣称采用，一份有依据的条件性决定即可。

## 异常与边界

- 无文本层：triage 退出 2，说明缺什么，申请文字版/OCR或原始表格；停止未经核验的定量结论。
- 文件损坏/加密：保留退出信息，停止；缺页/缺补充：只在提供范围内判断，写具体缺口与获取路径。
- Poppler 不可用时有 PyMuPDF 降级并标 warning；表格不清则看原页。看不到就标未知。
- 工具/预算失败时保留已有产物与未核项，不补写成功结果。不联网、执行新实验或发布，除非用户授权。
