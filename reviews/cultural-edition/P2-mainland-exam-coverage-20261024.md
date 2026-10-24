# P2 中国大陆教学拼音旁证与201主字任务台账（2026-10-24）

**仅建立审校证据与工作台账；不代表新书已审音或正式出版。**

## 本轮补充的真实依据

1. 汉考国际[中文考试服务网](https://admin.chinesetest.cn/goaboutus.do)的 [HSK二级“月亮”第10057项](https://admin.chinesetest.cn/standardsAction.do?leves=&means=getStandardWordsList&pager.offset=10050&pinyin=&words=&words_type=)拼作 `yuèliang`，与本字帖“上方按字标注”的 `yuè liang` 相容。
2. 同一考试服务商 [HSK一级“水果”第7543项](https://admin.chinesetest.cn/newhsk/standardsAction.do?leves=&means=getStandardWordsList&pager.offset=7540&pinyin=&words=&words_type=)拼作 `shuǐguǒ`，本字帖逐字教学版是 `shuǐ guǒ`。
3. [GB/T 16159—2012](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=5645BD8DB9D8D73053AD3A2397E15E74)为现行的《汉语拼音正词法基本规则》，[7.1条全文](https://www.htu.edu.cn/yw/2018/1008/c14029a129573/page.htm)允许小学低年级、幼儿识字读物根据需要按字注音。这是排版方式的规范依据，**不能作为具体词语的声调审音依据**。

上述两条汉考国际记录都是**中国大陆考试教学语料旁证**，不是《现代汉语词典》的正式词条审批。先前已登记的[台湾教育部“月亮”词条](https://dict.revised.moe.edu.tw/dictView.jsp?ID=164537&la=0&powerMode=0)写为 `yuè liàng`，这项跨地区差异继续保留在数据记录中，不擅自宣告所有词音获得审定。

[可机读的大陆教学词音旁证](../../data/cultural_edition/p2_mainland_exam_evidence_20261024.json)，两词 `publication_approved=false`。

## 全部201字审稿工作队列

- [B01–B07（70字）](../../data/cultural_edition/inventory/B01-B07.json)
- [B08–B14（70字）](../../data/cultural_edition/inventory/B08-B14.json)
- [B15–B21（61字）](../../data/cultural_edition/inventory/B15-B21.json)

本台账逐条从已有21个原字帖批次建立 `main_id`、汉字、源数据候选拼音、稿件阶段、主题插图草稿阶段、词音审校阶段。**源数据的候选拼音不自动升级为新版已采用拼音**。目前7字已有文化页面草稿（P1: 水、山、月、木；P4: 田、鼻、龠），剩余194字尚未编辑文化正文；4幅水、山、月、木的主题插画仅为待审SVG草稿。

[独立审核程序](../../scripts/cultural_editorial_coverage.py)与 [回归测试](../../scripts/test_cultural_editorial_coverage.py)确认每个ID/批次一一对应，检测漏字、重复、词音越级、美术未经审核即放行及月亮声调差异误删。CI产出`201-editorial-work-queue.json`，记录21批每批未编辑的具体数量。

## 下一步与发布门禁

- P2 Issue #189：寻找适用中国大陆出版的权威词典词条，完成多音字、轻声、引文及词义的**逐条人工签核**。首批35个不同词，19个台湾辅助直接词条，16个缺直接词条；额外2项中国大陆考试词表旁证不等于2项新规范词典签核。
- P3 Issue #190：其余197字的正式独立插图与全部201字的艺术审美审核，禁止同图换色充数；原笔顺图严格来自已发布PDF。
- P4/P5 Issues #191/#192：文化版真实分页覆盖更多字、逐页视觉质量、拼音/经典/授权联合放行。
- 所有旧`released`记录、v0.5.1 299页原PDF和在线打印功能保持不变。**新书正式发布总数仍为0字**。
