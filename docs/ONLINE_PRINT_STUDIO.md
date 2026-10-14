# P3：在线字帖打印（可调参数）

用户需求：原 PDF 练习格太大，期望像 [Z2H 汉字练字帖](https://z2h.cn/hanzi) 一样在线调整参数并打印。仅借鉴选项和交互类别；不复制第三方代码、商标、图片或字体。

## 入口和功能

入口为 `animation/print/index.html`（GitHub Pages路径 `/zitie/animation/print/index.html`）；汉字笔顺和基础书写页面均增加入口。默认 A4 纵向、15mm 田字格、10格/行、4行/字、两行描红/描淡再两行独立写。支持输入汉字、英文字母、数字、拼音；四种格型、10–25mm尺寸、列数、页边距、行距、练写行数、描红方式/数量、颜色、字形大小、描红深浅、标题和已有拼音开关。移动端有“预览/打印”浮动操作栏。

填写完成后点“打印／保存PDF”，在浏览器的原生打印对话框里选择 A4、**100%实际大小**、页边距“无”、关闭页眉页脚，选择打印机或另存为PDF。网站没有服务器端 PDF 导出接口；练习内容完全在浏览器排版、不会上传，不自动保存孩子的练习内容。

## 数据边界

201个主部首取 Pages 部署时重建的 `animation/book-pack.js`（已审核v0.5.1正式PDF同源矢量轮廓），运行时必须匹配其正式PDF SHA256 `7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90`。不改SVG outline/median、笔顺或教学数据。未收录汉字以终端系统字体显示，并在练习行标注“系统字体（未审核笔顺）”，也不编造拼音。字母／数字／拼音取现有 `animation/foundations/data.js` 独立书写数据；部分拼音模型仍待教学复核，较长拼音音节缩放进一格后可能较小。未捆绑第三方字体、CDN、受限教材文件或孩子的书写记录，遵守 `animation/NOTICE.md` 和 Arphic PL 许可。

正式v0.5.1的299页原PDF、此前v0.6.0-15mm-rc1候选PDF、`deliverables/manifest.json`、全部教学动画及其本地书写数据均不变。

## 打印几何与测试

`animation/print/core.js` 以毫米为单位决定纸张布局；可容纳列数为 `floor((210-2*margin+gap)/(cell+gap))`，每一字的练习行保持成组，自动分页，不拆开。印刷尺寸由SVG的CSS `mm` 属性与 `@page { size:A4 portrait; margin:0 }` 决定；屏幕缩放仅用于预览，不作用于打印。新版默认每页可放3组四行练习，因此6组共2页。输入超限、尺寸不允许排版时显式报错。

`animation/print/core.test.cjs` 验证A4尺寸、组合排版、分页、回退与无HTML注入；`animation/print/browser-smoke.html` 在真实Chromium桌面/手机视口测试内容与选项；`.github/workflows/print-checks.yml` 实际打印PDF后用PyMuPDF确认纸张为A4、格线为15mm、没有分页异常，并归档PDF、截图和校验报告。

第一轮 [打印CI #38507666029](https://github.com/netplus/zitie/actions/runs/38507666029)已通过Node+Chromium及3页A4，随后针对纸张留白和手机快捷入口进行第二轮修订，需要最终HEAD再次验收，不能借用历史检查作为新提交的成功证明。实际纸质打印、iOS Edge/Safari与Android实机、打印机色差及教师审美尚未验收，不能声明全部完成。
