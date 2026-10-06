# B18阶段1内容复核

批次：B18  
主项：非、齿、黾、隹、阜、金、鱼、隶、革、面  
状态：in_progress

## 已reviewed
依据仓库已实际审读并登记的S01-2009主表物理页6—8／原印3—5，以及`data/evidence/B18-content.json`：
- 十项均属于2009版201主部首中间索引；
- main_id连续为171—180；
- 非、齿、黾、隹、阜、金、鱼、隶位于8画分组；
- 革、面位于9画分组。

这些结论只支持2009基线身份、main_id和基线笔画分组，不替代GF0011—2022逐项精确字段。

## 本轮内容复核
- 非：整字语境取“悲”顶部；只记录迁移语境，不授予正式位置变体。
- 齿：整字语境取“龄”左部；左部写法不能直接代替独体主形。
- 黾：整字语境取“绳”右部；简化字中的对应关系继续待整字核验。
- 隹：整字语境取“谁”右部；字体压缩不能解释为减笔。
- 阜：本轮只核独立阜；常见左阝只作为后续迁移线索，主附关系待GF0011—2022。
- 金：整字语境取“鉴”下部；不把钅未经证据并入独体金。
- 鱼：整字语境取“鲜”左部；不凭静态字体推定减笔或附形。
- 隶：本轮保留独立字语境，位置迁移后续另证。
- 革：整字语境取“鞋”左部；比例和完整时序须回整字核验。
- 面：本轮保留独立字语境，不从字体样式推导位置变体。

十项均已形成两条教学提示、自查句、整字语境和迁移边界，详见`data/B18.json`。

## 仍pending
- GF0011—2022精确主项字形、附形、名称和编码；
- S03目标部件名称条目；
- 逐笔笔顺和细笔名；
- 采用读音；
- 正式结构分类和位置迁移整字核验。

本记录只授予baseline字段reviewed，不授予content_ready、artwork、PDF或release结论。

## 2026-10-06 Unicode 18.0 RS二级身份定位

来源：Unicode 18.0.0 `RSIndex.txt`（Unihan Radical-Stroke Index Collation Data，源文件日期2026-07-30）。本节逐项按Unicode标量值精确定位RS记录；仅作为`target_identity`的二级Unicode/RS交叉证据，**不替代GF0011—2022对201主部首身份、主附关系、名称或编码的正式裁决**。

| 主项 | Unicode | RS记录 | RS列 | 结论 |
|---|---|---|---|---|
| 非 | U+975E | 175.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |
| 齿 | U+9F7F | 211.0 | chinese_simplified_radicals | 标量值精确定位，GF0011—2022仍pending |
| 黾 | U+9EFE | 205.0 | chinese_simplified_radicals | 标量值精确定位，GF0011—2022仍pending |
| 隹 | U+96B9 | 172.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |
| 阜 | U+961C | 170.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |
| 金 | U+91D1 | 167.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |
| 鱼 | U+9C7C | 195.0 | chinese_simplified_radicals | 标量值精确定位，GF0011—2022仍pending |
| 隶 | U+96B6 | 171.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |
| 革 | U+9769 | 177.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |
| 面 | U+9762 | 176.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |

源文件：https://www.unicode.org/Public/18.0.0/charts/RSIndex.txt 。RSIndex为分号分隔文本：第1列是radical-stroke pair，第2—5列依次为traditional、Chinese simplified、non-Chinese simplified、secondary non-Chinese simplified排序列。本节不支持笔顺、细笔名、部件名称或位置变体结论。
