# P4 完成检查点：GF0011—2022身份门槛与position_migration

日期：2026-10-06

## 阶段结果

P4退出条件已经满足：201个主部首的身份门槛与位置迁移边界均已关闭为 reviewed 或精确 fail-closed，普通pending归零。

### 1. 主部首身份

- 201/201：主部首集合成员身份 + 项目main_id连续性 **reviewed**。
- 依据：教育部/国家语委2022发布说明明确“保持原有201个主部首”，结合已审读GF0011—2009主表。
- GF0011—2022逐项精确主形、正式附形、常用名称、国际编码：**201/201 source_blocked_fail_closed**。
- 不填造2022逐项值，不从2009版、相近字形、教学位置变体或Unicode IRG混合来源反推。

### 2. position_migration

全书201项：
- **198 reviewed**
- **3 conflict_fail_closed：屮、毋、瓦**
- **0普通pending**

关键时序/改笔已经在分轮evidence中保存：
- 匚→区、弋→式、囗→国等非连续/穿插映射；
- 疒、虍等包围/半包围必须保留完整整字时序；
- 车→辆 `1512→1521`；
- 矢→知、禾→和末笔捺→点；
- 疋、竹、足等代表整字中的位置形态变化。

### 3. P3转P4门槛收口

B04—B21：
- component_name：143 reviewed + **28 source_blocked_fail_closed**；
- structure：134 reviewed + **37 source_blocked_fail_closed**；
- 两者均0普通pending。

28个名称和37个结构不是被“猜出来”，而是因为其最终判定依赖GF0011—2022精确主项/附形关系；正式逐项数据未公开，因此统一精确fail-closed。

### 4. 32个附形/位置变体候选

`data/variants.json` 的32项继续作为教学附形/位置变体候选范围保留：
- 不宣称全部为GF0011—2022正式附形；
- 正式2022角色统一 `source_blocked_fail_closed_formal_attached_role_unavailable`；
- P5/P6可基于已完成的整字迁移证据决定教学呈现，但不得把教学角色写成规范附形身份。

## 来源阻塞证据

`sources/reviews/P4-GF0011-2022-exact-fields-source-blocked-20261006.json`

公开审计确认：
- 教育部2022发布说明存在，但不提供逐项表；
- 教育部规范索引未发现可重复取得的GF0011—2022逐项正式文件；
- 公开高校规范下载区和公开Git规范镜像只定位到2009版；
- Unicode IRG后续材料引用GF0011—2022并明确标注“not released”，其GCP数据是多规范混合来源，不能反推GF0011—2022逐项表。

## 重开条件

只有在以下条件之一满足时才重开P4精确字段：
1. GF0011—2022正式全文可重复公开获取，且可验证出版身份/完整性；
2. 教育部/国家语委或等效官方机构发布逐项数据集，可验证与GF0011—2022一致。

## 阶段切换

P4完成后进入 **P5：内容终审与content_ready收口**。

P4完成不表示：
- artwork_ready；
- PDF归档完成；
- manifest完成；
- release_eligible；
- 正式出版。
