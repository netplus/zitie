# 《循序渐进汉字部首字帖》v0.5.1

**正式版** · A4纵向 · 299页 · 201个主部首。

本版本修正 v0.5.0 中部分嵌入式 UMingCN 字体的中文横排句号、顿号位置，使字形落点符合居左下的排版要求：

- **句号“。”201处**、**顿号“、”82处**，合计283处，影响41页。
- 更新全书558处版本标识；其余笔顺矢量、格线尺寸、教学正文和读音结构均保持不变。
- 保留**238个书签**及**50个内部跳转**。完整299页差异核验、独立复核与确定性PDF派生已通过仓库CI。
- 预防性审计确认同类 UMingCN 嵌入字体的 **逗号173处、分号83处、冒号202处** 无同类偏居中问题；因此不额外改动 PDF。

## 正式 PDF

`zitie-v0.5.1-A4.pdf`（299页，7,478,502字节）

SHA256：`7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90`

原文件仓库路径：`deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf`。

本 GitHub Release 附件必须与仓库版本逐字节一致，绝不替换已发布的 v0.5.0 或历史RC文件。源为已验收的RC3终检版精确衍生PDF，不冒称更早版本源码的直接编译产物。

## 使用建议与限制

建议使用彩色打印，保持纸张为实际100%尺寸的 A4，避免“适应纸张”造成田字格缩放。**尚未进行实物纸张打印验收**。与 GF0011—2022等规范来源相关的未获证精确字段继续采用 fail-closed 教学限制，参考[来源Issue #4](https://github.com/netplus/zitie/issues/4)。

验证与勘误证据：[v0.5.1 原勘误记录](https://github.com/netplus/zitie/blob/main/reviews/v051-punctuation-erratum-20261008.md) · [标点预防性审计](https://github.com/netplus/zitie/blob/main/reviews/v051-punctuation-preventive-audit-20261009.md)。
