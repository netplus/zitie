# Q1：RC3终检文件版式验收（正式版仍待制作）

2026-10-08。此验收是对已经归档且已完成逐页审读的RC3 **精确文件** 作正式版式接受，
绑定 `deliverables/drafts/v0.5.0-rc3/zitie-v0.5.0-rc3-finalcheck.pdf`，299页，
SHA256 `d54184705c6849d6617c7ea201a659d77796cad9b05792782032b320127bbb27`。
验收记录：`data/evidence/Q1-RC3-acceptance-20261008.json`。

## 核验基础

- 真实RC2基线299页逐页可读尺度审读；RC3非版本改动的83页修订区域逐一复看，
  未变区域的逐页像素与矢量对象经可靠差异检查支持继承。
- RC3共41页用Poppler交叉渲染，4页灰度模拟。RGB96按原记录重新核对299/299。
  新笔红色与历史灰线在灰度中区分变弱，仍明确**推荐彩色打印**；并未做实物打印。
- 299页完整原复核记录 `reviews/q1-local-20261008/Q1-page-review-rc3.json`、
  最终文件机器完整性记录 `reviews/q1-local-20261008/Q1-final-integrity.json` 已随PR #71入库。
  同一Agent复看不能表述为独立专家审稿。本PR没有重新计数299页人工审读。
- A4、字体映射、田字格/线条、238书签、50内部链接以及来源限制逐页证据完整；
  **阻断排版问题为0**。RC3终检PDF只增加文档级附件，299页渲染与RC3原PDF完全一致。
- PR #71最终HEAD `39740a88eb00deb74c2ed97a61b3df15e5436968` 的归档CI
  [37767463548](https://github.com/netplus/zitie/actions/runs/37767463548) 实际成功。
  这不是本PR Q1关闭验收的CI，当前PR仍须自己的目标HEAD CI成功后合入。

## 版本及来源边界

`data/post_release.json` 中 `candidate` 为**历史M3冻结RC1**，不动、不改写生成来源。
原 `data/q1_review.json` 是旧RC1启动队列，仍为0/299，不混同本次对象。
原 `data/q1_local_review.json` 内 Q1_completed=false 是**导入时历史快照**，保留原字节。
本次Q1完成由**独立接受记录**和 `post_release.q1_review` 表示，校验器严格对比精确字节及复核证据。
来源#4的GF0011—2022等精确字段边界继续fail-closed，未作规范事实升级。

## 仍然不能直接正式发布

这是一份页内仍写有“发布候选”的RC3文件。通过Q1后，不允许直接复制/改名作为正式v0.5.0。
仍须按候选→正式版差异制作真正标为“正式发布”的独立PDF，并审读所有变更页面和关联导航，
记录新的PDF SHA256、生成/派生来源、manifest、最终PR目标HEAD CI，再可宣布正式版。
所以本PR `final_release_eligible=false`，历史v0.4.1仍为最新正式版。
