# P6 全书 A4 版式原型与高风险抽查

日期：2026-10-07  
阶段：P6 Artwork / 版式。  
范围：B01—B21，201个主部首。

## 基线

- main：`171e9496b0bb480da91b3bfedafa35daec0bfb4c`（PR #46 合入，201/201 artwork_ready）。
- P6版式分支：`feat/p6-layout-review-20261007`。
- 版式渲染器首次落库：`7061a3d839163a3963203c98e80e8660a83b3cd6`。
- 本地复现实验使用的源树为 PR 检查合并树 `f5f774e363d7f25f9737f7ec87bdd16ffe03ccac`；GitHub compare 对 main `171e9496...` 的文件差异为0，仅合并拓扑不同。
- 固定绘图材料沿用 P6 已审 pin：Hanzi Writer / Make Me a Hanzi revision `68d10a4b21150cae5e1ebbd223eed289cf32d90c`。

## 本轮解决的版式结构问题

旧 `scripts/build_batch.py` 仍以 B01/B02 和 <=6画为中心，无法承担全书 P6 layout gate。本轮新增独立的 `scripts/render_layout_review.py`，只生成 P6 临时版式审查候选，不触碰 deliverables/release：

- B01—B21 全部 frozen batch 均可渲染；
- 每页最多6个累计笔画步骤；
- 7画及以上自动分页，田字格和逐笔示范不因复杂度缩小；
- 练习区仍为每行8格、4行，第一行描红、第二行淡字、后两行范字+空格；
- 无独立读音时显示明确边界，不伪造拼音；
- fine_stroke_names 为 conflict/source-blocked 时只显示“第N笔”，不把候选笔名冒充 reviewed；
- 结构标签兼容 B01—B03 的旧 `structure_evidence` 与 B04以后字段化状态；
- 对楷体字库缺失的特殊部件字形启用已安装 CJK fallback，只用于版面文字显示，不改变绘图矢量。

## 全书生成结果

实际生成：

- 目标：**201/201**
- 临时 A4 版式页：**258页**
- >6画复杂目标：**53项**
- 复杂字分页规则：`ceil(stroke_count / 6)`
- 全书临时合并 PDF SHA256：
  `0471016950379008f91cf4b647b569205070400c5c25eb7ae0e4642c3c0b6fa2`

PDF preflight：258页、可打开、未加密、非XFA。

这些 PDF 只存在于 P6 临时审查环境，**没有**进入 `deliverables/drafts/`，也没有登记 manifest，更不是 release。

## 实际视觉抽查

本轮把代表性高风险页面真实渲染为 PNG 并检查：

- B01“一”：单页基础布局；
- B08“乛”：无独立读音 + 主楷体缺字 fallback；
- B12“屮”：fine_stroke_names fail-closed，不显示未审定笔名；
- B15“麦”：7画，两页；
- B20“高”：10画，两页；
- B20“鼎”：12画，两页；
- B20“鼓”：13画，三页；
- B21“龠”：17画，三页。

抽查结果：

- 当前笔红色、此前笔深灰关系正常；
- 累计步骤没有明显裁切或重叠；
- 复杂字分页后示范格未被压缩；
- 最后一页练习格保持完整4行×8格；
- 缺失/冲突读音与细笔名没有被版式层虚构。

## 当前边界

本轮只关闭“**全书版式原型能够生成，并且关键风险路径可正常分页/显示**”这一门槛。

尚未授予 `layout_ready`：必须继续完成 **258页全量视觉 QA**（含文本溢出、分页连续性、练习格、页脚来源、特殊字形、打印安全边距），并把问题修订回 renderer 后再次全量回归。

P7 仍未触发；实际 PDF 归档、manifest、全书交付 PDF QA、目标 HEAD CI 与 release 均属于后续门槛。
