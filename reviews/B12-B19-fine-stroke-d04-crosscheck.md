# B12—B19 D04独立二次细笔名交叉

日期：2026-10-06  
范围：B12—B19，共80个不同主部首。

## 第二套二次源

- repository：`cburgmer/cjklib`
- `cjklib/data/strokeorder.csv` blob：`d58796ec5e2c9ae5a5b3f1314c533a8ae2c47c31`
- `cjklib/data/strokes.csv` blob：`842caa32a1637b14f2ea2e9a791e180df6a50e81`
- license / notices：`COPYING` blob `0a9605dc2e9edc209df6230f0dd0695e0c197799`

D04与此前D03/cnchar相互独立，均只作为secondary data，不替代规范原页。

## 80项结果

- **22项**：两套二次数据逐笔名称序列完全一致；
- **5项**：两源兼容，仅存在粒度差异（如“撇/竖撇”）：皮、虍、酉、辰、鬼；
- **8项**：两套二次数据冲突并fail-closed：毋、鸟、臣、虫、缶、舟、里、角；
- **4项**：D03/cnchar未覆盖，但D04/cjklib成功补定位：屮、疒、癶、覀；
- **41项**：D04无目标条目，保留原D03状态。

## 冲突处理

所有8项冲突都只升级为`conflict_fail_closed_secondary_sources_disagree_fine_stroke_names`，不裁决哪套二次数据正确，必须回GF2001/GF0023/S04等规范原页。

## 边界

两套二次数据即使完全一致，也仍不等于规范原页reviewed；本轮不授予最终`fine_stroke_names reviewed`，也不授予GF0011—2022精确身份、位置变体、artwork、PDF或release结论。
