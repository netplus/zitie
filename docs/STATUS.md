# 当前工程状态

更新：2026-10-07。总控#58，来源#4。

## M1已完成；当前活动阶段M2

正式[《循序渐进汉字部首字帖》v0.4.1](../deliverables/releases/v0.4.1/B01-B21_v0.4.1_A4.pdf)已归档并合入main：276页、3,748,910 bytes，SHA256 `7270104b8698603fcce4eec14037a0194c31e33b868669d0a8dd0307a090a7e7`。

发布PR #61最终HEAD `21f317f822a436470bc4e3e0421a3bcea4d3caf6`的Book integrity checks run `37588926485` completed/success；merge `e22d2075c1cc6728b60d3580ec9aaa9bb4873354`。E001—E004均resolved。M1退出证据：`reviews/M1-completion-20261007.md`及既有精确字节影响QA。不是简单把候选改名，正式前言、版本和页脚均按模式生成。

## M2：新权威来源重开，进行中

已从21批canonical数据固定六类重开集合：2022精确字段201项、细笔名14项、位置迁移3项、读音11项、名称28项、结构37项；集合重叠不相加。34项读音不适用单独排除。

入口探查已记录：教育部原说明本次打开超时；Unicode UAX38 revision42草案的混合GCP来源说明不能代替2022逐项表。本轮0项规范字段升级，M2远未等于全部解决。记录：`reviews/M2-startup-20261007.md`、`data/evidence/M2-reopen-inventory-20261007.json`、`sources/reviews/M2-entry-source-audit-20261007.json`。

下一单元：按固定集合审计适用权威原件与精确字条，先核2022逐项数据渠道及14项细笔名残余；有新证据才重开相应字段。不要回到M1重复生成PDF。

## 后续门槛

顺序为M1完成→M2进行中→M3待开始→Q1待开始。M3结束只冻结v0.5.0候选，Q1对最终同一字节逐页复核后才发布。当前candidate=null、final_release_eligible=false。

## 不可变历史

v0.4.0、RC1及全部17份PDF与manifest历史条目保持；P0—P7和旧审读记录不改。现有201项内容/图形/版式里程碑是历史基线，不代表新来源已获证或Q1已通过。前言孤行、技术标识断行等版式改进继续在M3/Q1处理。

[阶段计划](POST_RELEASE_PLAN.md) · [旧版历史](history/v0.4.0-STATUS.md) · [交付目录](../deliverables/README.md)。
