# P3 其它字段扫尾完成检查点

日期：2026-10-06  
范围：B04—B21 共171个阶段1在编主项。B01—B03既有content_ready内容不在本阶段重复计数。

## pronunciation

最终状态：
- reviewed：126
- conflict_fail_closed：11
- not_applicable：34
- ordinary pending：0

本轮新增GF0015—2010原页审读：
- 25个GF0023精确规范字进入S06核验；
- 14项有直接字条或明确词素读音并关闭；
- 11项在初/中/高三级相应拼音区间原页均无目标条目/明确目标词素，收口为 `conflict_fail_closed_no_S03_or_S06_target_pronunciation`；
- 34个非GF0023精确目标的部件型项目，S03无目标自身读音，收口为 `not_applicable_P3_nonlexical_component_no_direct_target_self_pronunciation`，不借名称例字或古典字典读音。

证据：
- `data/evidence/P3-pronunciation-GF0015-original-page.json`
- `data/evidence/P3-pronunciation-nonlexical-component-not-applicable.json`

## component_name

最终状态：
- reviewed：143
- deferred to P4 exact-name gate：28
- ordinary pending：0

20项状态债在P3第一轮同步为S03 reviewed；27项S03完整主体表无精确独立主形条目，另B21龠本轮完成S03序号1—514完整主体表排除审读，全部转P4 GF0011—2022精确名称门槛，不标reviewed。

证据：
- `data/evidence/B08-component-name.json`
- `data/evidence/B14-component-name.json`
- `data/evidence/P3-component-name-S03-no-exact-route-P4.json`
- `data/evidence/B21-component-name-S03-applicability.json`

## structure

最终状态：
- reviewed：134
- deferred to P4 exact-identity gate：37
- ordinary pending：0

P3第二轮对100个S07未直接关闭项目处理：
- 63个GF0023精确规范字由S07+GF3001规范集合收口：15 undecomposable、48 decomposable；
- 37个非GF0023精确目标的部件型项目转P4 GF0011—2022精确目标身份/主附关系门槛，不标reviewed。

证据：
- `data/evidence/P3-structure-GF3001-synthesis.json`
- `reviews/P3-structure-GF3001-synthesis-20261006.md`

## 来源通道

S06/GF0015—2010 已加入 source-probe 可重复恢复：
- blob: `13c76ed4c0dd835d356dd2c4c0504e050a576061`
- bytes: 19,262,366
- pages: 157
- SHA256: `0d647e1378847480364e2603030fe6aa6102d99320c42cac631b2fb3155d18ce`
- successful run: `37449756736`
- artifact: `11406995313 normative-reference-acquisition`

同时修正历史来源ID一致性：GF3002—1999统一使用S08；S06保留给catalog既有GF0015—2010。

## 阶段结论

P3达到退出条件：除P4明确负责的GF0011—2022精确身份/名称/主附关系与位置迁移外，pronunciation/component_name/structure均无普通pending。

下一活动阶段：**P4 GF0011—2022精确身份与位置迁移**。

P3完成不改变content_ready总数，不代表artwork、PDF、manifest、CI或release完成。
