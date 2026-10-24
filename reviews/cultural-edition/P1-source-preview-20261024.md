# P0/P1 文化识字版源PDF重建审稿记录 · 2026-10-24

**仅为工程草稿（status=draft, release_eligible=false），不是已审定文化字帖，也不是对旧299页正式版的替换。**

## 来源与实际生成

- 冻结正式版：`deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf`，299页，SHA256 `7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90`。
- 输入/生成代码提交：`db163523857fe03ec6b7ee0beec3ad74336b3062`；由 GitHub Actions [Cultural PDF source-locked preview #40054959004](https://github.com/netplus/zitie/actions/runs/40054959004) 真正执行，completed/success；两个 PDF、审校摘要和来源映射文件均自动归档。
- `cultural-4-character-source-locked-DRAFT.pdf`：**4页**，水(ID077)、山(ID039)、月(ID088)、木(ID064)，**15幅正式PDF累计笔顺原图**，每一步使用原PDF剪裁的86pt矢量 Form XObject；新文化版预期区域（独立主题、字义/经典、主字拼音置顶、笔顺提示先于笔顺、相关词上方拼音、一字一句）已做版式演示。
- `stroke-source-atlas-201-TECHNICAL.pdf`：**202页、201条目、1045幅原图**；每格31mm、每页最多5列×3行；“龠”(ID201)17笔分连续两页(15 + 2)，本字该笔编号与正式PDF源页和源矢量剪裁一一对应。只是技术验证册，**没有文化编辑内容**。
- `scripts/cultural_source_audit.py` 用全量201 ID书签、原PDF每一步86pt框、逐步名称和索引审核，核对到1045笔、258张教学源页；不通过文字推断笔画，也不以图像生成补足缺失数据。

## 独立质量检验

- 四字样稿 [QA摘要](../../deliverables/drafts/cultural-v0.1/qa-summary.json)：PASS，4页15幅；原PDF逐框RGB平均误差3.6/255，最大4.815/255（抗锯齿/缩放差异）。
- 技术图册 [QA摘要](../../deliverables/drafts/cultural-v0.1/atlas-qa-summary.json)：PASS，201 ID 1045幅、202页；含龠17笔全序索引核对；高风险源图33幅独立缩放渲染对照，最大RGB平均误差3.185/255。
- 源矢量来源证据：`deliverables/drafts/cultural-v0.1/source-provenance.json` 与 `atlas-source-provenance.json`；单字本义、拼音缺失、细笔名称约束沿用原 v0.5.1 不新增断言。
- 字页保留底部“词音/引文待审”，草稿没有经过词音权威词条/引文/完整插图的逐项核定；目前的独有小型矢量主题画只是 P1 布局示意，**不代表正式 P3 美术质量**。

## 明确待办

1. Issue #189：词语拼音、经典原文及出处审校；**待审文案绝不能冒充权威**。
2. Issue #190：每字唯一的正式主题插画、版权及相似度审查。
3. Issue #191：把经验证的 1045笔技术分页能力融入文化页，而不是用临时 atlas 当正式书。
4. Issue #192：全书发布门禁、字/偏旁附形独立审核、最后候选和正式发布。

旧 v0.5.1 及 v0.6.0 15mm PDF 文件、SHA、既有 manifest 条目不动。本次只追加两个非正式草稿记录。

## 更新：引文草稿纠错及确定性构建（2026-10-24）

- 后续样稿改正山字引文，具体原文/出处见 [P2首轮复核](P2-first-batch-quotes-initial-20261024.md)。引文与词音未到签核状态，`review_pending` 仍为真。
- 生成器引入确定性开关，连续双构建PDF逐字节相等；GH Action [#40055521161](https://github.com/netplus/zitie/actions/runs/40055521161) succeeded，自动同步这两个非发布draft的manifest，刷新为4页 SHA256 `8b30ae365472e51190739131f9edc4ad60e2573908a234aed3c5fa6378f31d04`、202页 SHA256 `6224bbfef4d42b1f9953b5b64a72b5fda0065767a55b553ed10f19b11e328b51`。v0.5.1原正式PDF及原历史归档不变。
