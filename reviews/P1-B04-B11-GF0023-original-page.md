# P1：B04—B11 GF0023—2020笔顺规范原页复核

日期：2026-10-06  
范围：B04—B11，共80个不同主部首。  
执行者：ChatGPT；本轮为同一Agent原页审读，不称独立双人审定。

## 原件

S02：GF0023—2020《通用规范汉字笔顺规范》。

- SHA256：`0ff0890afc34c5e486edeebafb05350dec69a7bf0d1d75044d7d3f7b722ec3d0`
- 字节数：51,412,684
- 页数：581
- 通过`sources/normative-access.json`记录的run `37402630995` / artifact `11385916300`恢复并校验。

本轮实际渲染并查看PDF物理页9—21（原印3—15页）。对可精确定位目标，另外生成目标行放大裁图逐项查看；PDF文字层只用于索引字符、表序号、UCS和数字笔顺码，不用文字提取替代视觉审读。

## 结果

- B04：10 reviewed / 0 pending
- B05：10 / 0
- B06：5 / 5
- B07：0 / 10
- B08：3 / 7
- B09：10 / 0
- B10：8 / 2
- B11：9 / 1

合计：**55/80项在GF0023原页精确定位并视觉核对；25/80项未定位精确主表目标，继续pending。**

55项的规范原页数字笔顺码与canonical候选全部一致，0冲突。

## 25个GF0023未精确定位项目

匚、冂、勹、亠、冫、冖、凵、卩、厶、廴、艹、廾、宀、辶、彐、丨、丿、丶、乛、囗、彡、夂、丬、攴、罒。

这里的“未定位”只表示：在本轮GF0023相关主表原页范围及文本索引中没有找到精确目标条目。**不声明这些项目没有规范笔顺，也不把相近字形、secondary数据或位置变体替代为GF0023原页结论。** 这些项目转入P1残余队列，继续检查S04或其它适用规范。

## 字段状态

精确定位55项：

`reviewed_GF0023_2020_original_page`

未精确定位25项：

`GF0023_2020_original_main_table_reviewed_exact_target_not_located_alternative_source_pending`

“牙”的第2笔“撇折/竖折”属于`fine_stroke_names`冲突，本轮只关闭其数字笔顺`1523`，原细笔名冲突保持不变。

## 证据文件

- `data/evidence/B04-stroke-order-original-page.json`
- …
- `data/evidence/B11-stroke-order-original-page.json`

每条精确命中记录保存：原印页、PDF物理页、GF0023表序号、UCS、规范数字笔顺码和visual_review标志。

## P1剩余

1. B12—B19 80项GF0023规范原页审读；
2. B20/B21；
3. 本轮25个GF0023未精确定位项目转S04/其它适用规范；
4. P1全部关闭后才进入P2细笔名原页收口。

本记录不授予fine_stroke_names、GF0011—2022精确身份、位置迁移、artwork、PDF或release结论。
