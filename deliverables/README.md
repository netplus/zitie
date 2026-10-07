# PDF版本归档

## M1勘误候选 v0.4.1-rc1

[276页勘误候选PDF](drafts/v0.4.1-rc1/B01-B21_v0.4.1-rc1_A4.pdf)：修复5项变体索引缺字，并明确细笔名统计的171项范围。3,754,409 bytes；SHA256 `581101ba2b744f4cba32291731c35d391c3a1df13b5cc11c1abdd7ade2bb4895`。

状态为release_candidate、release_eligible=false；正式v0.4.1尚未发布，M1仍需处理正式前言措辞和正式版本验收。来源及受影响页记录见[候选复核](../reviews/M1-v0.4.1-rc1-review-20261007.md)。原正式版及历史稿不覆盖。

## 正式发布 v0.4.0

[《循序渐进汉字部首字帖》v0.4.0，276页](releases/v0.4.0/B01-B21_with_preface_toc_appendices_v0.4.0_A4.pdf)

本版已通过正式发布门槛并永久归档：3,749,164 bytes，SHA256 `ab3c23d7547872f4d0e2c128de397e9e89ed6de97b681876e2dff017ff5c4894`。最终PR #55 的 Book integrity checks run `37571448193` 成功，release manifest 标记为 `status=released`、`release_eligible=true`。

正式版继续披露已审计的 terminal fail-closed：细笔名14项、位置迁移3项、GF0011—2022逐项精确字段201项 source-blocked。发布不等于伪造这些未公开规范字段。


## v0.3.0：全书201主项编写稿

[全书编写稿，261页](drafts/v0.3.0/B01-B21_with_preface_draft_A4.pdf)

本版首次把B01—B21全部201个主部首汇总为单一A4全书draft。文件已由CI实际生成并永久归档，精确页数、字节数、SHA256和source commit见`manifest.json`。P6已完成201/201 artwork_ready与全书layout review；本PDF仍为**编写稿**，P7的目录/索引/附形与原27项回归、全书最终视觉QA、目标HEAD CI、release candidate和正式release尚未全部关闭。

## v0.2.1：第二批收尾修订

[前言＋前20项，23页](drafts/v0.2.1/B01-B02_with_preface_draft_A4.pdf) · [B02十页](drafts/v0.2.1/B02_draft_A4.pdf) · [前言三页](drafts/v0.2.1/preface_v0.2.1.pdf)

本版补齐B02采用读音，整理日、目、田横折末端；没有新增主项，仍为编写稿。旧版不替换，实际字节以manifest登记为准。

# PDF交付物

阶段性和最终PDF均直接保存在本Git仓库。Actions附件仅用于构建传输，不代替永久归档。

## 最新编写稿 v0.2.0

| 内容 | 页数 | PDF |
|---|---:|---|
| 前言＋前两批20项 | 23 | [阅读合集](drafts/v0.2.0/B01-B02_with_preface_draft_A4.pdf) |
| B02：水、火、木、日、月、田、目、手、牛、毛 | 10 | [第二批练习](drafts/v0.2.0/B02_draft_A4.pdf) |
| B01：一、十、人、八、大、工、土、口、山、巾 | 10 | [第一批练习](drafts/v0.2.0/B01_draft_A4.pdf) |
| 前言 | 3 | [前言v0.2](drafts/v0.2.0/preface_v0.2.pdf) |

B01已完成本批笔顺、笔名、结构与采用读音的来源对照；B02笔顺原件对照完成，读音及部分收笔字形尚待处理。日、目、田的横折末端是当前矢量检查发现的问题，不把书法回锋自动当作教学笔形。全书2022版主表全文核验仍未完成，以上均不是终审版。

## 保留的历史编写稿 v0.1.0

[前言3页](drafts/v0.1.0/preface_v0.1.pdf) · [B01练习10页](drafts/v0.1.0/B01_draft_A4.pdf) · [前言＋B01合集13页](drafts/v0.1.0/B01_with_preface_draft_A4.pdf)

这三份文件从原构建产物恢复，未重建覆盖；前言及合集与原会话交付文件逐字节一致。旧页保留当时的审稿状态，不能用新版已补齐的证据改写旧版脚注。

## 版本与校验

- `drafts/<version>/`保存已交付或送审的阶段性PDF，新版本用新目录，旧PDF不覆盖。
- `releases/<version>/`仅用于达到正式门槛后的版本。当前正式版为`releases/v0.4.0/`。
- [manifest.json](manifest.json)逐文件记录页数、字节数、SHA256、源提交、审稿记录和发布状态。
- [v0.2版面与字形检查](../reviews/v0.2-layout.md)记录实际看过的页面、修订及未决问题。
- CI检查二进制、目录及历史清单一致性；机器检查不授予内容审定结论。
- 原始字体文件、私人会话、第三方商业书籍全文不属于本仓库交付物。
