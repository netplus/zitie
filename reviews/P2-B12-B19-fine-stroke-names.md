# P2 B12—B19细笔名规范原页复核

日期：2026-10-06。

本轮覆盖B12—B19共80个主部首。实际审读P0已固定SHA的GF2001—2001原件PDF物理页4—9，并逐批复看GF0023—2020精确目标行及累计笔形。D03/cnchar与D04/cjklib仅作逐笔定位、歧义和风险筛选，不参与多数投票，也不从1/2/3/4/5数字笔顺码反推细笔名。

结果：**67项 reviewed_normative_original_pages，12项 pending，1项 conflict_fail_closed（矛）**。

12项pending：屮、巛、疒、疋、癶、覀、虍、糸、釆、龺、髟、鬥。它们在P1已完成GF0023主表原页审读但没有精确目标行；GF2001也没有足以直接给出其完整逐笔名称序列的目标字例。因此本轮只把“规范原件适用性已审读”入库，不把secondary序列提升为权威结论。

高风险secondary冲突经目标原页裁决的项目包括毋、鸟、臣、虫、缶、舟、里、角。典型裁决：毋首笔=竖折；臣末笔=竖折；缶第5笔=竖折；角第2笔=横撇。殳裁决为撇、横折弯、横撇、捺；穴第3笔=横钩；皮第1笔=横钩、第4笔=横撇；色/麦/龟/鱼的相关code-5折笔按目标字形裁为横撇；骨第5笔=横钩。

矛保留fail-closed：GF0023精确目标行已实际查看，但两个code-5折笔在当前扫描分辨率下不足以可靠区分“横撇/横钩”的细类，GF2001提供分类规则但没有足够的目标字直接桥接。不得用D03/D04的一致性替代规范原页裁决。

机器证据：
- `data/evidence/P2-B12-B15-fine-stroke-names-original-page.json`
- `data/evidence/P2-B16-B19-fine-stroke-names-original-page.json`

本轮只处理fine_stroke_names，不改变pronunciation、component_name、structure、GF0011—2022身份、position migration、artwork、PDF、manifest或release状态。

## Canonical同步状态

B12—B15、B17—B19已成功同步canonical。B16十项的规范原页evidence已经入库并判定为10/10 reviewed，但尝试更新`data/B16.json`时触发tooling_write_blocker，原始错误：`This tool call was blocked by OpenAI because we couldn't determine the safety status of the request.`。按工程约定停止该路径，不使用低层Git对象绕过；B16 canonical留作后续状态债，不把写入失败误记为source blocker或content conflict。
