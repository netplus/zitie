# P6 全书 A4 版式与复杂字分页复核

日期：2026-10-07  
范围：B01—B21，201个主部首，258个练习页。  
执行者：ChatGPT；同一Agent，不称独立双人审定。

## CI 与构建材料

- PR #47：`P6: unify A4 layout and paginate complex radicals`
- workflow run：`37560963767`
- workflow HEAD：`dcb52d2af614d58eb4893228bce170f6105aade3`
- artifact：`11456961693 zitie-p6-full-layout-research`
- artifact digest：`sha256:c87ce0b3d3bd7daa5d713bc54500223daa339b62e7581141560ac84dff64b7e1`
- artifact 内 `SOURCE_COMMIT.txt`：`5efd471df1de9ee43204a32effcd7a4bfc0f2711`（PR workflow 的临时合并提交）

该 run 已实际通过：
- B01—B21全部 frozen batch 结构校验；
- 32个 validation tests；
- 11个 deliverable tests；
- B01—B21全部 research A4 build；
- B01—B21全部 PDF structural preflight；
- formal publication gate 继续 fail-closed；
- source export 与 workflow artifact upload。

## 人工视觉复核

从 workflow artifact 取回 B01—B21 的 `Bxx_draft_A4.pdf`，全部真实渲染为PNG后查看。

### 全量浏览

- 共 **258/258 练习页**以72dpi渲染；
- 按五组 contact sheet 逐组查看：
  1. B01—B05
  2. B06—B10
  3. B11—B15
  4. B16—B19
  5. B20—B21

### 高风险放大复核

- B08：10页，120dpi；重点看无独立拼音分支及稀有部件字形；
- B20：23页，120dpi；重点看10—14画复杂字分页、长教学文字与长自查句；
- B21：3页，140dpi；重点看“龠”17画三页连续分页；
- B20“黍”第2页单页放大复看：长自查句已在固定区域内换成两行，无裁切。

## 结果

- 未见可见裁切；
- 未见文字与田字格/逐笔示范重叠；
- 未见黑块或目标字形缺字回归；
- 每页保持32个练习格；
- 每页累计示范最多6步；
- 复杂字通过分页保持练写尺寸，没有缩小到难以练写；
- B20/B21长自查句保留原文并正确换行；
- B21“龠”17画按 6 + 6 + 5 步连续展示，三页尺寸一致；
- B08无独立读音项显示“读音：本项目不单列”，未伪造拼音；
- fine_stroke_names 为 fail-closed 的条目继续仅显示“第N笔”等不越权标签。

**结论：P6 layout review 通过，201/201 artwork_ready + 全书统一A4版式/复杂字分页门槛关闭。**

## 阶段边界

本记录只关闭P6。以下仍属于P7，尚未因此完成：

- 实际PDF归档到 `deliverables/drafts/`；
- `deliverables/manifest.json` 的页数、字节数、SHA256、source_commit、review_record；
- 全书PDF/目录/页码/索引的最终视觉QA；
- 目标HEAD CI；
- `deliverables/releases/` 正式稿与 release。

既有语义 `conflict_fail_closed` / `source_blocked_fail_closed` 状态全部保持不变。
