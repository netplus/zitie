## A3.8 笔压风格与动画同屏（已上线）

原[完整201字毛笔播放器](book.html)的“笔压风格”被排到全部播放控制下方，不方便在书写时观察。现将其**移到与 SVG 书写画布同一个区域**：宽屏放在画布右侧，较窄屏幕放在画布上方并在滚动书写时保留可见读数。**A3.8 已上线（2026-10-11）**：[#132](https://github.com/netplus/zitie/pull/132) 完成布局，[#133](https://github.com/netplus/zitie/pull/133) 修复 1020px 笔记本字格缩水；合并 SHA [f4ae83e](https://github.com/netplus/zitie/commit/f4ae83e338cff68bc9460d3f0eacfaef919d949a) 的 [真实 Chromium 检查](https://github.com/netplus/zitie/actions/runs/38145041178)、[Book](https://github.com/netplus/zitie/actions/runs/38145041109) 与 [Pages 实际 Deploy](https://github.com/netplus/zitie/actions/runs/38145041123) 全部成功。稳定版默认、模拟笔压版圆环/力度曲线保持原A1.6行为，不创建第二份控件，不改PDF笔顺、墨迹或A3.6前缘防超前。详细布局、QA 与发布记录见 [A3.8](../docs/A38_PRESSURE_VISIBLE_LAYOUT.md)。

---

## A3.7：恢复完整201字的「稳定版 / 模拟笔压版」选择（已上线）

用户提供截图指出旧A1.6笔压风格在新 [201字字帖播放器](book.html) 遗失。现直接复用原本的`pressure-style.js`、`pressure-model.js`和`gesture-data.js`，恢复两档按钮、合成力度圆环/百分比/曲线；稳定版默认，模拟版只影响笔尖视觉，不改变已核墨迹、SVG轮廓/中心线、A3.6显墨守卫或PDF发布哈希。全201字/1045笔压力曲线及真实浏览器逐帧同墨测试新增CI；**A3.7 已上线（2026-10-11）。** [PR #129](https://github.com/netplus/zitie/pull/129) 最终 HEAD `2252d3de3df7ef9f9aa1eec3deb5d21572d52b5b` 的 [A1/Chromium CI #38138069650](https://github.com/netplus/zitie/actions/runs/38138069650) 与 [Book CI #38138069687](https://github.com/netplus/zitie/actions/runs/38138069687) 双 completed/success；合并 `main` SHA 为 `e8b4b8adefcf2381e8b0ed9a2fcd701794280c93`，对应的 [Pages #38138652608](https://github.com/netplus/zitie/actions/runs/38138652608) Configure、Upload、实际 Deploy 全 completed/success。**201字/1045笔**均生成模拟笔压曲线，14个细笔名受限主项不泄漏，12组真实 Chromium 稳定/模拟模式红墨光栅 **0 像素差异**，力环与当前笔尖100%对齐，风格切换不改变进度、倍率、播放、笔顺或源SVG墨迹；390px手机视口通过，A3.6原2090帧防超前回归不受影响。 [真实稳定/模拟截图与 QA metrics artifact #11702002988](https://github.com/netplus/zitie/actions/runs/38138069650/artifacts/11702002988)。[正式201字播放器](https://netplus.github.io/zitie/animation/book.html?id=77) 可直接使用。**模拟力值不是实测笔压，仅影响笔尖和提示，不改变墨迹宽度。**详细[说明与验收](../docs/A37_PRESSURE_STYLE_RESTORE.md)。

---

## A3.6 201字/1045笔：防止墨迹前缘跑在笔尖前方（已上线）

针对[Issue #125](https://github.com/netplus/zitie/issues/125)中「水」等折、钩和宽笔画提前着墨，新增 source arc Voronoi 可见区域守卫：保留原圆头墨迹并集但禁止提前绘出未来中线区域，沿每个源笔画按4 SVG单位划分可达区域；在100%保留原始PDF精确字形。新 [算法与全量验收说明](../docs/A36_INK_FRONT_AUDIT.md)。**默认201字 A3**和 A3.5 A/B 两侧使用该屏障，硬笔和九字旧回归不动。CI对201/1045源数据、2090帧逐笔真实Chromium像素和逐字495帧均已通过，已部署至主站。

**A3.6 已上线（2026-10-11）。** [PR #126](https://github.com/netplus/zitie/pull/126) 最终精确 HEAD `d410e398c6d94bfcd7d309cdd58372ff542ac2d1` 的 [A1 Chromium #38134493046](https://github.com/netplus/zitie/actions/runs/38134493046) 与 [Book integrity #38134493075](https://github.com/netplus/zitie/actions/runs/38134493075) 均 completed/success；合并 `main` 提交 `ea4a76e868cf9f9dbe3469fc0028604d4b5265b8` 对应的 [Pages #38135010764](https://github.com/netplus/zitie/actions/runs/38135010764) Configure、Upload、实际 Deploy 全 completed/success。

实测：**201 个字、1045 个笔画**全部有有效 source-arc 前缘守卫；**每笔两个 Chromium 像素帧，2090/2090 帧**，所有1045笔都显墨且笔内红墨回退为 **0 像素**，任一后续中线红墨领先 **超过12 SVG单位的帧为0**（所采样最大领先12单位）；另 **201字495帧**（31个高风险字加密），**水四笔16帧**、A3.5 A/B两时序40帧均合格，390px手机视口合格，旧 A3/A3.5 原始笔迹回归继续成功。 [截图及完整metrics artifact #11700378299](https://github.com/netplus/zitie/actions/runs/38134493046/artifacts/11700378299)。

根因与修复：旧宽圆头在折角附近会在未来中线上提前显墨；首次复合动态clipPath虽能限制前缘却导致Chromium抗锯齿重算时2—12已绘红像素消失，单纯加约3 SVG单位边缘重叠仍不够。**最终方案是每个已到达的Voronoi显墨区保留为独立红色SVG元素，在同一静态原轮廓clipPath及旧圆头alpha-mask内叠加**，不再反复修改复合裁剪轮廓。旧9字历史回归保持原渲染以便复现，A3默认201字及A3.5左右侧采用修复版；PDF的字形、笔顺、原median、计时、许可和299页正文均未修改。

边界：这是**采样位置与阈值内的工程验证**，不等于真实毛笔接触面每个边缘绝对不超前，也不代表运动学/书法教师已认可；A3.5新节奏仍只可选，硬笔仍冻结。

---

## A3.5 正式字帖毛笔运笔 A/B（研究版已上线，默认A3不变）

新 [毛笔运笔对照实验](experiments/brush-motion-lab.html) 使用与已发布 v0.5.1 PDF完全同源的201主部首、1045笔。两侧原SVG墨迹与中线不变；A为已发布的A3节奏，B按已核细笔名建立可解释的起笔、折钩、收笔时间重映射；不通过原中线回溯推断笔画名称、真实笔压力度或真人运动。不确定折钩和未核名称严格回退。Node验证轨迹单调，Chromium要求54对同步帧、同空间进度一致墨迹、390px；实际独立研究版 [A3.5 201字 A/B](https://netplus.github.io/zitie/animation/experiments/brush-motion-lab.html) 已上线：[PR #123](https://github.com/netplus/zitie/pull/123) 最终 HEAD `e7938b29725488dcf9491d143cf746391808533e` 的 [A1 Chrome #38125276874](https://github.com/netplus/zitie/actions/runs/38125276874) 与 [Book #38125276827](https://github.com/netplus/zitie/actions/runs/38125276827) 双 completed/success，合并至main SHA `0da37d5c1965a4f9d798b228de8d081263c1d81c`，其 [Pages #38125707083](https://github.com/netplus/zitie/actions/runs/38125707083) Configure、Upload和实际Deploy 全 success。**201字、1045笔**全部加载；960个有界运动候选、85个保守回退、193处来源中线角点候选事件；54对真实Chromium A/B 帧（两侧红墨不消失）、其中21对有时间运动差异，另21对相同空间位置的实际像素对照 **0 差异**，390px通过。截图/metrics见 [A1 QA artifact #11697280799](https://github.com/netplus/zitie/actions/runs/38125276874/artifacts/11697280799)。**人工审美/真实书法运笔教学审核仍待完成，绝不自动推广B为默认**；正式 [A3毛笔播放器](https://netplus.github.io/zitie/animation/book.html)、原PDF及硬笔冻结决策不变。见 [算法与来源限制](../docs/A35_BRUSH_MOTION_AB.md)、[A3 #120](https://github.com/netplus/zitie/issues/120)。已上线 [完整201字默认毛笔播放器](book.html) 不变，硬笔方向继续冻结。

---

## A3 PDF同源201字毛笔播放器（已正式部署；毛笔恢复默认）

用户已确定不再继续硬笔方向，现以正式 v0.5.1 PDF 为视觉与教学源。新的 [201字毛笔播放器](book.html) 从与 299 页正式PDF同源的 B01—B21 教学记录、固定上游SVG笔画、已核覆写以及 PDF 201条书签生成离线字库，按当前笔画自动关联真实 PDF 页码，支持17笔龠的3页连读、批次/字/笔画查询、逐笔时间轴和练习提示。原 [9字工程播放器](index.html) 恢复毛笔默认，硬笔暂保留为冻结实验选项。生成器和证据/许可边界见 [A3设计](../docs/A3_PDF_BRUSH_ANIMATION.md)、[Issue #120](https://github.com/netplus/zitie/issues/120)。最终功能 PR HEAD `b66a51dd31be7d06a2fcdbccd7e106f891617997` 的 [A1 动画 CI #38122954997](https://github.com/netplus/zitie/actions/runs/38122954997) 与 [Book 完整性 CI #38122955056](https://github.com/netplus/zitie/actions/runs/38122955056) 双 completed/success；[PR #121](https://github.com/netplus/zitie/pull/121) 合入 `main` 为 `452e79f078b3d80a515e3a2290f6489a37925760`，同一 merge SHA 的 [GitHub Pages #38123374018](https://github.com/netplus/zitie/actions/runs/38123374018) Configure、Upload、实际 Deploy 全部 completed/success。A1 83 项历史 Node 与 A3 5 项新 Node 全通过；**201 字/1045 笔/21 批次**及正式 v0.5.1 299页 PDF SHA256 `7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90` 已核对；A3 54 帧 Chromium 落墨 0 像素消失，27 帧可见笔尖，龠第17笔进入本字 PDF 第3张累计示范页，390px 适配通过。截图见 [A3 QA artifact #11696336104](https://github.com/netplus/zitie/actions/runs/38122954997/artifacts/11696336104)。[完整201字毛笔播放器](https://netplus.github.io/zitie/animation/book.html)及[只读正式 PDF](https://netplus.github.io/zitie/book/zitie-v0.5.1-A4.pdf)已发布。**这是工程动画的完整源一致性验证，未获得真人运笔轨迹的教学认证；硬笔仍冻结。**

---

## A2.4 整字结构关系与限幅端点连接（独立 A/B 已上线、待教师审查）

继续 [Issue #116](https://github.com/netplus/zitie/issues/116)，新增 [整字结构 A/B 研究页](experiments/kaishu-composition-lab.html)：A 为原 A2.3 楷书规整实验、B 为仅在声明了跨笔画关系且距离/局部方向均满足约束时才修正的 A2.4。初版检查交叉、端点相邻、按线宽近似的视觉质心及重复横画角度；九字40笔中仅对「水」捺画与主竖接头作一次 **22 SVG 单位** 的候选移动（线间距 37→15），「龠」与其余笔画不自动修改，保留故意留白。处理器对超距、锐角与负例拒绝自动更改。代码/局限见 [A24_KAISHU_COMPOSITION.md](../docs/A24_KAISHU_COMPOSITION.md) 和 [PR #117](https://github.com/netplus/zitie/pull/117)。原 A2.3、主站硬笔/毛笔与双笔压，以及 v0.5.1 PDF/manifest/201规范记录均不变。最终 PR HEAD `0a936967c06177a2834847a6a5345cabb6c11eba` 的 [A1 动画 CI #38101554487](https://github.com/netplus/zitie/actions/runs/38101554487) 和 [Book integrity CI #38101554455](https://github.com/netplus/zitie/actions/runs/38101554455) 双 completed/success；[PR #117](https://github.com/netplus/zitie/pull/117) 已合入 `main`，合并 SHA `cc90c7f4fd1591b9eebd56e2d6eea628ce732e61`，此提交的 [GitHub Pages #38102023812](https://github.com/netplus/zitie/actions/runs/38102023812) 已实际完成 Configure、Upload、Deploy（均 success、未跳过）。**83项 Node 测试全部通过**，9字40笔/72帧 Chromium 实际写字中0已绘红墨丢失、45帧笔尖轨迹匹配、7帧 A2.3 与 A2.4 真实差异，390px 窄屏通过。九字与水字的真实截图见 [A1 QA artifact #11688261422](https://github.com/netplus/zitie/actions/runs/38101554487/artifacts/11688261422)。独立[已上线 A2.4 楷书整字结构 A/B 实验](https://netplus.github.io/zitie/animation/experiments/kaishu-composition-lab.html)可体验。**仍是未教学审批的工程实验，水和龠整体专业度待人工复核，不替换主站。**

---

## A2.3 楷书字形与骨架规整 A/B（已独立上线、待书法复核）

目标从 A2.2 基础等宽硬笔升级为**专业硬笔楷书形态**。现有中心线从毛笔艺术字形派生，不天然符合硬笔楷书结构；仅改笔压和运笔速度不会使横画平直或结构端正。新 [九字楷书对照实验](experiments/regular-kaishu-lab.html) 将当前基础硬笔作为 A，经过横竖方向约束、折钩节点规整、撇捺受控收尖的候选作为 B；两者共用来源汉字笔顺与时间轴。新增 `regular-kaishu-model.js`（形态）和 `regular-kaishu-ink.js`（不可回缩的局部变宽圆头着墨），保留原官方SVG字形和书写顺序不变。详细设计见 [docs/A23_KAISHU_GEOMETRY.md](../docs/A23_KAISHU_GEOMETRY.md)、[Issue #113](https://github.com/netplus/zitie/issues/113)。[PR #114](https://github.com/netplus/zitie/pull/114) 已合并至 `main`（`ab096bc36f0e8664efa453355e746df3746ac6fa`），精确候选 HEAD 的 [动画 CI #38053296972](https://github.com/netplus/zitie/actions/runs/38053296972) 与 [Book CI #38053296950](https://github.com/netplus/zitie/actions/runs/38053296950) 双成功，合并后 [Pages #38094108471](https://github.com/netplus/zitie/actions/runs/38094108471) 真正 Deploy 成功。打开[九字楷书 A/B 研究页面](https://netplus.github.io/zitie/animation/experiments/regular-kaishu-lab.html)查看。77项Node测试、9字40笔、72帧Chrome的墨迹已绘部分0回退、63帧确有形态差异；口封口、月两内横连接已加入阻断测试。**专业楷书笔形与结体尚待人工审核**，特别是水、龠等复杂字；此前部署的主页面默认硬笔/毛笔原版切换和模拟笔压，以及正式PDF/规范数据均不变。

---

## A2.2 主站硬笔默认，毛笔原版保留（已部署）

用户指定[主动画页面](index.html)默认使用**硬笔**；当前偏毛笔笔形的原字帖SVG动画**作为「毛笔（原版）」保留并可直接切换**。硬笔由独立 `hardpen-stage.js` 渲染近乎恒线宽的圆头中心线笔迹，不再填满原毛笔粗细轮廓；主播放控制唯一，工具切换时保持同一时间点、原字形、倍率和播放状态。A1.6「稳定版／模拟笔压版」继续作为另一项独立风格设置，两种工具均可选择。对照的[硬笔独立研究页面](experiments/hardpen-lab.html)可用于进一步观察。

本版不使用毛笔的夸张蓄势、藏锋、逆锋，也不将模拟力度与钢笔线宽直接挂钩；来源骨架仍未通过教学审核。实现依据及限制见 [A2_HARDPEN_SCOPE](../docs/A2_HARDPEN_SCOPE.md)、[Issue #110](https://github.com/netplus/zitie/issues/110)。[PR #111](https://github.com/netplus/zitie/pull/111) 已合并为 `ddd360f95872264fe74131c37b8275901fece769`，精确最终HEAD的 [A1 CI #38040209141](https://github.com/netplus/zitie/actions/runs/38040209141) 与 [Book #38040209229](https://github.com/netplus/zitie/actions/runs/38040209229) 均成功，合并后 [Pages #38040703826](https://github.com/netplus/zitie/actions/runs/38040703826) 实际部署成功。现在访问[主页面](https://netplus.github.io/zitie/animation/)即可默认观看硬笔，并随时切回完整保留的毛笔原版；69项Node测试、7字硬笔63帧、9字主站63帧、0已写墨迹回退、原毛笔红色墨迹0变化以及390px布局均通过。原 v0.5.1 PDF/manifest 未改，硬笔轨迹仍属未经专家验证的工程骨架。

---

## A2.1 汉字基本笔画动作语法实验（已独立部署）

用户要求从横、竖、撇、折、钩本身研究真实动作，而不再把重点仅放在笔速或模拟笔压上。新增 [独立的基本笔画 A/B 实验](experiments/stroke-grammar-lab.html)：A侧使用原发布稳定版，B侧同一原始SVG字形与圆头填充，但按基本笔画语义重分配笔内进度，笔尖沿原轮廓约束/保留折角的细采样曲线移动，并可查看分段动作、候选中心线和速度变化图。该方案不改变主页面正式默认动作，也不重新声称medians教学有效。详细实现/论文和风险见 [A2_BASIC_STROKE_MODEL](../docs/A2_BASIC_STROKE_MODEL.md)、[Issue #107](https://github.com/netplus/zitie/issues/107)。[PR #108](https://github.com/netplus/zitie/pull/108) 已合并 `13d0f8ae1ea37149f9dd4305c168b87e7b7b5c80`；精确 PR HEAD `206fa730038d7b7e9fb0378b5d11016d6d2f1aea` 的 [动画 CI](https://github.com/netplus/zitie/actions/runs/38036907848) 和 [Book CI](https://github.com/netplus/zitie/actions/runs/38036907780) 双通过，合入后的 [Pages #38037395286](https://github.com/netplus/zitie/actions/runs/38037395286) 真正部署成功。可访问[在线A2.1基本笔画动作实验](https://netplus.github.io/zitie/animation/experiments/stroke-grammar-lab.html)：63项Node测试、7个范例×8帧、原红色墨迹差异0、54段曲线细化、1段源回退、0越源轮廓。轨迹语义仍未教学审核，不替换稳定播放器与正式v0.5.1 PDF。

---

## A1.6 主页面稳定版／模拟笔压版双风格（已合入并部署）

用户可以在[主笔顺播放页](index.html)的「笔压风格」中直接选 **稳定版**（默认）或 **模拟笔压版**。两种风格同用稳定 A1.3 圆头墨迹遮罩、笔画时序与纠偏圆圈轨迹；模拟笔压只改变圆形笔尖接触幅度、无白色遮挡的力度环，并显示合成力度和弧长位置曲线。切换时不重置播放位置，选择在切换字形、倍率、重播时持续生效。已增加针对9字45帧的双风格墨迹/掩码一致性、控制状态与移动端的阻断测试。详见 [设计边界](../docs/A1_PEN_STYLE_SELECTOR.md)、[Issue #104](https://github.com/netplus/zitie/issues/104)。[PR #105](https://github.com/netplus/zitie/pull/105) 已合并为 `d055e2d05fcd6c39635e8ec9d15fc234451e7327`，最终 [动画 CI](https://github.com/netplus/zitie/actions/runs/38030438772) 与 [全书 CI](https://github.com/netplus/zitie/actions/runs/38030438681) 双通过，合入后的 [Pages #38030935433](https://github.com/netplus/zitie/actions/runs/38030935433) 已实际部署成功。当前可直接在[主播放页](https://netplus.github.io/zitie/animation/)切换风格。原始墨迹/轮廓保持不变，合成压力不应冒称真实笔压；正式 v0.5.1 PDF 不修改。

---

## A1.5 合成笔压 A/B 实验已独立上线（2026-10-10）

根据用户反馈，继续以 A1.3 稳定圆头笔迹为准，不用椭圆笔尖代替。独立增加[稳定版 vs 模拟用力 A/B 预览](experiments/pressure-lab.html)：A、B 两侧使用同一真实SVG原轮廓、原始中心线、原填充并集和同一时间轴；**只有 B 的小圆圈接触程度、可选无白圈轮廓和压力曲线变化**，对照原墨迹必须逐像素完全一致。模拟压力是 0–1 合成强度，非力传感器实测/人体标定，且不把速度误当压力。研究数据授权边界、论文和算法详见 [A1.5研究记录](../docs/A1_PRESSURE_RESEARCH.md)、[Issue #101](https://github.com/netplus/zitie/issues/101)。[PR #102](https://github.com/netplus/zitie/pull/102) 已合并为 `c2c77a911aaba88b665ca6d2e20062d75fb199d7`，最终精确提交的 [动画 CI](https://github.com/netplus/zitie/actions/runs/38007144993) 与 [Book integrity](https://github.com/netplus/zitie/actions/runs/38007144972) 双通过；合入的 [GitHub Pages #38007775010](https://github.com/netplus/zitie/actions/runs/38007775010) 已实际部署。可直接打开[合成笔压在线实验](https://netplus.github.io/zitie/animation/experiments/pressure-lab.html)。6字×10帧真实浏览器 A/B 原始墨迹差异0像素，圆圈位置错误0；这不代表获得了真实笔压数据或教学审批。

---

## A1.3 稳定版圆圈与墨迹前缘同步（已合入并部署）

用户明确更偏好稳定版 A1.2.3 的圆头笔迹，后续不以椭圆笔尖取代它。本轮仅修复折、钩等笔画中“墨迹已经向前写，圆圈却仍落后”的视觉不同步：使用原圆头笔刷已经落墨的几何范围，计算单调递增的 **显示圆圈前缘**；中心线、笔速、原SVG填充、原始笔顺、墨迹逐帧测试全部保持稳定版原样。其几何是视觉指示而非真实笔尖压力和教学审核。详见[设计与回归](../docs/A1_STABLE_FRONTIER.md)、[Issue #98](https://github.com/netplus/zitie/issues/98)。[PR #99](https://github.com/netplus/zitie/pull/99) 已合入 `main`（`1ec9afb8b9f03657089cf61dd5551ed1fc0952ed`），最终 A1+Book CI 双通过，合并后的[GitHub Pages #37937065049](https://github.com/netplus/zitie/actions/runs/37937065049)已完成真实部署。[稳定版在线体验](https://netplus.github.io/zitie/animation/)已包含此修复。数值测试不等于独立教师审定。

---

## A1.4.4 真轮廓起笔与深色笔尖

A1.4 B侧不再假定原 median 首点就是字形起点，而是沿真实原始 SVG 轮廓寻找切向支撑点，先沿源方向显露左侧起笔轮廓，再进入原有笔内进度。恢复默认可见的深色笔尖，避免以前白圈造成移动空洞错觉。A/B 质量测试包括 512/768/1024px 的真实浏览器起笔投影检查和11组带笔尖关键帧。详见 [技术说明](../docs/A1_SOURCE_ONSET.md)。稳定版和正式字帖均不受影响。

---

## A1.4.3 起笔覆盖修复（实验版）

对“一”左上笔头延迟填红的反馈，实验性 source-fitted 补全由起笔固定延迟
改为初段随笔尖同步，笔刷宽度平滑压下，再逐渐切换正常行笔延迟；
新增早期3–5%空间进度的512/768/1024三分辨率逐像素源轮廓检验。
详见 [A1.4 实验说明](../docs/A1_PEN_CONTACT_EXPERIMENT.md) 与
[Issue #93](https://github.com/netplus/zitie/issues/93)。
仅影响独立实验 B 模型，默认 A1.2.3 保持不变。

---

## A1.4 独立笔尖 A/B 实验（不替换稳定播放器）

另有[六个部首的可变接触椭圆笔尖实验](experiments/pen-lab.html)，左侧直接使用 A1.2.3 稳定渲染器，右侧采用合成笔压/倾角与明确标注的折前驻留、短促出钩微时序；两个版本使用相同原始中心线、笔顺、最终原轮廓和统一 elapsed time。详见[实验说明与测试](../docs/A1_PEN_CONTACT_EXPERIMENT.md)和 [Issue #88](https://github.com/netplus/zitie/issues/88)。仅当独立 CI 与 Pages 部署完成后才认为线上可用；**合成动作参数不代表真实笔压或教学审核。**

---

## A1.4 工程研究，不更改当前播放器

已检查 [2014 静态书法恢复动画、2000 虚拟笔刷、Sigma–lognormal 手写动力学、2026 中文手写研究，以及 Tegaki/Perfect Freehand 的真实实现](../docs/A1_PEN_CONTACT_RESEARCH.md)，提出“笔内子动作规划 → 压力/接触状态 → 椭圆笔尖印迹累积”的实验架构。该设计尚未部署、参数未经实测，不改写 source medians、normative order 或已发布页面。详见 [Issue #88](https://github.com/netplus/zitie/issues/88)。

---

# A1.2.3 墨迹渲染修复（按来源轮廓裁剪的连续笔刷）

替换了旧的自交法向四边形遮罩与收笔补丁，采用独立圆头笔迹片段的递增并集，确保已显示墨迹不因填充规则而消失，并只显露原有 SVG 轮廓内的部分。保持已有位置自适应笔速与 0.5×～3× 按钮。逐像素集包含校验及真实 Chrome 关键帧复核见[填充算法设计](../docs/A1_FILL_AUDIT.md)。全部轨迹仍属于工程预览，教学方向不因渲染修复而获得规范背书。

---

# A1.2.2 分阶段笔速与直接倍率按钮

播放器现在按实际 medians 的距离和几何转折生成可复验的**位置→时间非线性映射**；直行相对较快，起收笔与明显折转处减速。全局速度按钮可直接点击 0.5×/1×/1.5×/2×/3×，不会重置笔内速度节奏。笔迹遮罩以更密的局部宽度采样和收敛的笔尖前沿绘制；原始最终轮廓字节不改。研究来源、公式、可调整常数、验证门槛和非实测免责声明：[A1 Motion](../docs/A1_MOTION.md)。

---

# A1.2.1 交互与笔迹精细度改进

播放器新增点击式主部首字形卡片、按批次筛选和搜索（汉字、规范已核细笔名、批次、主项ID）、逐字切换和可拖动时间轴，保持完整播放控制与离线部署。原固定170单位圆头遮罩已替换为根据原始填充轮廓测量局部左右宽度、沿未经修改的中心线推进的 SVG 渐进遮罩；最终完成状态严格复用原矢量。**此项属于图形呈现优化，不提供新增的规范审核或真实毛笔力度数据。** 参见 [A1.2.1 设计与 QA](../docs/A1_UX_PRECISION.md)。

---

# A1 experimental offline SVG stroke animation

**Browser preview:** [Official GitHub Pages demo](https://netplus.github.io/zitie/animation/) (deployed successfully on 2026-10-09, [run #37880818335](https://github.com/netplus/zitie/actions/runs/37880818335)). See [hosting notes](../docs/A1_PREVIEW.md). This engineering preview remains unapproved for pedagogical trajectory correctness.

**Open `animation/index.html` directly in a modern browser**, including via `file://`. No server, npm dependency, internet access or separate font is needed. Choose from nine authentic primary radicals, play/pause, replay, previous/next, single-stroke repeat, speed adjustment and show-full-shape.

The red stroke is the **actual existing filled SVG outline** revealed along the vendor's ordered **median writing path**; the final full silhouette is never approximated by the mask. Future outlines are pale gray, earlier strokes dark gray. One deterministic timeline drives all controls.

**Engineering prototype only** — the source medians are structurally present, but their starts, pen directions, folds and hooks are **not yet independently teaching-reviewed**. Do not market this as validated writing instruction. Fine names are displayed only when the source policy allows them. See [A1 technical/audit design](../docs/A1_ANIMATION.md), [source notice](NOTICE.md), [reviewing Issue #79](https://github.com/netplus/zitie/issues/79) and [existing source gate #4](https://github.com/netplus/zitie/issues/4).

Smoke checks on a developer machine:

~~~sh
node --test animation/tests/timeline.test.cjs animation/tests/precision.test.cjs
bash scripts/a1_browser_smoke.sh
# After existing python scripts/acquire_vectors.py --batches B01 ... B21:
python scripts/a1_audit.py --require-all
~~~

The browser check needs Chrome/Chromium, Python 3, and a free localhost port. It opens only local assets and waits for real animation frames. Data materials are source-pinned to a fixed upstream revision; the 201 original JSONs are downloaded to `build/vectors/` by existing scripts, not checked into the Git tree. Nine packaged samples run offline.

*Classification*: 201 main radicals in the canonical book; 9 **playable engineering previews**; 0 **trajectory teaching approvals** as of A1.2. Future attached-form, comparison, recall and full-word position-migration assets must be counted separately.
