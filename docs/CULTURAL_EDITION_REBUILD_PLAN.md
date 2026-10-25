# 文化识字版 PDF 重建 · 执行计划（2026-10-24）

> 状态：**实施中 / 草稿审核**。这是从既有《循序渐进汉字部首字帖》派生的**新文化阅读版**，不是替换 v0.5.1、不是重新进行旧版 PDF 勘误，也不是在线练习格系统改版。全量新书在完成内容、笔顺、拼音、引文、插图与打印质检之前，**禁止标注正式发布**。

## 0. 基线与不可变条件

- GitHub：`netplus/zitie`，主字源 **201 个主部首/字、1045 笔、21 批次**，正式 PDF `deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf`，**299 页**。
- 原版 SHA256 必须为 `7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90`，与 `deliverables/manifest.json` 完全一致。前一版本 v0.6.0-15mm-rc1、正式版、原版教学元数据、A3 动画、Pages 打印网页均**只读**。
- **关键的笔顺基线来自原正式 PDF 真实累计笔顺图**：每笔的 86pt 源矢量格（源PDF Form XObject，`show_pdf_page(clip=...)`），不采用生成图中的“仿笔顺”；连续折、撇、钩不能被拆分、替换或二次描画。所有 ID 必须和原书书签及逐页画面对应。
- “正式版已核字段”不是“所有字段都已核”：原工程已因 GF0011—2022 若干单项数据源不可取得而明确 fail-closed；此处继续遵守已有 `teaching-source-policy.json`，不推断/补写缺失细笔名、读音或附形部件。
- 彩色笔顺保留**已写灰、本笔红**；每步序号清楚。难字优先自动分行，仍放不下则分**连续教学页**，绝不裁切/压小为无法识读；笔画数与源图、页数、编号逐项一致。

## 1. 用户已确定的编辑与视觉规范

**统一版式，不重复内容**；A4 纵向、白底/暖白、朱红/墨灰、含传统水墨意象的清爽文化阅读页，**取消练习格**（练习转由 `animation/print/` 在线生成）。每一字/偏旁独立专属：

1. 顶部**独有主题句**（不在正文每页重复“一字一世界”，这个名字只保留封面/系列）。
2. 右上角**独有且与字义强相关的主题图**；不得拿同一张山水/舟/云反复顶替。为每项记录唯一 asset_id / SHA 与题材，另做人审相似度对照。
3. 主字（或主部首）；**完整单字**拼音放在字**上方**。非独立读音的**偏旁附形**不强行注音；不可将偏旁俗称“sān diǎn shuǐ”误做“氵”单字正音。
4. 字义/部义：准确简洁，不泛化字源/构形知识。
5. 经典一隅：**逐条核对原文、作者、篇章来源**；无可核引文时空缺并打待审状态，不把自创短句标成名人名言。
6. **笔顺提示在笔顺图之前**：优先复用原 PDF `tips`，尤其提示易错折笔、钩、合笔，必要时标明来源审定状态。
7. 笔顺：原 PDF 中的每一幅真实累计示范，1～N 不缺页、不乱序，按内容空间动态 1/2/3 行或延展到连续页；不能为了固定美工模板损失笔顺教学。
8. 相关字词/常见字例：**字词在下，带调拼音在上**，尽量一词一组 4～6 项。此栏的“拼音是逐字教学对齐”与 GB/T 16159 正词法词写法是不同表达，数据层同时记录，不能用机器转换结果冒充权威核对。
9. **一字一句/一部一句**：有画面、哲思、灵气，简练不过度幼稚，不模仿套话；所有页面互不重复。
10. 页脚 provenance（源版本、ID、是否待审、页码）小字号，不进入儿童正文重点区。

## 2. 范围及任务拆解

