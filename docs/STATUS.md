# 当前工程状态

更新：2026-10-08。总控#58，权威源Issue #4仍开放。

## Q1版式验收：RC3终检文件已接受（待本PR最终CI后生效）

299页RC3终检文件的逐页审读与完整性回归已有精确档案：
`deliverables/drafts/v0.5.0-rc3/zitie-v0.5.0-rc3-finalcheck.pdf`，
SHA256 `d54184705c6849d6617c7ea201a659d77796cad9b05792782032b320127bbb27`。
前次299/299视觉覆盖、41页第二渲染器、4页灰度模拟；本轮不冒称新的视觉审读。
无布局阻断，238书签与50内部链接等保持；未做实物打印，推荐彩色打印。

PR #71成功归档3份PDF及复核证据，目标HEAD `39740a88...` 的CI
[37767463548](https://github.com/netplus/zitie/actions/runs/37767463548)成功。
本次新增不可变的Q1接受记录 `data/evidence/Q1-RC3-acceptance-20261008.json`，
与原RC1冻结来源、原RC1队列和本地导入时快照并存而不改写。
**本次Q1接受须以本PR目标HEAD CI成功并合入为准。**

**尚未正式发布v0.5.0**：RC3仍是“发布候选”，不能改名冒充正式文件。
须另做正式版字节、标识/末页复核、manifest归档及独立目标HEAD CI。
`final_release_eligible=false`；最新正式版仍v0.4.1。

[Q1验收证据](../reviews/Q1-acceptance-20261008.md) · [旧RC1冻结候选](../deliverables/drafts/v0.5.0-rc1/zitie-v0.5.0-rc1.pdf)

## 先前RC1检查点（历史保留）

以下为导入之前的状态。其“0/299”仅描述旧RC1队列，不代表本地RC3没有经过复核。

# 当前工程状态

更新：2026-10-08；总控#58，来源#4。

## M3完整候选已冻结，当前进入Q1

M1完成，正式v0.4.1保留；M2本周期completed_with_source_blocks，来源#4继续开放。M3的F01—F05五包已实现，完整v0.5.0-rc1已真实归档并登记manifest，M3退出证据见`reviews/M3-candidate-freeze-20261008.md`。阶段切换以最终归档PR #69目标HEAD CI通过及合入为准，不以生成run代替。

[完整发布候选v0.5.0-rc1（299页）](../deliverables/drafts/v0.5.0-rc1/zitie-v0.5.0-rc1.pdf)

4,252,161 bytes；SHA256 `3b26fd0a85b063b83f7090f9b38735908b6e64dc763614c12f17e4f727ef556a`。实际生成HEAD `35e4c2a7123cb9d51d5426fda3a945506946d48c`、tree `d9b8d8af43bf41c3692ca50255ed59c456312933`；生成run `37707956206`成功，artifact `11520662343`。原始generation JSON及配置/字体环境/导航输入哈希完整保存。

构成：2说明+3目录+258主项练习+6比较+6回忆+10整字迁移+14附录，主项仍201；238书签、50内部跳转。独立候选模式明确尚待Q1，不是dev2改名。manifest状态release_candidate、candidate_frozen=true；release_eligible和Q1_completed仍false。

## Q1当前进度：0/299页

`data/q1_review.json`已初始化并绑定同一候选字节；尚未写入任何Q1通过页。M3实际查看的10页候选边界页面、2页第二渲染器及280教学页限定区域像素回归单独记录，不沿用为Q1全书验收。

下一工作单元：按`docs/Q1_REVIEW.md`对归档候选全书逐页检查，记录缺字、裁切/重叠、笔顺颜色/时序、提示、格子、页码与跳转；风险页第二渲染器交叉，检查A4实际尺寸并做灰度模拟。未做实物打印，Q1完成前不得发布正式v0.5.0。

## 验证与历史边界

本地267项唯一测试、21批结构检查通过。新增候选后18份PDF均登记；旧17份原字节、manifest条目、canonical规范数据和审读证据不改。冻结门禁核对当前输入哈希与候选原生成记录；任何修改须显式重新生成/冻结，不能沿用旧视觉记录。

M3编译输入中的未冻结标志保留生成时语义；当前生命周期以`data/post_release.json`及freeze记录为准。2022精确身份201、细笔名14、迁移2、读音9、名称28、结构37限制保持，集合重叠不相加。

[候选冻结证据](../data/evidence/M3-candidate-freeze-20261008.json) · [Q1执行计划](Q1_REVIEW.md) · [最新正式v0.4.1](../deliverables/releases/v0.4.1/B01-B21_v0.4.1_A4.pdf)。
