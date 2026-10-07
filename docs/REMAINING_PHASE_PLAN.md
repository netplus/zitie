# 剩余完书阶段计划

更新：2026-10-07。

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

P0已完成：2026-10-06新的`source-probe` run 37402630995成功，artifact 11385916300重新取得并强制校验S02/S04/S05/S01-2009字节。后续停止继续寻找D05/D06等二次源，除非规范原件出现无法解决的真缺口。\n\n**P0—P7全部完成；v0.4.0正式发布已完成。**

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

**已于2026-10-06完成。** 主部首身份连续性201/201 reviewed；position_migration 198 reviewed + 3 conflict_fail_closed（屮、毋、瓦），0普通pending；GF0011—2022逐项精确主形/附形/名称/编码因正式逐项数据未公开，201/201按来源审计精确收口为source_blocked_fail_closed，不填造值。完成检查点：`reviews/P4-completion-20261006.md`。

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

第二轮B12—B21共91项也已完成同层级身份连续性复核。当前B04—B21 **171/171** 个在编主项的主部首成员身份/main_id连续性已reviewed；2022精确主形/附形/名称/编码仍pending。下一步做B01—B03 30项P4连续性回归，并把主吞吐转向完整整字位置迁移。

### P4身份连续性里程碑（2026-10-06）

B01—B03 30项P4回归已完成。至此全书**201/201主部首成员身份/main_id连续性reviewed**：
- 30项B01—B03回归；
- 80项B04—B11；
- 91项B12—B21。

该里程碑只关闭官方2022发布说明明确支持的“保持原有201个主部首”层级；2022逐项精确主形、附形、名称和国际编码仍等待正式全文/官方逐项数据。P4主吞吐转向position_migration与附形/位置变体完整整字核验。

### P4 position_migration 当前进展（2026-10-06）

B06—B11共60项完成代表整字GF0023原页核验，60/60 reviewed。重点：
- 匚→区 [1,4]、弋→式 [1,5,6]、囗→国 [1,2,8] 为非连续整字笔画映射；
- 矢→知、禾→和第5笔均为捺→点；
- 甘→甜位置由left纠正为right；
- 风self语境无位置迁移。

B04/B05 20项当前main缺少权威整字语境evidence，保持pending，不以编辑例字凑数。

B12—B19第二轮80项已完成整字迁移原页核验：**78 reviewed + 2 conflict_fail_closed（屮、毋）**。疒、虍保留完整整字时序门槛；疋、竹、足记录了进入代表整字后的粗粒度笔画类别变化。累计B06—B19共140项position_migration为**138 reviewed + 2 fail-closed**。

后续继续B20/B21、B04/B05及B01—B03位置迁移回归；GF0011—2022正式附形身份仍独立等待逐项官方数据。

### P4 position_migration 收口（2026-10-06）

position_migration 已完成201/201：
- **198 reviewed**
- **3 conflict_fail_closed：屮、毋、瓦**
- **0普通pending**

证据总检查点：`reviews/P4-position-migration-completion-20261006.md`。

P4当前只剩GF0011—2022逐项精确字段门槛：201项主部首集合/main_id连续性已reviewed，但2022精确主形、正式附形、名称、国际编码仍等待正式全文或官方逐项数据。由于该来源尚无可重复公开访问通道，P4保持active，不提前进入P5。

## P5 内容终审与content_ready收口

目标：把B04—B21逐批验收，而不是继续按字段横向铺开。

**已于2026-10-07完成。**

终审规则：
- 所有已跟踪内容字段必须是terminal状态：`reviewed_*`、`not_applicable_*`、`conflict_fail_closed_*`或`source_blocked_fail_closed_*`；
- 每项必须有两条教学提示和自查句；
- whole-character context与position_migration必须与P4实际审读结果同步；
- unresolved不得保留普通pending，只允许有明确重开条件的fail-closed/source-blocked边界；
- content_ready不等于artwork_ready或release_eligible。

P5清理的主要状态债：
- 40项教学文本最终一致性同步；
- B08 6项stroke_count规范行同步；
- B12—B21 91项whole-character context同步；
- B07/B11 19项陈旧“候选/待核”教学措辞修订；
- 清理已被P2/P3/P4覆盖的历史unresolved文本。

逐项验收结果：
- `data/evidence/P5-B04-B12-final-content-acceptance.json`：90/90 accepted；
- `data/evidence/P5-B13-B21-final-content-acceptance.json`：81/81 accepted；
- B04—B21：171/171 content_ready；
- 加B01—B03既有30项：**201/201 content_ready，0 content_in_progress**。

完成检查点：`reviews/P5-completion-20261007.md`。

退出条件**201/201 content_ready**已满足，阶段正式切换P6。

## P6 Artwork / 版式（已完成：2026-10-07）

目标：201项进入稳定图形和版式流程。

完成结果：
- 全书201项固定revision矢量材料审计：201 compatible / 0 missing / 0 stroke-count mismatch；
- B01—B21累计笔画人工审图完成：201/201 artwork_ready；
- 通用A4 builder已覆盖B01—B21，非独立读音不伪造拼音，细笔名fail-closed项不渲染候选笔名；
- 复杂字每页最多6个累计步骤，保持练写格尺寸，不通过缩小解决；
- PR #47 workflow run `37560963767` 已实际完成全21批research build与PDF structural preflight；
- artifact `11456961693`（digest `sha256:c87ce0b3d3bd7daa5d713bc54500223daa339b62e7581141560ac84dff64b7e1`）中的B01—B21共258个练习页全部渲染并完成视觉layout review；
- B08、B20、B21另做高分辨率复看；B21“龠”17画按6+6+5三页连续展示；
- 未见可见裁切、文字/格线重叠、黑块或目标字形缺失。

P6退出条件已满足：**201/201 artwork_ready + 全书layout_ready**。

证据：
- `data/evidence/P6-full-book-layout-review-20261007.json`
- `reviews/P6-full-book-layout-review-20261007.md`
- 既有P6 artwork evidence/review继续保留。

## P7 PDF、全书QA与正式发布（已完成：2026-10-07）

正式v0.4.0已经完成全部P7门槛：
- 全书structured draft与RC1均已归档；
- 201主项、32项教学变体、原V001—V027、目录/索引/页码/来源台账完成QA；
- formal preflight HEAD `9149a6e9b751bfbc97e95c3bbfc64a5c8681f7fd` 的 run `37570965306` 成功；
- 正式PDF已进入 `deliverables/releases/v0.4.0/B01-B21_with_preface_toc_appendices_v0.4.0_A4.pdf`；
- 276页，3,749,164 bytes，SHA256 `ab3c23d7547872f4d0e2c128de397e9e89ed6de97b681876e2dff017ff5c4894`；
- final release PR #55 HEAD `61ab933143137766f3fb00e5f946e7897d2e2349` 的 Book integrity checks run `37571448193` 成功；
- PR #55 已合入main，merge commit `576812fec7cc681df45ed85b36f51a1abe5ad4bb`；
- manifest条目为 `status=released`、`release_eligible=true`。

terminal fail-closed继续明确披露：
- fine_stroke_names：14；
- position_migration：3；
- GF0011—2022逐项精确字段：201 source_blocked_fail_closed。

这些终态边界是经过审计的发布状态，不等于普通pending，也不因正式发布而消失。

**P7退出条件已满足，P0—P7全部完成。** 后续仅做维护、勘误或新权威来源触发的重开。

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
