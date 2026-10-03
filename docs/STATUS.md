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

本轮覆盖B19+B20共20个不同主部首。

### B19：韭、骨、香、鬼、食、音、首、髟、鬲、鬥

当前已真实入库：
- `data/evidence/B19-content.json`：S01-2009 baseline身份、main_id 181—190、9/10画分组；
- `reviews/B19-content.md`：人工阶段1内容复核；
- `data/B19.json`：canonical阶段1内容稿。

已reviewed范围：baseline身份、main_id、baseline笔画分组，以及教学提示／自查句／整字语境／迁移边界的非权威人工编辑复核。

仍pending：GF0011—2022精确身份、正式结构、逐笔笔顺、细笔名、采用读音、S03部件名称、正式附形和整字位置迁移证据。

### B20：高、黄、麻、鹿、鼎、黑、黍、鼓、鼠、鼻

当前已真实入库：
- `data/evidence/B20-content.json`：S01-2009 baseline身份、main_id 191—200、10—14画分组；
- `reviews/B20-content.md`：人工阶段1内容复核；
- `data/evidence/B20-teaching-review.json`：教学字段编辑一致性evidence；
- `data/B20.json`：canonical阶段1内容稿，`teaching_text`已同步为`reviewed_editorial_non_authoritative`。

仍pending的权威字段与B19相同，不因编辑复核而提前升级。

## 已知内容层缺口

按实时批次记录继续收口：
- B14：baseline machine evidence仍缺；
- B16：canonical data和baseline evidence已在库，人工review文字仍有旧状态描述待同步；
- B17：canonical data、baseline evidence与教学evidence已在库，人工content review仍缺；
- B21：baseline evidence已在库，canonical `data/B21.json`和人工review仍缺；
- 更早B04—B13仍需继续逐项关闭名称、笔顺／细笔名、采用读音、结构与位置迁移等字段。

## B03阶段2/3尾项

B03内容层视为`content_ready`。artwork/layout人工记录已存在；PDF归档、manifest、通用hard-gate和最终PR收尾属于独立工程尾项，不阻塞阶段1内容吞吐。

## PDF状态

最新仓库合集仍为：

`deliverables/drafts/v0.2.1/B01-B02_with_preface_draft_A4.pdf`

23页；当前阶段1没有新增或修改PDF。

## 下一内容工作

1. 优先补B21 canonical data与人工review，闭合201号主项的阶段1主记录；
2. 补B17人工content review和B16 review文字同步；
3. 补B14 baseline machine evidence；
4. 以20个不同主部首为一轮，批量关闭S03名称、笔顺／细笔名、采用读音、结构和位置迁移字段；
5. GF0011—2022逐项精确字段继续由Issue #4并行追踪。
