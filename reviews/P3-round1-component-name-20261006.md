# P3 第一轮：component_name 状态债清理与P4路由

日期：2026-10-06

## 范围与结果

本轮实际推进47个不同主部首的component_name状态：

- B08十项：恢复并入库既有S03原页证据，10/10同步为 `reviewed_S03_GF0014_2009`；
- B14十项：已有 `data/evidence/B14-component-name.json` 的10个精确S03目标行，本轮10/10同步canonical；
- 另外27项：canonical此前已经明确记录 `S03_reviewed_no_exact_standalone_row_alternative_source_pending`。P4阶段明确负责GF0011—2022精确主项身份、主形/附形、名称与编码，因此这些项目从P3普通pending改为 `deferred_P4_GF0011_2022_exact_name_gate_after_S03_no_exact_row`，不标reviewed、不借相近字形补名。

27项为：支、比、屮、毋、疋、齐、羽、麦、走、足、邑、釆、青、龺、齿、黾、阜、骨、香、音、髟、鬥、麻、黍、鼓、鼠、鼻。

证据：
- `data/evidence/B08-component-name.json`
- `data/evidence/B14-component-name.json`
- `data/evidence/P3-component-name-S03-no-exact-route-P4.json`

## 当前P3边界

本轮只处理component_name。P3中component_name普通缺口现在只剩B21龠1项；27项P4路由仍未reviewed，必须在GF0011—2022精确名称证据到位后才能关闭。

pronunciation和structure没有因本轮名称处理而升级。当前主要工作量转向这两个字段。
