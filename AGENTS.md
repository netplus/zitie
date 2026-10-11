# 当前接续：A3.7 恢复201字播放器的两档笔压（2026-10-11，修复候选）

用户指出历史截图中的「笔压风格　稳定版｜模拟笔压版」在正式 animation/book.html 缺失。旧九字 animation/index.html 保留原A1.6完整模块，故直接在新主页面重新引入 script gesture-data.js、pressure-model.js、pressure-style.js；在 book-ui.js复用StyleController，不新设计压力算法。UI默认稳定版，模拟版恢复圆环、力度百分比/阶段、曲线，风格跨字、跳笔、倍速、pause/play保留；不应出现墨迹变化。新A3.7测试需完整201/1045压力模型、12帧等红墨实际Chromium测试、A3.6 2090逐笔前缘测试、390px；PR最终HEAD A1/Book双成功→merge→Pages实际Deploy才放行。正式 v0.5.1 PDF、manifest、来源审读数据、原SVG、1045笔笔顺、A3.6 source-arc guard及A3.5研究路线都保持不变。详见 docs/A37_PRESSURE_STYLE_RESTORE.md、Issue #128。硬笔仍冻结；禁止使用 chn-ops。

---

# 当前接续：A3.6 201字墨迹前缘领先笔尖问题（2026-10-11，已修复部署）

用户明确指出水等字有“墨迹填充快于笔尖位置”，要求逐字全量复查。正式source仍为v0.5.1 299页PDF以及21批201字1045笔，禁止改笔顺、轮廓、median、PDF/manifest、Arphic许可。新增 animation/ink-front-guard.js 源中线4SVG单位Voronoi按时显墨区域；最终用**独立持久红色SVG片段**在静态原字形clipPath/既有宽圆头mask内叠加，防止宽圆头提前染到未到达的后段且避免复合动态clipPath引起的已绘像素回退。启用在正式 animation/book.html 的201字毛笔和A3.5实验两侧，旧9字历史回归保留原版以便对照。详见 docs/A36_INK_FRONT_AUDIT.md、Issue #125。单靠不掉红墨素CI不够，必须201/1045 Node空间不超前、Chromium真实多字多帧与水4笔、390px以及原201 A3/A3.5基线回归。**A3.6 已上线（2026-10-11）。** [PR #126](https://github.com/netplus/zitie/pull/126) 最终精确 HEAD `d410e398c6d94bfcd7d309cdd58372ff542ac2d1` 的 [A1 Chromium #38134493046](https://github.com/netplus/zitie/actions/runs/38134493046) 与 [Book integrity #38134493075](https://github.com/netplus/zitie/actions/runs/38134493075) 均 completed/success；合并 `main` 提交 `ea4a76e868cf9f9dbe3469fc0028604d4b5265b8` 对应的 [Pages #38135010764](https://github.com/netplus/zitie/actions/runs/38135010764) Configure、Upload、实际 Deploy 全 completed/success。

