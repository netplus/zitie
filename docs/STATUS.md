# 当前工程状态

更新：2026-10-07。总控Issue #58，来源Issue #4。

## 当前阶段：M2新权威来源重开

**M1已完成，正式v0.4.1已发布；M2已启动，M3/Q1未开始。**M2尚未完成本周期新来源审计，不新增任何规范字段reviewed。

PR #61归档HEAD `21f317f822a436470bc4e3e0421a3bcea4d3caf6` 的Book integrity checks run `37588926485` completed/success，merge `e22d2075c1cc6728b60d3580ec9aaa9bb4873354`。阶段退出证据：`reviews/M1-completion-20261007.md`；机器状态：`data/post_release.json`。

## 最新正式PDF

[《循序渐进汉字部首字帖》v0.4.1，276页](../deliverables/releases/v0.4.1/B01-B21_v0.4.1_A4.pdf)

3,748,910 bytes；SHA256 `7270104b8698603fcce4eec14037a0194c31e33b868669d0a8dd0307a090a7e7`。生成HEAD `0c55d903ed23db565853541c664fdcc44395a2f1`，run `37587438677`，artifact `11467072366`；生成与最终归档CI分开记录。

E001五项变体/七处显示、E002统计范围、E003重建说明、E004正式前言全部resolved。17份PDF已归档，原16份历史字节不变。98项测试、21批结构检查及最终目标HEAD CI通过。

## M2首轮检查点：精确队列与来源入口初探

已从21批canonical数据固定六类集合：GF0011—2022精确字段201项、细笔名14项、位置迁移3项、采用读音11项、部件名称28项、结构37项。集合重叠，不相加作为不同主项；34项采用读音not_applicable单独排除。

精确main_id、成员及21个数据文件SHA256见`data/evidence/M2-reopen-inventory-20261007.json`。入口探查只得到：教育部旧发布说明此次访问超时；Unicode UAX38 revision42草案的GCP混合来源说明不能代替201项2022正式主表。未获取可用于升级字段的新证据，不推断原件不存在。

记录：`reviews/M2-startup-20261007.md`、`sources/reviews/M2-entry-source-audit-20261007.json`。当前仍为M2进行中；本轮0项规范字段升级，入口探查不等于六类字段全部来源审计完成。

## 下一最小工作单元

沿用Issue #4和已固定的六类字段集合，继续审计GF0011—2022正式逐项表/等价官方数据；其后按既定范围复查细笔名、位置迁移、采用读音、部件名称和结构。新证据须实际页码/字条审读，搜索摘要或同源转载不授予reviewed；未取得保持准确阻塞，不把阶段启动写成解决。

M3功能增强完成后再做独立Q1全书排版复核。前言孤行、技术标识断行等已列入后续质量项。本轮影响复核不替代Q1，v0.5.0的final_release_eligible=false。

## 不可变历史与边界

v0.4.0、v0.4.1-rc1及所有旧PDF/manifest条目保留。P0—P7既有里程碑不回退；细笔名14项、位置迁移3项、GF0011—2022精确字段201项的既有fail-closed边界不因M1发布而改变。

[阶段计划](POST_RELEASE_PLAN.md) · [旧版完整历史](history/v0.4.0-STATUS.md) · [交付清单](../deliverables/manifest.json)。
