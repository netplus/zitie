# M1完成：v0.4.1正式勘误修订版

日期：2026-10-07。关联总控Issue #58，来源Issue #4。

PR #61最终归档HEAD `21f317f822a436470bc4e3e0421a3bcea4d3caf6` 的Book integrity checks run `37588926485` 已实际completed/success，随后非破坏性合入main，merge `e22d2075c1cc6728b60d3580ec9aaa9bb4873354`。这不同于生成run `37587438677`；只有归档后的最终HEAD通过，才记录M1退出。

正式PDF：`deliverables/releases/v0.4.1/B01-B21_v0.4.1_A4.pdf`，276页、3,748,910 bytes，SHA256 `7270104b8698603fcce4eec14037a0194c31e33b868669d0a8dd0307a090a7e7`。manifest为released/release_eligible=true。原始生成HEAD `0c55d903ed23db565853541c664fdcc44395a2f1`和原始generation元数据不改；不把后续归档提交写成生成来源。

## 验收闭环

- E001：5项变体、7处显示修复进入正式版并复核；E002：第274页注明B04—B21/171项；E003：重建说明已纠正；E004：正式前言正文与版本模式一致。
- 精确PDF与已审看文件逐字节一致；13个受影响/代表页实际查看，6页用第二渲染器复看；258练习页正文、12页卷末按记录完成像素回归，新版页脚另检。
- 98项本地测试、21批结构检查通过；17份归档PDF检查和旧16份不可变性通过。最终CI包含这些测试、候选与正式重建、两个版本的归档门禁及源码导出。
- 临时写权限任务已移除；最终workflow仅contents:read。没有修改旧PDF、历史manifest条目、规范状态，未分发字体文件。

详细证据：`reviews/M1-v0.4.1-formal-review-20261007.md`、`data/evidence/M1-v0.4.1-formal-QA-20261007.json`。其中生成/归档前的pending表述保留当时语义，以本完成检查点记录后续CI与合入结果，不反向改写历史。

## 阶段切换

M1标为completed，E001—E004全部resolved，M2切换in_progress。M2现在只表示工作阶段启动，尚未完成本周期新权威来源审计，也没有新增任何规范字段reviewed。下一步按Issue4及POST_RELEASE_PLAN逐字段核对原件和残余集合。

M3和Q1仍planned；candidate=null、final_release_eligible=false仍针对未来v0.5.0。正式v0.4.1的release_eligible=true不允许越过M2/M3/Q1发布v0.5.0。既有前言孤行和技术标识断行留给M3/Q1，本记录不冒充全书新一轮人工排版验收或真实纸张打印。
