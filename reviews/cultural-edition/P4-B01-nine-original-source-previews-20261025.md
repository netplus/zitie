# 文化识字版 B01 九字：原PDF真笔顺样张与语音资料分层（2026-10-25）

## 本次可交付与明确边界

**本轮是 P4 工程样张，不是文化版全书，也不是经审核的儿童正式读物。**

B01 已有 \`山(ID039)\` 的 P1 PDF 样张；本次为余下九字提供独立可运行的 9 页 A4 构建器，逐字来自 B01 的九张 P2 编辑卡：

| 序号 | 字 | 原B01主ID | 预期原PDF笔数 |
|---|---|---:|---:|
| 1 | 一 | 001 | 1 |
| 2 | 十 | 006 | 2 |
| 3 | 人 | 012 | 2 |
| 4 | 八 | 011 | 2 |
| 5 | 大 | 033 | 3 |
| 6 | 工 | 028 | 3 |
| 7 | 土 | 029 | 3 |
| 8 | 口 | 037 | 3 |
| 9 | 巾 | 040 | 3 |

总计**9页/22个原PDF逐笔矢量示范**。这里的笔数是既有 B01 来源声明，**PDF 构建必须重新从已发行299页v0.5.1 PDF审计并核验实际步骤才可通过**；不采用其他SVG、字体、AI笔画造图。

- 生成器：[\`scripts/build_cultural_b01_preview.py\`](../../scripts/build_cultural_b01_preview.py)
- 完全独立的22源图逐幅像素比对：[\`scripts/test_cultural_b01_preview.py\`](../../scripts/test_cultural_b01_preview.py)
- 专用工作流：[\`cultural-b01-preview.yml\`](../../.github/workflows/cultural-b01-preview.yml)。产物暂存 Actions 14天artifact：未审PDF、9张逐页PNG、源页/裁剪框 provenance、QA JSON、审计阻断项与全套失败即阻断测试；**已将独立的待审PDF追加归档到 `deliverables/drafts/cultural-v0.4/`，只在manifest增加 `draft/release_eligible=false` 的新条目；不写入正式发行目录、不改变历史条目**。
- 九张右上角为与字义分别关联的**向量构图示意**，仅供验证阅读页布局及与原笔顺隔离的渲染架构；还不属于P3正式插图、没有审核通过的asset ID。由稿件编辑卡单独驱动，每页不复用同一种场景。下一步需要完成真正的美术质量复核。
- 主字使用原PDF抠取真实范字图（不是重新生成教学字），左下所有1/2/3笔使用原PDF逐幅 \`show_pdf_page(clip=)\`；图上方明确先排原PDF笔顺提示。单字拼音只读取 \`pinyin_from_pdf\`，缺省则显示待核。
- 相关词显示 **36条未核拼音候选**用于审读排版，页脚明确“内容/读音待审，非正式稿”；无任何B01引文获得原典审查，一律显示“经典引文待核验”。本次没有出版批准。

## 中国大陆资料核对：三条直接教育词表旁证，非词典签核

已真实检索到汉考国际中文考试词表**精确词条行**：

| 词 | 页面行号 | 词表正词法 | 直接来源 | 验证限制 |
|---|---:|---|---|---|
| 土地 | 8156 | \`tǔdì\` | [汉考国际词表8151–8160](https://admin.chinesetest.cn/standardsAction.do?leves=&means=getStandardWordsList&pager.offset=8150&pinyin=&words=&words_type=) | 四级、名词；不是中国大陆字典义项人工签核 |
| 土壤 | 8159 | \`tǔrǎng\` | 同上 | 高等、名词；不是出版审音 |
| 口水 | 4787 | \`kǒushuǐ\` | [汉考国际词表4781–4790](https://admin.chinesetest.cn/newhsk/standardsAction.do?leves=&means=getStandardWordsList&pager.offset=4780&pinyin=&words=&words_type=) | 高等、名词；不是出版审音 |

固定证据与未批准字段：[\`p2_b01_mainland_education_evidence_20261025.json\`](../../data/cultural_edition/p2_b01_mainland_education_evidence_20261025.json)，[反向门禁](../../scripts/test_cultural_b01_mainland_education_evidence.py)。其他33条词语候选仍需逐条取得适用的大陆权威词条/教材印刷证据。已经在HSK词表找到的3条也**仍为 \`review_pending\`**，不会自动修改原P2候选的发音审批状态。

## “一”字发音及教学标注的两套字段必须分离

这里尤其要防止将字典里**单字读音 \`yī\`**、口语变调 \`yí / yì\` 和规范拼音拼写混为一谈。

- [中国大学生在线刊登的“假如‘一’字会说话”](https://dxs.moe.gov.cn/zx/a/jj/220422/1761400.shtml)（2022年《人民日报海外版》文章）明确区分字典单字本调\`yī\`与口语中可变成二/四声的语流读法。它是教学说明而非四个具体候选词的逐词审音表。
- [河南师范大学发布的 GB/T 16159—2012 正词法标准转录](https://www.htu.edu.cn/yw/2018/1008/c14029a129573/page.htm)第1.5.4条给出序数词\`第一\`为正词法写法\`dì-yī\`（有连接号），也不等于教学卡片按汉字分别标音的\`dì yī\`。第7.1条允许幼儿、低年级按字注音。
- [人民教育出版社转载的一年级教材评述](https://www.pep.com.cn/xw/zt/hd/sktbjc/bxgs/202606/t20260611_2006816.html)确认修订教材强化变调指导；但该文不提供四个具体词语的全部编辑审音结果。
- **工程编辑策略**：保留\`pinyin_display_candidate\`未审状态；另建将来需逐字核实的\`orthographic\`与\`spoken_sandhi\`，经过教材/词典证据和正式人工审核才能进入儿童正式印刷。对“一个”“一起”“第一”“一年”暂不自动改写。

## 放行门禁与需人工完成

1. 原 v0.5.1 PDF SHA256 必须为 \`7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90\`、页数299、201 ID、1045幅教学逐笔图、258个教学页；
2. B01九字对应22个步骤必须与原PDF序号、名称、源页/clip完全一致；目标最小31mm；逐幅像素归一误差严格阈值；
3. PDF **9页必须全部导出PNG**供人工看图；重复生成字节相同；不得覆盖或修改原v0.5.1/主动画/已发行物；
4. 未审的词音和引文不能因为脚本成功而获批；真实的P3插图/许可/全局审美去重尚未结束；没有专业编辑人工过目不应合并正式出版。

后续：先读 GitHub Actions QA 数值和页面实图，再改进视觉布局；通过工程门禁后仅可合并**构建能力**和证据，最终文化版本发行遵循 Issue #192 的独立放行门槛。

## P4 B01 实际构建与逐页检查（2026-10-25）

- 专用CI已完成且通过：9页 A4、22个原PDF累计笔顺、二次构建字节完全一致、原图/新图逐步独立像素对比最大RGB MAE **3.4054/255**；产物SHA256为 `148792aa78f264db869ecc66c0c79eec57e3362153627b5c71c1c82d9461158b`，大小3,366,297字节。
- 人工查看全部九页后发现并修复“一”的大字范图被强行拉伸成正方形的错误（该错误**只影响大范字，不影响原PDF笔顺**）。现在根据原图非空像素长宽比缩放到48mm范围并居中；新回归检查禁止再次形变，修复后重新查看“一”的大范字正常。
- [9页PDF待审稿](../../deliverables/drafts/cultural-v0.4/B01-9-character-source-locked-UNREVIEWED.pdf)、[原22笔逐步溯源表](../../deliverables/drafts/cultural-v0.4/B01-original-source-step-provenance.json)、[独立像素QA报告](../../deliverables/drafts/cultural-v0.4/B01-source-pixel-qa.json)均已在隔离分支归档；manifest仅追加该条草稿，`release_eligible=false`。
- 此时已拥有 **16字文化阅读工程PDF样张**（此前7字 + B01九字），不是16字获得出版许可；其余185字文化稿仍待制作。36个新相关词候选、9幅专属正式美术与引文、全部201字以及附形偏旁、P5/P6审核发布仍待开展；文化正式版发行0。
