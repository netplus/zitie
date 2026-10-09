# A1.2.1 新界面与精细运笔优化（2026-10-09）

已新建独立改进阶段，见 [设计与已知限制](A1_UX_PRECISION.md)、[用户反馈 Issue #82](https://github.com/netplus/zitie/issues/82)。9个已存在部首原型改为卡片搜索、批次筛选、可拖动时间轴；渲染改为依据实际轮廓的中心线局部宽度遮罩，避免统一170单位圆头笔刷过早显露。**原始轮廓/medians/规范笔顺数据不改，教学方向仍需独立验收。** 合入和CI状态以 PR 为准，不预先称完成。

---

# A1 独立动画研发阶段（2026-10-09）

- 分支 `feat/a1-svg-stroke-animation` 开发离线 SVG+JS 笔顺动态书写；独立审计及原型成果以 [A1文档](A1_ANIMATION.md)、[动画目录](../animation/README.md) 和 [Issue #79](https://github.com/netplus/zitie/issues/79) 为准。
- 既有 201/201 主部首的笔画数量与最终矢量轮廓已经审核；固定版上游 Hanzi Writer 数据含 `medians`，独立轨迹教学审定仍为 **0/201**。当前工程原型 **9/201 可播放**，但都标记 `engineering_preview_unreviewed`；全面数据结构审计以 A1 CI `build/a1/coverage-report.json` 为准，不提前声称201项轨迹完全可用。
- 第一次 A1 开发不修改任何既有 PDF、release、manifest 或规范审核记录。来源 Issue #4 及纸张 Issue #77 继续保持原状态。
- 下列 v0.5.1 历史正文和数字不作修改。

---

# 当前正式版本：v0.5.1 标点位置勘误版

2026-10-08。根据读者报告，v0.5.0 中一部分 UMingCN 字体的横排句号（。）与顿号（、）落点偏中。本版遵照 [GB/T 15834—2011 第5.1.1条](https://www.moe.gov.cn/ewebeditor/uploadfile/2015/01/13/20150113091548267.pdf) 将它们校正到字格左下位置。

- [**v0.5.1 正式 A4 PDF（299页）**](../deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf)：7,478,502 bytes；SHA256 `7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90`。
- 修正201处句号与82处顿号，共41页受影响；同时更新全书558处版本标识。299页精确像素比较中修改范围外差异0，238书签和50内部链接不变。
- 从已接受的 RC3 终检 PDF 确定性重建，两次输出逐字节一致。原 v0.5.0 等22份PDF全部保留；现有规范来源 fail-closed 边界、201主项、练习格和笔顺矢量不改。
- 在 `main` 上，该正式归档应已通过本次发布 PR 的目标 HEAD CI；仅有 staging blob、分支或本地构建不代表正式发布。没有实物打印，建议彩色打印。

[详细勘误与QA](../reviews/v051-punctuation-erratum-20261008.md) · [来源限制Issue #4](https://github.com/netplus/zitie/issues/4)

## 下文为历史 v0.5.0 及其之前的发布记录

# 当前工程状态：v0.5.0 正式发布完成

更新：2026-10-08。**《循序渐进汉字部首字帖》v0.5.0 已通过 PR #73 正式归档并合入 `main`**；合并提交 `32e874ec60dad28cc46e5d8ee1e3cd2f3724fc31`。该 PR 最终 HEAD `a85f569d4cea36c1d05fbee61f6bc47d0d0fe109` 的 [Book integrity checks](https://github.com/netplus/zitie/actions/runs/37782153674) 已成功，非临时生成任务的替代结果。

- **当前正式 PDF**：[v0.5.0 A4（299页）](../deliverables/releases/v0.5.0/zitie-v0.5.0-A4.pdf)；7,481,279 bytes；SHA256 `10f5177221ff4817ea412f9e5f187e68d59eabfce8f94e2ebf4179f4398f6880`；manifest 状态 `released`，`final_release_eligible=true`。
- **审读**：Q1 已通过 [PR #72](https://github.com/netplus/zitie/pull/72) 完成验收；RC3 终检 299/299 页复核、41个第二渲染器风险页与4页灰度模拟；正式版仅限文字与版本说明更动，299页非文字区域差异验证通过。
- **可重复性与来源**：从精确哈希绑定的 RC3 终检版使用 `scripts/build_v050_formal.py` 派生；原有238书签、50个内部链接保留。没有将其冒称为 RC1 编译输出。
- **历史完整性**：旧21份 PDF 与 manifest 历史条目均保留；没有上传字体、许可不明规范原文或临时提权工作流。实物打印仍未做，建议彩色打印。
- **后续**：总控 [Issue #58](https://github.com/netplus/zitie/issues/58) 已关闭；仅 [规范来源 Issue #4](https://github.com/netplus/zitie/issues/4) 继续在取得适用权威新证据时定点重开。未决字段维持 fail-closed，不因发布自动提升为已审定。

[正式版来源与 QA](../reviews/Q1-v0.5.0-formal-QA-20261008.md) · [Q1验收记录](../reviews/Q1-acceptance-20261008.md) · [发布 PR #73](https://github.com/netplus/zitie/pull/73)

---

## 下文为Q1阶段验收记录（历史）

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
