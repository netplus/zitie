# B15阶段1内容复核

批次：B15  
主项：齐、衣、羊、米、聿、艮、羽、糸、麦、走  
状态：in_progress

## 人工复核已完成，baseline机器evidence待入库
复用仓库已实际审读并登记的S01-2009主表物理页6—8／原印3—5，逐项对照当前2009基线索引：
- 十项均位于2009版201主部首索引的连续区间；
- 候选main_id为141—150，与现有基线索引顺序一致；
- 齐、衣、羊、米、聿、艮、羽、糸位于6画分组；
- 麦、走位于7画分组。

原计划同步写入`data/evidence/B15-content.json`，但该写操作被连接器安全检查明确拒绝。按照fail-closed规则，在机器evidence真实入库前，`data/B15.json`中的baseline_identity、main_id和stroke_count不升级为reviewed，只保留candidate状态。

原始错误：

`This tool call was blocked by OpenAI's safety checks. Please double check what you are sending.`

## 本轮新增内容
- 为十项建立阶段1正式内容稿；
- 每项补入两条教学提示、自查句、整字迁移语境、迁移边界；
- 显式增加结构字段，但结构分类本轮只记录为pending，不从整字例字或字体外观推断正式结构；
- “糸”保留规范字形／编码对应待核，不用相近现代字体形态替代规范主形；
- “走”在“超”等整字中的左下包托关系必须后续回完整整字核验。

## 仍pending
- B15机器evidence真实入库，以及由此允许的baseline字段reviewed升级；
- GF0011—2022精确主项字形、附形、名称和编码；
- 正式结构分类与整字位置关系；
- S03目标部件名称条目；
- 逐笔笔顺和细笔名；
- 采用读音；
- 位置迁移的真实整字形态和时序。

本记录只说明人工复核和阶段1内容稿已经入库；在machine evidence缺失时不授予baseline字段reviewed，更不授予artwork、layout、PDF或release结论。
