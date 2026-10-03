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

本轮主吞吐为B07+B13，共20个不同主部首。

### B07：冖、凵、卩、厶、廴、艹、廾、宀、辶、彐

新增`data/evidence/B07-teaching-review.json`。十项的两条教学提示、自查句、整字语境和迁移边界已完成非权威编辑一致性复核。尝试新增`data/evidence/B07-content.json`、`reviews/B07-content.md`及同步canonical教学状态时均被连接器安全检查拒绝，因此B07的baseline机器evidence仍未入库，canonical旧标签也未据此改写。

### B13：矛、耒、老、耳、臣、覀、而、页、至、虍

新增`data/evidence/B13-teaching-review.json`，为十项已有教学字段补齐独立机器可读编辑复核记录。既有`data/evidence/B13-content.json`与`reviews/B13-content.md`继续支持2009 baseline身份、main_id和笔画分组；其它权威字段继续pending。

本轮未新增content_ready批次；B01—B03仍为30项content_ready，B04—B21共171项content_in_progress。未推进artwork、PDF、manifest、CI或release。

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
