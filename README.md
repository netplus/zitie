# 循序渐进汉字部首字帖

201个主部首＋常用附形与位置变体；A4田字格；逐笔示范与分层练习。

**当前处于阶段1：内容覆盖。不是201项全部完成的正式字帖。**

从2026-10-02起，仓库改为三阶段：
1. **内容覆盖**：先完成201项字段级内容与证据链；
2. **图形与版式**：再统一处理矢量、逐笔示范、A4排版和PDF视觉检查；
3. **归档与发布**：最后处理manifest、目标HEAD CI、release和全书终审。

这使单个PDF/CI问题不再阻塞后续批次内容编写。详见[内容优先工作流](docs/CONTENT_FIRST_WORKFLOW.md)。

## PDF下载

**[最新合集：前言＋前两批20项，23页](deliverables/drafts/v0.2.1/B01-B02_with_preface_draft_A4.pdf)**

[第二批10页](deliverables/drafts/v0.2.1/B02_draft_A4.pdf) · [第一批10页](deliverables/drafts/v0.2.1/B01_draft_A4.pdf) · [前言3页](deliverables/drafts/v0.2.1/preface_v0.2.1.pdf) · [全部版本与校验清单](deliverables/README.md)

阶段1不会为了保持“每批同步制页”而强制生成新PDF。实际交付或送审PDF仍必须保存到仓库并登记manifest。

## 当前内容状态

| 范围 | 内容状态 | 图形/发布状态 |
|---|---|---|
| B01—B03（30项） | content_ready | 分批进入阶段2/3；B03归档尾项独立处理 |
| B04—B21（171项） | content_in_progress | deferred，不阻塞内容推进 |

201个主部首现已**201/201完成批次范围分配**。当前content_ready仍为30项；其余171项已经进入字段级内容与证据闭合流程，各批闭合程度不同，不等同于171项全部完成。

### 最新阶段检查点

2026-10-05，阶段1工作已通过PR #9阶段性合入`main`，merge commit为：

`8b6213b0ec5f85ae26915aa6f823dcb2ba04c187`

当前已不再停留在“建批次内容稿”阶段：B04—B21均有canonical内容记录。2026-10-05已完成B06—B13两轮各40项GF0013结构审读，并在本轮进一步完成B14—B20共70项structure审读；B04十项GF0023—2020笔顺目标行也已精确定位。未命中structure项保持fail-closed，不反推为合体字。B20的S03完整主体表视觉审读已登记来源台账，machine evidence仍待补。

阶段1已连续完成两轮80项采用读音复核；B04—B11完成GF0023派生笔顺码交叉，B12—B19完成secondary stroke-order locator。细笔名方面，B04—B11已完成一轮80项二次交叉/定位；B12—B19先完成cnchar locator，随后又用独立D04/cjklib对同80项做第二套二次交叉：22项完全一致、5项粒度兼容、8项二次源冲突、4项补缺、41项D04无条目。所有二次数据都不替代规范原页review。下一主吞吐集中到**GF0023/GF2001/S04原页笔顺与细笔名review**以及剩余位置迁移。常规单轮目标为80个不同主部首。

GF0011—2022逐项全文、附形、名称和编码仍是全书级待核项，但不会阻止其它可独立核验字段继续推进。\n### 当前剩余阶段\n\n2026-10-06起改为P0—P7阶段化收口：**P0规范源通道已完成，当前进入P1笔顺规范原页收口**。新的reference workflow可以重新取得并强制SHA256校验GF0023—2020、1997笔顺规范和GF2001折笔规范；恢复原件不等于内容review。后续停止无目的扩展secondary数据源，优先把已有locator/crosscheck回到规范原页并升级为reviewed。
P1已经完成第一轮B04—B11共80项GF0023规范原页笔顺复核：**55项精确目标升级为stroke_order reviewed，25项未定位精确主表条目并转S04/其它规范残余队列；55项规范码与canonical候选0冲突。** 下一轮进入B12—B19 80项原页收口。
\n

## 项目入口

[当前状态](docs/STATUS.md) · [剩余完书阶段计划](docs/REMAINING_PHASE_PLAN.md) · [内容优先工作流](docs/CONTENT_FIRST_WORKFLOW.md) · [编写计划](docs/EDITORIAL_PLAN.md) · [前言源稿](book/front-matter/preface.md) · [201项索引](data/coverage.json) · [批次计划](data/batches.json) · [附形候选](data/variants.json) · [来源台账](sources/catalog.json) · [质量门槛](docs/QUALITY_GATES.md) · [总控Issue](https://github.com/netplus/zitie/issues/1)

## 阶段1内容标准

每个主项优先完成：
- 主项ID和目标规范身份状态；
- 结构；
- 笔数、笔顺、细笔名；
- 采用读音；
- 部首／部件名称；
- 两条教学提示与自查句；
- 整字语境和迁移边界；
- 字段级来源、实际页码／字条、冲突和未决。

阶段1的content_ready**不等于**artwork_ready或release_eligible。

## 重建与检查

现有构建链仍可用于B01/B02和B03工程尾项：

```sh
python -m pip install -r requirements.txt
python scripts/validate_project.py --batch B01
python scripts/validate_project.py --batch B02
python scripts/test_validation.py
python scripts/test_deliverables.py
python scripts/verify_deliverables.py
python scripts/acquire_vectors.py --batches B01 B02
python scripts/test_artwork.py
python scripts/build_batch.py --draft --batch B01
python scripts/build_batch.py --draft --batch B02
python scripts/build_collection.py
```

第一阶段原则上保持生成/CI脚本稳定，优先更新`data/`、`reviews/`和`sources/`。工程重构集中处理，不再要求每个内容批次都修改workflow。

字体由使用者在自己的系统安装，本仓库不提供字体文件。

每批10个主项，最后1项，共21批；单次内容运行常规目标80项，无真实阻塞时至少推进60项。附形和复习另计，不重复计算主项覆盖。
