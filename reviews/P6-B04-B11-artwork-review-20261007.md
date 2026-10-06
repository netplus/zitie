# P6 B04—B11 累计笔画 artwork 视觉复核

日期：2026-10-07  
范围：B04—B11，共80个主部首。  
执行者：ChatGPT；同一Agent，不称独立双人审定。

## 审图材料

- 固定绘图材料：Hanzi Writer / Make Me a Hanzi revision `68d10a4b21150cae5e1ebbd223eed289cf32d90c`；
- workflow run：`37548434948`；
- artifact：`11452390328 p6-artwork-review-b04-b11`；
- artifact digest：`sha256:0d010d8e219bde36cac95fb4fcb08c2adf40e72c4075f1c7f42d8c8817bed4f0`；
- 每个主项一页：完整字形 + 每一步累计笔画，当前笔红色、此前笔深灰；
- 8个批次PDF全部渲染为120dpi PNG，逐批contact sheet实际查看。

## 结果

- B04—B11：**80/80 artwork reviewed**
- artwork conflict：**0**
- ordinary artwork pending：**0**
- targeted second pass：牙、瓦、廴、心、罒

检查内容：
- 矢量笔数与P5已终审内容一致；
- 累计笔画顺序与canonical stroke order一致；
- 当前笔红色、旧笔深灰关系正确；
- 完整字形轮廓连贯，无明显裁切或重叠；
- 折钩、包围和易混项目做额外单页复看。

牙的P2细笔名语义冲突保持原状：P6只接受当前绘图形态/顺序，不据artwork消解“撇折/竖折”等命名冲突。

## 证据

- `data/evidence/P6-B04-artwork-review.json`
- `data/evidence/P6-B05-artwork-review.json`
- `data/evidence/P6-B06-artwork-review.json`
- `data/evidence/P6-B07-artwork-review.json`
- `data/evidence/P6-B08-artwork-review.json`
- `data/evidence/P6-B09-artwork-review.json`
- `data/evidence/P6-B10-artwork-review.json`
- `data/evidence/P6-B11-artwork-review.json`

## 边界

本轮授予的是`artwork_ready`，不是final layout/PDF/release：
- A4正式页面布局、练习格密度、复杂字分页仍需P6后续统一版式review；
- 实际送审PDF归档、manifest、全书视觉QA和release属于P7；
- 第三方矢量仍只是绘图材料，规范语义权威来自前序内容证据。
