# 当前编写状态

更新：2026-10-03。工程处于“阶段1：内容覆盖优先”。

## 当前阶段

阶段1目标是先完成201个主部首的字段级内容和证据链；artwork、PDF、manifest和CI尾项不再阻塞后续内容字段推进。阶段2统一处理图形与版式，阶段3处理归档与发布。阶段1的`content_ready`不等于`artwork_ready`或`release_eligible`。

## 范围与计数

- 主部首范围：**201/201已分配**，B01—B20各10项，B21为龠1项。
- `content_ready`：**30项**，B01—B03。
- `content_in_progress`：**171项**，B04—B21。
- 已形成练习页：20项（B01+B02）。
- Git内阶段PDF：11份draft。
- 正式release：0。
- GF0011—2022逐项精确字形、附形、名称和编码继续作为全书级pending；不阻塞其它独立字段。

## 最新阶段1检查点

本轮主吞吐按20个不同主部首计为B12+B16；另补入B06 baseline evidence，不把附带补录重复计入20项吞吐。

### B12：屮、巛、殳、毋、鸟、疒、穴、疋、皮、癶

新增`data/evidence/B12-teaching-review.json`。十项的两条教学提示、自查句、整字语境和迁移边界已完成非权威编辑一致性复核；该证据不支持GF0011—2022精确身份、正式结构、逐笔笔顺、细笔名、采用读音、S03名称或正式位置变体。canonical `data/B12.json`中的`teaching_text`状态尚未同步，仍以evidence的范围为准。

### B16：赤、豆、酉、辰、豕、卤、里、足、邑、身

既有`data/evidence/B16-content.json`和`data/evidence/B16-teaching-review.json`继续作为证据；本轮已将`data/B16.json`十项的`teaching_text`同步为`reviewed_editorial_non_authoritative`。人工`reviews/B16-content.md`仍含旧的“evidence尚未入库”描述，更新该review文件的写入被连接器安全检查拒绝，因此该文本滞后不反向否定已在库evidence。

### 附带补录：B06

新增`data/evidence/B06-content.json`，确认厂、匚、卜、冂、勹、儿、匕、几、亠、冫与已审S01-2009中间索引的main_id及二画baseline分组一致。B06教学review及B07 baseline evidence写入均被连接器安全检查拒绝，未升级相应字段。

## 已知内容层缺口

按实时批次记录继续收口：
- B14：baseline machine evidence仍缺；
- B16：canonical data和baseline evidence已在库，人工review文字仍有旧状态描述待同步；
- B17：canonical data、baseline evidence与教学evidence已在库，人工content review仍缺；
- B21：baseline evidence、canonical `data/B21.json`与人工review均已入库；教学字段已完成人工非权威编辑复核；
- 更早B04—B13仍需继续逐项关闭名称、笔顺／细笔名、采用读音、结构与位置迁移等字段。

## B03阶段2/3尾项

B03内容层视为`content_ready`。artwork/layout人工记录已存在；PDF归档、manifest、通用hard-gate和最终PR收尾属于独立工程尾项，不阻塞阶段1内容吞吐。

## PDF状态

最新仓库合集仍为：

`deliverables/drafts/v0.2.1/B01-B02_with_preface_draft_A4.pdf`

23页；当前阶段1没有新增或修改PDF。

## 下一内容工作

1. 补B17人工content review和B16 review文字同步；
2. 补B14 baseline machine evidence；
3. 以20个不同主部首为一轮，批量关闭S03名称、笔顺／细笔名、采用读音、结构和位置迁移字段；
4. GF0011—2022逐项精确字段继续由Issue #4并行追踪。
