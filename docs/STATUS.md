# 当前编写状态

更新：2026-10-06。工程处于“阶段1：内容覆盖优先”。

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
