# B16阶段1内容复核

批次：B16  
主项：赤、豆、酉、辰、豕、卤、里、足、邑、身  
状态：in_progress（人工内容稿已形成；data/B16.json写入受阻）

## 基线定位
复用仓库已实际审读并登记的S01-2009主表物理页6—8／原印3—5，当前2009基线索引把十项连续定位为main_id 151—160，均处于7画分组。由于本轮`data/B16.json`创建操作被连接器安全检查明确拒绝，且机器evidence也尚未入库，本记录不把baseline_identity、main_id或stroke_count升级为reviewed，只作为人工核对后的候选定位。

原始错误：

`This tool call was blocked by OpenAI's safety checks. Please double check what you are sending.`

## 十项阶段1内容稿

| 主项 | 候选ID | 基线笔数 | 整字语境 | 教学提示与迁移边界 |
|---|---:|---:|---|---|
| 赤 | 151 | 7 | 赦（左部） | 先识别七画基线主形；逐笔顺序待目标行确认。“赦”仅作迁移语境，左部压缩不自动视为正式附形。 |
| 豆 | 152 | 7 | 豌（左部） | 先辨认整体框架；口部与下部笔组的逐笔关系待核。左部豆的真实形态和时序回整字原页确认。 |
| 酉 | 153 | 7 | 酒（右部） | 先识别框架与内部横画；收框关系不凭静态字体推断。右部酉的比例和时序待整字证据。 |
| 辰 | 154 | 7 | 辱（上部） | 先识别七画主形；折、撇、捺类细笔名待原页裁决。上部压缩形态不从独体辰直接外推。 |
| 豕 | 155 | 7 | 家（下部） | 先识别七画基线主形；弯钩、撇捺类细名待目标规范。下部豕的真实笔形和时序须回完整整字。 |
| 卤 | 156 | 7 | 卤（独立字） | 本轮只保留独立字语境，不强行指定位置变体。任何偏旁形态、主附关系或替代字形继续待核。 |
| 里 | 157 | 7 | 埋（右部） | 先识别七画主形；框内横竖关系的真实笔顺待目标行确认。右部收窄不能解释为减笔。 |
| 足 | 158 | 7 | 跑（左部） | 先识别独体足；“跑”仅作迁移线索，不把常见足字旁无证据地等同于独体足。正式附形待GF0011—2022与整字证据。 |
| 邑 | 159 | 7 | 都（右部） | 先识别邑主形；“都”右侧阝只作迁移线索，不直接认定为邑的正式附形。主附关系、字形和时序均待规范裁决。 |
| 身 | 160 | 7 | 躬（左部） | 先识别七画基线主形；内部横撇关系的顺序待原页核验。左部收窄与独体主形分开记录。 |

## 字段状态
- teaching_text：已形成阶段1人工稿；
- whole_character_context：已选择，但全部保持`pending_whole_character_verification`；
- structure：pending，不授予正式结构分类；
- baseline_identity / main_id / stroke_count：候选，待data/evidence真实入库后才能升级reviewed；
- stroke_order / fine_stroke_names / pronunciation / component_name：pending；
- GF0011—2022精确主项字形、附形、名称和编码：pending。

本记录不授予content_ready，更不授予artwork、layout、PDF或release结论。

## 2026-10-06 Unicode 18.0 RS二级身份定位

来源：Unicode 18.0.0 `RSIndex.txt`（Unihan Radical-Stroke Index Collation Data，源文件日期2026-07-30）。本节逐项按Unicode标量值精确定位RS记录；仅作为`target_identity`的二级Unicode/RS交叉证据，**不替代GF0011—2022对201主部首身份、主附关系、名称或编码的正式裁决**。

| 主项 | Unicode | RS记录 | RS列 | 结论 |
|---|---|---|---|---|
| 赤 | U+8D64 | 155.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |
| 豆 | U+8C46 | 151.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |
| 酉 | U+9149 | 164.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |
| 辰 | U+8FB0 | 161.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |
| 豕 | U+8C55 | 152.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |
| 卤 | U+5364 | 25.5 + 197.0 | traditional_radicals + chinese_simplified_radicals | 多RS关联，全部保留，不自动裁决 |
| 里 | U+91CC | 166.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |
| 足 | U+8DB3 | 157.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |
| 邑 | U+9091 | 163.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |
| 身 | U+8EAB | 158.0 | traditional_radicals | 标量值精确定位，GF0011—2022仍pending |

源文件：https://www.unicode.org/Public/18.0.0/charts/RSIndex.txt 。RSIndex为分号分隔文本：第1列是radical-stroke pair，第2—5列依次为traditional、Chinese simplified、non-Chinese simplified、secondary non-Chinese simplified排序列。本节不支持笔顺、细笔名、部件名称或位置变体结论。
