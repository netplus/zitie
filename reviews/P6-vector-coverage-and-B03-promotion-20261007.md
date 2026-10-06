# P6 启动检查点：全书矢量材料覆盖与B03状态正规化

日期：2026-10-07

## 全书矢量材料覆盖

固定绘图材料：Hanzi Writer / Make Me a Hanzi revision `68d10a4b21150cae5e1ebbd223eed289cf32d90c`。

P6 vector coverage workflow run `37513572597` 实际遍历B01—B21全部201个主项，逐项下载固定revision矢量并以已经终审的内容笔数做一致性检查：

- target：201
- compatible：**201**
- missing：**0**
- stroke_count_mismatch：**0**
- other_errors：**0**
- artwork_ready_granted：**0**

临时artifact：`11435744872 p6-vector-coverage`，digest `sha256:1db8dd6f85a8d66f3168aa23f93c22d71fc30ac997a8286faf977d9ae028fa67`。

这只关闭“绘图材料是否存在、笔数是否一致”的P6材料门槛；**不授予任何新项目 artwork_ready**。

## B03 P6正规化

B03十项此前已经在2026-09-30完成真正的逐笔矢量人工复核：
- 固定同一Hanzi Writer revision；
- 对照已审S02/GF0023—2020与S04原图；
- 每一步累计渲染，当前笔/旧笔关系逐项检查；
- 10项共34笔，未发现矢量笔数、顺序或记录的笔形关系冲突；
- 白第3笔专项确认为“横折”无钩；
- B03 vector source SHA和逐项结果保存在`data/evidence/B03-artwork.json`。

此前B03的`artwork_ready_local_candidate`主要因为PDF尚未归档，而不是artwork复核未完成。P6按“artwork与PDF归档分离”的阶段模型，将B03正规化为 **artwork_ready**；其PDF归档、manifest和正式发布仍由P7独立处理。

## 边界

- B01/B02保持既有artwork_ready；
- B03本轮不声称重新做了一次独立视觉审定，而是把已真实完成的artwork复核映射到P6状态模型；
- B04—B21当前只有“vector material compatible”结论，仍须逐项规范原图/累计笔画人工复核后才能升级artwork_ready。