实测：**201 个字、1045 个笔画**全部有有效 source-arc 前缘守卫；**每笔两个 Chromium 像素帧，2090/2090 帧**，所有1045笔都显墨且笔内红墨回退为 **0 像素**，任一后续中线红墨领先 **超过12 SVG单位的帧为0**（所采样最大领先12单位）；另 **201字495帧**（31个高风险字加密），**水四笔16帧**、A3.5 A/B两时序40帧均合格，390px手机视口合格，旧 A3/A3.5 原始笔迹回归继续成功。 [截图及完整metrics artifact #11700378299](https://github.com/netplus/zitie/actions/runs/38134493046/artifacts/11700378299)。

根因与修复：旧宽圆头在折角附近会在未来中线上提前显墨；首次复合动态clipPath虽能限制前缘却导致Chromium抗锯齿重算时2—12已绘红像素消失，单纯加约3 SVG单位边缘重叠仍不够。**最终方案是每个已到达的Voronoi显墨区保留为独立红色SVG元素，在同一静态原轮廓clipPath及旧圆头alpha-mask内叠加**，不再反复修改复合裁剪轮廓。旧9字历史回归保持原渲染以便复现，A3默认201字及A3.5左右侧采用修复版；PDF的字形、笔顺、原median、计时、许可和299页正文均未修改。

边界：这是**采样位置与阈值内的工程验证**，不等于真实毛笔接触面每个边缘绝对不超前，也不代表运动学/书法教师已认可；A3.5新节奏仍只可选，硬笔仍冻结。 **已完成修复发布；后续提交仍须重新过全量门槛**。硬笔继续冻结，A3.5运动模型仍独立候选。

---

# 当前接续：A3.5 毛笔运笔 A/B 研究版已部署（2026-10-11，待人工观感验收）

按用户指令继续A3.5，绝不继续默认硬笔的审美模型。以正式 v0.5.1 299页PDF及其201字/1045笔Arphic PL矢量作为不可变源；保留A3正式201字毛笔播放器默认。新增单独的 animation/experiments/brush-gesture-model.js、brush-motion-lab.html/js 只比较笔内时间分配：已审定笔画名称+源折角经有界时序建模，无法安全判读则回退；不改原SVG轮廓、median、笔顺、单笔时长或停顿。用原StrokePlayer在共同时间轴的A/B比较；Node须验证所有原九字40笔的时间单调与漂移<12.5%，Chrome加载全201字/1045笔并对54对真实墨迹帧、21对同空间位置画面对照以及390px布局测试。正式PDF、manifest、201规范记录、授权矢量不得改变，不能声称真人速度/笔压或教师验收。进展见 docs/A35_BRUSH_MOTION_AB.md 与 Issue #120。实际独立研究版 [A3.5 201字 A/B](https://netplus.github.io/zitie/animation/experiments/brush-motion-lab.html) 已上线：[PR #123](https://github.com/netplus/zitie/pull/123) 最终 HEAD `e7938b29725488dcf9491d143cf746391808533e` 的 [A1 Chrome #38125276874](https://github.com/netplus/zitie/actions/runs/38125276874) 与 [Book #38125276827](https://github.com/netplus/zitie/actions/runs/38125276827) 双 completed/success，合并至main SHA `0da37d5c1965a4f9d798b228de8d081263c1d81c`，其 [Pages #38125707083](https://github.com/netplus/zitie/actions/runs/38125707083) Configure、Upload和实际Deploy 全 success。**201字、1045笔**全部加载；960个有界运动候选、85个保守回退、193处来源中线角点候选事件；54对真实Chromium A/B 帧（两侧红墨不消失）、其中21对有时间运动差异，另21对相同空间位置的实际像素对照 **0 差异**，390px通过。截图/metrics见 [A1 QA artifact #11697280799](https://github.com/netplus/zitie/actions/runs/38125276874/artifacts/11697280799)。**人工审美/真实书法运笔教学审核仍待完成，绝不自动推广B为默认**；正式 [A3毛笔播放器](https://netplus.github.io/zitie/animation/book.html)、原PDF及硬笔冻结决策不变。 后续如要替换默认须用户/教师明确确认；新修改必须重新执行最终HEAD双CI及实际Pages部署。禁止 chn-ops。

---

# 当前接续：A3 PDF同源201主部首毛笔笔顺（2026-10-11，已部署、继续真实教学轨迹复核）

用户否定 A2.4 硬笔审美方案，明确要求**毛笔恢复默认、硬笔路线暂停**；现主线 [A3 #120](https://github.com/netplus/zitie/issues/120) 是基于字帖正式 v0.5.1 299页 PDF 生成201个主部首的毛笔笔顺。实际 PDF 不是运动数据文件：从其生成同源数据（B01—B21、源许可版本固定矢量、SHA锁定的覆写、M3展示政策）创建 animation/book-pack.js；生成过程中必须核对正式PDF SHA和201个 ID书签，任何不符 fail closed。独立 animation/book.html + book-ui.js 全201主项、PDF书签页码/六步一页、搜索与毛笔逐笔动画；原 index.html 九字回归改为毛笔默认、硬笔只保留可选冻结模型；Pages根入口指向201字。最终功能 PR HEAD `b66a51dd31be7d06a2fcdbccd7e106f891617997` 的 [A1 动画 CI #38122954997](https://github.com/netplus/zitie/actions/runs/38122954997) 与 [Book 完整性 CI #38122955056](https://github.com/netplus/zitie/actions/runs/38122955056) 双 completed/success；[PR #121](https://github.com/netplus/zitie/pull/121) 合入 `main` 为 `452e79f078b3d80a515e3a2290f6489a37925760`，同一 merge SHA 的 [GitHub Pages #38123374018](https://github.com/netplus/zitie/actions/runs/38123374018) Configure、Upload、实际 Deploy 全部 completed/success。A1 83 项历史 Node 与 A3 5 项新 Node 全通过；**201 字/1045 笔/21 批次**及正式 v0.5.1 299页 PDF SHA256 `7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90` 已核对；A3 54 帧 Chromium 落墨 0 像素消失，27 帧可见笔尖，龠第17笔进入本字 PDF 第3张累计示范页，390px 适配通过。截图见 [A3 QA artifact #11696336104](https://github.com/netplus/zitie/actions/runs/38122954997/artifacts/11696336104)。[完整201字毛笔播放器](https://netplus.github.io/zitie/animation/book.html)及[只读正式 PDF](https://netplus.github.io/zitie/book/zitie-v0.5.1-A4.pdf)已发布。**这是工程动画的完整源一致性验证，未获得真人运笔轨迹的教学认证；硬笔仍冻结。** 后续提交仍必须重新通过同样的精确 HEAD A1/Book 双 CI 及实际 Pages Deploy。原正式 PDF、manifest、201审核、任何字体文件均不可修改/提交。SVG中线与合成速度依然未经教学/真人书写核验；不将201项笔顺审读冒充201项轨迹教学通过。见 docs/A3_PDF_BRUSH_ANIMATION.md。硬笔美感课题 #119 冻结，除非用户重启，不推进。禁止用 chn-ops。

---

# 当前接续：A2.4 楷书跨笔画结构首轮候选（2026-10-11，PR #117 已部署，继续 A2.4 专家复核）

下一阶段是 [Issue #116](https://github.com/netplus/zitie/issues/116) 整字结体、跨笔画连接和专业视觉审核。首轮 [PR #117](https://github.com/netplus/zitie/pull/117) 新增 `animation/experiments/kaishu-composition.js`、`kaishu-composition-stage.js` 和 `kaishu-composition-lab.js/html`，基于原 A2.3 九字40笔的**只读**二阶候选。几何检查包含近邻投影/相交/视觉质心/重复横画；只给「水」捺起点→主竖一个显式的有界连接候选（37→15，位移22 SVG单位），保护故意断开，「龠」复杂构件不作自动吸附。Node负例/全字/72帧Chrome单调落墨和移动端均加入CI，具体限度参见 `docs/A24_KAISHU_COMPOSITION.md`。不得把自动结果宣称已获教师批准，不得在此阶段推广成201字或替换主站默认；原A2.2硬笔、A1.3毛笔、A1.6双笔压、A2.3页面、v0.5.1 PDF/manifest/201规范来源审核记录保持不变。最终 PR HEAD `0a936967c06177a2834847a6a5345cabb6c11eba` 的 [A1 动画 CI #38101554487](https://github.com/netplus/zitie/actions/runs/38101554487) 和 [Book integrity CI #38101554455](https://github.com/netplus/zitie/actions/runs/38101554455) 双 completed/success；[PR #117](https://github.com/netplus/zitie/pull/117) 已合入 `main`，合并 SHA `cc90c7f4fd1591b9eebd56e2d6eea628ce732e61`，此提交的 [GitHub Pages #38102023812](https://github.com/netplus/zitie/actions/runs/38102023812) 已实际完成 Configure、Upload、Deploy（均 success、未跳过）。**83项 Node 测试全部通过**，9字40笔/72帧 Chromium 实际写字中0已绘红墨丢失、45帧笔尖轨迹匹配、7帧 A2.3 与 A2.4 真实差异，390px 窄屏通过。九字与水字的真实截图见 [A1 QA artifact #11688261422](https://github.com/netplus/zitie/actions/runs/38101554487/artifacts/11688261422)。独立[已上线 A2.4 楷书整字结构 A/B 实验](https://netplus.github.io/zitie/animation/experiments/kaishu-composition-lab.html)可体验。**仍是未教学审批的工程实验，水和龠整体专业度待人工复核，不替换主站。** 后续仍必须取新的最终 PR HEAD 的 A1+Book 双成功，再核实 Pages 实际 Deploy；主站不得自动推广。**不要调用 chn-ops。**

---

# 当前接续：A2.3 楷书 A/B 研究实验已部署、主站硬笔待专业复核（2026-10-11）

用户拒绝把 A2.2 基础等宽描线称为专业硬笔书法，要求楷书结构、基本笔画形态和整字工整性。真实根因是 source `median` 继承毛笔风格，横画「一」就有不必要波浪。新候选见 `docs/A23_KAISHU_GEOMETRY.md`、`animation/experiments/regular-kaishu-model.js`、`regular-kaishu-ink.js`、`regular-kaishu-lab.js/html` 和 [Issue #113](https://github.com/netplus/zitie/issues/113)。A2.3 以结构/方向为先，轻度右仰的横画、坚挺竖画、折的单拐点、短小出尖钩、撇捺末段收尖与跨笔画平行间距作质量门槛。新的九字示范点**全部是未教学审批的工程骨架**，不可代替真人书写轨迹或导入来源原SVG。[PR #114](https://github.com/netplus/zitie/pull/114) 已合入 `main`（`ab096bc36f0e8664efa453355e746df3746ac6fa`）。其最终 HEAD `17669b2dad0c5c1b1875e3b251bd7fa48e5c4669` 的 A1 CI #38053296972、Book CI #38053296950 双成功，Pages #38094108471 在合并提交上实际Deploy成功。[九字 A/B 实验](https://netplus.github.io/zitie/animation/experiments/regular-kaishu-lab.html) 已上线：77 Node，9字40笔，72帧0已写墨迹回退，63帧新旧形态确不同，口/月底部与内部横画已做跨笔画结构连接验证。此仅表示实验可用，**水/龠等复杂字仍不能当作专业硬笔楷书规范**；不能以自动指标通过代替教师人工鉴定，不能直接改主播放器的默认硬笔，原始A1.3毛笔、A1.6压力和v0.5.1 PDF/manifest/201教案审核记录继续保持原样。保留 A2.2 现有硬笔、A1.3 毛笔可切换、A1.6笔压双风格、v0.5.1 299页PDF/manifest/201来源审核状态；不提交第三方字体/商业字帖。GitHub 只能分支-PR-最终HEAD动画/Book CI双成功后合入，核实 Pages 实际部署；无验证不可宣称专业楷书完成。不用 chn-ops。

---

# 当前接续：A2.2 硬笔默认、毛笔原版可切换，均已主站部署（2026-10-10）

用户对A2.1毛笔式效果提出纠正：下阶段研究方向为普通钢笔/硬笔楷书，而**毛笔原版本身仍须保留并可切换**，主页面「书写工具」默认硬笔。设计/真实来源限制见 `docs/A2_HARDPEN_SCOPE.md`、[Issue #110](https://github.com/netplus/zitie/issues/110)。A2.2 的独立 `animation/hardpen-stage.js` 与 `animation/experiments/hardpen-model.js` 沿着受限幅度细化的原median中心线，以恒线宽圆头着墨；原毛笔 `animation/player.js` 的 source-outline mask、brush-union、A1.3笔尖纠偏、时序均不覆盖。二工具同步唯一 A1 时间轴，切换不暂停、不重置字形/倍率/笔画；A1.6笔压风格稳定版/模拟版在两工具上仍可切换，但它只调小笔尖接触提示而不改变硬笔墨迹粗细。由来源毛笔字形抽取的medians仍为未经教学审核的工程骨架，不得因几何测试通过称为真实硬笔规范。

[PR #111](https://github.com/netplus/zitie/pull/111) 已合并 `ddd360f95872264fe74131c37b8275901fece769`；其最终精确HEAD `9f8d3e9947f0aeefda8910797cb6d752874d5ce8` 的 A1 CI #38040209141 和 Book CI #38040209229 双成功，合并后 Pages #38040703826 完成实际 Configure/Upload/Deploy。主站[硬笔默认 / 毛笔可切换](https://netplus.github.io/zitie/animation/)真实上线；69 Node、7字硬笔63帧、9字主站63帧、硬笔已写墨迹0回退、毛笔原字形0修改、4次连续播放中的工具切换、390px布局均成功。今后硬笔研发在此双工具架构上研究起笔、折角、撇钩与真实压感标定，不直接覆写毛笔A1.3源轮廓与原正式v0.5.1 PDF或201来源审核记录。硬笔当前仍是未教学批准的工程演示。绝不修改正式v0.5.1 299页PDF、manifest、201规范来源记录/审核或将A2实验直接扩展成全字库验证；不使用chn-ops。

---

# 当前接续：A2.1 基本笔画动作语法实验已部署（2026-10-10）

用户认为现有轨迹建模不足以表现横、竖、撇、折、钩的真实书写动作。新阶段按 `docs/A2_BASIC_STROKE_MODEL.md`、[Issue #107](https://github.com/netplus/zitie/issues/107) 与 `animation/experiments/stroke-primitives.js`、`stroke-grammar-lab.js/html` 接续。A2.1 必须区分基本笔画的动作语义、受原SVG填充轮廓约束的分段曲线与运动学时序。折角和出钩顶点必须保留原始median，曲线禁止出原轮廓，违约时回退原线段并记录；不准只把全笔画平滑成单曲线。当前新动作轨迹未经教学/真人数据审核，只能作独立A/B研究实验。A/B两侧仍用原A1.3稳定SVG墨迹填充，B只改变笔内语义化时序和显示轨迹；任何时刻不能修改正式 `animation/player.js`、`motion.js`、`brush-union.js`、`timeline.js`、`samples.js`、A1.6两档笔压风格、v0.5.1 299页PDF/manifest、201主项来源审核记录。[PR #108](https://github.com/netplus/zitie/pull/108) 已合入 `main`，真实合并提交 `13d0f8ae1ea37149f9dd4305c168b87e7b7b5c80`，最终 PR HEAD `206fa730038d7b7e9fb0378b5d11016d6d2f1aea` 的动画 CI #38036907848、Book CI #38036907780 双通过，合入后 Pages #38037395286 完成 Configure/Upload/Deploy。[独立线上A2.1实验](https://netplus.github.io/zitie/animation/experiments/stroke-grammar-lab.html) 可直接试用，7字56帧、源SVG红墨0差异、54段曲线细化、1段回退、0越界，63项Node测试通过。这个结果仅是工程几何与可复现动作检查，不准冒称201项已真人教学审核。接下来A2.2要对横竖撇折钩逐笔做专家自然度复核和合法采集的真实轨迹标定，再讨论改动默认A1.6稳定播放器。

---

# 当前接续：A1.6 主播放器双笔压风格已上线（2026-10-10）

用户明确要求在已部署的 `animation/index.html` 直接提供两档笔压风格：「稳定版」（默认）、「模拟笔压版」；不用离开主页面。当前实现见 `animation/pressure-style.js`、`animation/ui.js`、`docs/A1_PEN_STYLE_SELECTOR.md`、[Issue #104](https://github.com/netplus/zitie/issues/104)。压力模型仅复用 A1.5 的合成归一化力度和已标识未审定的手势，真实字形源、原稳定 A1.3 圆头墨迹、源轮廓、光学纠偏圆圈位置、按位置变速和201规范数据不动。切换风格必须不暂停、不重置时间或倍率，稳定版恢复精确原始标记。原官方 v0.5.1 PDF/manifest 不动；新增9字×5时间点45帧 Chromium 墨迹/掩码逐像素检查、Node、移动端布局及双CI门槛。[PR #105](https://github.com/netplus/zitie/pull/105) 已合并到 `main`（`d055e2d05fcd6c39635e8ec9d15fc234451e7327`），最终 PR HEAD 动画 CI #38030438772 与全书 CI #38030438681 均 success；合并后 Pages #38030935433 Configure/Upload/Deploy 真正成功，[主页面](https://netplus.github.io/zitie/animation/)可直接切换两档。未有真实笔压授权或标定，不能冒称实际受力。

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
