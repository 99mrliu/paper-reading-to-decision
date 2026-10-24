# 重做阅读与复核旧结果

## 无模型账号：检查原文并复算保存产物

Python 3.11+，只用标准库，在仓库根目录运行`python3 recheck.py`。预期status=passed，Table13七行差的范围为-0.001至0.018，SD=0.20、n=400的假设精度半宽约0.0196，目标0.005对应约6147。它还运行原来的引文账本和数字检查器。退出成功不证明科学语义或本地系统性能。

原件固定为materials/fusion-tax.pdf。打开PDF第14页确认Table13的Reranked Dense与Interp两列，再核对runs/A2-with/out/table13.json，不能混用First stage列。Table13不是BM25+reranker对融合+reranker的直接比较。再读第5页实验配置、第12页修复/新增受损、第15页外推与精度限制。相邻页和全文均本地保留。

## 有AI账号：在新目录重做同一案例

1. `python3 prepare_case.py --destination /tmp/my-fresh-adoption-case`；目标目录须尚不存在。只复制PDF、原任务、冻结Skill与实际提示，不复制原答案。
2. 在一个新的、有本地文件和Python工具的AI会话中打开此目录，把prompt.txt全文作为指令。保留模型标签、可知版本、环境、提示、工具记录、失败及out/report.md。没有此类工具时不能声称复现了原工作流。
3. 按cases/A/acceptance.md检查回答的比较对象、完整表格范围、条件与精度逻辑。它是原项目运行前冻结的自查标准，不是比赛隐藏评分标准。只对自己的新答案评价，不要求账本格式相同。
4. 检查是否把相对dense的结果偷换成相对BM25+reranker；是否遗漏-0.001或零值；是否把跨零当等效；是否把假设SD当本地pilot方差。保留失败，不能复制旧报告称作新运行。

原实践环境：macOS Apple Silicon，Python3.14.7，PyMuPDF1.28.2，Poppler26.08.0，Codex CLI0.163.0-alpha.11.2，模型标签gpt-6.1-sol。精确服务快照及账单不可取得。原run_session.py保存于provenance，只作为原采集器记录；其中应用路径依赖当时macOS安装，不能直接当跨平台通用命令。本次新目录准备和离线复算已测试，完整AI重跑未在本次新增执行，不能保证不同模型逐字相同或等价质量。

Skill的triage依赖PyMuPDF；原环境同时有Poppler。新运行按Skill中的路径调用，参数以随附源码为准。所有解析失败和原修复记录保留在runs/A2-with/out，不将首次失败藏掉。
