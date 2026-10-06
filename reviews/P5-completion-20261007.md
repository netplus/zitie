# P5 内容终审完成检查点

日期：2026-10-07  
范围：B04—B21 共171个阶段1在编主项；与既有B01—B03 30项合并后形成全书201项内容终审状态。

## 验收规则

每个主项只有在以下条件同时满足时进入 `content_ready`：

1. 身份、结构、笔数、笔顺、细笔名、读音、部件名称、位置迁移等已跟踪字段均处于 terminal 状态：
   - `reviewed_*`
   - `not_applicable_*`
   - `conflict_fail_closed_*`
   - `source_blocked_fail_closed_*`
2. 两条教学提示和自查句存在；
3. whole-character context 与 position_migration 已同步到P4实际审读结果；
4. unresolved 中不再存在普通pending，只允许有明确重开条件的fail-closed/source-blocked边界；
5. 不把content_ready误写成artwork_ready、PDF archived、release_eligible或正式发布。

## 本轮状态债清理

P5没有扩新secondary源，主要清理P1—P4已闭合证据与canonical之间的状态债：

- B06/B08/B10/B14共40项：教学文案从旧“候选/待核”语气同步为与已关闭笔顺、细笔名、位置迁移一致的最终教学表述；
- B08 6项：stroke_count从`candidate_pending_target_row`同步到精确规范笔顺行支持的reviewed状态；
- B12—B21共91项：whole_character_context从旧pending状态同步到P4实际整字原页审读结果；
- B07/B11共19项：删除已经失效的候选/待核措辞，保留真正的整字时序、位置变化和形态区别；
- 清理B05/B06/B09/B10/B11/B13/B16/B21中已被后续阶段取代的历史unresolved文本；牙、矛等真实冲突保留为显式fail-closed并写明重开条件。

## 逐项终审结果

- `data/evidence/P5-B04-B12-final-content-acceptance.json`：90/90 accepted，0 blocked；
- `data/evidence/P5-B13-B21-final-content-acceptance.json`：81/81 accepted，0 blocked；
- B04—B21：**171/171 content_ready**；
- 加上B01—B03既有30项：**201/201 content_ready**。

显式保留的边界不是普通pending：
- P2细笔名：既有14项conflict_fail_closed；
- P3读音：既有11项conflict_fail_closed、34项not_applicable；
- P4位置迁移：屮、毋、瓦3项conflict_fail_closed；
- GF0011—2022逐项精确主形/附形/名称/编码：201项source_blocked_fail_closed，正式逐项数据出现后再重开。

## 阶段结论

P5退出条件 **201/201 content_ready** 已满足。

下一活动阶段：**P6 Artwork / 版式**。

P6开始后仍必须保持：
- content_ready ≠ artwork_ready；
- artwork_ready ≠ PDF archived；
- PDF archived ≠ release_eligible；
- 正式发布仍需P7全书draft、逐页视觉QA、manifest、目标HEAD CI、release candidate和全书终审。
