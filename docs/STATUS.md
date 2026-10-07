# 当前编写状态

更新：2026-10-07。P1—P6均已完成，P0—P7已全部完成；当前为v0.4.0正式发布后的维护状态。

## 最新阶段检查点：P6完成并进入P7（2026-10-07）

- 内容：**201/201 content_ready，0 content_in_progress**；
- artwork：**201/201 artwork_ready**；
- layout：**201/201 layout_ready**，B01—B21共258个练习页已全部渲染并完成视觉复核；
- P6 CI：PR #47 workflow run `37560963767` 成功，全21批结构校验、research build、PDF structural preflight、formal-release fail-closed检查、source export和artifact upload全部通过；
- P6 artifact：`11456961693 zitie-p6-full-layout-research`，digest `sha256:c87ce0b3d3bd7daa5d713bc54500223daa339b62e7581141560ac84dff64b7e1`；
- 视觉QA：258/258页按五组contact sheet全量查看；B08、B20、B21另做高分辨率复核；未见裁切、重叠、黑块或复杂字缩小；
- P6 review：`reviews/P6-full-book-layout-review-20261007.md`；
- P6 evidence：`data/evidence/P6-full-book-layout-review-20261007.json`；
- 正式release仍为 **0**。P6完成不等于P7归档/manifest/release完成。

P7下一步：先生成并真实归档全书draft到`deliverables/drafts/`，登记manifest，再做全书PDF目录/页码/索引/附形回归视觉QA，最后以目标HEAD CI和release gate收口。

## P7最新检查点：v0.3.0全书draft已归档（2026-10-07）

- 全书draft：`deliverables/drafts/v0.3.0/B01-B21_with_preface_draft_A4.pdf`
- 页数：**261**
- 字节：**3,652,431**
- SHA256：`6c8ddf162b0f72ef921a8624095096cce177128efd4ccf8d50c5168b31cb4773`
- source commit：`a7b0ffa385417d84c8d8651ada0ed56a5b8cfa7b`
- 归档workflow run：`37561985856`
- review：`reviews/v0.3.0-full-book-draft-ci.md`
- manifest：已登记，`release_eligible=false`
- B01—B21均已标记为包含在该全书draft归档中。

这只关闭P7的“全书draft真实归档+manifest登记”门槛；正式release仍为0。下一步继续全书PDF/目录/页码/索引/附形及原27项回归QA、manifest终审、目标HEAD CI、release candidate和正式release。

## 当前阶段

阶段1目标是先完成201个主部首的字段级内容和证据链；artwork、PDF、manifest和CI尾项不再阻塞后续内容字段推进。阶段2统一处理图形与版式，阶段3处理归档与发布。阶段1的`content_ready`不等于`artwork_ready`或`release_eligible`。

## 阶段检查点

PR #9 已于2026-10-05阶段性合入 `main`，合并提交：

`8b6213b0ec5f85ae26915aa6f823dcb2ba04c187`

该次合入保留阶段1内容优先重构、B03内容成果、B04—B21内容稿以及已真实入库的字段级review/evidence。合入前PR HEAD `45f90049496445206bbd2a265dc43be700c5ccfa` 的 `Book integrity checks` 已成功。该阶段合入不表示全书内容完成、artwork完成或正式发布。

## 范围与计数

- 主部首范围：**201/201已分配**，B01—B20各10项，B21为龠1项。
- `content_ready`：**201项**，B01—B21全部完成。
- `content_in_progress`：**0项**。
- 已形成练习页：20项（B01+B02）。
- Git内阶段PDF：11份draft。
- 正式release：0。
- GF0011—2022逐项精确主形/附形/名称/编码已在P4按公开来源审计收口为`source_blocked_fail_closed`；正式逐项数据可重复取得后再重开，不在P6伪造补值。

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
- **B20**：baseline、教学字段、structure、S03 component-name machine evidence和pronunciation evidence均已在库；高/黄/鹿/鼎/黑名称精确行已复核，其余5项保持S03无精确独立整形条目。
- **B21**：baseline evidence、canonical数据和人工review均已在库。

以上只表示对应字段的证据链进展，不表示各批次已经达到`content_ready`。

## 最新40项结构推进（2026-10-05）

B06—B09共40个不同主部首完成GF0013—2009《现代常用独体字表》结构适用性原页审读并入库专用evidence：
- B06：5项精确命中（厂、卜、儿、匕、几），5项S07不适用；
- B07：0项精确命中，10项S07不适用；
- B08：0项精确命中，10项S07不适用；
- B09：7项精确命中（气、长、片、斤、爪、父、文），3项S07不适用。

