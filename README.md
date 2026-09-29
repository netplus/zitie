# 循序渐进汉字部首字帖

201个主部首＋常用附形与位置变体；A4田字格；逐笔示范与分层练习。

**当前是分批编写与复核工程，不是201项全部完成的正式字帖。**

## PDF下载

**[最新合集：前言＋前两批20项，23页](deliverables/drafts/v0.2.1/B01-B02_with_preface_draft_A4.pdf)**

[第二批10页](deliverables/drafts/v0.2.1/B02_draft_A4.pdf) · [第一批10页](deliverables/drafts/v0.2.1/B01_draft_A4.pdf) · [前言3页](deliverables/drafts/v0.2.1/preface_v0.2.1.pdf) · [全部版本与校验清单](deliverables/README.md)

阶段性和最终PDF均直接保存到本仓库，旧版本不覆盖。Actions附件不替代永久归档。

## 当前状态（2026-09-29）

| 内容 | 已完成 | 未决 |
|---|---|---|
| 主索引 | 201项中间索引 | 2022版全文及附形范围核验 |
| B01基础起步 | 10项笔顺原件对照及笔名、结构、采用读音证据 | 全书2022版范围门槛 |
| B02常见独体形 | 10项笔顺、读音及收笔整理复核完成 | 全书2022版范围门槛 |
| B03简单独体 | 10项34笔原件对照完成；细笔名与采用读音逐项复核完成 | 正文、部件名称、矢量与版面等仍待完成 |
| 前言与版面 | 前言3页＋练习20页，已检查及修订 | 不把版式通过算作字形全部审定 |
| 正式发布 | 0 | 达到全部相应门槛后再发布 |

笔顺对照采用2020版及语文出版社1997版实际原图；两者有继承关系，不作为相互独立的证据体系，也不称独立专家审定。

## 项目入口

[当前状态](docs/STATUS.md) · [编写计划](docs/EDITORIAL_PLAN.md) · [前言源稿](book/front-matter/preface.md) · [201项索引](data/coverage.json) · [附形候选](data/variants.json) · [来源台账](sources/catalog.json) · [质量门槛](docs/QUALITY_GATES.md) · [总控Issue](https://github.com/netplus/zitie/issues/1)

[第三批细笔名与读音复核](reviews/B03-metadata.md) · [第三批笔顺原件核对](reviews/B03-primary-cross.md) · [首批交叉复核](reviews/B01-cross.md) · [第二批笔顺原件核对](reviews/B02-primary-cross.md) · [第二批收尾复核](reviews/B02-completion.md) · [本轮版式回归](reviews/v0.2.1-layout.md)

## 重建与检查

```sh
python -m pip install -r requirements.txt
python scripts/validate_project.py --batch B01
python scripts/validate_project.py --batch B02
python scripts/test_validation.py
python scripts/test_deliverables.py
python scripts/verify_deliverables.py
python scripts/acquire_vectors.py --batches B01 B02
python scripts/test_artwork.py
python scripts/build_batch.py --draft --batch B01
python scripts/build_batch.py --draft --batch B02
python scripts/build_collection.py
```

字体由使用者在自己的系统安装，用`--font`和`--latin-font`指定；本仓库不提供字体文件。正式构建不加`--draft`，证据或字形门槛未齐时必须拒绝。

每批10个主项，最后1项，共21批；附形和复习不重复计数。分支＋PR合入，保留历史，不公开私人会话或第三方商业出版物全文。