| 阶段 | 任务 | 本阶段可验收产物 | 强制放行条件 |
|---|---|---|---|
| P0 基线锁定 | 核对源PDF SHA、299页、201个 ID 书签、源笔顺图实际位置 | 自动源审计报告与冻结列表 | 不一致立即失败 |
| P1 版式引擎 | 与装饰/编辑内容分离的 source-locked SVG/PDF 矢量笔顺裁剪；图前提示；智能分栏和分页 | **可重复生成** A4 草稿（先水/山/月/木） | 每幅图源页和 clip 有证据；无遗漏、无未来笔画，读字优先 |
| P2 编辑数据 | 建逐字/逐偏旁内容清单：字义、主题句、短句、词、拼音、引文、审校来源 | 每项数据有 status、source refs、reviewer/date | **不可**用自动翻译/发音工具结果直接标 reviewed |
| P3 视觉资产 | 给每个主字/偏旁策划一图一主题的图册，素材许可及唯一性检验 | `asset_id` + hash + theme + 设计图/权限 | 非法来源、缺件或高重复率一律阻断正式版 |
| P4 分批合成 | 21 批主字逐步产出，偏旁**附形单设数据域** | 候选书/校验 JSON /页码映射 | 逐批词音/引用/主题图等内容校验全部通过 |
| P5 质量门禁 | 渲染逐页看图、嵌字字体检查、PDF可搜、灰度/彩色、布局、字符OCR仅末选 | 批次统计、完整实测与打印建议 | 无截断/交叉、笔画数一致、无重复 theme/asset |
| P6 发布 | 人工审批后一并合成封面/目录/字页/偏旁页及版本记录 | **新** release candidate，再审定发布 | 旧版不覆盖；manifest 按可核字段单独追加新条目 |

**阶段 P1/P2 首批目标（当前迭代）**：从 v0.5.1 实际示范页建立 4 个文化阅读样板：`水(ID077)`、`山(ID039)`、`月(ID088)`、`木(ID064)`，覆盖横/折/钩、不同字义、三笔/四笔。第一批只作**待审样板**；相关词/引文未全部获权威词条核验时，不升级正式出版。随后复核复杂字 `龠(ID201,17笔)` 的跨源页采样与分页。

**附形偏旁是单独阶段**：`氵`、`亻`、`扌`等不能直接拿主字 `水/人/手` 的已审定源笔顺替代；必须经附形源、位置迁移、字形/笔序和名称的逐项资料复核。资料不够时明确停在 `blocked`，不伪造。

## 3. 数据契约、验收与不允许的捷径

- 程序输入：源PDF + manifest + `data/B01-B21.json` + `data/teaching-source-policy.json` + **编辑审核 JSON** + 独立插图资产。运行环境和版本固定。
- `editorial_status`：`draft` / `source_verified` / `reviewed` / `blocked`；`source_verified` 专指已有发布信息的复用，**不等于**词语/古诗/插图已审。记录 `review_evidence` 的可访问 URL/版本/页码及审核日期。
- 词条每项：`hanzi`、`pinyin_display`、`pinyin_orthographic`、`dictionary_source`、`status`；无依据的词项只允许出现在明显标注的审稿样张，绝不准正式发行。
- 每个源笔顺步骤：`main_id, source_pdf_sha256, source_page, source_crop_rect, step_index, stroke_name_status`，总数必须等于原数据声明笔画数，不能把一个折笔拆成两项。
- 字词、短句、图：分别检查复用（精确文本与接近重复）。多音字、轻声、变调、儿化和方言差异按实际词义/规范单独复核。
- 正式版中凡含“笔顺”教学图的 PDF 只能从原发布 PDF 真实剪裁矢量步骤生成；AI 图可做**非教学插图**，不得有任何机会进入笔顺图或替换范字。
- 不能以 201 个单字已上线推断已覆盖 201 个附形偏旁或每个字的全部规范拼音。

## 4. 当前推进状态（持续更新）

