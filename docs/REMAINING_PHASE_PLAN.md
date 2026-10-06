# 剩余完书阶段计划

更新：2026-10-06。

本文件把当前“阶段1内容覆盖优先”进一步拆成可收口的剩余阶段。目标是不再无限横向扩充secondary evidence，而是按“规范原页 → 内容收口 → artwork → 发布”的顺序把全书推进到release。

## P0 规范源通道打通（已完成：2026-10-06）

目标：让GF0023—2020、1997《现代汉语通用字笔顺规范》S04、GF2001—2001折笔规范S05可以稳定恢复、校验并用于逐页复核。

完成门槛：
- 固定公开托管路径、Git blob、SHA256、字节数与页数；
- `.github/workflows/source-probe.yml`能够重新取得原件并强制SHA256匹配；
- 规范PDF只通过临时reference artifact流转，不提交到公开仓库、不作为字帖deliverable；
- 恢复原件本身不授予任何字段reviewed；
- 建立后续P1/P2原页review的页码/目标定位入口。

当前已知：
- S02 GF0023—2020：581页，51,412,684字节，SHA256 `0ff0890...`；
- S04 1997笔顺规范：458页，13,214,987字节，SHA256 `ca8a013...`；
- S05 GF2001—2001：9页，177,325字节，SHA256 `68a1420...`；
- 2026-10-06已从历史Actions artifact恢复三份原件并重新核验SHA256、字节数和页数。

P0已完成：2026-10-06新的`source-probe` run 37402630995成功，artifact 11385916300重新取得并强制校验S02/S04/S05/S01-2009字节。后续停止继续寻找D05/D06等二次源，除非规范原件出现无法解决的真缺口。\n\n**当前活动阶段：P4 2022身份与位置迁移。**

## P1 当前进展（2026-10-06）

第一轮B04—B11共80项已完成GF0023原页复核：55项精确命中并升级为`reviewed_GF0023_2020_original_page`；25项继续pending并转S04/其它适用规范，0笔顺码冲突。

第二轮B12—B19共80项也已完成GF0023原页复核：68项精确命中并升级为`reviewed_GF0023_2020_original_page`；12项在目标数字笔顺码排序邻接区间的原页中仍未见精确目标，继续pending并转S04/其它适用规范；68项规范码与既有secondary locator一致，0冲突。

第三轮B20—B21共11项也已完成GF0023原页复核：**11/11精确命中，0 pending，0 conflict**。

GF0023主表阶段已扫完B04—B21全部171项：**134/171 reviewed，37/171 residual**。GF3002—1999公开8页原件真实可见行关闭5项。随后GB/T 25741—2010规范性附录C对固定32项逐条原页视觉复核，**32/32精确命中、0笔顺码冲突**。因此P1已经达到退出条件：全书**201/201 stroke_order reviewed，0 residual**。

## P1 笔顺规范原页收口

目标：关闭B04—B21的`stroke_order`。

执行顺序：
1. B04—B11：GF0023原页review已完成；
2. B12—B19：GF0023原页review已完成；
3. B20—B21：GF0023原页review已完成；
4. GF3002—1999公开8页原件可见精确字条关闭5项；GB/T 25741—2010规范性附录C进一步关闭其余32项。P1完成：201/201 reviewed，0 residual。

原则：
- secondary locator只负责找字、找页，不授予最终结论；
- 实际查看GF0023目标原页；必要时与S04继承版原页交叉；
- 每项保存原印页、PDF物理页、目标行/表序号、实际审读范围；
- 只有原页实际查看后才升级到`reviewed_*`。

退出条件：201项stroke_order均为reviewed或精确conflict_fail_closed。**已于2026-10-06满足：201/201 reviewed，0 residual，0 P1 conflict。**

## P2 细笔名规范原页收口

目标：关闭`fine_stroke_names`。

**已于2026-10-06完成。** B04—B21共171项最终为：
- **157 reviewed**：均由GF2001—2001术语/折笔规范结合GF0023目标整字原页等规范证据逐项裁决；
- **14 conflict_fail_closed**：牙、矛，以及屮、巛、疒、疋、癶、覀、虍、糸、釆、龺、髟、鬥；
- **0普通pending**。

其中牙、矛属于视觉/术语无法可靠裁决的精确冲突；其余12项属于`conflict_fail_closed_normative_target_gap`：GF2001、GF0023和S04均已按规定路径实际审读，但没有覆盖精确目标字形且足以给出完整逐笔名称的规范证据，secondary locator不得升级。只有取得覆盖精确目标字形的适用规范原页或权威桥接规则时才重开。

证据：
- `data/evidence/P2-B04-B11-fine-stroke-names-original-page.json`
- `data/evidence/P2-B12-B15-fine-stroke-names-original-page.json`
- `data/evidence/P2-B16-B19-fine-stroke-names-original-page.json`
- `data/evidence/P2-B20-B21-fine-stroke-names-original-page.json`
- `data/evidence/P2-normative-target-gap-failclosed.json`
- `reviews/P2-completion-20261006.md`

退出条件“绝大多数细笔名reviewed，残余均为有证据、有解决路径的fail-closed冲突”已满足。阶段正式切换到P3。

## P3 其它字段扫尾

目标：关闭剩余`pronunciation`、`component_name`、`structure`。

**已于2026-10-06完成。** B04—B21共171项最终状态：

