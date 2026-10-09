# v0.5.1 纸质打印验收：可直接打印的 11 页代表包

**状态：数字预检通过，实物打印尚未进行。** 本 QA 包不是 v0.5.2，也不是用来替代299页的 v0.5.1 正式交付文件。

- 当前正式版：`deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf`，SHA256 `7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90`。
- 纸面测试包：[`qa/print/v0.5.1/v051-print-acceptance-samples-A4.pdf`](../qa/print/v0.5.1/v051-print-acceptance-samples-A4.pdf)，共11页，第1页为独立校准和记录页；后10页精确导出已发布版本的1、2、6、34、263、264、265、284、292、299页。
- 校准：A4纵向，**100%/实际大小**输出，关闭自动适配/缩放。测量第1页的100 mm标尺及原页田字格尺寸，记录实际值与预期差异。应核查所有阴影/红色打印层次。
- 纸面项目：颜色（红笔/灰笔/淡描）、标点位置（尤其句号、顿号）、拼音、正文、格线、外边距、缺字/黑块、单双面/装订；详细勾选栏和打印设备设置栏位于校准页。
- 对纸面验收结果，**只**使用打印环境中取得的打印日期、设备/驱动、设置、测量与可见缺陷。未经纸面检查的自动化验证结果只能写入 `digital_preflight`，绝不写成 `physical_print_passed`。
- 如纸测未通过，记录原页码、问题描述、打印配置及可能的重现步骤；必要时开新版本勘误 PR，旧正式 PDF 不覆盖。合格后才可关闭 [Issue #77](https://github.com/netplus/zitie/issues/77)。

复现：

```sh
python scripts/build_v051_print_qa.py
python scripts/test_v051_print_qa.py
```

脚本只读取已验证 SHA256 的原版 PDF 和**系统安装的** AR PL KaitiM GB 字体；仓库中未加入原始字体文件。测试比较原版10页的提取文本、72dpi渲染、A4页面大小和包的可重复生成 SHA256。详细数字预检证据见 `data/evidence/v051-print-qa-preflight-20261009.json`。