- [x] P0 源文件 SHA256、299 页、目标水/山/月/木官方书签索引与源图 86pt 版式抽样完成。
- [x] P0 严格 201 ID 全量源图审计脚本及 CI 完成（1045 笔、258 个教学页、原 86pt 裁剪框逐页对齐）。
- [x] P1 可运行 A4 草稿生成器、四字样板（**水 ID077、山 ID039、月 ID088、木 ID064**）及 source-step provenance；每幅示范直接复制正式 PDF 矢量（15/15 幅通过像素差异门槛）。
- [x] P1 **技术图册**实现 31mm 源笔顺格、每页最多3行×5列、长字续页，201项1045笔202页、龠17笔按15+2连续分页均通过原PDF比对；**未**与文化正文融合，四字文化页生成器仍故意拒绝 >4 笔（正式文化排版见 Issue #191）。
- [~] P2 首批引文已修正《论语·雍也》原文顺序；**36处词语使用/35不同词，19词取得教育部门词典直接词条、16词缺少直接词条、1处跨地区读音冲突（月亮）**。此为台湾词典辅助证据，不代表中国大陆发布已审核。详见 [P2/P3审计](../reviews/cultural-edition/P2-P3-source-art-20261024.md) 与 Issue #189。
- [~] P3 **四幅独立的非教学矢量插图草稿**已按水流/山峦/月下屋檐/古木主题分别实现，source Git Blob SHA 锁定、离线渲染及可见差异验证通过，另存4页PDF草稿；**最终美术审定和201字插画仍未完成**。详见 [P3原SVG注册](../data/cultural_edition/p3_artwork_draft_registry.json) 与 Issue #190。
- [~] P4 **5～17笔主字文化版分页引擎已完成首轮实测**：田5笔1页、鼻14笔2页（6+8）、龠17笔2页（6+11），真实文化内容与原PDF矢量36步统一排版；全201字内容及附形审核仍未完成，详见 [P4 QA](../reviews/cultural-edition/P4-multipage-source-QA-20261024.md) 与 Issue #191。
- [ ] P5 全量版式/字体/文字/拼音/插图及打印质检。
- [ ] P6 明确审定后独立发行；旧版保持不可变。

## 5. 操作与交付约束

- 先在独立 feature 分支提交计划与源引擎/草稿，建立 PR；用户能通过 PR 审核样板与 provenance。
- 先输出可运行的**草稿 PDF 和源信息表**，一旦校验失败即报告，绝不通过剪裁错误或替换图像绕过门禁。
- 新工程只能**新增** `scripts/cultural_edition_*.py`、`data/cultural_edition/`、`deliverables/drafts/cultural-v0.1/`、`reviews/cultural-edition/`、单独 CI；不得改变旧正式 PDF、其 SHA、manifest 的既有条目或线上练习与动画逻辑。
- 当次实现结尾明确写出**完成了哪一阶段**和哪些仍阻塞，绝不以一份 P1 草稿宣称已完成全书。


### P0/P1 第一批实测与文件（2026-10-24）

