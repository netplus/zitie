# B04—B11细笔名二次数据交叉核验

日期：2026-10-05  
范围：B04—B11，共80个不同主部首。

## 二次数据源

- repository：`theajack/cnchar`
- pinned ref：`b8397db3e08e88ebbf8acf92b5cbab1a7e4c1550`
- `stroke-order-jian.json` blob：`848fcb630a5a0ebbb868afd9f3f5abc63e847ac3`
- `stroke-table.json` blob：`6c07faad47c543ee06daeac22aec8eaedf11c603`
- license：MIT

cnchar文档明确说明五组同码笔形无法区分：卧钩/斜钩、横折弯/横折折、横折折折钩/横撇弯钩、横撇/横钩、竖折折/竖折撇。因此本数据只作为细笔名二次定位和交叉核验，不替代GF2001、GF0023或S04规范原页。

## 80项结果

- 32项：candidate与二次逐笔细分类**精确一致**；
- 5项：二次源自身存在同码双名，但candidate位于其兼容集合内；
- 20项：二次逐笔细分类已定位，但canonical没有可直接逐笔比对的candidate；
- 4项：candidate与二次数据不一致，保持fail-closed；
- 19项：该二次数据不覆盖目标字形。

canonical层因“牙”已有更高优先级的权威冲突状态而继续保留该冲突，所以实际状态分布为：32 crosschecked + 5 source-ambiguous-compatible + 19 secondary-located + 4 secondary-conflict + 19 source-missing + 牙1项existing conflict = 80。

## 二次冲突

- **几**：candidate「撇、横折弯钩」；cnchar「撇、横斜钩」。
- **凵**：candidate「竖折、竖」；cnchar「竖弯、竖」。
- **风**：candidate「撇、横折弯钩、撇、点」；cnchar「撇、横斜钩、撇、点」。
- **心**：candidate「点、斜钩、点、点」；cnchar首笔记作「点2」，第2笔记作「斜钩|卧钩」。该源本身存在命名约定和歧义，不能据此裁决candidate错误。

以上4项都只触发secondary conflict，不做最终裁决。

## 源自身歧义但candidate兼容

弋、支、攴、氏、欠。

## 既有冲突保持

牙第2笔“撇折/竖折”继续`conflict_fail_closed`；本轮cnchar二次序列只作为附加locator，不覆盖GF2001/GF0023/S04待裁决边界。

## 边界

本轮不授予任何项目最终`fine_stroke_names reviewed`。正式关闭仍需要适用规范原页。也不授予GF0011—2022精确身份、位置变体、artwork、PDF或release结论。
