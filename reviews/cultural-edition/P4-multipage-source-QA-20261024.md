# P4 真实文化阅读页 × 5–17笔源PDF：分页实验审校（2026-10-24）

**状态：工程样稿 / `draft` / `release_eligible=false`，不替代正式 v0.5.1，也不冒充全书出版。**

## 本轮真正解决的问题

原 [P1四字样板](../../deliverables/drafts/cultural-v0.1/cultural-4-character-source-locked-DRAFT.pdf) 只支持1–4笔；上一次202页图册虽然有201字1045笔，但不是带主题句、字义、词条、短句的文化页。本 P4 样本首次把**原始PDF累计步骤直接嵌入完整文化阅读页**，覆盖三种笔数：田5、鼻14、龠17。

- **封面式文化页**：独有主题句、来源主字（原正式PDF图像）、字义、经典一隅（如无准确引文则显式标“待核验”）、原书笔顺提示在笔顺之前、相关词上方拼音、短句、原PDF逐笔示范。
- **长字续页**：每字前6笔编排在文化页左侧2行×3格，其余在无附加练习区的续页最多3行×5格，每格**31mm**；字的全部原始步骤按顺序排列。龠17笔：6 + 11；鼻14笔：6 + 8；田5笔：单页。
- **只复制已发布源PDF的真实矢量**：`Page.show_pdf_page(..., clip=source_rect)`，不由图像模型重新绘制，不拆分横撇、横折、竖钩等复合笔画。源书 SHA256 `7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90`。
- **非正式内容硬性边界**：所有词语读音仅候选；引文若无适合的逐条核实来源则显示“经典引文待核验”；“龠”原PDF不单列读音，文化样页显示“读音待审核”，绝不擅自用外部字典结果提升为已审定。

## 质量事实

源码 `scripts/build_cultural_multipage.py`；测试 `scripts/test_cultural_multipage.py`；审稿数据 `data/cultural_edition/p4_multipage_prototypes.json`；CI `.github/workflows/cultural-multipage-p4.yml`。

GitHub Actions [首轮 P4 验证 #40065701772](https://github.com/netplus/zitie/actions/runs/40065701772) 和 [排版细节修正版 #40065950698](https://github.com/netplus/zitie/actions/runs/40065950698) 为 **completed/success**，包括：

- PDF **5页、36幅完整源图**、全部步骤索引/页码/框与原正式版一致；
- 全部36幅图独立栅格化与原图逐幅比较，最大 RGB 绝对误差均值 **6.3425/255**（阈值 9.5/255），原文档源哈希匹配；
- 两次独立构建 PDF 的二进制字节完全一致；
- 田=5；鼻=6+8；龠=6+11，31mm 不压缩到难读的尺寸；
- 每页渲染 PNG，人工查看后修正了长笔顺提示末尾孤立句号以及主题图占位说明位置；
- P4页的“三点水”之类附形未混入主字源，原字帖书签和在线练习页完全未改。

## 不可回避的后续审定

此处的插图是用于测试布局与独立主题的**程序线稿占位**，不是用户批准的每字专属正式水墨插画；相关词、引文与“龠”的完整规范注音仍需适用中国大陆字典/规范的校对；不能将台湾教育部字典辅助旁证直接升级为大陆正式教材用音。见 [P2词音旁证记录](P2-secondary-lexicon-20261024.md)、Issue [#189](https://github.com/netplus/zitie/issues/189)、[#190](https://github.com/netplus/zitie/issues/190)、[#191](https://github.com/netplus/zitie/issues/191)、[#192](https://github.com/netplus/zitie/issues/192)。

最终文化版中所有偏旁附形仍需单独来源审核。本次只解决“5～17笔主字文化阅读版自动分页”的**工程可行性**，并没有声称完成201页文化内容。
