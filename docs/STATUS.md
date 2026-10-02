# 当前编写状态

更新：2026-10-02。工程已切换为“内容层先行、图形与发布层后置”的三阶段工作流。

## 当前阶段

**阶段1：201个主部首内容覆盖。**

阶段1优先完成字段级内容和证据链，不再让单个批次的矢量、PDF、manifest或CI尾项阻塞后续批次内容。详见`docs/CONTENT_FIRST_WORKFLOW.md`。

阶段2统一处理图形与版式；阶段3统一处理PDF归档、manifest、CI、release和全书终审。阶段1的`content_ready`不等于`release_eligible`。

## 当前内容范围

| 批次 | 主项 | content | artwork | publication |
|---|---|---|---|---|
| B01 | 一十人八大工土口山巾 | content_ready | artwork_ready | draft_archived |
| B02 | 水火木日月田目手牛毛 | content_ready | artwork_ready | draft_archived |
| B03 | 刀力又子女小王石白立 | content_ready | artwork_ready_local_candidate | archive_pending |
| B04 | 干寸夕广门尸己弓飞马 | in_progress | deferred | deferred |
| B05 | 无犬歹车牙戈瓦止贝见 | in_progress | deferred | deferred |

B04/B05的内容范围现已进入阶段1，但这不表示GF0011—2022逐项身份、附形、artwork或正式发布已经通过。

## B03状态

B03十项的结构、笔顺、细笔名、采用读音、正文、部件名称、artwork人工记录和layout人工记录已形成仓库记录。当前主要剩余项是阶段2/3尾项：
- 通用hard-gate脚本/CI尚未完整覆盖B03；
- B03候选PDF尚未以新的真实source_commit归档；
- manifest尚未增加B03阶段稿；
- PR #9仍未进入最终ready/merge。

这些尾项现在**不再阻塞B04/B05及后续批次的阶段1内容工作**。

## 阶段1计数

| 指标 | 数量 | 说明 |
|---|---:|---|
| 主索引 | 201 | 2009基线索引；GF0011—2022逐项精确字段仍有全书级待核 |
| 已确定内容范围 | 50 | B01—B05 |
| content_ready | 30 | B01—B03 |
| content_in_progress | 20 | B04+B05 |
| 已形成练习页 | 20 | B01+B02 |
| 已归档阶段PDF | 11份 | 全部draft |
| 正式发布 | 0 | 阶段3前不变 |
| 附形／位置变体 | 独立计数 | 不计入201主项完成数 |

## 内容门槛

阶段1每项重点跟踪：
- 主项ID与目标规范身份状态；
- 结构前提；
- 笔数、笔顺、细笔名；
- 采用读音；
- 部首／部件名称；
- 教学提示、自查句；
- 整字语境与迁移边界；
- 字段级来源、实际页码／字条、冲突和未决。

GF0011—2022全文尚未公开取得时，相关精确字段继续标记pending，不阻止其它字段和后续批次内容推进。

## PDF状态

仓库最新合集仍是：

`deliverables/drafts/v0.2.1/B01-B02_with_preface_draft_A4.pdf`

23页；历史11份PDF及manifest保持不变。当前阶段1不为“保持每批同步制页”而强制生成PDF。

## 下一内容工作

阶段1下一步优先：
1. 将B04、B05建立为正式内容记录，而不是继续只存在本地候选；
2. 对20项逐字段收敛内容证据和冲突；
3. 继续分配B06、B07的20项内容范围；
4. GF0011—2022等全书共性来源并行追踪，但不阻塞内容铺开。

B03的hard-gate和PDF归档转入独立工程尾项，在不影响内容更新的前提下继续处理。
