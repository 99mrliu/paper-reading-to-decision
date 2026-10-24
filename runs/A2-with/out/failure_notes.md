保留的失败与修复：
- table8_failed.json：全表因两方法重复语料行名被助手拒绝；改为按原方法分块，无删行。
- build_evidence_failed.py：初次正文边界截断不精确，行数断言失败；改为在后续正文之前截断。
- table8_interp_failed.json、table8_rrf_failed.json：上游未产出分块文件导致缺文件；保留后复算。
- build_evidence_failed2.py：跨换行的 expensive 结束锚点不匹配；改用原文 not Lucene; 锚点。
- memo_check_failed.json 与 report_before_numeric_fix.md：初稿范围同句引用标签、逐行派生值及负门槛登记不足；补逐行派生证据，拆开数字引用并登记有符号门槛。未改变论文数值来迁就检查。
