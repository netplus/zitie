# 当前编写状态

更新：2026-10-06。工程处于“阶段1：内容覆盖优先”，当前活动阶段为P3其它字段扫尾。

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
