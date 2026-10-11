# A3.7 — 恢复201字字帖主播放器的稳定版/模拟笔压版

## 完成的合入、上线及实测证据

**A3.7 已上线（2026-10-11）。** [PR #129](https://github.com/netplus/zitie/pull/129) 最终 HEAD `2252d3de3df7ef9f9aa1eec3deb5d21572d52b5b` 的 [A1/Chromium CI #38138069650](https://github.com/netplus/zitie/actions/runs/38138069650) 与 [Book CI #38138069687](https://github.com/netplus/zitie/actions/runs/38138069687) 双 completed/success；合并 `main` SHA 为 `e8b4b8adefcf2381e8b0ed9a2fcd701794280c93`，对应的 [Pages #38138652608](https://github.com/netplus/zitie/actions/runs/38138652608) Configure、Upload、实际 Deploy 全 completed/success。**201字/1045笔**均生成模拟笔压曲线，14个细笔名受限主项不泄漏，12组真实 Chromium 稳定/模拟模式红墨光栅 **0 像素差异**，力环与当前笔尖100%对齐，风格切换不改变进度、倍率、播放、笔顺或源SVG墨迹；390px手机视口通过，A3.6原2090帧防超前回归不受影响。 [真实稳定/模拟截图与 QA metrics artifact #11702002988](https://github.com/netplus/zitie/actions/runs/38138069650/artifacts/11702002988)。[正式201字播放器](https://netplus.github.io/zitie/animation/book.html?id=77) 可直接使用。**模拟力值不是实测笔压，仅影响笔尖和提示，不改变墨迹宽度。**

## 用户反馈与原问题

2026-10-11 用户提供历史界面截图：“笔压风格　稳定版｜模拟笔压版”，指出迁移到完整201字的主界面后该功能丢失。问题不在笔顺或新 PDF 里：A1.6 九字旧工程（animation/index.html）一直保留了这两档，正式 A3 的 animation/book.html / book-ui.js 在移植时遗漏了三个原有脚本的引用、按钮和力度曲线 UI。

跟踪 [Issue #128](https://github.com/netplus/zitie/issues/128)。

## 设计与实现

- **直接复用 A1.6** 的 animation/pressure-style.js、animation/experiments/pressure-model.js 及 animation/experiments/gesture-data.js，不自行发明新笔压模型。
- 主页面在播放工具栏后恢复截图风格的“笔压风格　稳定版｜模拟笔压版”可访问切换按钮。
- 默认 **稳定版**：笔尖保留白描边、原半径8单位的红色圆点；模拟曲线和力度仪表隐藏，原有 A3.6 source-arc 显墨守卫持续启用。
- **模拟笔压版**：已核原中线对应的合成力度影响视觉笔尖大小与跟随圆环，显示力度百分比、阶段标签与当前笔画的归一化力度曲线；未经过真实压力传感器测量。
- **最重要的边界**：两种模式只有笔尖和附加视觉提示不同，均不改正式 v0.5.1 299页 PDF 的任何字节、不改轮廓/中心线/笔顺、不改 A3.6 1045笔源前缘守卫、不改 SVG alpha-mask、既有红墨像素或播放器毫秒时钟。切换时不暂停/seek，移动到别字时保留所选笔压风格。
- A3.5 运笔 A/B 研究页保持仅对比时间轴的独立路线；旧九字版本的原功能不改，避免改变历史回归基线。

## 已通过的质量门槛

1. Node静态/数据审计：网页必须以正确顺序加载旧三个A1.6模块；控制按钮/ARIA和 stable 默认存在；201主部首合计1045笔均能从原官方数据构造只读模拟笔压规划，14个未审核细笔画名称的主部首不被强行分配新笔形。
2. 真正 Chromium 操作：两档按键可点、按钮选中状态正确、模拟力度非实测、画布真实绘制曲线、力环与当前笔尖同心、稳定版恢复原半径和描边；至少12个代表帧确认两档**红墨像素严格一致**和 SVG mask/原字笔轮廓不变。
3. 全201字模拟风格跨字保持、在播放时切换不改elapsed/playing/速度、倒拖/跳笔/收笔正确处理力环，以及390px窄屏无横向溢出。
4. A1/A3/A3.5/A3.6 历史动作CI保持原门槛（A3.6 的2090真实逐笔帧继续执行），Book 对v0.5.1 299页及发布清单哈希全部通过；Pages确保这三个脚本、按钮和PDF在同一部署资源里。
5. PR 最终 HEAD 动画+Book双CI成功后合入，确认 merge SHA 的Pages Configure/Upload/实际 Deploy 全success，再关闭回退项并更新状态。

**含义提醒**：图示模拟力度是合成书写接触感，不等价于一支真实电子笔测到的力、也不更改毛笔墨迹粗细；如果后续要做“力度真正影响落墨”，须另做独立实验和墨迹回归，而不是借此直接修改已审SVG。
