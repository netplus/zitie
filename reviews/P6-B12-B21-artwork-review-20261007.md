# P6 B12—B21 累计笔画 artwork 视觉复核

日期：2026-10-07  
范围：B12—B21，共91个主部首。  
执行者：ChatGPT；同一Agent，不称独立双人审定。

## 审图材料

- 固定绘图材料：Hanzi Writer / Make Me a Hanzi revision `68d10a4b21150cae5e1ebbd223eed289cf32d90c`；
- workflow run：`37549583534`；
- artifact：`11452452267 p6-artwork-review-b12-b21`；
- artifact digest：`sha256:c6d536587de540e2c9cb0a2ff7ff5c61ae607fc9b538a7d81f8f2e37a3e10519`；
- 每项一页：FULL + 每一步累计笔画，当前笔红色、此前笔深灰；
- B12—B21全部91页渲染为120dpi PNG，10个批次contact sheet全部实际查看；
- 屮、毋、鬥、龠另做单页放大复核。

## fail-closed标签策略

P2已有部分目标（如屮、毋、覀、糸、釆、龺、髟、鬥）没有可提升为权威结论的完整细笔名序列。P6不得为了审图伪造名称。

因此审图器对这类项目：
- 只使用已经reviewed的stroke_count / stroke_order控制绘图步数和顺序；
- 页面显示STEP 1…N，不显示未审定笔画名称；
- 不改变原有fine_stroke_names fail-closed状态。

## 结果

- B12—B21：**91/91 artwork reviewed**
- artwork conflict：**0**
- ordinary artwork pending：**0**
- current-red / previous-gray关系正确
- 累计步序与已审stroke_order一致
- 完整字形轮廓连贯，未见明显裁切或重叠
- B20高复杂度字及B21龠17画均可在审图页完整展示

本轮artwork审核不解除任何前序语义fail-closed，也不把Hanzi Writer矢量提升为规范依据。

## 证据

- `data/evidence/P6-B12-artwork-review.json` 至 `data/evidence/P6-B21-artwork-review.json`
- 临时审图artifact仅用于P6 QA，不进入deliverables。

## 阶段边界

完成本轮后，全书 **201/201 artwork_ready**。

但P6尚未结束：仍需统一正式A4版式、练习层级、复杂字分页策略和全书layout review。实际PDF归档、manifest、全书PDF视觉QA与release属于P7。
