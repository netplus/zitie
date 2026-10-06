# B05 位置迁移来源语义复核

来源：S03 / GF0014—2009，复用已入库的原页目标行审读。只抽取名称中的显式位置词；裸名称不据此推断正式位置。最终 `position_migration` 仍须回整字视觉核验。

| 主项 | S03名称 | 显式位置角色 | 结论 |
|---|---|---|---|
| 无 | 无（wú） | 无 | no_explicit_position_word；whole-character verification pending |
| 犬 | 犬（quǎn） | 无 | no_explicit_position_word；whole-character verification pending |
| 歹 | 歹（dǎi） | 无 | no_explicit_position_word；whole-character verification pending |
| 车 | 车（chē） | 无 | no_explicit_position_word；whole-character verification pending |
| 牙 | 牙（yá） | 无 | no_explicit_position_word；whole-character verification pending |
| 戈 | 戈（gē） | 无 | no_explicit_position_word；whole-character verification pending |
| 瓦 | 瓦（wǎ） | 无 | no_explicit_position_word；whole-character verification pending |
| 止 | 止（zhǐ） | 无 | no_explicit_position_word；whole-character verification pending |
| 贝 | 贝（bèi） | 无 | no_explicit_position_word；whole-character verification pending |
| 见 | 见（jiàn） | 无 | no_explicit_position_word；whole-character verification pending |

牙第2笔“撇折/竖折”继续 `conflict_fail_closed`；本位置语义复核不参与该冲突裁决。

限制：不证明GF0011—2022主附身份，不证明整字内比例、几何压缩、字形变体或完整书写时序；不得据此把位置变体升级为最终reviewed。

## 2026-10-06 Unicode 18.0 RS二级身份定位

来源：Unicode 18.0.0 `RSIndex.txt`（源文件日期2026-07-30）。本节只增加Unicode标量值与radical-stroke分类的二级交叉证据，不改变GF0011—2022正式主部首身份pending状态，也不参与牙第2笔“撇折/竖折”冲突裁决。

| 主项 | Unicode | RS记录 | RS列 |
|---|---|---|---|
| 无 | U+65E0 | 71.0 | traditional_radicals |
| 犬 | U+72AC | 94.0 | traditional_radicals |
| 歹 | U+6B79 | 78.0 | traditional_radicals |
| 车 | U+8F66 | 159.0 | chinese_simplified_radicals |
| 牙 | U+7259 | 92.0 | traditional_radicals |
| 戈 | U+6208 | 62.0 | traditional_radicals |
| 瓦 | U+74E6 | 98.0 | traditional_radicals |
| 止 | U+6B62 | 77.0 | traditional_radicals |
| 贝 | U+8D1D | 154.0 | chinese_simplified_radicals |
| 见 | U+89C1 | 147.0 | chinese_simplified_radicals |

源文件：https://www.unicode.org/Public/18.0.0/charts/RSIndex.txt 。RSIndex第1列为radical-stroke pair，第2—5列依次为traditional、Chinese simplified、non-Chinese simplified、secondary non-Chinese simplified排序列。本节不支持部首名称、附形、笔顺、细笔名或位置几何结论。
