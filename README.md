## 文化识字版新书重建（实施中，非正式发行）

按已确定的新版式（主题句+专属图、主字上方原书已核拼音、字义/经典、**笔顺提示先于笔顺**、源PDF逐笔累计步骤、相关词上方拼音、一字一句，**无练习格**）开始独立重建。已提交 [执行计划](docs/CULTURAL_EDITION_REBUILD_PLAN.md)、[全量201字源图审计](scripts/cultural_source_audit.py)、[首批四字待审 PDF](deliverables/drafts/cultural-v0.1/cultural-4-character-source-locked-DRAFT.pdf) 与 [逐幅溯源 QA](deliverables/drafts/cultural-v0.1/qa-summary.json)。**这只是四字 P1 排版草稿**：词语拼音、古文引文和正式插图仍待审核，复杂字跨页与剩余字项还未完成；不替换旧 v0.5.1 299 页正式发行版。

---

## 在线字帖打印 · A4 自定义排版（P3）

[在线打印页面](animation/print/index.html)：支持汉字、字母、数字、拼音四类练习，田字格／米字格／方框格／四线三格，方格尺寸10–25 mm，按A4实时预览、调节行列间距、描红方式与颜色并使用浏览器打印或保存PDF（推荐默认15 mm、10格/行）。201主部首使用正式v0.5.1 PDF同源矢量；未收录汉字明确提示系统字体回退，拼音沿用已有分源数据，不声称均获得教学认证。新增可选的「打印逐笔笔顺示范」（默认勾选，可手动取消，限已有原版201字的源矢量；当前笔红、此前笔灰，复杂字完整分页；未收录字只显示明确提示），不捏造笔画顺序。纯本机处理，无第三方字体/CDN；不触碰v0.5.1正式PDF与v0.6.0候选版，详见 [设计与测试](docs/ONLINE_PRINT_STUDIO.md)。

---

## A3.8：写字时实时可见“笔压风格”（已上线）

