# B12—B19细笔名二次定位

日期：2026-10-05  
范围：B12—B19，共80个不同主部首。

## 二次数据源

- repository：`theajack/cnchar`
- pinned ref：`b8397db3e08e88ebbf8acf92b5cbab1a7e4c1550`
- `stroke-order-jian.json` blob：`848fcb630a5a0ebbb868afd9f3f5abc63e847ac3`
- `stroke-table.json` blob：`6c07faad47c543ee06daeac22aec8eaedf11c603`
- license：MIT

这是二次数字化数据，只用于逐笔细类定位，不替代GF2001、GF0023或S04规范原页。

## 80项结果

- **62项**：取得单义逐笔细分类序列；
- **12项**：取得逐笔序列，但源自身存在同码双名：殳、穴、疋、皮、矛、虍、色、麦、龟、角、鱼、骨；
- **6项**：该二次数据不覆盖目标：屮、疒、癶、覀、龺、鬥；
- **0项**：逐笔序列长度与canonical baseline笔数冲突。

B12—B19此前canonical均没有逐笔细笔名candidate，因此本轮只形成secondary locator，不称crosscheck，也不据此选择双名中的某一项。

## 状态口径

- 单义locator：`secondary_fine_stroke_names_located_unambiguous_original_page_pending`
- 源歧义locator：`secondary_fine_stroke_names_source_ambiguous_locator_original_page_pending`
- 源未覆盖：`secondary_fine_stroke_dataset_target_missing_original_page_pending`

所有项目在适用规范原页review前均不得标最终`fine_stroke_names reviewed`。

## 并行分支历史

同名分支的早期并行推进曾在B19写入时触发tooling_write_blocker，于是先切换B20。随后B19写入已恢复成功。B20的额外locator evidence保留，但**不计入本轮B12—B19的80项主吞吐**。

本记录不授予GF0011—2022精确身份、位置变体、artwork、PDF或release结论。
