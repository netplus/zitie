# 当前工程状态

更新：2026-10-07。总控Issue #58，来源Issue #4。

## M1进行中：正式v0.4.1归档，待最终PR61 CI与阶段收口

新周期顺序：M1勘误 → M2新权威来源重开 → M3 v0.5.0增强 → Q1全书排版复核。当前只有M1已启动。

正式修订文件：`deliverables/releases/v0.4.1/B01-B21_v0.4.1_A4.pdf`，276页、3,748,910 bytes，SHA256 `7270104b8698603fcce4eec14037a0194c31e33b868669d0a8dd0307a090a7e7`。生成HEAD `0c55d903ed23db565853541c664fdcc44395a2f1`，run `37587438677`成功，artifact `11467072366`。文件已按精确字节归档并登记manifest。最终PR61目标HEAD CI与合入仍需独立确认，不能使用生成run代替。

E001五项变体/七处显示、E002统计范围、E004正式前言已在本正式产物修复并完成影响回归；E003文档已修正。E001/E002/E004主状态先保留open，直到最终CI成功/合入后的M1收口。记录：`reviews/M1-v0.4.1-formal-review-20261007.md`和`data/evidence/M1-v0.4.1-formal-QA-20261007.json`。

258练习页正文与RC1逐页像素一致，12页卷末整页一致，正式版本声明和页脚单独校验。人工查看13个受影响/代表页，6页用第二渲染器复看；不是Q1全书验收。既有孤行和技术标识断行留给M3/Q1。

下一工作单元：确认PR61最终HEAD CI并合入，记录M1正式完成与M2启动。M2/M3/Q1未开始，v0.5.0的final_release_eligible=false。

## 不可变历史

v0.4.0和v0.4.1-rc1及全部历史PDF不覆盖；原P0—P7、细笔名14项/位置迁移3项/2022精确字段201项边界不变。不新增任何规范字段reviewed。

[阶段计划](POST_RELEASE_PLAN.md) · [旧版完整历史](history/v0.4.0-STATUS.md) · [交付清单](../deliverables/manifest.json)。