- pronunciation：**126 reviewed + 11 conflict_fail_closed + 34 not_applicable + 0普通pending**；
- component_name：**143 reviewed + 28 deferred_P4_exact_name_gate + 0普通pending**；
- structure：**134 reviewed + 37 deferred_P4_exact_identity_gate + 0普通pending**。

关键收口：
- GF0015—2010通过source-probe run `37449756736` / artifact `11406995313`恢复并强校验；25个GF0023精确规范字完成原页pronunciation审读，14项关闭、11项精确fail-closed；
- 34个部件型/非GF0023精确目标，S03无目标自身读音，pronunciation按当前教学表面收口为not-applicable，不借名称例字或字典古音；
- B08/B14共20项component_name状态债同步reviewed；28个S03无精确主形名称条目的目标转P4 GF0011—2022精确名称门槛，不标reviewed；
- structure此前100项缺口中，63个GF0023精确规范字由S07+GF3001规范集合关闭，37个部件型目标转P4精确身份/主附关系门槛。

证据总检查点：`reviews/P3-completion-20261006.md`。

退出条件“除GF0011—2022和位置迁移外，字段pending基本清零”已满足，活动阶段正式切换P4。

## P4 2022身份与位置迁移

目标：处理全书级语义门槛。

GF0011—2022：
- 精确主项身份；
- 主形/附形；
- 名称；
- 编码；
- 2009→2022差异。

位置迁移：
- 回完整整字核验；
- 记录部件位置、笔画索引、形变/改笔、完整书写时序；
- 包围结构不得只记录部件自身局部顺序。

退出条件：201主项身份和位置迁移边界均闭合或精确fail-closed。

### P4当前进展（2026-10-06）

第一轮B04—B11共80项完成“主部首身份连续性”复核：教育部/国家语委2022发布说明确认保持原有201个主部首，结合已审读GF0011—2009主表，80/80项主部首成员身份与项目main_id连续性已reviewed。2022逐项精确主形字形、附形、名称、编码仍等待GF0011—2022正式全文或官方逐项数据，不冒充完成。

当前GF0011—2022公开访问边界：正式发布说明可重复访问；正式全文尚未定位到可重复公开通道。该source blocker只影响逐项2022字段，不阻塞位置迁移及后续80项身份连续性复核。

证据：
- `data/evidence/P4-B04-B11-main-radical-identity-continuity.json`
- `sources/reviews/P4-GF0011-2022-public-access-audit-20261006.json`

下一轮：B12—B19 80项身份连续性 + 可独立的整字位置迁移核验。

## P5 内容终审与content_ready收口

目标：把B04—B21逐批验收，而不是继续按字段横向铺开。

每项检查：
- 身份/结构/笔数/笔顺/细笔名/读音/名称；
- 两条教学提示、自查句、整字语境；
- 位置迁移边界；
- field-level evidence/review；
- conflict与pending必须精确且有解决路径。

退出条件：**201/201 content_ready**。

## P6 Artwork / 版式

目标：201项进入稳定图形和版式流程。

工作：
- 固定矢量来源；
- 逐笔累计示范；
- 当前笔红色、旧笔深灰；
- A4田字格；
- 描红/淡灰/独立书写；
- 拼音、结构和教学说明；
- 复杂字按可练写原则分页。

退出条件：201项artwork_ready。

## P7 PDF、全书QA与正式发布

顺序：
1. 全书draft；
2. 分段逐页视觉QA；
3. 修版与回归；
4. manifest；
5. 目标HEAD CI；
6. release candidate；
7. 201主项/附形/原27项/目录索引/页码终审；
8. 正式release。

退出条件：正式PDF进入`deliverables/releases/`且release门槛全部通过。

## 吞吐约定

- P1—P4仍以80个不同主部首/轮为常规目标；
- P0、P5—P7按阶段门槛推进，不用“80项”强行凑数；
- 某一来源/字段受阻时切换同阶段其它可独立工作；
- secondary evidence不再作为主要吞吐目标，除非用于解决规范原件定位的真实缺口；
- content_ready、artwork_ready、release_eligible始终分开统计。

## P1 residual source audit: GF3002—1999（2026-10-06）

已完成GF3002—1999候选原件探针与视觉审计：Actions run `37410985779` / artifact `11389595541` 成功取得 `gf3002-1999.pdf`，文件为6,730,497字节，SHA256 `cb5cb74f108dafed41a3583bc8d33d8dd318d1a21d714923c0f1ced89443cf3e`。

实际渲染并检查PDF全部8页后确认：该镜像不是完整20902字正文。目录明确写明GF3002规范正文/字表跨原印第4—343页，但当前文件只有8个PDF物理页；末页样表到序号134即出现“（略）”。因此本镜像不能用于外推未显示条目；但主表序号1—134中真实可见且逐项视觉核对的精确条目可以单独作为原页证据。现已关闭丨、丿、丶、乛、丬5项，证据见`data/evidence/B08-stroke-order-gf3002-original-page.json`与`data/evidence/B10-stroke-order-gf3002-original-page.json`。

P1最终为**201/201 reviewed，0/201 residual**。固定32项已由GB/T 25741—2010规范性附录C逐项目标原页视觉复核关闭；证据见`P1-GBT25741-appendix-C-residual-original-page-20261006.json`。阶段已切换到P2，不再继续扩P1来源。