精确命中项的structure已同步为\`reviewed_S07_GF0013_2009_undecomposable\`；未命中项只标记为“S07已审读但不能关闭结构，等待其它适用权威来源”，不反推为合体字。对应evidence为\`data/evidence/B06-structure.json\`至\`B09-structure.json\`，原页审读已登记\`sources/catalog.json\`。

## 最新40项结构推进：B10—B13（2026-10-05）

B10—B13共40个不同主部首完成GF0013—2009《现代常用独体字表》原印2—3页/PDF 5—6页结构适用性原页审读，并入库专用evidence：

- **B10**：5项精确命中——氏、方、斗、户、心；其余5项S07不适用；
- **B11**：8项精确命中——甘、龙、业、皿、生、矢、禾、瓜；其余2项S07不适用；
- **B12**：1项精确命中——鸟；其余9项S07不适用；
- **B13**：5项精确命中——矛、耳、臣、而、页；其余5项S07不适用。

共**19/40项**的structure已同步为`reviewed_S07_GF0013_2009_undecomposable`；其余21项只记录“S07已审读但不能关闭结构，等待其它适用权威来源”，不反推为合体字。对应evidence为`data/evidence/B10-structure.json`至`B13-structure.json`。

本轮还把B12/B13既有S03名称与教学evidence同步回canonical：B12为7项名称精确命中+3项S03无精确独立整形条目；B13十项名称全部精确命中。教学文本与整字语境只升级为非权威编辑review，不替代正式位置迁移核验。

## 最新80项推进（2026-10-05）

本轮实际推进80个不同主部首：

- **B14—B20共70项structure**：实际查看GF0013—2009《现代常用独体字表》原印第3页/PDF第6页。共20项精确列入独体字表并关闭structure：B14虫/肉/血/舟；B15衣/羊/米；B16酉/豕/卤/里/身；B17言/雨；B18隶/革/面；B19鬼/首；B20鼠。其余50项只记录S07已审读但不适用，不反推为合体字。
- **B04十项stroke-order locator**：教育部官方GF0023—2020精确目标行已定位，保存表序号、UCS、原印页/PDF页和笔顺码；因本轮未完成对应原页视觉review，canonical只升级为“目标行已定位、视觉review待完成”，不提前标reviewed。

本轮80项对应证据已经真实入库；content_ready总数未因此自动提升，因为细笔名、采用读音、剩余structure和位置迁移等字段仍有未决。

## 最新80项采用读音推进（2026-10-05）

B10—B17共80个不同主部首完成GF0014—2009《现代常用字部件及部件名称规范》原印7—20页／PDF 10—23页采用读音适用性原页复核。判定规则为：只有S03精确目标部件名称栏以目标字形自身开头并直接给出该目标自身括号拼音时，才关闭`pronunciation`。

结果为：
- B10：9 reviewed / 1 pending（丬）；
- B11：9 / 1（罒）；
- B12：4 / 6（屮、巛、毋、疒、疋、癶）；
- B13：8 / 2（覀、虍）；
- B14：10 / 0；
- B15：5 / 5（齐、羽、糸、麦、走）；
- B16：8 / 2（足、邑）；
- B17：7 / 3（釆、青、龺）。

合计**60/80项采用读音关闭，20/80项保持pending**。对应machine evidence为`data/evidence/B10-pronunciation.json`至`B17-pronunciation.json`，人工复核摘要为`reviews/B10-B17-pronunciation.md`。名称型标签中的其它字读音不得替代目标主形读音。

## 最新80项采用读音推进（二）（2026-10-05）

B04、B05、B06、B07、B09、B18、B19、B20共80个不同主部首完成S03采用读音适用性复核。

结果：
- B04：10 reviewed / 0 pending；
- B05：10 / 0；
- B06：5 / 5；
- B07：2 / 8；
- B09：8 / 2；
- B18：7 / 3；
- B19：5 / 5；
- B20：5 / 5。

合计**52/80项pronunciation关闭，28/80项保持pending**。B20同时补齐`data/evidence/B20-component-name.json`，高、黄、鹿、鼎、黑精确目标行重新核对；麻、黍、鼓、鼠、鼻继续保持S03无精确独立整形条目。

## 最新80项笔顺码交叉核验（2026-10-05）

B04—B11共80个不同主部首完成GF0023派生TSV逐字交叉核验。数据源为公开项目`takushun-wu/han-ideographs-stroke-order`的`order.tsv`（blob `ecf422f0bb9d1d07d661250796269bfa752ebd`），该项目声明其数据来源包括GF0023—2020等资料。

结果为：**80/80 canonical候选笔顺码与派生数据一致，0冲突，0缺失**。对应machine evidence为`data/evidence/B04-stroke-order-crosscheck.json`至`B11-stroke-order-crosscheck.json`，人工摘要为`reviews/B04-B11-stroke-order-crosscheck.md`。

证据边界：该TSV属于二次数字化材料，因此本轮只把`stroke_order`推进到`crosschecked`，**不替代GF0023—2020规范原页视觉review，不提前标最终reviewed**。B05“牙”的第2笔细笔名冲突继续独立保持`conflict_fail_closed`。

## 最新80项笔顺二次定位：B12—B19（2026-10-05）

B12—B19共80个不同主部首完成GF0023派生TSV二次定位。固定数据源为`takushun-wu/han-ideographs-stroke-order/order.tsv`（blob `ecf422f0bb9d1d07d661250796269bfa752ebd`）。

结果：
- **80/80目标精确可定位**；
- **80/80派生笔数与canonical baseline一致**；
- **0目标缺失、0笔数冲突**。

由于B12—B19此前没有canonical笔顺候选码，本轮不是“候选码交叉通过”，而是新增secondary locator：每项目标保存派生笔顺码、Unicode、排序序号和笔数；canonical `stroke_order`推进为`secondary_GF0023_derived_order_located_original_page_pending`。

证据边界：该TSV是二次数字化材料，**不替代GF0023—2020规范原页视觉review**；`fine_stroke_names`也不能由五类笔顺码反推，继续独立pending。

## 最新80项细笔名二次交叉核验（2026-10-05）

B04—B11共80个不同主部首完成`cnchar-order`二次逐笔细分类定位/交叉。固定来源为`theajack/cnchar` pinned ref `b8397db3e08e88ebbf8acf92b5cbab1a7e4c1550`，使用固定`stroke-order-jian.json`和`stroke-table.json` blob。

结果：
- **32项**candidate与二次细笔序列精确一致；
- **5项**二次源自身同码双名、candidate兼容：弋、支、攴、氏、欠；
- **20项**二次细笔序列已定位但canonical无逐笔candidate；canonical层其中牙继续保留既有权威冲突，因此19项进入secondary locator状态；
- **4项**二次冲突并fail-closed：几、凵、风、心；
- **19项**该二次数据不覆盖目标。

cnchar文档明确存在五组同码双名，因此本轮**只推进secondary crosscheck/locator，不替代GF2001、GF0023或S04规范原页**。牙第2笔“撇折/竖折”继续原有`conflict_fail_closed`。

## 最新80项细笔名二次定位：B12—B19（2026-10-05）

B12—B19共80个不同主部首完成`cnchar-order`二次逐笔细分类定位。固定来源为`theajack/cnchar` pinned ref `b8397db3e08e88ebbf8acf92b5cbab1a7e4c1550`。

结果：
- **62项**取得单义逐笔细分类序列；
- **12项**取得序列但源自身存在同码双名：殳、穴、疋、皮、矛、虍、色、麦、龟、角、鱼、骨；
- **6项**该二次数据不覆盖目标：屮、疒、癶、覀、龺、鬥；
- **0项**出现序列长度与canonical baseline笔数冲突。

B12—B19此前没有逐笔细笔名candidate，因此本轮只形成secondary locator，不称crosscheck。所有项目在GF2001/GF0023/S04等适用规范原页review前都不得标最终`fine_stroke_names reviewed`。

同名分支早期并行推进曾因B19写路径触发tooling_write_blocker而切换到B20；随后B19已经恢复成功。B20额外locator evidence保留，但不计入本轮80项主吞吐。

## 最新80项细笔名独立二次交叉：B12—B19（2026-10-06）

B12—B19共80个不同主部首新增第二套独立二次源D04/cjklib，与既有D03/cnchar逐笔比较。

结果：
- **22项**两源逐笔完全一致；
- **5项**粒度兼容：皮、虍、酉、辰、鬼；
- **8项**两源冲突并fail-closed：毋、鸟、臣、虫、缶、舟、里、角；
- **4项**补上cnchar缺口：屮、疒、癶、覀；
- **41项**D04无条目，保留既有D03状态。

两套二次源即使一致也不替代规范原页；8个冲突必须回GF2001/GF0023/S04原页裁决。

## 剩余阶段状态（2026-10-06）

剩余工作已改为P0—P7阶段化收口，详见`docs/REMAINING_PHASE_PLAN.md`。

- **P0 规范源通道：完成。** 新`source-probe` run `37402630995`成功，artifact `11385916300 normative-reference-acquisition`重新取得并强制SHA256校验S02/GF0023—2020、S04/1997笔顺规范、S05/GF2001—2001和S01-2009；当前artifact有效至2026-10-13。恢复原件本身不授予任何字段reviewed。
- **P1 笔顺规范原页收口：当前活动阶段。** B04—B21的GF0023主表原页review已全部扫完：134/171 reviewed，37/171进入固定residual queue；加上B01—B03既有30项，全书164/201项stroke_order已reviewed。下一步只处理这37项S04/其它适用规范残余。
- P2：细笔名规范原页收口；P3：其它字段扫尾；P4：2022身份与位置迁移；P5：201项content_ready终审；P6：artwork/layout；P7：PDF/QA/release。

从P1开始不再主动扩D05/D06等secondary数据源，除非规范原件出现真实无法定位缺口。

## P1第一轮：B04—B11笔顺规范原页收口（2026-10-06）

已从通过SHA256校验的GF0023—2020原件实际渲染/查看PDF物理页9—21（原印3—15页），并对精确目标行生成放大裁图逐项核对。

结果：
- B04：10/10 reviewed；
- B05：10/10 reviewed；
- B06：5 reviewed / 5 pending；
- B07：0 / 10；
- B08：3 / 7；
- B09：10/10；
- B10：8 / 2；
- B11：9 / 1。

合计 **55/80项stroke_order升级为`reviewed_GF0023_2020_original_page`，25项保持pending，0笔顺码冲突**。

25项未精确定位：匚、冂、勹、亠、冫、冖、凵、卩、厶、廴、艹、廾、宀、辶、彐、丨、丿、丶、乛、囗、彡、夂、丬、攴、罒。这里不声明“无规范笔顺”，只转入P1残余队列继续查S04或其它适用规范。

“牙”的数字笔顺`1523`本轮已经GF0023原页reviewed，但第2笔“撇折/竖折”仍属于独立的`fine_stroke_names conflict_fail_closed`。

人工记录：`reviews/P1-B04-B11-GF0023-original-page.md`。

## P1第二轮：B12—B19笔顺规范原页收口（2026-10-06）

已从通过SHA256校验的GF0023—2020原件实际渲染目标原页。对68个精确目标生成放大裁图逐项查看；对12个未精确定位目标，按secondary locator的数字笔顺码回到排序邻接区间原页，实际查看目标码前后边界。

结果：
- B12：5 reviewed / 5 pending；
- B13：8 / 2；
- B14：10 / 0；
- B15：9 / 1；
- B16：10 / 0；
- B17：8 / 2；
- B18：10 / 0；
- B19：8 / 2。

合计 **68/80项stroke_order升级为`reviewed_GF0023_2020_original_page`，12项保持pending，0笔顺码冲突**。

12项未精确定位：屮、巛、疒、疋、癶、覀、虍、糸、釆、龺、髟、鬥。这里的“未定位”已经包含对应笔顺码排序邻接区间的原页视觉检查，仍不声明“无规范笔顺”；全部转入P1残余队列继续查S04或其它适用规范。

前两轮B04—B19累计：**123/160项stroke_order已GF0023原页reviewed，37/160项进入残余队列**。

人工记录：`reviews/P1-B12-B19-GF0023-original-page.md`。

## P1第三轮：B20—B21笔顺规范原页收口（2026-10-06）

B20—B21共11个主部首已逐项回GF0023—2020原页视觉复核，**11/11精确命中，0 pending，0 conflict**：

- B20：10/10 reviewed；
- B21：1/1 reviewed。

精确目标为：高、黄、麻、鹿、鼎、黑、黍、鼓、鼠、鼻、龠。每项已保存PDF物理页、原印页、《字表》序号、UCS和规范数字笔顺码。

由此，B04—B21共171项的GF0023主表扫描已经全部完成：
- **134/171** 精确目标升级为`reviewed_GF0023_2020_original_page`；
- **37/171** 不在GF0023主表中以当前精确目标字形定位，进入固定P1 residual queue；
- 精确定位项0笔顺码冲突。

加上B01—B03既有30项内容层笔顺已关闭，全书201项当前为 **164 reviewed + 37 residual**。后续P1不再扫描新的GF0023批次，只处理这37项S04/其它适用规范残余。

37项：匚、冂、勹、亠、冫、冖、凵、卩、厶、廴、艹、廾、宀、辶、彐、丨、丿、丶、乛、囗、彡、夂、丬、攴、罒、屮、巛、疒、疋、癶、覀、虍、糸、釆、龺、髟、鬥。

人工记录：`reviews/P1-B20-B21-GF0023-original-page.md`。

## P2第一轮：B04—B11细笔名规范原页收口（2026-10-06）

B04—B11共80个主部首已完成GF2001—2001折笔规范与目标整字规范原页逐项复核。结果：**79项 fine_stroke_names reviewed，1项牙保持 conflict_fail_closed，0普通pending**。关键裁决：几=撇、横折弯钩；凵=竖折、竖；欠第2笔=横撇；风第2笔=横斜钩；心第2笔=卧钩。secondary D03/D04只作locator/crosscheck，不参与多数投票。

证据：`data/evidence/P2-B04-B11-fine-stroke-names-original-page.json`；人工摘要：`reviews/P2-B04-B11-fine-stroke-names.md`。canonical `data/B04.json`—`data/B11.json`已同步；牙仍保留精确冲突和解决路径。P1保持201/201 stroke_order reviewed。

## P2第二轮：B12—B19细笔名规范原页收口（2026-10-06）

B12—B19共80个主部首完成GF2001—2001术语/折笔分类与GF0023目标原页复核。结果：**67项 fine_stroke_names reviewed，12项 alternative-source pending，1项矛 conflict_fail_closed**。12项pending：屮、巛、疒、疋、癶、覀、虍、糸、釆、龺、髟、鬥；这些目标在GF0023主表没有精确行，GF2001也无直接目标字例，secondary locator不得升级。

高风险secondary冲突毋、鸟、臣、虫、缶、舟、里、角已由规范目标原页裁决；例如毋首笔=竖折、臣末笔=竖折、缶第5笔=竖折、角第2笔=横撇。矛的两个code-5折笔在当前规范扫描下仍不足以可靠区分横撇/横钩，保持fail-closed。

B12—B15、B17—B19 canonical已同步；B16十项evidence为10/10 reviewed，但`data/B16.json`更新触发tooling_write_blocker，保留canonical状态债。证据：`data/evidence/P2-B12-B15-fine-stroke-names-original-page.json`、`data/evidence/P2-B16-B19-fine-stroke-names-original-page.json`、`reviews/P2-B12-B19-fine-stroke-names.md`。

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

1. 继续清理少量review/状态同步债；B20 component-name machine evidence已补齐；
2. **P1的GF0023主表阶段已完成到B21：B04—B21为134/171 reviewed，37/171 residual；全书为164/201 reviewed。** 下一步只对固定37项使用S04/其它适用规范做P1 residual closure，关闭后进入P2细笔名原页收口。
3. 结构字段继续利用GF0013—2009等适用来源逐批闭合，但不外推2022部首身份；
4. 位置迁移继续回目标整字核验；
5. GF0011—2022逐项精确字段继续由Issue #4并行追踪。

## P1 residual来源审计：GF3002—1999（2026-10-06）

为37项固定stroke-order residual尝试引入GF3002—1999《GB 13000.1字符集汉字笔顺规范》。PR #26 合入后，source-probe run `37410985779` 成功取得镜像，artifact `11389595541`；文件6,730,497字节，SHA256为 `cb5cb74f108dafed41a3583bc8d33d8dd318d1a21d714923c0f1ced89443cf3e`。

已实际渲染/查看全部8个PDF物理页。结果确认该镜像为节录版：目录指向正文/字表原印第4—343页，但当前文件仅8页；末页样表到序号134即标“（略）”。因此本轮**0/37项升级reviewed**，37项集合保持不变；该镜像已标记为`abridged_not_admissible_for_P1_residual_closure`，避免后续把“题名正确”误当“正文完整”。

随后对该8页原件中实际可见的主表序号1—134继续逐项视觉复核，精确关闭丨、丿、丶、乛、丬5项，0冲突；只允许使用真实显示且已审读的精确字条，“（略）”之后的未显示条目不得外推。全书stroke_order由164/201推进为**169/201 reviewed，32/201 residual**。下一步获取完整GF3002—1999、GB/T 25741—2010附录C或其它适用权威原件，对固定32项继续集中收口。


## P1完成：GB/T 25741—2010附录C关闭最后32项（2026-10-06）

已从固定公开Git blob经Actions临时reference artifact恢复GB/T 25741—2010《信息技术 汉字编码字符集 汉字部首序和笔顺序》附录C，文件43,054,573字节、323个PDF物理页、SHA256 `0514f50e310ae2eb32a743a3813d2630be9accec28b8bf244b06499d1d737baf`。附录C首页明确标注“规范性附录 汉字笔顺序”，并说明对27,533个汉字按笔顺序规则排序。

对P1固定32项residual逐项使用文本层定位候选，再实际渲染目标原页并视觉核对精确字形、表序号、笔数和数字笔顺。审读PDF物理页1、2、3、7、9、10、12、18、26、35、74、80；结果**32/32精确命中，0笔顺码冲突**。其中龺在PDF 35／原印345页／表序号2960，8画，笔顺码`12251112`，不再需要单独来源兜底。

因此P1最终达到：**201/201 stroke_order reviewed，0 residual，0 P1 conflict**。字段级总证据：
`sources/reviews/P1-GBT25741-appendix-C-residual-original-page-20261006.json`。

当前活动阶段正式切换为**P2：fine_stroke_names规范原页收口**。P2优先集合仍按阶段计划：牙、几、凵、风、心、毋、鸟、臣、虫、缶、舟、里、角及D03/D04源歧义项；优先GF2001—2001，再用GF0023/S04整字原页裁决。P1完成不改变content_ready总数，也不表示artwork/PDF/manifest/CI/release完成。


## P2完成并切换P3（2026-10-06）

P2细笔名规范原页收口已达到阶段退出条件。B04—B21共171项最终为：**157 reviewed、14 conflict_fail_closed、0普通pending**。14项fail-closed为牙、矛、屮、巛、疒、疋、癶、覀、虍、糸、釆、龺、髟、鬥。

本检查点新增完成：
- B20—B21 11项细笔名由GF2001术语规则 + GF0023精确目标原页关闭，11/11 reviewed；
- B16此前10项evidence已reviewed但canonical未同步的状态债已清理；
- 12个规范目标缺口项在GF2001、GF0023、S04规定来源均已实审后，收口为`conflict_fail_closed_normative_target_gap`，不从secondary数据反推完整细笔名。

证据：`data/evidence/P2-B20-B21-fine-stroke-names-original-page.json`、`data/evidence/P2-normative-target-gap-failclosed.json`、`reviews/P2-completion-20261006.md`。

**当前活动阶段正式切换为P3：pronunciation / component_name / structure扫尾。** P1仍为201/201 stroke_order reviewed；P2完成不改变content_ready统计，也不表示artwork、PDF、manifest、CI或release完成。


## P3第一轮：component_name状态债与P4路由（2026-10-06）

本轮实际推进47个不同主部首的component_name：B08十项恢复既有S03原页证据并同步canonical，B14十项把已在库的S03精确目标行同步canonical，共20项正式`reviewed_S03_GF0014_2009`。另27项此前已完成S03原页审读且明确无精确独立主形条目，本轮不再作为P3普通pending，而按阶段职责路由至P4的GF0011—2022精确名称门槛；这些27项**不标reviewed**。

27项为：支、比、屮、毋、疋、齐、羽、麦、走、足、邑、釆、青、龺、齿、黾、阜、骨、香、音、髟、鬥、麻、黍、鼓、鼠、鼻。P3中的component_name普通缺口目前仅剩B21龠1项。pronunciation与structure未因本轮名称处理而升级，仍是P3后续主吞吐。

证据：`data/evidence/B08-component-name.json`、`data/evidence/B14-component-name.json`、`data/evidence/P3-component-name-S03-no-exact-route-P4.json`、`reviews/P3-round1-component-name-20261006.md`。


## P3第二轮：structure规范集合收口（2026-10-06）

本轮实际推进**100个不同主部首**的structure，全部来自此前S07未直接关闭的项目。

来源链：
- S07 / GF0013—2009：既有原页适用性审读；
- S10 / GF3001—1997《信息处理用GB13000.1字符集汉字部件规范》：教育部官方规范身份，固定公开Git blob `fe3d4405e7af2438ee923d89c64825ff17d7b8a1`；规范定义“基础部件”为最小、不再拆分的部件；
- A01 / 邵霭吉《〈通用规范汉字表〉独体字统计与思考》（2021）：公开发表的规范集合完整转录/比较，给出GF3001的230个成字基础部件，并确认其与S07的191项重合及39项GF3001补充独体字。A01只作成员转录/交叉，不作为独立权威体系。

结果：
- **63项GF0023精确规范字完成structure关闭**
  - 15项 `undecomposable`：弋、韦、幺、示、毋、皮、缶、竹、聿、艮、豸、非、金、食、黑；
  - 48项 `decomposable`：既不在S07独体字表，也不在GF3001补充39独体字集合；本轮只关闭“可拆/合体”层，不虚构左右/上下/包围等更细拓扑。
- **37项非GF0023精确目标的部件型主项**不套通用规范汉字295独体字集合，全部转P4 GF0011—2022精确目标身份/主附关系门槛；这些项目不标structure reviewed。
- **P3 structure普通pending由100降为0。**

证据：
`data/evidence/P3-structure-GF3001-synthesis.json`、
`reviews/P3-structure-GF3001-synthesis-20261006.md`。

P3当前剩余主吞吐：pronunciation；component_name普通缺口仅B21龠1项。P4路由项不计作P3普通pending，也不冒充reviewed。


## P3完成并切换P4（2026-10-06）

P3 `pronunciation / component_name / structure` 已达到阶段退出条件，B04—B21三个字段普通pending全部归零：

- **pronunciation**：126 reviewed、11 conflict_fail_closed、34 not_applicable、0普通pending；
- **component_name**：143 reviewed、28项完成S03适用性审读后转P4 GF0011—2022精确名称门槛、0普通pending；
- **structure**：134 reviewed、37项非GF0023精确目标转P4精确身份/主附关系门槛、0普通pending。

本轮pronunciation关键新增：S06/GF0015—2010正式扫描件已通过source-probe run `37449756736`、artifact `11406995313`恢复并强校验（19,262,366字节、157页、SHA256 `0d647e1378847480364e2603030fe6aa6102d99320c42cac631b2fb3155d18ce`）。25个GF0023精确规范字完成原页核验，14项取得直接字条/明确词素读音，11项在初中高三级对应拼音区间均无目标证据而fail-closed。34个部件型项目收口为当前教学表面pronunciation不适用。

B21龠完成S03主体表序号1—514全表排除审读，未见精确独立名称条目，component_name正式转P4而不标reviewed。

证据：`data/evidence/P3-pronunciation-GF0015-original-page.json`、`data/evidence/P3-pronunciation-nonlexical-component-not-applicable.json`、`data/evidence/B21-component-name-S03-applicability.json`、`reviews/P3-completion-20261006.md`。

当前活动阶段正式切换为 **P4：GF0011—2022精确身份、主形/附形、名称、编码与位置迁移**。P1/P2/P3完成不改变content_ready总数，也不表示artwork、PDF、manifest、CI或release完成。


## P4第一轮：B04—B11主部首身份连续性（2026-10-06）

本轮实际推进**80个不同主部首**。教育部/国家语委2022年发布说明明确GF0011—2022为2009版修订，并“保持原有201个主部首”，修订重点包括附形部首增补微调、部分常用部首名称与信息处理国际编码。

结合已实际审读的GF0011—2009主表，B04—B11八批80项的`target_identity`已从笼统的`baseline_2009_reviewed_2022_pending`细化为：

`P4_main_radical_membership_continuity_reviewed_exact_2022_fields_pending`

已关闭：201主部首集合成员身份连续性、项目固定main_id连续性。  
仍pending：2022精确主形字形、正式附形/从属形、常用名称、信息处理国际编码。

本轮没有宣称取得GF0011—2022完整正文。公开访问审计确认：官方发布说明可重复访问，但尚未定位可重复公开获取的正式全文；Unicode/IRG材料可证明2022规范已被中国部件工作使用，但不替代逐项正文。因此该问题记为**source blocker（仅针对2022逐项精确字段）**，不阻塞P4位置迁移或后续批次的主部首身份连续性复核。

证据：
- `data/evidence/P4-B04-B11-main-radical-identity-continuity.json`
- `reviews/P4-B04-B11-main-identity-continuity.md`
- `sources/reviews/P4-GF0011-2022-public-access-audit-20261006.json`

P4下一轮按计划推进B12—B19 80项；同时可独立处理位置迁移，不等待2022全文。


## P4第二轮：B12—B21主部首身份连续性（2026-10-06）

本轮实际推进**91个不同主部首**：B12—B19八批80项，再顺带完成B20/B21 11项。全部按与第一轮相同的证据边界，只关闭GF0011—2022官方发布说明明确支持的“201主部首集合连续性 + 项目main_id连续性”，不把发布说明冒充逐项正文。

结果：
- **91/91** `P4_main_radical_membership_continuity_reviewed_exact_2022_fields_pending`；
- 与第一轮累计，**B04—B21共171/171个在编主项**的主部首成员身份/main_id连续性已reviewed；
- 2022逐项精确主形、附形、名称和国际编码仍全部等待正式全文或官方逐项数据；
- position_migration仍未因此关闭，继续独立回完整整字核验。

证据：
- `data/evidence/P4-B12-B19-main-radical-identity-continuity.json`
- `data/evidence/P4-B20-B21-main-radical-identity-continuity.json`
- `reviews/P4-B12-B21-main-identity-continuity.md`

P4的身份连续性下一步只剩B01—B03既有30项回归；P4主工作将逐步转向位置迁移和2022精确逐项字段。


## P4身份连续性里程碑：201/201（2026-10-06）

完成B01—B03既有30项P4回归后，全书201个主部首均已完成GF0011—2022“主部首集合成员身份 + 项目main_id连续性”复核：

- B01—B03：30/30；
- B04—B11：80/80；
- B12—B21：91/91；
- **累计201/201。**

证据边界保持不变：教育部/国家语委2022发布说明明确保持原有201个主部首，可以关闭成员身份连续性；但正式全文仍未定位到可重复公开通道，因此2022逐项精确主形、附形、常用名称和国际编码仍全部pending。该source blocker不否定201集合连续性，也不阻塞位置迁移。

P4现在的主工作从“主项是否仍在201集合中”转为：
1. GF0011—2022逐项精确字段；
2. 完整整字position_migration；
3. 附形/位置变体冻结与完整时序核验。

证据：`data/evidence/P4-B01-B03-main-radical-identity-continuity.json`、`reviews/P4-B01-B03-main-identity-continuity.md`。


## P4 position_migration 第一轮：B06—B11（2026-10-06）

本轮实际推进**60个不同主部首**的位置迁移整字核验。由于B04/B05当前main没有可复用的权威整字语境evidence，没有为凑80而使用编辑例字升级状态。

使用source-probe已SHA固定的GF0023—2020原件，对B06—B11已选定的59个唯一整字目标逐行实际渲染、视觉查看跟随式累计笔画图，并保存整字页码、表序号、UCS、数字笔顺、部件在整字中的笔画索引和改笔信息。

结果：
- **60/60 position_migration reviewed，0普通pending（本轮范围内）**；
- 甘→甜的canonical位置由错误的`left`修正为`right`；
- 匚→区=`[1,4]`、弋→式=`[1,5,6]`、囗→国=`[1,2,8]`，明确要求完整整字时序，不能按部件自写顺序连续播放；
- 矢→知第5笔、禾→和第5笔均确认**捺→点**；
- 风→风为self语境，确认当前无位置迁移。

证据：
- `data/evidence/P4-B06-B11-position-migration-whole-character.json`
- `reviews/P4-B06-B11-position-migration.md`

边界：本轮只关闭记录的代表整字语境，不把它提升为GF0011—2022正式附形认定；2022精确附形/名称/编码仍受全文访问门槛约束。B04/B05 20项下一轮补权威整字目标后继续。


## P4 position_migration 第二轮：B12—B19（2026-10-06）

本轮实际推进**80个不同主部首**的完整整字位置迁移核验，全部使用GF0023—2020代表整字原页并保存部件在整字中的笔画索引、位置、映射类型、改笔及是否必须保留完整整字时序。

结果：
- **78 reviewed**
- **2 conflict_fail_closed：屮、毋**
- **0普通pending**

关键项：
- 疒、虍：包围/半包围关系要求保留完整整字时序，不能只按部件局部顺序播放；
- 疋、竹、足：记录到独体主形进入代表整字后的粗粒度笔画类别变化；
- 屮→屯、毋→每：GF0023整字原页已实际查看，但独体目标的完整粗粒度笔顺无法在代表整字中可靠一一映射，因此fail-closed，不借候选例字或secondary数据强行授予reviewed。

累计P4 position_migration（B06—B19）：**138 reviewed + 2 fail-closed，共140项**。GF0011—2022正式附形身份仍与位置迁移分离，不能由本轮整字形态自动提升。

证据：
- `data/evidence/P4-B12-B19-position-migration-whole-character.json`
- `reviews/P4-B12-B19-position-migration.md`

下一步：B20/B21 11项整字迁移、B04/B05 20项补权威整字语境，以及B01—B03既有30项位置迁移回归。


## P4 position_migration 全书收口（2026-10-06）

P4位置迁移已完成全书201项收口：

- **198 reviewed**
- **3 conflict_fail_closed：屮、毋、瓦**
- **0普通pending**

最后一轮完成61项：
- B01—B03 + B20/B21 共41项：复用此前已实际完成的GF0023目标整字原页核验，只关闭self-context“无位置迁移”层；
- B04—B05 共20项：19项通过既有GF0023代表整字原页 + 可靠笔画索引映射关闭；瓦→瓶因持久化整字码在进入瓦前截断，无法可靠恢复瓦的4笔索引/改笔，精确fail-closed。

累计关键边界：
- 包围/穿插部件必须保留完整整字时序；
- 车→辆确认独体粗粒度码`1512`到左旁位置形`1521`的改笔；
- 矢→知、禾→和末笔捺→点；
- 疋、竹、足等已记录代表整字中的粗粒度类别变化。

证据总检查点：`reviews/P4-position-migration-completion-20261006.md`。

P4尚未退出：**GF0011—2022正式全文/官方逐项数据仍是独立source blocker**。当前201/201主部首集合连续性已reviewed，201/201 position_migration也已reviewed/fail-closed；但2022逐项精确主形、正式附形、常用名称和国际编码仍pending，不能冒充完成。


## P4完成并切换P5（2026-10-06）

P4已满足阶段退出条件。

全书主部首身份：
- **201/201** 主部首集合成员身份/main_id连续性 reviewed；
- GF0011—2022逐项精确主形、正式附形、常用名称和国际编码：**201/201 source_blocked_fail_closed**，不填造值。

全书position_migration：
- **198 reviewed**
- **3 conflict_fail_closed：屮、毋、瓦**
- **0普通pending**

P3转P4字段：
- component_name（B04—B21）：143 reviewed + 28 source_blocked_fail_closed；
- structure（B04—B21）：134 reviewed + 37 source_blocked_fail_closed；
- 普通pending均为0。

GF0011—2022正式全文/官方逐项数据的公开访问审计已固定：教育部发布说明只支持“保持原有201主部首”等总体事实；公开规范索引、高校下载区、公开Git规范镜像均未定位正式2022逐项正文；Unicode IRG后续材料引用GF0011—2022并明确标注“not released”。因此P4按“精确source-blocked fail-closed + 明确重开条件”收口，不无限横向扩secondary数据。

P4完成检查点：
- `reviews/P4-completion-20261006.md`
- `sources/reviews/P4-GF0011-2022-exact-fields-source-blocked-20261006.json`
- `reviews/P4-position-migration-completion-20261006.md`

**当前活动阶段正式切换P5：逐批内容终审与content_ready收口。**
当前content_ready仍为30（B01—B03），content_in_progress仍为171（B04—B21），只有P5逐批验收通过后才增加content_ready。P4完成不表示artwork、PDF、manifest、CI发布门槛或正式release完成。


## P5完成：201/201 content_ready（2026-10-07）

P5逐批内容终审已经完成。B04—B21共171项逐项检查身份、结构、笔数、笔顺、细笔名、读音、部件名称、教学提示、自查句、整字语境、位置迁移与field-level evidence；普通pending全部清零。

本轮P5主要清理P1—P4已闭合证据与canonical之间的状态债：
- B06/B08/B10/B14共40项教学文案由旧候选语气同步为与已审笔顺/细笔名/位置迁移一致的最终教学表述；
- B08 6项stroke_count由旧candidate状态同步为精确规范笔顺行reviewed；
- B12—B21 91项whole_character_context同步P4整字原页结果；
- B07/B11 19项删除已经失效的“候选/待核”措辞；
- 清理若干已被后续阶段取代的历史unresolved文本，同时保留牙、矛、屮、毋、瓦等真正fail-closed边界及重开条件。

终审evidence：
- `data/evidence/P5-B04-B12-final-content-acceptance.json`：90/90 accepted；
- `data/evidence/P5-B13-B21-final-content-acceptance.json`：81/81 accepted；
- `reviews/P5-completion-20261007.md`。

因此：
- B01—B03既有30项content_ready；
- B04—B21新增171项content_ready；
- **全书201/201 content_ready，0 content_in_progress。**

这只表示内容层完成，不表示artwork、PDF、manifest、CI发布门槛或正式release完成。当前活动阶段正式切换为**P6 Artwork / 版式**。


## P6启动：201项矢量材料覆盖与B03正规化（2026-10-07）

P6已完成全书绘图材料覆盖审计。固定Hanzi Writer / Make Me a Hanzi revision `68d10a4b21150cae5e1ebbd223eed289cf32d90c`，workflow run `37513572597` 实际遍历B01—B21全部201项：

- 201/201矢量可取得；
- 201/201矢量笔数与内容层终审笔数一致；
- 0 missing；
- 0 stroke_count_mismatch；
- 0 other_errors。

该结果只关闭“绘图材料存在且笔数兼容”，**不授予B04—B21 artwork_ready**。证据：`data/evidence/P6-vector-material-coverage-20261007.json`。

B03此前已在2026-09-30完成真实逐笔矢量人工复核（`data/evidence/B03-artwork.json`、`reviews/B03-artwork.md`），其`artwork_ready_local_candidate`只是旧阶段模型把PDF归档绑在一起。P6将B03正规化为`artwork_ready`，PDF归档仍独立留给P7。

当前artwork_ready：**30/201（B01—B03）**。B04—B21共171项下一步必须逐项做累计笔画视觉QA，不能从本次材料覆盖审计自动升级。


## P6第一轮：B04—B11 artwork视觉复核（2026-10-07）

本轮使用固定Hanzi Writer revision `68d10a4b21150cae5e1ebbd223eed289cf32d90c`，由workflow run `37548434948`生成B04—B11 80项临时累计笔画审图包（artifact `11452390328`）。8个批次PDF全部渲染为120dpi PNG后逐批实际查看；牙、瓦、廴、心、罒额外做单页第二遍复核。

结果：
- **80/80 artwork reviewed**
- 0 artwork conflict
- 0 ordinary artwork pending
- 当前笔红色/旧笔深灰关系正确
- 累计笔画顺序与content_ready数据一致
- 未见明显轮廓裁切、重叠或笔数不符

牙的P2细笔名语义冲突保持fail-closed；P6不借绘图材料解决术语冲突。

因此B04—B11全部升级为`artwork_ready`。连同B01—B03，当前全书为 **110/201 artwork_ready**，剩余B12—B21共91项继续同流程审图。

证据：`reviews/P6-B04-B11-artwork-review-20261007.md`及`data/evidence/P6-B04-artwork-review.json`至`P6-B11-artwork-review.json`。

注意：artwork_ready不等于layout_ready或PDF/release完成；最终A4版式与P7归档仍独立。


## P6第二轮：B12—B21 artwork视觉复核与201/201里程碑（2026-10-07）

本轮对B12—B21共**91个主部首**完成累计笔画artwork视觉QA。workflow run `37549583534` 成功生成临时审图artifact `11452452267 p6-artwork-review-b12-b21`；91页全部渲染为120dpi PNG，10个批次contact sheet全部实际查看，屮、毋、鬥、龠另做单页放大复核。

为保持前序fail-closed边界，P6审图器对没有权威细笔名序列的目标只按已reviewed的笔数/笔顺生成STEP 1…N，不伪造笔画名称。

结果：
- **91/91 artwork reviewed**
- 0 artwork conflict
- 0 ordinary artwork pending
- B20复杂字与B21龠17画累计示范完整，无明显裁切/重叠
- 前序语义fail-closed全部保持，不由绘图材料解除

至此全书：
- B01—B03：30 artwork_ready
- B04—B11：80 artwork_ready
- B12—B21：91 artwork_ready
- **累计201/201 artwork_ready**

证据：`reviews/P6-B12-B21-artwork-review-20261007.md`、`data/evidence/P6-B12-artwork-review.json`至`P6-B21-artwork-review.json`。

**P6仍未完成。** 下一门槛是全书统一A4版式、练习层级以及复杂字分页策略；实际PDF归档、manifest、全书PDF视觉QA和正式release仍属于P7。

## P7 v0.4.0 structured draft archive（2026-10-07）

PR #49 已合入 main，merge commit `81c6c6b9bb282966b29a9c96c1c8bb016e54ab76`。该 PR 完成了 P7 结构化全书导航：2 页目录、201 主部首索引、32 项教学附形/位置变体索引、原 V001—V027 回归表、来源/字段复核说明与版本/勘误页。

目标 HEAD `327b732f15aa4a01406606aad1fed80dbae144fb` 的 Book integrity checks run `37565130391` 成功。其 artifact `11458786539 zitie-p7-structured-draft-research` 已实际生成 276 页结构化全书 draft；artifact digest 为 `sha256:5b415bc111ff30da91bc25c17858d9c1cc37f5354487188992947287826e821e`。

P7 新增页面已完成实际视觉 QA：
- 目录 2 页；
- 201 主部首索引 6 页，main_id 001—201 连续，`201 龠 -> B21 -> 261–263`；
- 32 项教学候选变体索引 2 页；
- 原 V001—V027 回归表 2 页；
- 来源/字段复核与来源台账 2 页；
- 版本、勘误与发布状态 1 页。

共 15/15 个本轮新增页面实际渲染查看通过；长来源标题已改为换行展示，不再硬截断。证据：`data/evidence/P7-structured-draft-visual-QA-20261007.json`、`reviews/P7-structured-draft-visual-QA-20261007.md`。

随后通过一次性 feature-branch archive workflow 固定下载上述已审 artifact，强校验页数、字节数和 SHA256，并已真实写入：
- `deliverables/drafts/v0.4.0/B01-B21_with_preface_toc_appendices_draft_A4.pdf`
- 276 页
- 3,683,612 bytes
- SHA256 `b44c7b13a38b020f8e5e83cc3b8058736a10d4556998689ed4d15076b54cc9eb`

`deliverables/manifest.json` 已登记 v0.4.0，`release_eligible=false`。一次性 archive workflow 在归档提交中已自行删除，不留驻 main 的临时自动化。

当前 P7 尚未完成：归档 PR 的目标 HEAD CI、全书级 release gate、release candidate 和正式 `deliverables/releases/` 仍保持 pending。GF0011—2022 逐项精确字段仍按 P4 既有结论 source-blocked fail-closed，不因归档 PDF 而升级。

## P7 v0.4.0 RC1 archive（2026-10-07）

PR #52 已完成候选渲染能力并合入 main，merge commit `c29574180e1a3f11324313be7e5179c208077d46`。RC1 使用独立 `--candidate` 模式，不复用正式 `--release`，因此不会把旧逐批 `release_eligible=false` 强行改真。

最终候选构建：
- source HEAD：`5ab536f32ac7f1c2909236e0261d3f8db745f6a5`
- workflow run：`37569826763`
- artifact：`11460128190 zitie-p7-draft-and-rc1-research`
- artifact digest：`sha256:e518eec768e5a72f6d82581d87e31b4e9afb67aba2c7b8eed33088d04eca888e`
- RC1 PDF：276页，3,756,330 bytes，SHA256 `fb88257a792c39aa147bb6074fd00656bd7c3c7458dd12c4b6750ddb65498bff`

RC1全文机器预检：
- `编写中` / `编写稿` / `前言初稿`：0；
- 3个前言页均显示“发布候选稿 RC1”；
- 258个练习页均显示“发布候选稿 RC1”；
- 合计261个候选标记；
- GF0011—2022 source-blocked / conflict fail-closed披露继续保留；
- 正式release仍为0。

RC1视觉QA实际查看16个代表页，并继承P6对258个练习页完整layout review及P7对15个导航/卷末新增页完整视觉review。证据：
- `data/evidence/P7-RC1-visual-QA-20261007.json`
- `reviews/P7-RC1-visual-QA-20261007.md`

RC1已通过一次性feature-branch归档流程真实写入：
`deliverables/drafts/v0.4.0-rc1/B01-B21_with_preface_toc_appendices_rc1_A4.pdf`

`deliverables/manifest.json`已登记为`status=release_candidate`、`release_eligible=false`。这表示候选稿已归档，但仍不是`deliverables/releases/`正式稿。

当前P7仅剩：RC1归档PR目标HEAD CI、最终formal-release gate、正式PDF生成/终审、`deliverables/releases/`归档与release记录。GF0011—2022逐项精确字段继续保持201项source_blocked fail-closed，不因候选归档而升级。

## P7 v0.4.0正式发布归档候选（2026-10-07）

正式发布版已由PR #54目标HEAD `9149a6e9b751bfbc97e95c3bbfc64a5c8681f7fd`生成并完成formal gate与视觉QA。对应Book integrity checks run `37570965306`成功，artifact `11460761965 zitie-p7-draft-rc1-formal-preflight`。

固定正式PDF：
- 路径：`deliverables/releases/v0.4.0/B01-B21_with_preface_toc_appendices_v0.4.0_A4.pdf`
- 页数：276
- 字节：3,749,164
- SHA256：`ab3c23d7547872f4d0e2c128de397e9e89ed6de97b681876e2dff017ff5c4894`
- visual QA：`reviews/P7-formal-v0.4.0-visual-QA-20261007.md`

正式PDF全文预检确认：不存在“编写稿”“前言初稿”“编写中”“发布候选稿 RC1”等预发布标签；3个前言页和258个练习页均使用正式发布状态文字；目录、201主部首索引、32项教学变体、原V001—V027、来源台账和版本页保留。GF0011—2022逐项精确字段仍明确披露为201项source_blocked fail-closed，不因正式发布而改记reviewed。

`deliverables/manifest.json`已在当前release分支登记`status=released`、`release_eligible=true`，并保存release gate snapshot。terminal fail-closed继续披露为：细笔名14项、position_migration 3项、GF0011—2022逐项精确字段201项；`unresolved_conflicts=0`仅表示没有未分类/未路由的发布冲突，不表示这些fail-closed字段消失。

**当前仍未宣布P7完成。** 唯一剩余门槛是本正式release归档PR的目标HEAD CI；只有该CI成功后才更新P7为completed并合入main。



## P7完成：v0.4.0正式发布（2026-10-07）

全书正式发布门槛已全部通过。

正式PDF：
- 路径：`deliverables/releases/v0.4.0/B01-B21_with_preface_toc_appendices_v0.4.0_A4.pdf`
- 页数：276
- 字节数：3,749,164
- SHA256：`ab3c23d7547872f4d0e2c128de397e9e89ed6de97b681876e2dff017ff5c4894`
- formal preflight source HEAD：`9149a6e9b751bfbc97e95c3bbfc64a5c8681f7fd`
- formal preflight run：`37570965306`
- visual QA：`reviews/P7-formal-v0.4.0-visual-QA-20261007.md`

最终release归档PR：
- PR #55
- HEAD：`61ab933143137766f3fb00e5f946e7897d2e2349`
- Book integrity checks run：`37571448193` — **success**
- merge commit：`576812fec7cc681df45ed85b36f51a1abe5ad4bb`

`deliverables/manifest.json`正式条目为`status=released`、`release_eligible=true`，并保存release gate snapshot。

全书最终里程碑：
- 201/201 content_ready
- 201/201 artwork_ready
- 201/201 layout_ready
- 正式PDF已归档
- P0—P7全部完成

发布版继续公开披露终态fail-closed边界：
- fine_stroke_names：14项
- position_migration：3项（屮、毋、瓦）
- GF0011—2022逐项精确主形/附形/名称/编码：201项source_blocked_fail_closed

这些是有明确重开条件的终态边界，不是未分类普通pending；正式发布不伪造GF0011—2022未公开逐项数据。

后续仅进入维护/勘误模式；若GF0011—2022正式逐项数据出现可重复公开通道，再按现有reopen_condition开启新版本修订。
