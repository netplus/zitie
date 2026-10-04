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

本轮主吞吐为B06+B07，共20个不同主部首。

### B06：厂、匚、卜、冂、勹、儿、匕、几、亠、冫

重新对照`data/B06.json`与`data/coverage.json`的S01-2009中间索引，十项main_id与baseline笔画分组全部一致；既有`data/evidence/B06-content.json`继续支持2009 baseline身份、main_id和2画baseline分组。

本轮同时逐项检查两条教学提示、自查句、整字迁移语境和迁移边界，十项均保持候选／待核边界。尝试新增`data/evidence/B06-teaching-review.json`和`reviews/B06-content.md`时，连接器均返回`This tool call was blocked by OpenAI's safety checks. Please double check what you are sending.`，因此教学字段本轮不升级reviewed，canonical旧标签保持不变。

### B07：冖、凵、卩、厶、廴、艹、廾、宀、辶、彐

本轮逐项将canonical main_id与笔画数对照S01-2009中间索引，十项全部一致：冖、凵、卩、厶、廴为2画；艹、廾、宀、辶、彐为3画。既有`data/evidence/B07-teaching-review.json`继续支持两条教学提示、自查句、整字语境和迁移边界的非权威编辑一致性。

尝试新增`data/evidence/B07-content.json`和`reviews/B07-content.md`时遭遇同一连接器安全检查，因此baseline_identity、main_id和baseline笔画分组本轮不据此升级reviewed；只保留本次实际交叉检查记录。

本轮没有新增content_ready批次；B01—B03仍为30项content_ready，B04—B21共171项content_in_progress。未推进artwork、PDF、manifest、CI或release。

## 已知内容层缺口

按实时批次记录继续收口：
- B14：`data/evidence/B14-content.json`已实际存在；此前“baseline machine evidence仍缺”描述已过时，后续不重复补证据。
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
