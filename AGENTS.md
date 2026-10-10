# 当前开发阶段：A1.6 主播放器双笔压风格（2026-10-10）

用户明确要求在已部署的 `animation/index.html` 直接提供两档笔压风格：「稳定版」（默认）、「模拟笔压版」；不用离开主页面。当前实现见 `animation/pressure-style.js`、`animation/ui.js`、`docs/A1_PEN_STYLE_SELECTOR.md`、[Issue #104](https://github.com/netplus/zitie/issues/104)。压力模型仅复用 A1.5 的合成归一化力度和已标识未审定的手势，真实字形源、原稳定 A1.3 圆头墨迹、源轮廓、光学纠偏圆圈位置、按位置变速和201规范数据不动。切换风格必须不暂停、不重置时间或倍率，稳定版恢复精确原始标记。原官方 v0.5.1 PDF/manifest 不动；新增9字×5时间点45帧 Chromium 墨迹/掩码逐像素检查、Node、移动端布局及双CI门槛。仅在最终 PR HEAD 动画和 Book integrity 均 success、完成合入并核实 Pages Configure/Upload/Deploy 后称新主页面正式上线。未有真实笔压授权或标定，不能冒称实际受力。

---

# 当前接续：A1.5 稳定版合成笔压 A/B 实验已独立部署（2026-10-10）

以 `docs/STATUS.md`、`docs/A1_PRESSURE_RESEARCH.md`、`animation/README.md` 和 [Issue #101](https://github.com/netplus/zitie/issues/101) 为入口。[PR #102](https://github.com/netplus/zitie/pull/102) 已合入 `main`，GitHub Pages #38007775010 真实部署成功；独立在线实验 `animation/experiments/pressure-lab.html`。用户明确更偏好 A1.3 稳定圆头笔迹，不推广椭圆笔尖为默认。合成笔压曲线独立于速度、只改变视觉接触圈与力度图表；不能称实测、不能从笔速直接推力。CASIA-onDo/OHFC 与 DCOH-120K 有学术/非商业许可限制，未获授权时禁止下载、加入仓库、用于标定或公开训练。稳定版原SVG字形/medians/墨迹填充、v0.5.1 正式PDF/manifest/201规范数据均保持不变；下一阶段应先做人工自然度复核与数据来源合法性、设备标定，再考虑进一步模型改进。仓库修改继续采用分支、PR、最终HEAD动画与Book CI、实际Pages核实；不使用 chn-ops。

---

# 当前新增开发：A1 汉字笔顺交互动画（2026-10-09）

用户已明确授权在 v0.5.1 之后启动**独立** A1 动画阶段。先读 `docs/A1_ANIMATION.md`、`animation/README.md` 和 `docs/STATUS.md`；只在 A1 路径或必要CI中新增，不把既有发布后 PDF 维护规则理解为禁止本次经过授权的新阶段。永久保持 v0.5.1 及历史正式 PDF、manifest、规范数据/审核记录字节不变；动画轨迹与原矢量审查须分开统计，未经审定的 medians 只能是工程原型。延续 branch/PR/最终HEAD CI 合入流程，来源 #4、纸张 #77 仍独立；不使用 chn-ops。

---

# 当前接续：v0.5.1 标点勘误发布后维护（2026-10-08）

以 `docs/STATUS.md`、`data/post_release.json.current_release`、`deliverables/manifest.json` 为当前版本权威入口。最新PDF为 `deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf`，299页；SHA256 `7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90`。本补丁修复 UMingCN 横排201处“。”及82处“、”的字形左下定位。旧22份PDF的路径/原字节与来源材料保持不变；不重复重建已经关闭的 M1/M2/M3/Q1 内容。

后续仅处理明确勘误、CI维护或来源 Issue #4 的新权威逐项证据；不得以旧版2022规范发布说明解除任何字段的fail-closed限制。本次新增代码须保持字形轮廓修补为**字体子集内局部字节修改**，不改变文本内容流、间距、笔顺矢量及导航。所有正式发布以目标 HEAD CI success 且通过PR合入为门槛。禁止强推、覆盖历史、提交字体源文件/商业规范全文；该工程不使用 `chn-ops`。

## 下文保留 v0.5.0 及早期断点记录

# 当前接续：v0.5.0 已正式发布（2026-10-08）

以 `data/post_release.json`、`deliverables/manifest.json`、`docs/STATUS.md` 为当前状态依据。PR #73 的目标 HEAD CI 已通过，正式 PDF `deliverables/releases/v0.5.0/zitie-v0.5.0-A4.pdf`（299页，SHA256 `10f5177221ff4817ea412f9e5f187e68d59eabfce8f94e2ebf4179f4398f6880`）已合入 `main`；总控 #58 已关闭。

**接下来仅进行有依据的勘误、构建/CI/文档维护或来源 #4 的新证据定点复查**。不要重复 M1/M2/M3/Q1、299页逐页审读、已归档PDF入库或先前 PR 操作。没有新的适用正式规范逐项原件，不解除 `data/teaching-source-policy.json` 的 fail-closed 限制。

保持已有22份 PDF 的版本独立性与原字节；不得覆盖历史、删除 Git 记录、强推、发布原始字体或许可不明规范材料。每次修订使用分支＋PR、目标 HEAD CI 校验；区分 GitHub 提交、CI、合入和正式 PDF 生成。没有实物打印证据时不声称已完成实物打印。该工程不使用 `chn-ops`。

## 历史接续记录

# 当前接续：Q1终检候选接受，正式PDF待制作

PR #71已归档RC2/RC3/RC3-finalcheck及299页逐页复核证据；当前PR以RC3终检精确字节
关闭Q1版式验收，证据见`data/evidence/Q1-RC3-acceptance-20261008.json`。
旧RC1冻结及RC1的0/299队列保持历史事实；旧RC3本地导入快照 Q1_completed=false 仍保持原字节。
Q1本轮必须等待目标HEAD CI成功再合入；不要重复人工审读299页。
**正式v0.5.0尚未发布，final_release_eligible=false。** 下阶段制作真正的正式版PDF，
不得简单复制/改名RC3；需要对更改区域和目录跳转做终验、登记manifest、通过发布PR目标HEAD CI。
规范来源#4阻塞继续保留。避免`chn-ops`和再生成交接PDF。

## 以下为此前记录（保留）

# Agent工作约定

## 当前接续：Q1逐页复核（2026-10-08）

M3完整299页v0.5.0-rc1已归档；当前以docs/STATUS.md、data/post_release.json与data/q1_review.json为准。先核归档PDF SHA256，再按docs/Q1_REVIEW.md逐页实际检查。目前Q1认可页0/299，不把M3影响审读自动计入。不得重复M1/M2/F01—F05实现，不把候选改名发布。编译输入/原生成metadata中的未冻结标志是历史快照；生命周期以post_release及freeze记录为准。保留18份归档PDF、旧manifest条目及原审读证据；任何新修改须新候选字节和重新绑定，不覆盖旧文件。来源#4继续开放，字体和规范原件不导出。

## PR68接续记录（历史）（2026-10-08）

以docs/STATUS.md、data/post_release.json为准：M3的F01—F05均已实现，六例完整整字迁移10页/44笔已集成；内部工程预览299页，不是候选。下一步冻结并归档完整v0.5.0候选、核对最终生成提交/字节/CI，再退出M3并启动Q1。不要重复M1/M2或F03实现；以下旧断点仅供历史追溯。17份历史PDF/manifest/规范数据不可覆盖，来源#4继续开放。

## PR67实现检查点（历史，2026-10-07）

F01学生/辅导者分层说明与F02六组比较/回忆已实现，内部工程预览实际288页；F03整字迁移未生成，F04导航/F05字段策略已接入当前模块但待迁移集成。五包完成2，不是M3已完成。232书签、28目录跳转、201主项逐字段呈现检查已运行；全部12个比较/回忆页实际查看。下一步实现完整整字迁移，不重复M1/M2收口。

工程预览不是冻结候选、不作为正式PDF交付；旧17份PDF及manifest不改。来源阻塞保持，Q1未开始，candidate=null、final_release_eligible=false。当前细节以[STATUS](docs/STATUS.md)和`data/m3_scope.json`为准，复核见`reviews/M3-foundation-comparison-20261007.md`。

## 既有阶段记录（本轮之前）

## M2退出时的接续记录（历史）

当前以`docs/STATUS.md`、`data/post_release.json`为准。M1完成、正式v0.4.1保留；M2本周期按`completed_with_source_blocks`结束，累计采用瓦位置映射及麦/齿读音3个字段，来源#4仍open。当前M3已启动，先读`docs/M3_SCOPE.md`和`data/teaching-source-policy.json`，不要重复M1发布或将M2结束理解为残余已证实。M3启动时五个功能包尚未完成；最新实现以上方检查点为准，Q1仍planned；按字段限制出题/展示，不禁用无关已核字段，不补造精确2022结论。下列P0—P7是历史基线规则。

## 当前工作模式：内容优先

从2026-10-02起，工程采用“阶段1内容覆盖 → 阶段2图形版式 → 阶段3归档发布”的解耦流程，详见`docs/CONTENT_FIRST_WORKFLOW.md`。

阶段1内容层已于2026-10-07完成201/201 content_ready。以下阶段1规则作为内容回归约束保留：
- 先持续完成201个主部首的字段级内容和证据链；
- 内部每批10项，单次运行常规目标推进80个不同主部首（连续8批）；无真实阻塞时至少实质推进60项，40项只作为真实阻塞下的退化结果；
- B03的PDF归档、hard-gate和CI尾项不得再阻塞B04/B05及后续批次的内容编写；
- artwork/layout/publication状态单独跟踪，不与content_status混成一个“全有或全无”的完成状态；
- 全书级未决（例如GF0011—2022逐项全文）可以明确保留pending，但不阻塞其他已可独立核验字段和后续批次内容；
- 第一阶段原则上不频繁修改`scripts/`和`.github/workflows/`。除非工程结构本身阻止内容落库，否则优先写`data/`、`reviews/`和`sources/`。

阶段1的content_ready不等于release_eligible。正式发布仍必须完成图形、版式、PDF、manifest、CI和全书级门槛。

\n## 剩余完书阶段\n\n2026-10-06起按\`docs/REMAINING_PHASE_PLAN.md\`分阶段收口。P0规范源通道已完成，**P0—P7已全部完成；v0.4.0正式PDF已进入`deliverables/releases/`。**\n\n- P1—P4继续以80个不同主部首/轮为常规吞吐；\n- P0、P5—P7按阶段门槛推进，不为了计数凑80项；\n- 不再横向增加D05/D06等secondary数据源，除非规范原件出现真实无法定位的缺口；\n- secondary locator/crosscheck只用于原页定位和风险筛选，不能授予最终reviewed；\n- 当前状态：正式v0.4.0已发布；后续只做维护、勘误或新权威来源触发的重开。201/201 content_ready、201/201 artwork_ready且layout_ready；GF0011—2022逐项精确字段继续保持source-blocked fail-closed，不因正式发布伪造补值。\n\n## 接续入口
先读README.md、docs/STATUS.md、docs/CONTENT_FIRST_WORKFLOW.md、docs/EDITORIAL_PLAN.md、data/coverage.json和当前批次文件；再读当前分支、开放Issue及PR。仓库事实优先于会话记忆。不重新从零规划，不把阶段稿改名充当终审稿。

## 授权边界
已授权维护本字帖工程、文稿、数据和脚本、Issue、分支、PR、测试及合入。保留历史，不强推、不删除仓库、不改变公开范围、不操作其他仓库、不购买内容服务。除首次空仓初始化外使用分支＋PR。不得公开私人会话、个人资料、原始字体或许可不明的商业书籍全文。

## 内容规则
- 覆盖201个主部首；附形、位置变体、对照字及复习项分别计数，不套用214部体系。
- 字形、笔顺、笔画名称、部首／部件名称、拼音、结构和教学提示逐字段核验；一份来源支持某字段不等于支持整项。
- 书目介绍不是内页，搜索摘要不是规范全文，多个站点转载同一文献只算一份原件。不同年份出版物可能继承同一规则，须披露，不称独立来源体系。
- 汉典等网络字典辅助检索，Hanzi Writer仅提供绘图材料。机器测试不授予内容审定结论。
- 变体在所在整字中核验并保存笔画索引；包围部件保存完整书写时序。
- 注意笔画路径的收笔细节。日／目／田横折的字体回锋不能自动解释为规范的钩，月等真正带钩笔画不可一并删除。
- 不确定时保留准确未决状态和解决路径。同一Agent复看不是独立双人审定。

## 分批与阶段

主项B01—B20各10项，B21为1项。当前阶段1允许在前一批尚未完成artwork/PDF归档时继续下一批内容，但不能把前一批publication_status写成完成。

阶段1每批至少经过：范围确定 → 材料定位 → 字段核验 → 中间文稿 → 内容复核。达到content_ready后即可继续后续内容批次。

阶段2再集中处理：逐笔矢量、规范原图匹配、PDF生成、逐页视觉检查。

阶段3处理：draft归档、manifest、目标HEAD CI、release和全书终审。

每个实际交付或送审的PDF都必须按版本保存在deliverables/drafts/；正式PDF满足相应门槛后放deliverables/releases/。同时维护manifest.json中的页数、字节数、SHA256、source_commit、复核记录和发布状态。Actions附件只是临时传输，不代替仓库文件。旧版PDF不得覆盖或更改状态脚注，新版使用新目录。排查用的未交付临时渲染可以只留构建目录。

正式页需规范原件定位、其他权威出版物的字段交叉证据、冲突解决、矢量核验和逐页视觉验收；最终全书另需201主项、附形、原27项回归和总目录／页码核验。机器检查、原件阅读、字形匹配、版面检查分别记录。

批次内容完成更新STATUS、复核记录、覆盖表和总控Issue。常规工作不需逐项请示；付费、授权材料或无法自主判断的教学取舍集中报告。
