# P1：B12—B19 GF0023—2020笔顺规范原页复核

日期：2026-10-06  
范围：B12—B19，共80个不同主部首。  
执行者：ChatGPT；本轮为同一Agent原页审读，不称独立双人审定。

## 原件

S02：GF0023—2020《通用规范汉字笔顺规范》。

- SHA256：`0ff0890afc34c5e486edeebafb05350dec69a7bf0d1d75044d7d3f7b722ec3d0`
- 字节数：51,412,684
- 页数：581
- 通过`sources/normative-access.json`记录的run `37402630995` / artifact `11385916300`恢复并校验。

本轮对68个可精确定位目标生成目标行放大裁图并逐项查看；对12个未精确定位目标，按secondary locator给出的数字笔顺码回到GF0023按笔顺码排序的相邻行原页逐项查看其前后边界。PDF文字层只用于索引字符、表序号、UCS和数字笔顺码，不替代视觉审读。

## 结果

- B12：5 reviewed / 5 pending
- B13：8 / 2
- B14：10 / 0
- B15：9 / 1
- B16：10 / 0
- B17：8 / 2
- B18：10 / 0
- B19：8 / 2

合计：**68/80项在GF0023原页精确定位并视觉核对；12/80项在对应笔顺码邻接区间未见精确目标，继续pending。**

68项规范原页数字笔顺码与既有secondary locator全部一致，**0冲突**。

## 12个GF0023未精确定位项目

屮、巛、疒、疋、癶、覀、虍、糸、釆、龺、髟、鬥。

“未定位”只表示：在GF0023按数字笔顺码排序的目标邻接区间原页中没有看到精确目标条目。**不声明这些项目没有规范笔顺，也不把secondary数据、相近字形或位置变体替代为GF0023原页结论。** 这些项目转入P1残余队列，继续检查S04或其它适用规范。

## 字段状态

精确定位68项：

`reviewed_GF0023_2020_original_page`

未精确定位12项：

`GF0023_2020_original_main_table_reviewed_exact_target_not_located_alternative_source_pending`

## 证据文件

- `data/evidence/B12-stroke-order-original-page.json`
- `data/evidence/B13-stroke-order-original-page.json`
- `data/evidence/B14-stroke-order-original-page.json`
- `data/evidence/B15-stroke-order-original-page.json`
- `data/evidence/B16-stroke-order-original-page.json`
- `data/evidence/B17-stroke-order-original-page.json`
- `data/evidence/B18-stroke-order-original-page.json`
- `data/evidence/B19-stroke-order-original-page.json`

精确命中记录保存原印页、PDF物理页、GF0023表序号、UCS、规范数字笔顺码和visual_review标志；未命中记录保存实际审读页及目标笔顺码相邻行边界。

## P1剩余

前两轮B04—B19共160项累计：**123项stroke_order已GF0023原页reviewed，37项进入残余队列**。

下一步：
1. B20/B21；
2. 前两轮37个GF0023未精确定位项目统一转S04/其它适用规范；
3. P1全部关闭后进入P2细笔名规范原页收口。

本记录不授予fine_stroke_names、GF0011—2022精确身份、位置迁移、artwork、PDF或release结论。