[201字毛笔播放器](animation/book.html)的笔压栏从播放器下方重新布局到字格附近：宽屏与字格并排、手机在字格上方并保持滚动可见，因此可以在写字时观察当前模拟力度和曲线。**A3.8 已上线（2026-10-11）**：[布局 PR #132](https://github.com/netplus/zitie/pull/132) 与 [1020px 画布宽度修复 PR #133](https://github.com/netplus/zitie/pull/133) 均已合入；最终 `main` SHA [`f4ae83e`](https://github.com/netplus/zitie/commit/f4ae83e338cff68bc9460d3f0eacfaef919d949a) 的 [A1 Chromium](https://github.com/netplus/zitie/actions/runs/38145041178)、[Book](https://github.com/netplus/zitie/actions/runs/38145041109) 及 [Pages 实际 Deploy](https://github.com/netplus/zitie/actions/runs/38145041123) 均成功。保留稳定版默认、模拟力度非实测、SVG源墨迹/笔顺及A3.6防超前算法不变。参见 [布局设计、多视口测试与发布记录](docs/A38_PRESSURE_VISIBLE_LAYOUT.md)。

---

## A3.7：恢复201字主播放器的稳定版 / 模拟笔压版（已上线）

用户指出截图中的「笔压风格　稳定版｜模拟笔压版」在 A3 完整201字界面消失。已在 `animation/book.html` 和 `book-ui.js` 接回原 A1.6 压力控制器，默认稳定版，模拟版恢复笔尖圆环、百分比、接触阶段与曲线。**不修改原始墨迹、笔速、1045笔前缘屏障、PDF、规范数据或旧九字实验。** 新增全201字/1045笔模型完整性及真实Chromium两档切换/12帧等墨迹/390px测试，**A3.7 已上线（2026-10-11）。** [PR #129](https://github.com/netplus/zitie/pull/129) 最终 HEAD `2252d3de3df7ef9f9aa1eec3deb5d21572d52b5b` 的 [A1/Chromium CI #38138069650](https://github.com/netplus/zitie/actions/runs/38138069650) 与 [Book CI #38138069687](https://github.com/netplus/zitie/actions/runs/38138069687) 双 completed/success；合并 `main` SHA 为 `e8b4b8adefcf2381e8b0ed9a2fcd701794280c93`，对应的 [Pages #38138652608](https://github.com/netplus/zitie/actions/runs/38138652608) Configure、Upload、实际 Deploy 全 completed/success。**201字/1045笔**均生成模拟笔压曲线，14个细笔名受限主项不泄漏，12组真实 Chromium 稳定/模拟模式红墨光栅 **0 像素差异**，力环与当前笔尖100%对齐，风格切换不改变进度、倍率、播放、笔顺或源SVG墨迹；390px手机视口通过，A3.6原2090帧防超前回归不受影响。 [真实稳定/模拟截图与 QA metrics artifact #11702002988](https://github.com/netplus/zitie/actions/runs/38138069650/artifacts/11702002988)。[正式201字播放器](https://netplus.github.io/zitie/animation/book.html?id=77) 可直接使用。**模拟力值不是实测笔压，仅影响笔尖和提示，不改变墨迹宽度。**详见 [回归与修复说明](docs/A37_PRESSURE_STYLE_RESTORE.md)、[Issue #128](https://github.com/netplus/zitie/issues/128)。

---

## A3.6 201字墨迹前缘与笔尖同步（已发布）

针对水等字的提前填墨问题，在原PDF矢量和原圆头并集上新增按源中线行程开放墨迹区域的剪裁，目标是**墨迹不能跑到笔尖前面**。已建立1045笔几何守卫及真实Chromium全201字逐笔/逐帧质量门槛。详见 [算法审计](docs/A36_INK_FRONT_AUDIT.md)、[Issue #125](https://github.com/netplus/zitie/issues/125)。最终CI与Pages均已实际完成验证，不改任何v0.5.1 PDF或规范笔顺数据。

**A3.6 已上线（2026-10-11）。** [PR #126](https://github.com/netplus/zitie/pull/126) 最终精确 HEAD `d410e398c6d94bfcd7d309cdd58372ff542ac2d1` 的 [A1 Chromium #38134493046](https://github.com/netplus/zitie/actions/runs/38134493046) 与 [Book integrity #38134493075](https://github.com/netplus/zitie/actions/runs/38134493075) 均 completed/success；合并 `main` 提交 `ea4a76e868cf9f9dbe3469fc0028604d4b5265b8` 对应的 [Pages #38135010764](https://github.com/netplus/zitie/actions/runs/38135010764) Configure、Upload、实际 Deploy 全 completed/success。

实测：**201 个字、1045 个笔画**全部有有效 source-arc 前缘守卫；**每笔两个 Chromium 像素帧，2090/2090 帧**，所有1045笔都显墨且笔内红墨回退为 **0 像素**，任一后续中线红墨领先 **超过12 SVG单位的帧为0**（所采样最大领先12单位）；另 **201字495帧**（31个高风险字加密），**水四笔16帧**、A3.5 A/B两时序40帧均合格，390px手机视口合格，旧 A3/A3.5 原始笔迹回归继续成功。 [截图及完整metrics artifact #11700378299](https://github.com/netplus/zitie/actions/runs/38134493046/artifacts/11700378299)。

根因与修复：旧宽圆头在折角附近会在未来中线上提前显墨；首次复合动态clipPath虽能限制前缘却导致Chromium抗锯齿重算时2—12已绘红像素消失，单纯加约3 SVG单位边缘重叠仍不够。**最终方案是每个已到达的Voronoi显墨区保留为独立红色SVG元素，在同一静态原轮廓clipPath及旧圆头alpha-mask内叠加**，不再反复修改复合裁剪轮廓。旧9字历史回归保持原渲染以便复现，A3默认201字及A3.5左右侧采用修复版；PDF的字形、笔顺、原median、计时、许可和299页正文均未修改。

边界：这是**采样位置与阈值内的工程验证**，不等于真实毛笔接触面每个边缘绝对不超前，也不代表运动学/书法教师已认可；A3.5新节奏仍只可选，硬笔仍冻结。

---

## A3.5：毛笔运笔自然度（独立 A/B 研究已上线）

在正式[201字毛笔动画](animation/book.html)保持默认不变的条件下，新增[起笔/折钩/收笔运笔A/B研究页](animation/experiments/brush-motion-lab.html)与[模型说明](docs/A35_BRUSH_MOTION_AB.md)。A与B同源于正式 v0.5.1 的1045笔，使用完全相同的SVG轮廓与原毛笔墨迹并集；B只对已核笔画名称和可信的中线转角施加有界、单调的时间重参数化。该模型属于未教学审定的工程启发，不代表实测运笔数据。实际独立研究版 [A3.5 201字 A/B](https://netplus.github.io/zitie/animation/experiments/brush-motion-lab.html) 已上线：[PR #123](https://github.com/netplus/zitie/pull/123) 最终 HEAD `e7938b29725488dcf9491d143cf746391808533e` 的 [A1 Chrome #38125276874](https://github.com/netplus/zitie/actions/runs/38125276874) 与 [Book #38125276827](https://github.com/netplus/zitie/actions/runs/38125276827) 双 completed/success，合并至main SHA `0da37d5c1965a4f9d798b228de8d081263c1d81c`，其 [Pages #38125707083](https://github.com/netplus/zitie/actions/runs/38125707083) Configure、Upload和实际Deploy 全 success。**201字、1045笔**全部加载；960个有界运动候选、85个保守回退、193处来源中线角点候选事件；54对真实Chromium A/B 帧（两侧红墨不消失）、其中21对有时间运动差异，另21对相同空间位置的实际像素对照 **0 差异**，390px通过。截图/metrics见 [A1 QA artifact #11697280799](https://github.com/netplus/zitie/actions/runs/38125276874/artifacts/11697280799)。**人工审美/真实书法运笔教学审核仍待完成，绝不自动推广B为默认**；正式 [A3毛笔播放器](https://netplus.github.io/zitie/animation/book.html)、原PDF及硬笔冻结决策不变。硬笔仍冻结。

---

## A3（已上线）｜PDF同源201字毛笔笔顺

新主线 [A3 #120](https://github.com/netplus/zitie/issues/120)：默认改回毛笔，硬笔研究暂停；基于正式 v0.5.1 299页《循序渐进汉字部首字帖》及其建书输入生成201字逐笔SVG动画，建立 PDF 书签页码联动。见 [A3 技术边界](docs/A3_PDF_BRUSH_ANIMATION.md)、[201字动画入口](animation/book.html)。最终功能 PR HEAD `b66a51dd31be7d06a2fcdbccd7e106f891617997` 的 [A1 动画 CI #38122954997](https://github.com/netplus/zitie/actions/runs/38122954997) 与 [Book 完整性 CI #38122955056](https://github.com/netplus/zitie/actions/runs/38122955056) 双 completed/success；[PR #121](https://github.com/netplus/zitie/pull/121) 合入 `main` 为 `452e79f078b3d80a515e3a2290f6489a37925760`，同一 merge SHA 的 [GitHub Pages #38123374018](https://github.com/netplus/zitie/actions/runs/38123374018) Configure、Upload、实际 Deploy 全部 completed/success。A1 83 项历史 Node 与 A3 5 项新 Node 全通过；**201 字/1045 笔/21 批次**及正式 v0.5.1 299页 PDF SHA256 `7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90` 已核对；A3 54 帧 Chromium 落墨 0 像素消失，27 帧可见笔尖，龠第17笔进入本字 PDF 第3张累计示范页，390px 适配通过。截图见 [A3 QA artifact #11696336104](https://github.com/netplus/zitie/actions/runs/38122954997/artifacts/11696336104)。[完整201字毛笔播放器](https://netplus.github.io/zitie/animation/book.html)及[只读正式 PDF](https://netplus.github.io/zitie/book/zitie-v0.5.1-A4.pdf)已发布。**这是工程动画的完整源一致性验证，未获得真人运笔轨迹的教学认证；硬笔仍冻结。**

---

## A1.4 虚拟笔尖 A/B 对照实验（独立工程路线）

依据[虚拟笔尖研究报告](docs/A1_PEN_CONTACT_RESEARCH.md)实现[独立 A/B 实验](docs/A1_PEN_CONTACT_EXPERIMENT.md)：六个真实来源部首在同一时间轴上并排比较 **A1.2.3 稳定基线** 与 **实验性椭圆接触印迹＋转锋微时序**，支持倍率按钮、进度拖动和笔内运动/接触曲线。**新实验不改变现有教学播放器、笔顺、最终轮廓或正式 PDF。** PR [#90](https://github.com/netplus/zitie/pull/90) 完成最终 CI 与部署后，可通过[独立实验网页](https://netplus.github.io/zitie/animation/experiments/pen-lab.html)观看；未完成部署前不得宣称该链接已上线。

---

## A1.4 仿真笔尖与自然运笔研究（尚未上线）

针对“起笔、落笔、折、钩衔接不像真实写字”的反馈，已开展[虚拟笔尖、运动学、汉字笔迹重建与开源实现研究](docs/A1_PEN_CONTACT_RESEARCH.md)（Issue [#88](https://github.com/netplus/zitie/issues/88)）。研究的核心结论是：现有 A1.2.3 保证源码轮廓内的墨迹递增，但缺少笔尖接触力度、朝向、笔锋印迹和不同动作语义。后续先建立与现有播放器隔离的对照实验，再决定是否切换正式预览；**当前在线动画、201个主部首与 v0.5.1 PDF 不变**。

---

# A1.2.3 笔迹填充异常治理（工程预览）

针对在线动画填充出现的异常，新的[几何审计与修复方案](docs/A1_FILL_AUDIT.md)取代过去可能自交的四边形遮罩：使用原始笔顺中心线上的独立圆角笔触累积，并与原始笔画轮廓严格相交，取消收笔处突然扩张的圆形补丁。新增逐像素的“已写墨迹不可消失”检查、局部游离片段检测、收笔跳变定量复核；最终以 [PR #87](https://github.com/netplus/zitie/pull/87) 的目标HEAD CI/合入/Pages部署为准。原始 PDF 与规范数据不受影响。

---

# A1.2.2 位置自适应笔速与按钮速度（工程预览）

根据最新线上反馈，新增[运动学启发的笔内动态笔速](docs/A1_MOTION.md)：起笔渐快、转折局部减速、直行恢复速度、收笔渐慢，保持原笔顺、笔画中心线、最终矢量轮廓和统一播放时间轴不变。播放倍率由原下拉框改为**0.5×/1×/1.5×/2×/3× 直接点击按钮**；笔迹遮罩采样和笔尖边缘也进一步精细化。该速度分布是工程教学启发式而非采集到的真人笔速或笔压。追踪 [Issue #84](https://github.com/netplus/zitie/issues/84)，必须通过最终 PR HEAD CI 后再上线。

---

# A1.2.1 在线交互改进（工程预览）

根据线上反馈，**已实现可搜索字形卡片＋批次筛选**，取代原生下拉选字；动画以原轮廓宽度为依据生成沿笔顺中心线推进的局部 SVG 遮罩，降低固定粗画刷导致的提前显露。增加可拖动时间轴及键盘操作，所有9个样例保持离线可用、原笔顺与原轮廓不变。质量门槛、尚未完成的教学审定见 [A1.2.1 实施与限制](docs/A1_UX_PRECISION.md) 和 [Issue #82](https://github.com/netplus/zitie/issues/82)。通过 PR 和最终HEAD CI 前不计正式教学验收。

---

# A1 动态笔顺工程预览（独立于 v0.5.1 正式 PDF）

**在线查看动画（GitHub Pages）：**[直接打开正式托管的工程预览](https://netplus.github.io/zitie/animation/)。Pages 已于2026-10-09通过[部署工作流 #37880818335](https://github.com/netplus/zitie/actions/runs/37880818335)成功上线；后续 `main` 动画更新自动重新部署。仍是轨迹未经独立教学核验的工程预览，参见[部署说明](docs/A1_PREVIEW.md)。

新增 A1 动画研发阶段：已归档 [9个主部首的离线 SVG 动态书写原型](animation/index.html)、[动画控制与复核说明](animation/README.md)、[A1 技术设计和独立验收门槛](docs/A1_ANIMATION.md)。可以下载仓库并在浏览器直接打开 `animation/index.html`；不会联网。**这些 medians 仅为工程预览，尚未完成独立教学轨迹审定**，已有201主部首矢量笔顺审核不能视为动画方向审核。正式 PDF 仍是 v0.5.1，历史不变。A1任务见 [Issue #79](https://github.com/netplus/zitie/issues/79)。

**[15 mm 中号田字格练习版（299页独立候选）](deliverables/drafts/v0.6.0-15mm-rc1/zitie-v0.6.0-A4-15mm-candidate.pdf)**：练习格从 21.22 mm 缩为 15 mm，每个练习区从 8×4 提升到 10×4；不改变原有笔顺示范、汉字造型或在线动画依赖的 v0.5.1 源 PDF。**此版待实物打印和教学验收，不替代当前正式版**。详见 [设计、构建与校验](docs/PRINT_GRID_15MM.md)。

---

# 循序渐进汉字部首字帖 · v0.5.1

**[最新正式版 PDF：v0.5.1（A4、299页）](deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf)** — 修正简体横排句号/顿号字格左下位置。SHA256：`7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90`。

以 v0.5.0 的Q1验收范围为依据，只对已确认的283处标点做轮廓位置微调，并同步558处版本标识；201主部首和教学内容、299页A4、238书签及50链接完全保留。规范字段未决按原fail-closed规则继续保留；实物打印未做。

- [本轮勘误证据](reviews/v051-punctuation-erratum-20261008.md)
- [发布与历史状态](docs/STATUS.md)
- [仍开放的规范来源Issue #4](https://github.com/netplus/zitie/issues/4)

## 以下为此前正式 v0.5.0 及历史阶段记录

# 循序渐进汉字部首字帖 · v0.5.0

**[正式 v0.5.0 PDF（A4，299页）](deliverables/releases/v0.5.0/zitie-v0.5.0-A4.pdf)** — 已通过 [PR #73](https://github.com/netplus/zitie/pull/73) 的最终目标 HEAD CI 并合入 `main`，正式发布生效。全书201主部首及教学比较/回忆/整字迁移，沿用已完成的Q1版式验收；保留2022来源限制。

SHA256 `10f5177221ff4817ea412f9e5f187e68d59eabfce8f94e2ebf4179f4398f6880`；可重复构建：`python scripts/build_v050_formal.py`，输入为已归档的RC3终检候选PDF（不是最初RC1生成源码）。238书签、50跳转、299页A4；推荐彩色打印，未进行实物打印测试。

[发布审计与版本来源](reviews/Q1-v0.5.0-formal-QA-20261008.md) · [当前状态](docs/STATUS.md) · [历史候选记录](reviews/Q1-acceptance-20261008.md)。以下条目均为旧阶段历史，不覆盖当前状态。

---

# 本地逐页复核成果待归档

RC2、RC3及终检文件已有逐页复核与精确来源记录；当前准备导入本地修订，不代表远端CI或正式发布完成。最新状态见[STATUS](docs/STATUS.md)，导入详情见[Q1记录](reviews/Q1-local-import-20261008.md)。原M3 RC1记录和全部旧文件保留。

## 以下为此前版本入口（历史）

# 循序渐进汉字部首字帖

## 当前交付：v0.5.0-rc1完整候选已冻结

[下载299页完整发布候选](deliverables/drafts/v0.5.0-rc1/zitie-v0.5.0-rc1.pdf)。M3已完成候选归档，当前进入独立Q1；Q1队列0/299页，不是正式v0.5.0发布。文件4,252,161字节，SHA256 `3b26fd0a85b063b83f7090f9b38735908b6e64dc763614c12f17e4f727ef556a`。

实际生成run `37707956206`成功；最终归档PR #69仍以其目标HEAD CI及合入结果为准。完整配置、字体环境、页码映射和生成记录已绑定。旧17份PDF与来源限制保持，最新正式版仍v0.4.1。

[当前状态](docs/STATUS.md) · [冻结记录](reviews/M3-candidate-freeze-20261008.md) · [Q1执行计划](docs/Q1_REVIEW.md)。以下均为各自时点的历史记录，不能覆盖上方当前状态。

## PR68实现检查点（历史）（2026-10-08）

F03六例完整整字迁移已实现并完成全模块导航/字段策略接入；F01—F05五包均已实现。内部工程预览为299页，六例迁移新增10页，全部44个整字步骤保持原时序；201主项计数不变。国的部件对应1、2、8笔，区对应1、4笔，近的辶在第5—7笔；不将非连续部件截成连续独写。新增34项迁移测试，含误用上游radStrokes、截断笔顺与越权字段检查。

这仍是内部工程预览，不是冻结候选或正式发布。M3阶段仍in_progress，下一步真实归档完整候选并绑定生成来源，再进入独立Q1。旧17份PDF、manifest及规范字段保持。详见[当前状态](docs/STATUS.md)、[本轮复核](reviews/M3-migration-integration-20261008.md)。

## PR67实现检查点（历史，2026-10-07）

F01学生/辅导者分层说明与F02六组比较/回忆已实现，内部工程预览实际288页；F03整字迁移未生成，F04导航/F05字段策略已接入当前模块但待迁移集成。五包完成2，不是M3已完成。232书签、28目录跳转、201主项逐字段呈现检查已运行；全部12个比较/回忆页实际查看。下一步实现完整整字迁移，不重复M1/M2收口。

工程预览不是冻结候选、不作为正式PDF交付；旧17份PDF及manifest不改。来源阻塞保持，Q1未开始，candidate=null、final_release_eligible=false。当前细节以[STATUS](docs/STATUS.md)和`data/m3_scope.json`为准，复核见`reviews/M3-foundation-comparison-20261007.md`。

## 既有阶段记录（本轮之前）

面向简体中文基础书写教学的 A4 部首练字工程：覆盖 **201 个主部首**，并保留常用附形、位置变体、历史 27 项回归、目录与索引等全书级检查。

## M2退出与M3启动记录（历史）

正式v0.4.1保留；M1完成。M2本周期六类来源审计已按`completed_with_source_blocks`退出，累计采用3个字段更新，本轮新增采用0项；仍有来源缺口，来源Issue #4继续open，不称全部解决。

当时进入**M3功能与教学质量增强**：冻结六组比较/回忆、六个已核整字迁移及说明/导航改进范围，并建立按字段的教学限制检查。该启动检查点尚未完成功能包，Q1未开始，无新PDF发布。

[当前状态](docs/STATUS.md) · [M2完成与残余](reviews/M2-completion-20261007.md) · [M3范围](docs/M3_SCOPE.md) · [最新正式v0.4.1 PDF](deliverables/releases/v0.4.1/B01-B21_v0.4.1_A4.pdf)

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

1. **内容覆盖**：逐字段核验 201 个主部首的身份、笔顺、细笔名、采用读音、部件名称、拼音、结构、教学提示和整字语境；
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
