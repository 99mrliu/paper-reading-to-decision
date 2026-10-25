# 论文的比较，回答了我们的采纳问题吗？

这是一次adoption-review 1.1.0的真实AI辅助阅读分享，问题是：已有BM25+cross-encoder的技术文档服务，是否应在重排前增加dense融合？任务背景是构造情境，论文是真实原件。我们复用2026-10-23的A2-with独立会话，没有新增模型实验、检索训练或上线测量。

## 实际输入、方法与回答

[原任务全文](evidence/task.md)、[实际会话提示](evidence/prompt.txt)、[实际环境与用时](evidence/session.json)原样或等值保留。原会话模型标签gpt-6.1-sol，Codex CLI0.163.0-alpha.11.2，用时348.958秒；精确服务快照与账单未知。实际模型当时读取完整18页PDF，当前包按新文本限额提供覆盖全部账本引文的七页完整原文提取件，见[原文范围](sources/SOURCE.md)。

[冻结Skill](skill/SKILL.md)先把现有系统、论文实际基线和候选系统分开，再读方法、目标表格与下游重排实验；用全行表格助手检查范围，用精度助手检查测量计划，最后分别做字面与语义核查。选择这些步骤，是因为首阶段平均收益不能替代最终排序收益，表格局部行也不能给出完整范围。

下面逐字引自[实际AI报告全文](evidence/report.md)：

> **建议：有条件采用；目前保留现有管线，只进入离线验证。** 只有融合在相同重排预算下，相对当前生产管线带来有实际价值的最终排序收益，同时满足单查询退步和 CPU 延迟门槛，才值得上线。不能仅凭首阶段平均收益批准，也不能因为已有可靠 reranker 就认定 dense 无价值：它可能补进当前候选集缺失的相关文档，这恰是本地实验要验证的增量。

作者侧判断：这份条件性建议有原文支持，但没有证明本地融合必然更好。所给PDF第5页的方法与第14页Table13以dense及融合候选的重排结果为比较；当前BM25+reranker并非Table13中的直接比较列。逐查询oracle需要标签，也不能当作现有可部署系统。完整补充表不在原输入中，因此应写“未直接测量”，保留本地验证，而不是由论文直接批准上线。

## 原文、全表与解释

来源为Chauhan与Agarwal的The Fusion Tax，固定arXiv:2610.30612v1、IEEE Access2026，CC BY4.0。核查[第5页](sources/pages/p05.txt)比较设计与[第14页](sources/pages/p14.txt)完整表头和上下文。

![论文PDF第14页，Table13/14；原作者与许可见SOURCE](sources/page14.png)

图像为原论文页图，署名和出处见sources/SOURCE.md。数值和表头还以文字提供，不要求只靠图片解读。以下计算Reranked Interp减Reranked Dense，不混用First stage列：

| 语料 | 重排Dense | 重排Interp | Interp−Dense |
| --- | ---: | ---: | ---: |
| SciFact | 0.739 | 0.738 | -0.001 |
| FiQA | 0.426 | 0.429 | 0.003 |
| NFCorpus | 0.340 | 0.350 | 0.010 |
| ArguAna | 0.479 | 0.490 | 0.011 |
| SciDocs | 0.190 | 0.190 | 0.000 |
| TREC-COVID | 0.808 | 0.826 | 0.018 |
| Quora | 0.893 | 0.893 | 0.000 |

完整七行范围为−0.001至+0.018，包含两个零值。它不是融合相对当前BM25+reranker的收益或通用上界；跨零也不能证明等效。原始结果为[table13.json](evidence/table13.json)，原始布局为[p14.txt](sources/tables/p14.txt)，调用如下：

```sh
python3 skill/scripts/table_stats.py --layout sources/tables/p14.txt --table 13 --columns FirstDense,FirstInterp,RerankDense,RerankInterp,RerankRRF,InterpBefore,InterpAfter,InterpNet,RRFBefore,RRFAfter,RRFNet --rows 7 --diff RerankInterp:RerankDense --out /tmp/table13.json
```

列名由读者根据原页指定，脚本不能理解表头；遇到缺行、列数不符、重复名称就失败。原Table8解析因两种方法共享行名而失败，原会话按原方法分块、保留全行后重算，未删负值。失败结果、实际规范化布局、修正前报告和失败说明均保留于evidence/。

## 平均提升、个体风险与精度

第14页Table13的FiQA插值受损率从14.7%变15.6%，TREC-COVID从14.0%变22.0%；平均差为正不等于每类查询受益。第12页匹配查询分析中SciFact修复原受损30个中的27个，同时新增17个。净受损率下降不代表原问题全部消失，且比较对象仍是dense。原图、页文、完整AI报告与账本允许逐项核查这些解释。

原AI的[精度情景](evidence/precision_scenario.json)假设独立等权配对均值SD=0.20，按h=z×s/√n，n=400的95%半宽约0.0196，目标0.005需约6147。它是明确标注的反例，不是实际流量方差、功效保证或生产样本量承诺。论文dense−BM25的方差不能冒充融合+reranker减BM25+reranker的方差；应先pilot估计实际比较，并按意图簇、分层回权等设计另行规划。

## 真实失败、复核与复读

[原始失败说明](evidence/failure_notes.md)、[修正前报告全文](evidence/report_before_numeric_fix.md)、[失败数字检查](evidence/memo_check_failed.json)与最终检查均保留；[必要操作记录](evidence/selected-operations.jsonl)保留整次原始命令和完整输出，包含成功与失败。完整原生轨迹按平台协议另外保留，不称本文件为完整轨迹。

[原文账本](evidence/ledger.json)保留全部原始主张与引文；[语义自查](evidence/semantic_review.md)明确比较臂、统计单位和外推边界。字面检查只能确认引文与有限算术，不能证明科学语义、原作者底层实验或本地效果；作者侧AI自查也不是独立真人审稿。

执行`python3 recheck.py`可复算旧产物并确认所有账本引文在所供原文页中存在，不调用模型。按[REPRODUCE.md](REPRODUCE.md)可用本地片段准备新会话；这是缩小输入范围后的复读，不声称等价于完整PDF新实验。原模型的实际提示和输出完整保留，新的适配提示明确标注尚未执行。

这次分享的贡献是把“论文平均效果”转成不偷换比较对象、保留完整范围并知道该测什么的决策过程。适用范围和贡献见[SOURCES.md](SOURCES.md)。正文没有据一个案例宣称稳定提效，也没有把文件齐全当作科研验证。
