# 文化识字版 P2/P3 词音证据与专属插画源稿（2026-10-24）

**当前是 `draft`，没有中国大陆规范拼音的最终出版审核，也没有正式美术审批。不得将 CI 完成等同于内容审定。**

## P2：可核对的词条，不是自动拼音

- [首批+P4共36处词语使用位置](../../data/cultural_edition/first_batch_draft.json)与 [P4审稿内容](../../data/cultural_edition/p4_multipage_prototypes.json)；同一词“水田”在两页出现，因此只有35个不同词。
- 新建 [20条真实词典记录](../../data/cultural_edition/p2_direct_lexicon_evidence_20261024.json)：其中**19个直接词条**，外加“龠”**一个字条旁证（不是词条）**。来源为台湾教育部《国语辞典简编本》与《重编国语辞典修订本》，页面均带独立词条ID和汉语拼音。不是对中国大陆适用规范的裁决。
- [自动审计器](../../scripts/cultural_p2_source_audit.py)与 [负面回归用例](../../scripts/test_cultural_p2_source_audit.py)输出实际覆盖情况，重复词按全部使用页核验；无来源的词仍标“待查”，**不能用两个单字的拼音拼凑出“权威词语拼音”**。
- 特别的跨区域读音差异：**“月亮”当前样稿 `yuè liang`，台湾教育部词条标 `yuè liàng`**，见[原词条](https://dict.concised.moe.edu.tw/dictView.jsp?ID=44596&la=0&powerMode=0)。不能把两者直接判成错字，而应等待大陆版适用审音词典和人工核对。自动审计必须明确标记为冲突。
- 轻声与义项：木头 `mù tou`（[词条](https://dict.concised.moe.edu.tw/dictView.jsp?ID=5001&la=0&powerMode=0)）；“鼻子”指嗅觉器官时 `bí zi`，作古义“初生儿”时 `bí zǐ`（[完整词条](https://dict.revised.moe.edu.tw/dictView.jsp?ID=17461&la=0&powerMode=0)）。必须保留语义分支。
- “龠”的外部 `yuè` 字条[可查](https://dict.revised.moe.edu.tw/dictView.jsp?ID=11771&la=0&powerMode=0)，但旧正式 v0.5.1 PDF **未收录可显示的已采用拼音**，因此新稿暂不单列音。
- 严格区分**上方逐字教学注音**与 **GB/T 16159—2012 以词为基本单位的汉语拼音正词法**，见[国家教育部原规范](https://www.moe.gov.cn/ewebeditor/uploadfile/2015/01/13/20150113091717604.pdf)。现有审稿内容没有擅自改变任何原版单字拼音。
- [教育部对国家语委字典网上服务的历史说明](https://www.moe.gov.cn/moe_879/moe_1252/s8447/201412/t20141204_179571.html)不能充当目前仍有效的直接词条链接；正式大陆规范词音核验任务继续保留在 [Issue #189](https://github.com/netplus/zitie/issues/189)。

## P3：四幅独立主字意象的可编辑原生矢量源稿

| 主字 | 画面主题 | 本次原创矢量源文件 | 主要意象 |
|---|---|---|---|
| 水 | 河谷清流 | [river-current.svg](../../data/cultural_edition/artwork/drafts/river-current.svg) | 河道、水纹、石岸、岸草 |
| 山 | 高岭云岚 | [peaks-and-clouds.svg](../../data/cultural_edition/artwork/drafts/peaks-and-clouds.svg) | 三重峰脊、云岚、古松 |
| 月 | 月照屋檐 | [moon-over-rooftops.svg](../../data/cultural_edition/artwork/drafts/moon-over-rooftops.svg) | 圆月、屋檐、水巷倒影 |
| 木 | 古木春生 | [seasonal-rooted-tree.svg](../../data/cultural_edition/artwork/drafts/seasonal-rooted-tree.svg) | 根、树干、树冠、嫩叶 |

- 源稿登记在 [P3原图注册表](../../data/cultural_edition/p3_artwork_draft_registry.json)，每图使用唯一 `asset_id`、`theme_key`、Git Blob SHA、语义标签、替代文本和待审状态。可审源SVG比“复用同一张背景图改颜色”更容易查重。
- [P3绘制与来源安全验证](../../scripts/cultural_p3_artwork.py)仅接收离线 SVG 画线/填色节点；禁止脚本、外链图片、字体下载、任意文本覆盖。它只画右上方文化氛围，**绝不代替源PDF笔顺图和原版主字轮廓**。
- [四字PDF接入生成器](../../scripts/build_cultural_p3_preview.py)复用 P1 的四页正文与已发布 PDF 裁剪步骤，只替换独有文化主题图。 [P3质量脚本](../../scripts/test_cultural_p3_artwork.py)检查原样稿不变、4幅艺术主题唯一、实际 PDF 裁剪画面间有可见差异、可重新生成。
- 这四幅是工程源稿，不是已经通过终稿审美的水墨美术。它们必须经过用户对**笔触、留白、主题关联、儿童阅读体验**的复核。不能把通过程序查重当成美学认可。涉及全部201字的去重、版权、主题句与短句质量还需要P3下一阶段推进（[Issue #190](https://github.com/netplus/zitie/issues/190)）。

## 本轮准入准则

1. 原 v0.5.1 PDF 的201字1045笔源图/原字形、现有练习网页版、299页原书和所有历史 `released` 记录不变。
2. 如果绘画源SHA变化或画面与字错配、PDF原笔顺发生改变、跨地区读音差异被隐藏，CI 必须失败。
3. 此次新增四页 P3 PDF 只能是 `deliverables/drafts/cultural-v0.3/` 下 **draft / release_eligible=false**，不得替代已批准正式版本。
4. 最终词音和古籍引用只在具备大陆适用权威资料、逐项语义和人工签核后才可升级为 reviewed。

## P2/P3 已运行的质量门槛结果（2026-10-24）

- CI [Cultural P2 evidence and P3 distinct art proofs #40085682283](https://github.com/netplus/zitie/actions/runs/40085682283) **completed/success**；旧 P1 四字PDF重新生成 SHA 未变；新P3样稿两次字节级重建相等，四页15幅原PDF真实笔顺源图均一致。
- P2审计报告：[35个不同词、19个直接词条、16个仍待直接资料、1个明确冲突](../../deliverables/drafts/cultural-v0.3/p2-evidence-coverage.json)。没有一个词可以由本审计自动提升为大陆正式规范读音。
- P3审计报告：[SVG源哈希、场景ID及PDF右上角图像差异](../../deliverables/drafts/cultural-v0.3/p3-artwork-visual-check.json)：4幅源SVG互不相同、最小两图平均RGB绝对差异 **22.885/255**，确保不是直接复制同图；但图像相似度算法通过仍不代表人工美术审查。
- [P3原图 PDF](../../deliverables/drafts/cultural-v0.3/cultural-4-unique-artwork-P3-DRAFT.pdf) 在 `deliverables/manifest.json` 中 `status=draft, release_eligible=false`，原 v0.5.1 299页发布PDF及现有动画无改动。
