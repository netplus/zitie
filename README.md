# A1.2.1 在线交互改进（工程预览）

根据线上反馈，**已实现可搜索字形卡片＋批次筛选**，取代原生下拉选字；动画以原轮廓宽度为依据生成沿笔顺中心线推进的局部 SVG 遮罩，降低固定粗画刷导致的提前显露。增加可拖动时间轴及键盘操作，所有9个样例保持离线可用、原笔顺与原轮廓不变。质量门槛、尚未完成的教学审定见 [A1.2.1 实施与限制](docs/A1_UX_PRECISION.md) 和 [Issue #82](https://github.com/netplus/zitie/issues/82)。通过 PR 和最终HEAD CI 前不计正式教学验收。

---

# A1 动态笔顺工程预览（独立于 v0.5.1 正式 PDF）

**在线查看动画（第三方临时预览）：**[直接打开](https://raw.githack.com/netplus/zitie/main/animation/index.html)。GitHub Pages 官方自动发布工作流已准备，但站点尚待首次启用，不能将 `https://netplus.github.io/zitie/` 视作当前已上线。详见 [在线预览和 Pages 设置](docs/A1_PREVIEW.md)。

新增 A1 动画研发阶段：已归档 [9个主部首的离线 SVG 动态书写原型](animation/index.html)、[动画控制与复核说明](animation/README.md)、[A1 技术设计和独立验收门槛](docs/A1_ANIMATION.md)。可以下载仓库并在浏览器直接打开 `animation/index.html`；不会联网。**这些 medians 仅为工程预览，尚未完成独立教学轨迹审定**，已有201主部首矢量笔顺审核不能视为动画方向审核。正式 PDF 仍是 v0.5.1，历史不变。A1任务见 [Issue #79](https://github.com/netplus/zitie/issues/79)。

---

# 循序渐进汉字部首字帖 · v0.5.1

**[最新正式版 PDF：v0.5.1（A4、299页）](deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf)** — 修正简体横排句号/顿号字格左下位置。SHA256：`7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90`。

以 v0.5.0 的Q1验收范围为依据，只对已确认的283处标点做轮廓位置微调，并同步558处版本标识；201主部首和教学内容、299页A4、238书签及50链接完全保留。规范字段未决按原fail-closed规则继续保留；实物打印未做。

- [本轮勘误证据](reviews/v051-punctuation-erratum-20261008.md)
- [发布与历史状态](docs/STATUS.md)
- [仍开放的规范来源Issue #4](https://github.com/netplus/zitie/issues/4)

## 以下为此前正式 v0.5.0 及历史阶段记录

# 循序渐进汉字部首字帖 · v0.5.0

**[正式 v0.5.0 PDF（A4，299页）](deliverables/releases/v0.5.0/zitie-v0.5.0-A4.pdf)** — 已通过 [PR #73](https://github.com/netplus/zitie/pull/73) 的最终目标 HEAD CI 并合入 `main`，正式发布生效。全书201主部首及教学比较/回忆/整字迁移，沿用已完成的Q1版式验收；保留2022来源限制。

SHA256 `10f5177221ff4817ea412f9e5f187e68d59eabfce8f94e2ebf4179f4398f6880`；可重复构建：`python scripts/build_v050_formal.py`，输入为已归档的RC3终检候选PDF（不是最初RC1生成源码）。238书签、50跳转、299页A4；推荐彩色打印，未进行实物打印测试。

[发布审计与版本来源](reviews/Q1-v0.5.0-formal-QA-20261008.md) · [当前状态](docs/STATUS.md) · [历史候选记录](reviews/Q1-acceptance-20261008.md)。以下条目均为旧阶段历史，不覆盖当前状态。

---

# 本地逐页复核成果待归档

RC2、RC3及终检文件已有逐页复核与精确来源记录；当前准备导入本地修订，不代表远端CI或正式发布完成。最新状态见[STATUS](docs/STATUS.md)，导入详情见[Q1记录](reviews/Q1-local-import-20261008.md)。原M3 RC1记录和全部旧文件保留。

## 以下为此前版本入口（历史）

# 循序渐进汉字部首字帖

## 当前交付：v0.5.0-rc1完整候选已冻结

[下载299页完整发布候选](deliverables/drafts/v0.5.0-rc1/zitie-v0.5.0-rc1.pdf)。M3已完成候选归档，当前进入独立Q1；Q1队列0/299页，不是正式v0.5.0发布。文件4,252,161字节，SHA256 `3b26fd0a85b063b83f7090f9b38735908b6e64dc763614c12f17e4f727ef556a`。

实际生成run `37707956206`成功；最终归档PR #69仍以其目标HEAD CI及合入结果为准。完整配置、字体环境、页码映射和生成记录已绑定。旧17份PDF与来源限制保持，最新正式版仍v0.4.1。

[当前状态](docs/STATUS.md) · [冻结记录](reviews/M3-candidate-freeze-20261008.md) · [Q1执行计划](docs/Q1_REVIEW.md)。以下均为各自时点的历史记录，不能覆盖上方当前状态。

## PR68实现检查点（历史）（2026-10-08）

F03六例完整整字迁移已实现并完成全模块导航/字段策略接入；F01—F05五包均已实现。内部工程预览为299页，六例迁移新增10页，全部44个整字步骤保持原时序；201主项计数不变。国的部件对应1、2、8笔，区对应1、4笔，近的辶在第5—7笔；不将非连续部件截成连续独写。新增34项迁移测试，含误用上游radStrokes、截断笔顺与越权字段检查。

这仍是内部工程预览，不是冻结候选或正式发布。M3阶段仍in_progress，下一步真实归档完整候选并绑定生成来源，再进入独立Q1。旧17份PDF、manifest及规范字段保持。详见[当前状态](docs/STATUS.md)、[本轮复核](reviews/M3-migration-integration-20261008.md)。

## PR67实现检查点（历史，2026-10-07）

F01学生/辅导者分层说明与F02六组比较/回忆已实现，内部工程预览实际288页；F03整字迁移未生成，F04导航/F05字段策略已接入当前模块但待迁移集成。五包完成2，不是M3已完成。232书签、28目录跳转、201主项逐字段呈现检查已运行；全部12个比较/回忆页实际查看。下一步实现完整整字迁移，不重复M1/M2收口。

工程预览不是冻结候选、不作为正式PDF交付；旧17份PDF及manifest不改。来源阻塞保持，Q1未开始，candidate=null、final_release_eligible=false。当前细节以[STATUS](docs/STATUS.md)和`data/m3_scope.json`为准，复核见`reviews/M3-foundation-comparison-20261007.md`。

## 既有阶段记录（本轮之前）

面向简体中文基础书写教学的 A4 部首练字工程：覆盖 **201 个主部首**，并保留常用附形、位置变体、历史 27 项回归、目录与索引等全书级检查。

## M2退出与M3启动记录（历史）

正式v0.4.1保留；M1完成。M2本周期六类来源审计已按`completed_with_source_blocks`退出，累计采用3个字段更新，本轮新增采用0项；仍有来源缺口，来源Issue #4继续open，不称全部解决。

当时进入**M3功能与教学质量增强**：冻结六组比较/回忆、六个已核整字迁移及说明/导航改进范围，并建立按字段的教学限制检查。该启动检查点尚未完成功能包，Q1未开始，无新PDF发布。

[当前状态](docs/STATUS.md) · [M2完成与残余](reviews/M2-completion-20261007.md) · [M3范围](docs/M3_SCOPE.md) · [最新正式v0.4.1 PDF](deliverables/releases/v0.4.1/B01-B21_v0.4.1_A4.pdf)

## 既有正式版状态

**v0.4.0 已于 2026-10-07 正式发布，P0—P7 全部完成。**

| 门槛 | 最终状态 |
|---|---:|
| 主部首内容终审 | 201/201 content_ready |
| 逐笔图形审查 | 201/201 artwork_ready |
| A4 版式审查 | 201/201 layout_ready |
| P7 全书 QA / manifest / release | completed |
| 正式发布 | v0.4.0 released |

正式 PDF：

**[《循序渐进汉字部首字帖》v0.4.0（276 页）](deliverables/releases/v0.4.0/B01-B21_with_preface_toc_appendices_v0.4.0_A4.pdf)**

发布校验信息：

- 文件大小：3,749,164 bytes
- SHA256：`ab3c23d7547872f4d0e2c128de397e9e89ed6de97b681876e2dff017ff5c4894`
- formal preflight source HEAD：`9149a6e9b751bfbc97e95c3bbfc64a5c8681f7fd`
- final release PR：#55
- final release target-HEAD Book integrity checks：run `37571448193`，success
- 状态收口 PR：#56，已合入 `main`
- 总控 Issue #1：completed / closed

完整版本归档与校验信息见 [deliverables/README.md](deliverables/README.md) 和 [deliverables/manifest.json](deliverables/manifest.json)。

## 已审计的 fail-closed 边界

正式发布不等于伪造无法从公开权威来源取得的字段。v0.4.0 明确保留以下 terminal fail-closed：

- `fine_stroke_names`：14 项；
- `position_migration`：3 项（屮、毋、瓦）；
- GF0011—2022 逐项精确主形／附形／名称／编码：201 项 `source_blocked_fail_closed`。

`data/coverage.json` 中的 `target_edition_status=fulltext_pending` 是这个来源边界的明确记录，不是普通待办。只有在 GF0011—2022 正式逐项表或等价官方数据能够稳定、可重复取得时才重开相关字段。

## 工程方法

项目按三个解耦层推进并已经全部收口：

1. **内容覆盖**：逐字段核验 201 个主部首的身份、笔顺、细笔名、采用读音、部件名称、拼音、结构、教学提示和整字语境；
2. **图形与版式**：固定矢量来源，逐笔累计示范，A4 田字格和分层练习，复杂字分页，逐页视觉 QA；
3. **归档与发布**：structured draft、RC1、目录／索引／附形和原 27 项回归、manifest、目标 HEAD CI、正式 release。

证据原则始终保持：secondary locator 只用于定位和交叉，不授予规范结论；机器检查不代替原页审读；不确定项必须 fail-closed。

## 项目入口

- [当前权威状态](docs/STATUS.md)
- [P0—P7 收口计划与最终状态](docs/REMAINING_PHASE_PLAN.md)
- [内容优先工作流](docs/CONTENT_FIRST_WORKFLOW.md)
- [编写计划](docs/EDITORIAL_PLAN.md)
- [201 项覆盖与阶段证据](data/coverage.json)
- [批次定义](data/batches.json)
- [附形／位置变体候选](data/variants.json)
- [来源台账](sources/catalog.json)
- [质量门槛](docs/QUALITY_GATES.md)
- [PDF 版本归档](deliverables/README.md)

## 本地检查

安装依赖：

```sh
python -m pip install -r requirements.txt
```

常用一致性检查：

```sh
python scripts/test_validation.py
python scripts/test_deliverables.py
python scripts/verify_deliverables.py
python scripts/verify_formal_release_gate.py
```

正式发布验证脚本同时接受发布后的仓库状态，并检查 201 项 content/artwork/layout、RC1、manifest、正式 PDF 元数据以及 terminal fail-closed 披露。

## 维护模式

当前工程进入发布后维护状态。后续只处理：

- 明确勘误；
- 构建、CI、文档或归档维护；
- 新权威来源出现后，对对应 fail-closed 字段按证据链重开；
- 新版本需求明确后再建立新的版本阶段。

历史 draft/RC/PDF 和原审读记录不覆盖、不改写来源口径。仓库不提供字体文件，也不公开许可不明的商业规范全文。
