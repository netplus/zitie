# 循序渐进汉字部首字帖

面向简体中文基础书写教学的 A4 部首练字工程：覆盖 **201 个主部首**，并保留常用附形、位置变体、历史 27 项回归、目录与索引等全书级检查。

## 最新正式版与当前阶段

**[下载v0.4.1正式勘误修订版（276页）](deliverables/releases/v0.4.1/B01-B21_v0.4.1_A4.pdf)**

M1已完成：5项变体/7处索引缺字、统计范围、重建说明和正式前言模式均已修正。正式PDF为3,748,910 bytes，SHA256 `7270104b8698603fcce4eec14037a0194c31e33b868669d0a8dd0307a090a7e7`；PR #61最终HEAD CI run `37588926485`成功并合入main。

当前进入**M2新权威来源重开**：已按GF0023完整原页关闭瓦→瓶的第7—10笔映射，当前工作数据的位置迁移为199 reviewed + 2 fail-closed；旧正式版快照不改。GF0025原页已支持两项目标语素读音，具体范围见下方本轮记录。M2仍进行中；M3 v0.5.0功能与教学增强、Q1全书排版复核仍未开始。最新阶段入口：[当前状态](docs/STATUS.md) · [阶段计划](docs/POST_RELEASE_PLAN.md) · [M1完成记录](reviews/M1-completion-20261007.md)。

原v0.4.1-rc1候选和全部旧PDF保留。以下v0.4.0表格是历史正式基线，不是最新版下载入口。

本轮M2：采用GF0025原页“小麦/牙齿”的第二语素读音，麦mài、齿chǐ两项关闭；剩余9项仍待证据。仅有限候选范围未命中，不称全书未收录。工作读音128 reviewed+34不适用+9保留阻塞（B04—B21）；旧发布PDF不改。见[本轮读音审读](reviews/M2-GF0025-pronunciation-20261007.md)。

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

1. **内容覆盖**：逐字段核验 201 个主部首的身份、笔顺、细笔名、采用读音、部件名称、结构、教学提示和整字语境；
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
