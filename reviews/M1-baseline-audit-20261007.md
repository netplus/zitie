# M1首轮基线审计与勘误登记

日期：2026-10-07。执行者：ChatGPT（同一Agent工程复核，不称独立专家审定）。关联Issue #58。当前M1进行中，未修复E001/E002，未发布新PDF。

## 可重复基线

上游main：`1d6a3a797a8e61264f34337274aecc35e2f623e7`，Git tree：`f2301b2162155f362ff6ad6199914b77cb7ffaa5`。

通过GitHub connector下载PR #57 run `37577828051` 的artifact `11463223206`。下载ZIP的SHA256实际计算为`5384e8814d3a1495c64ffa8f91aeb1a37edbd0fbf583eb448148dea0fcba7e52`，与服务返回值一致。解开`zitie-source.zip`、恢复归档权限后，本地`git write-tree`也为上述tree，证明本次检查的源码与main完全一致，不只是凭文件名推断。

正式PDF：`deliverables/releases/v0.4.0/B01-B21_with_preface_toc_appendices_v0.4.0_A4.pdf`。
实际检查：276页，3,749,164字节；SHA256 `ab3c23d7547872f4d0e2c128de397e9e89ed6de97b681876e2dff017ff5c4894`。

全部15份归档PDF通过字节、A4尺寸、页数、状态、review路径与manifest检查：13份draft、1份RC、1份released，合计17,550,724字节。没有改变任何历史PDF或manifest条目。

## 已实际查看的页面与问题

本轮实际打开MuPDF渲染的第270、272、274页，并打开Poppler渲染的第270页。其它已生成预览不计作视觉已审；本轮不是276页全量视觉验收。

### E001：V007目标字形缺失（open，阻止M1结束）

`data/variants.json`的V007为parent=手、form=龵、example=看、position=top。

第270页MuPDF渲染在“手→”后空白；第272页“手 / 龵 / 看”中的龵也空白。第270页Poppler渲染显示缺字方框。pypdf仍能从两页提取龵，而MuPDF文本层丢失该字：**字符串存在与字体可显示不能等同**。

`build_book_matter.py`的卷末目前统一使用未嵌入的STSong-Light CID字体；下一修复需验证form专用嵌入式fallback、所有32项form覆盖，以及实际渲染效果。不得以“字体注册成功”“文本提取得到龵”关闭此问题。修复进入新v0.4.x产物，不能覆盖旧正式PDF。

### E002：细笔名统计缺少范围（open，阻止M1结束）

第274页显示“P2细笔名：157 reviewed + 14 conflict_fail_closed”，与全书201项状态并列而未标范围。

`data/coverage.json`中`phase1_content_progress.p2_fine_stroke_names.scope=B04-B21`、`target_count=171`。原157/14本身没有算错，遗漏的是统计范围，不能将其当作201项合计。下一修订应明确B04—B21/171项；需要全书合计时另核B01—B03的30项，不直接改大数字。

### E003：过期重建说明（本次文档修复）

原BUILD.md仍写“首批简单独体形”“每字不超过6笔”，与当前全21批、每页最多6个步骤且复杂字分页的生成器不一致。本次文档已同步全书research构建路径，并明确当前版本硬编码、新版本需同步配置/页脚/校验器、重建成功不等于视觉通过。

## 本轮测试与边界

已执行：21批结构校验；原数据测试32项、归档测试13项、绘图测试10项；新增阶段状态测试9项；历史交付物不变性检查；v0.4.0正式状态门禁；新周期状态校验。

首次本地绘图测试因矢量缓存未放到build/vectors而失败；从同一已核SHA的artifact恢复到正确目录后，10项全部通过，没有改动绘图测试或矢量内容。新状态测试使用独立fixture，不把后续阶段推进误当作测试失败。

新增检查只验证阶段顺序、退出记录、阻断勘误、候选字节与最终页覆盖的记录一致性；不授予来源审定或视觉验收。输出当前M1、E001/E002 open、final_release_eligible=false。目标HEAD CI结果以后续实际workflow为准，不预填成功。

原docs/STATUS.md按原字节移入docs/history/v0.4.0-STATUS.md；新入口描述M1→M2→M3→Q1。旧P0—P7及内容字段状态未改。

## 下一最小工作单元

修复E001/E002，建立v0.4.x候选的正确版本标识及字体覆盖检查，重看所有受影响页和关联索引。M1未退出，不进入M2；最终Q1留待M3候选冻结之后。