- [生成器](../scripts/build_cultural_sample.py)｜[201 ID 全量审计](../scripts/cultural_source_audit.py)｜[独立源图QA](../scripts/test_cultural_sample.py)｜[首批内容数据](../data/cultural_edition/first_batch_draft.json)。
- [四字 PDF 待审草稿](../deliverables/drafts/cultural-v0.1/cultural-4-character-source-locked-DRAFT.pdf)｜[逐幅原图溯源](../deliverables/drafts/cultural-v0.1/source-provenance.json)｜[QA 摘要](../deliverables/drafts/cultural-v0.1/qa-summary.json)。
- GitHub Actions [Cultural PDF source-locked preview #40054585895](https://github.com/netplus/zitie/actions/runs/40054585895) **completed/success**，源 PDF SHA 匹配、201项1045笔258教学页全通过，4页15幅原图逐一对照均通过（平均RGB通道误差3.6/255、最大4.815/255，允许字体缩放引入轻微抗锯齿差异）。
- 源 PDF 有部分主项**不单列拼音或明确未审核**；不能把无注音附形当成已审定单字拼音。词语注音、古文引文、最终独特插画还未获得P2/P3正式审定，新草稿页脚明确标“待审”；**整本新书尚未构建或发布**。

### P1 全201字长字续页检验（2026-10-24）

- 已由[完整技术图册生成器](../scripts/build_cultural_stroke_atlas.py)和[源图测试](../scripts/test_cultural_stroke_atlas.py)验证：**201主字、1045步、202张A4技术图册**；每个笔顺图边长 **31mm**，最多5列×3行。
- [完整201字笔顺技术图册（只作工程核验，202页）](../deliverables/drafts/cultural-v0.1/stroke-source-atlas-201-TECHNICAL.pdf)、[逐步源PDF页码及矩形映射](../deliverables/drafts/cultural-v0.1/atlas-source-provenance.json)、[独立QA数据](../deliverables/drafts/cultural-v0.1/atlas-qa-summary.json)。
- **龠(ID201) 17笔**按第一张15笔＋续张2笔分行与分页，所有原PDF步骤次序、笔画名、源图矩形完全匹配。33幅风险源步重新栅格化校验最大通道误差3.185/255。
- [GitHub Actions #40054959004](https://github.com/netplus/zitie/actions/runs/40054959004) 为 completed/success。文化阅读页面的长字分页整合仍列 [Issue #191](https://github.com/netplus/zitie/issues/191)，不能将技术 atlas 冒称完整文化版。
- 两份新增PDF均按仓库强制归档机制在 `deliverables/manifest.json` **仅追加** `status=draft`、`release_eligible=false`、源生成提交/页数/字节/hash 和 [P1审核记录](../reviews/cultural-edition/P1-source-preview-20261024.md)；历史文件及manifest条目字节不变。

### 已登记后续任务

- [P2 权威词音与经典引文审校 #189](https://github.com/netplus/zitie/issues/189)
- [P3 逐字主题插画授权与全局去重 #190](https://github.com/netplus/zitie/issues/190)
- [P4 将长字真实笔顺融入文化页而不是只做 atlas #191](https://github.com/netplus/zitie/issues/191)
- [P5/P6 全书候选及发布验收 #192](https://github.com/netplus/zitie/issues/192)

### P1 可重复构建及归档门禁（2026-10-24）

- 使用 ReportLab `invariant=1` 与 PyMuPDF `no_new_id=True` 保证字节级可重复生成；CI 连续构建两遍样稿和完整 atlas，使用 `cmp` 证明完全一致。
- 生成器发生改变时，GitHub Actions 仅针对这两个 **draft** 归档条目自动同步 `sha256/bytes/pages/source_commit`（`status=draft`, `release_eligible=false` 强校验），绝不更改已发行历史条目；示范页与书签冻结源依旧为 v0.5.1 原 299 页。
- 完成新数据后的四字样本已自动更新：《论语》山字引文纠正为“**知者乐水，仁者乐山**”，其余引文附首轮来源 URL 但人工审定仍 pending。首轮 P2 来源见 [核对记录](../reviews/cultural-edition/P2-first-batch-quotes-initial-20261024.md)。
- 最新稳定草稿实际哈希：`cultural-4-character-source-locked-DRAFT.pdf` = `8b30ae365472e51190739131f9edc4ad60e2573908a234aed3c5fa6378f31d04`；`stroke-source-atlas-201-TECHNICAL.pdf` = `6224bbfef4d42b1f9953b5b64a72b5fda0065767a55b553ed10f19b11e328b51`，并已与manifest两条草稿记录匹配。来源提交标记为 `a5f8d0b3138bcdd7878875523664177f6437b426`。
- [CI #40055521161](https://github.com/netplus/zitie/actions/runs/40055521161) 完成两次比对和原PDF独立来源对照（completed/success）。合并前仍需 `Book integrity checks` 直接从最终 HEAD 成功执行，防止任何未登记PDF污染正式repo。

### P4 文化阅读页长笔顺分页实测（2026-10-24）

- **以前的202页笔顺技术图册已经能够分页，但不含实际文化内容**。本次 [5页文化版草稿](../deliverables/drafts/cultural-v0.2/cultural-5-14-17-stroke-P4-DRAFT.pdf) 将题句、字义、引文槽位、原PDF笔顺提示、相关词、文学短句、源PDF笔顺原图与正式续页放到同一版式。
- [P4编辑数据](../data/cultural_edition/p4_multipage_prototypes.json) — 田ID106（5笔）、鼻ID200（14笔）、龠ID201（17笔）。每字先6个源步放在2行×3列中，其余按每页最多3行×5列；**31mm**不缩小，不漏笔，跨页编号连续。
- [源图排版生成器](../scripts/build_cultural_multipage.py) + [逐幅真实PDF对照测试](../scripts/test_cultural_multipage.py)；[CI记录](https://github.com/netplus/zitie/actions/runs/40066375728) success，**5页共36幅原PDF步骤**全部原文位置/笔序及像素渲染通过，最大 RGB绝对误差平均值6.3425/255；双次构建PDF byte-identical。
- 实际PDF、[provenance](../deliverables/drafts/cultural-v0.2/page-provenance.json)、[QA摘要](../deliverables/drafts/cultural-v0.2/qa-summary.json)已在 `deliverables/manifest.json` 中仅以 `draft/release_eligible=false` 登记；生成文件与哈希独立同步，不影响历史已发行版。人工看样后修复了笔顺提示孤立标点和主题占位图说明重叠。
- `龠`原正式PDF未单列可信读音，仍打印“读音待审核”，后续只能用适用的中国大陆权威词典与正式审核补足；不自动抄外部词典音标。相关词拼音/经典目前仍待权威复核，插图仍属 P4 占位。
- P2 新增[有来源的辅助核对记录](../data/cultural_edition/p2_lexicon_secondary_20261024.json)（水果、木头、田野、鼻子、龠），区分“鼻子”的具体词义，**非大陆权威出版签核**；见 [P2审核说明](../reviews/cultural-edition/P2-secondary-lexicon-20261024.md)。
- 仍待：将生成器推广到全部201条目的真正文化文案、每字唯一的正式主题插图、词音/引文审核、附形专属来源，最终按 P5/P6 页页审核。

### P2/P3 字词与独立插图首批落地（2026-10-24）

- [36词语使用位置与词典来源覆盖表](../deliverables/drafts/cultural-v0.3/p2-evidence-coverage.json)：共35个不同词，19个有台湾教育部直接词条，另16个无直接词条，**“月亮”存在 `yuè liang` vs `yuè liàng` 差异**。外部“龠 yuè”词典字条仍不能提升为原PDF已审单字拼音。 [P2源数据](../data/cultural_edition/p2_direct_lexicon_evidence_20261024.json) 与 [自动反向门禁](../scripts/cultural_p2_source_audit.py) 明确阻止未经大陆规范审核的词音升级；词条不能用自动拼音代替人工核验。
- [四字独立插图 P3 待审PDF](../deliverables/drafts/cultural-v0.3/cultural-4-unique-artwork-P3-DRAFT.pdf) 将水、山、月、木四个分别原创矢量 SVG 嵌入原有文化版，**15幅笔顺仍取 v0.5.1 正式PDF，不进入插图渲染器**。四种主题取水纹河石、云峰古松、月照屋檐、古木根叶；每张图都是独立源SVG。
- [P3画面差异验证](../deliverables/drafts/cultural-v0.3/p3-artwork-visual-check.json)：不同字的右上角图像，两两 PDF 实际画面差异均大于21 RGB/255，四个源文件SHA互异；不使用外部图片/脚本或补全未审写字轨迹。
- GitHub Actions [#40085682283](https://github.com/netplus/zitie/actions/runs/40085682283) **completed/success**：P2 审计、原P1四字PDF**字节完全不变**、新P3四字PDF重新构建一致、源笔顺15张一致、四幅画面差异和安全检查通过。新增PDF仅登记为 `draft/release_eligible=false`，其他历史 PDF 不覆盖。
- 仍待：词音中国大陆适用权威来源+人工签核、首次题材图审美/版权签核、全部201字独特画面与语义去重、附形偏旁真实教学源、P5全书页级视觉校验。

### P2 中国大陆考试词汇旁证与201字总账（2026-10-24）

- [21批201字编辑总账](../reviews/cultural-edition/P2-mainland-exam-coverage-20261024.md)已建立；4个P1字＋3个P4字有文化阅读草稿，其余**194字未开始正文写作**，4幅独立插图均未通过正式美术审核，绝不能将源笔顺核定状态推广成内容审定状态。
- [HSK 中国大陆教学词表](../data/cultural_edition/p2_mainland_exam_evidence_20261024.json)证实候选“月亮” `yuèliang`、“水果” `shuǐguǒ` 在考试词表出现；这是**教学依据而非词典出版审音**。台湾词典“月亮 `yuè liàng`”差异仍待编辑判定，未篡改样板。
- [现行GB/T 16159—2012](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=5645BD8DB9D8D73053AD3A2397E15E74)第7.1条允许儿童识字读物按字注音，符合我们拼音在汉字上方的排版；语音本身仍须逐词权威校验。
- [源数据/P2失败即阻断审核器](../scripts/cultural_editorial_coverage.py)为每个 ID 核查旧 B01-B21 源身份、无遗漏/重复、未经批准不得发布；项目仍按 draft 推进。


### P2 B01 九字编辑候选与分层状态（2026-10-25）

- [九字编辑卡](../data/cultural_edition/p2_b01_editorial_briefs_20261025.json)：B01排除已出P1样板的山，对其余**一/十/人/八/大/工/土/口/巾**加入9个独有主题、36个未核词音、9份互异艺术创作说明。并**未**生成这九字的文化页或美术文件；“一”字变调、书面注音与轻声须独立审核，任何候选拼音不得升为正式出版。
- [B01独立失败即阻断审计](../scripts/cultural_b01_editorial_audit.py)、[负面测试](../scripts/test_cultural_b01_editorial_audit.py)、[详查记录](../reviews/cultural-edition/P2-B01-editorial-briefs-20261025.md)并入原201字覆盖工作流。状态数应明确分层：**16字有内容草稿，仍仅7字有文化版PDF样本，185字尚无内容草稿，194字尚无PDF样本；正式批准=0**。
- 以上不触碰原 v0.5.1 299页字帖、A3动画、旧版已发行记录与其它候选PDF；下一步按 [#189](https://github.com/netplus/zitie/issues/189) 补大陆权威词条与P2审核，[#190](https://github.com/netplus/zitie/issues/190) 将9张视觉构想转为带授权和人工复核的差异化艺术资产，再按P4/P5生成真正阅读页。


### P4 B01 1～3笔真实源图样张与 P2 大陆证据（2026-10-25）

- 前次P2初稿[PR #196](https://github.com/netplus/zitie/pull/196)已合并：九字文字编辑卡完成但先前**0页PDF**。现新增[独立B01文化页生成器](../scripts/build_cultural_b01_preview.py)、[全22步骤原PDF独立像素复核](../scripts/test_cultural_b01_preview.py)与[Actions出图工作流](../.github/workflows/cultural-b01-preview.yml)，目标**一/十/人/八/大/工/土/口/巾 9字、9张A4技术样张、22笔**。源图真实剪裁，不自行生成笔顺，主字拼音只复用原PDF已印字段，练字原版和动画不改。此为技术生成与测试流程，**不得在CI跑完之前宣称样张已经通过完整验证**。
- [大陆教育词表3条直接行](../data/cultural_edition/p2_b01_mainland_education_evidence_20261025.json)：土地、土壤、口水；另据教育部平台及 GB/T 16159—2012明确区分“一”字单字本调、词组语流变调、词语正词法与儿童逐字注音。**全部未获出版审校批准**，已添加反向审计；没有词条的其余33个候选继续待审。
- 9张右上主题画只提供独立、语义相关的工程构图占位，不属于完成的P3正式插图；需人工审美复核、授权和全局视觉去重，详见[项目记录](../reviews/cultural-edition/P4-B01-nine-original-source-previews-20261025.md)。
- 稿件覆盖统计按阶段分别记录：**16个字已有文化文字草稿、7个字已经在仓库有文化PDF样本**；新增九字样本只有CI生成后才可称为候选草稿PDF（合计16项），此前发布的文化字帖页数依然0。即使CI成功，194/185的原统计也需注明是“尚无既有PDF页”或“尚无文字草稿”，**禁止把技术样稿算正式出版**。

### P4 B01 九字文化工程PDF样张已完成并归档（2026-10-25）

- B01除既有山字以外的 **一/十/人/八/大/工/土/口/巾** 共9页技术PDF已由 GitHub Actions 实际生成。严格沿用正式v0.5.1的**22幅原逐步累计笔顺图**和原PDF的范字与单字拼音；原PDF/manifest历史记录和动画均不修改。逐图相似度测量最高RGB MAE 3.4054/255，所有九页的源页、笔名、序号均核对，二次构建字节相同。
- 完整人工浏览缩略图后修正“一”字大范字原裁剪图失真，今后必须按原始宽高比缩放；新增回归检查。当前[9页候选PDF](../deliverables/drafts/cultural-v0.4/B01-9-character-source-locked-UNREVIEWED.pdf)及[溯源报告](../deliverables/drafts/cultural-v0.4/B01-original-source-step-provenance.json)、[QA结果](../deliverables/drafts/cultural-v0.4/B01-source-pixel-qa.json)已经仅以`draft/release_eligible=false`、追加登记方式归档。MD5/SHA不得以重复编译外观来替代原始SHA256核验。
- 分层统计现为：**16/201** 个字已有未审文化PDF工程样稿（早先7+新增9），**185/201** 尚无文化正文；正式审校批准/新文化正式发布仍为**0**。9份示意构图不是最终P3插图，36条词语/读音仍待中国大陆词典、教学规范及专业人审。版式与资产全书 P5/P6 均未完成。
