# B04—B11笔顺码派生数据交叉核验

日期：2026-10-05  
范围：B04—B11，共80个不同主部首。

## 数据源

交叉核验数据：
- 仓库：`takushun-wu/han-ideographs-stroke-order`
- 文件：`order.tsv`
- blob SHA：`ecf422f0bb9d1d07d661250796269bfa752ebd`
- 许可证：CC0-1.0
- 项目声明的数据来源包括GF0023—2020《通用规范汉字笔顺规范》、ExcelHome笔画序库及CNMan/UnicodeCJK-WuBi。

这是**二次数字化数据**，只作为交叉核验，不替代GF0023—2020规范原页视觉review，也不算独立权威来源体系。

## 结果

B04—B11各10项逐字比较canonical笔顺候选码与派生TSV：
- B04：10/10一致
- B05：10/10一致
- B06：10/10一致
- B07：10/10一致
- B08：10/10一致
- B09：10/10一致
- B10：10/10一致
- B11：10/10一致

合计：**80/80一致，0冲突，0目标缺失，0候选缺失**。

## 状态口径

- 匹配项的`stroke_order`推进为`crosschecked_GF0023_derived_dataset_original_page_pending`；
- B04已有GF0023精确目标行locator，因此状态更具体为`GF0023_2020_exact_target_row_located_derived_crosschecked_visual_review_pending`；
- 原页视觉review完成前**不得**标记最终`reviewed`；
- “牙”第2笔“撇折/竖折”是`fine_stroke_names`冲突，与本轮五大类笔顺码一致性不矛盾，继续`conflict_fail_closed`。

本记录不授予细笔名、正式位置变体、GF0011—2022精确身份、artwork、PDF或release结论。
