# B12—B19笔顺二次数据定位

日期：2026-10-05  
范围：B12—B19，共80个不同主部首。

## 数据源

- 仓库：`takushun-wu/han-ideographs-stroke-order`
- 文件：`order.tsv`
- blob SHA：`ecf422f0bb9d1d07d661250796269bfa752ebd`
- 许可证：CC0-1.0
- 项目声明的数据来源包括GF0023—2020《通用规范汉字笔顺规范》、ExcelHome笔画序库、CNMan/UnicodeCJK-WuBi。

这是二次数字化数据，只用于目标定位和一致性检查，不替代GF0023—2020规范原页视觉review。

## 结果

B12—B19每批10项，共80项：
- 80/80在固定TSV blob中精确找到目标字；
- 80/80派生笔数与canonical baseline笔数一致；
- 0目标缺失；
- 0笔数冲突。

本轮为每个目标保存：
- 派生笔顺码；
- Unicode；
- 派生排序序号；
- 派生笔数；
- 固定blob来源。

## 状态口径

这些批次此前没有canonical笔顺候选码，因此本轮不称“候选码交叉通过”，而是把`stroke_order`从`pending_target_row`推进到：

`secondary_GF0023_derived_order_located_original_page_pending`

即：二次GF0023派生数据已经完成定位，但GF0023规范原页视觉review仍未完成。

`fine_stroke_names`不从1/2/3/4/5五类笔顺码推导，继续单独等待适用规范原页。

本记录不授予GF0011—2022精确身份、正式结构、正式位置变体、artwork、PDF或release结论。
