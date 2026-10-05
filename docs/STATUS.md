# 当前编写状态

更新：2026-10-05。工程处于“阶段1：内容覆盖优先”。

## 当前阶段

阶段1目标是先完成201个主部首的字段级内容和证据链；artwork、PDF、manifest和CI尾项不再阻塞后续内容字段推进。阶段2统一处理图形与版式，阶段3处理归档与发布。阶段1的`content_ready`不等于`artwork_ready`或`release_eligible`。

## 阶段检查点

PR #9 已于2026-10-05阶段性合入 `main`，合并提交：

`8b6213b0ec5f85ae26915aa6f823dcb2ba04c187`

该次合入保留阶段1内容优先重构、B03内容成果、B04—B21内容稿以及已真实入库的字段级review/evidence。合入前PR HEAD `45f90049496445206bbd2a265dc43be700c5ccfa` 的 `Book integrity checks` 已成功。该阶段合入不表示全书内容完成、artwork完成或正式发布。

## 范围与计数

- 主部首范围：**201/201已分配**，B01—B20各10项，B21为龠1项。
- `content_ready`：**30项**，B01—B03。
- `content_in_progress`：**171项**，B04—B21。
- 已形成练习页：20项（B01+B02）。
- Git内阶段PDF：11份draft。
- 正式release：0。
- GF0011—2022逐项精确字形、附形、名称和编码继续作为全书级pending；不阻塞其它独立字段。

## 当前字段闭合进展

阶段1已经从“批次范围分配”进入“既有批次字段级证据闭合”。截至本检查点，仓库中的进展至少包括：

- **B04**：baseline、教学字段、S03部件名称和structure evidence均已在库；10项均直接列入GF0013—2009《现代常用独体字表》，canonical structure已同步reviewed。
- **B05**：baseline、教学字段、S03部件名称和structure evidence均已在库，canonical已同步相关reviewed状态。牙第2笔“撇折/竖折”继续 `conflict_fail_closed`。
- **B06**：baseline、S03部件名称和structure evidence已在库；baseline/name canonical状态已同步；教学字段专用evidence仍待补。
- **B07**：baseline、S03部件名称、教学字段和structure evidence均已在库；baseline笔数canonical状态已同步。
- **B08**：baseline和教学字段evidence已在库。
- **B09**：baseline、教学字段、S03人工review、S03 machine evidence和structure evidence均已在库；名称canonical状态已同步。
- **B10—B11**：baseline、S03名称evidence已在库，canonical已完成一轮证据状态同步；B11教学字段evidence亦在库。
- **B12—B14**：baseline、教学字段和S03名称evidence已形成；部分canonical/review文字仍有同步债。
- **B15—B18**：已有baseline、教学字段与S03名称/适用性证据；B15、B16、B17、B18均已有不同程度的canonical同步。
- **B19**：baseline、教学字段与 `data/evidence/B19-component-name.json` 已在库；canonical名称状态已同步。
- **B20**：baseline和教学字段evidence已在库；S03完整主体表视觉审读已经登记在 `sources/catalog.json`，machine component-name evidence仍待补。
- **B21**：baseline evidence、canonical数据和人工review均已在库。

以上只表示对应字段的证据链进展，不表示各批次已经达到`content_ready`。

## 最新40项结构推进（2026-10-05）

B06—B09共40个不同主部首完成GF0013—2009《现代常用独体字表》结构适用性原页审读并入库专用evidence：
- B06：5项精确命中（厂、卜、儿、匕、几），5项S07不适用；
- B07：0项精确命中，10项S07不适用；
- B08：0项精确命中，10项S07不适用；
- B09：7项精确命中（气、长、片、斤、爪、父、文），3项S07不适用。

精确命中项的structure已同步为\`reviewed_S07_GF0013_2009_undecomposable\`；未命中项只标记为“S07已审读但不能关闭结构，等待其它适用权威来源”，不反推为合体字。对应evidence为\`data/evidence/B06-structure.json\`至\`B09-structure.json\`，原页审读已登记\`sources/catalog.json\`。

## 当前主要未决字段

1. GF0011—2022精确主项字形、附形、名称和编码；
2. B04以后大量批次的正式结构、逐笔笔顺、细笔名和采用读音；
3. 位置变体必须回到完整整字逐项核验，包围部件需保存完整书写时序；
4. B05“牙”第2笔权威材料冲突继续单字段fail-closed；
5. 部分批次存在“evidence已入库但canonical/review/状态文档尚未同步”的状态债。

GitHub部分写入路径曾间歇触发 `This tool call was blocked by OpenAI's safety checks...`。该类情况统一记为 `tooling_write_blocker`，不是来源阻塞或内容冲突；单一路径失败不得停止整体阶段1推进。

## B03阶段2/3尾项

B03内容层视为`content_ready`。artwork/layout人工记录已存在；PDF归档、manifest、通用hard-gate和最终发布属于阶段2/3尾项，不阻塞阶段1内容吞吐。

## PDF状态

最新仓库合集仍为：

`deliverables/drafts/v0.2.1/B01-B02_with_preface_draft_A4.pdf`

23页；当前阶段1没有新增或修改PDF。

## 下一内容工作

1. 继续清理残余状态债，当前重点只剩B20 component-name machine evidence及少量review文字同步；
2. 主吞吐从S03名称逐步转向**笔顺、细笔名和采用读音**；常规单轮目标提高为40个不同主部首，无真实阻塞时至少推进30项；
3. 结构字段继续利用GF0013—2009等适用来源逐批闭合，但不外推2022部首身份；
4. 位置迁移继续回目标整字核验；
5. GF0011—2022逐项精确字段继续由Issue #4并行追踪。
