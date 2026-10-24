# 首批文化阅读版经典引文原文校对（2026-10-24，阶段性来源定位）

> **仅完成首轮公开来源定位与纠错，尚未人工审定（review_pending）**。本文件不替代字词拼音词典核对、原典版本校勘或正式编辑签核。逐条原引文见 `data/cultural_edition/first_batch_draft.json`。

| 字 | 样板引文 | 核查来源 | 结果 |
|---|---|---|---|
| 水 | 上善若水。 | [Chinese Text Project《道德经》第八章](https://ctext.org/dao-de-jing/zh) | 该连续字串确见原文（其后接“水善利万物而不争”）；字样候选可保留，正式版仍待版本/标点复核 |
| 山 | **知者乐水，仁者乐山。** | [Chinese Text Project《论语·雍也》](https://ctext.org/analects/yong-ye/zhs) | **已纠正**初稿“仁者乐山，智者乐水”不按原文先后顺序且替换“知”的问题；新候选严格照原典顺序 |
| 月 | 海上生明月，天涯共此时。 | [香港教育局《望月懷遠》教学资料](https://www.edb.gov.hk/attachment/tc/curriculum-development/kla/chi-edu/resources/secondary-edu/lang/chi_chapter/P016.pdf) | 官方教育材料直接载明两句与张九龄作品；待审核繁简文字排版转换 |
| 木 | 木欣欣以向荣，泉涓涓而始流。 | [维基文库《归去来辞》](https://zh.wikisource.org/zh-hans/%E5%BD%92%E5%8E%BB%E6%9D%A5%E8%BE%9E)；[古文岛原文](https://m.gushiwen.cn/mingju/juv_2dce202d1e82.aspx) | 原句确见两资料，尚欠纸本权威版次/异文校核；仍 review_pending |

## 数据与发布准则

1. P1样稿中的题材图是生成程序的布局占位图；原 v0.5.1 的正确笔顺仍使用原PDF真矢量裁剪，**不允许用任何图像生成覆盖教学笔画**。
2. 对四字引文只记录来源与第一轮比对，未获得人工编辑签核，因此 `quote.status` 一律不升为 `reviewed`；保留在 P2 Issue [#189](https://github.com/netplus/zitie/issues/189) 下继续检查。
3. 相关词 `terms[*].status` 全部仍为 `review_pending`，尤其须审核轻声、词内读音和拼音拼写模式；本次没有盲目替换已有候选注音。
4. 变更的草稿PDF须由原生成脚本重建、重新核算SHA/页数、同步draft manifest元数据、重跑201源图完整性及四字原图一致性QA；合入前必须通过 **Book integrity checks**。正式版 v0.5.1 原文和历史PDF不能改动。
