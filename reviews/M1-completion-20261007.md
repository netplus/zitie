# M1完成：正式v0.4.1发布与M2启动

日期：2026-10-07。关联总控#58、发布PR #61。同一Agent工程复核，不是独立专家审定。

## 退出证据

PR #61最终归档HEAD `21f317f822a436470bc4e3e0421a3bcea4d3caf6`的Book integrity checks run `37588926485`已completed/success；实际读取job `112685488749`，结构、历史归档、候选构建、正式构建/测试/归档门禁和源码导出全部成功。随后以merge `e22d2075c1cc6728b60d3580ec9aaa9bb4873354`非破坏性合入main。生成run与最终归档HEAD CI分开记录。

正式文件：`deliverables/releases/v0.4.1/B01-B21_v0.4.1_A4.pdf`；276页、3,748,910字节、SHA256 `7270104b8698603fcce4eec14037a0194c31e33b868669d0a8dd0307a090a7e7`。生成源码`0c55d903ed23db565853541c664fdcc44395a2f1`、run `37587438677`、artifact `11467072366`及原始generation记录不变。

E001（5项变体/7处显示）、E002（P2统计范围）、E003（重建说明）、E004（正式前言措辞）均已修复。完整字节绑定的影响验收沿用`reviews/M1-v0.4.1-formal-review-20261007.md`和对应QA JSON；本次关闭的是最终CI/合入门槛，不虚构重新全书审读。

## 本次续接复验

重新下载最终HEAD artifact `11467947081`，ZIP SHA256 `ac431c5af7e8f86a83bd18183482cd9d01f97c3f32ba54cde43d50b7a400061a`匹配；恢复源码git write-tree为`2ecd3242318c739d09922d375fc11e1c506fe736`，与PR一致。归档PDF再次计算大小、页数、哈希一致。

实际打开120dpi MuPDF页面3、270、271、274：正式前言正确、5个特殊变体可见、171项范围注明。其它已渲染页面不计入本次实看范围。原PR已记录的双渲染器影响复核不因本次接续重复计数。

本次本地重新通过32数据、13归档、10绘图、18候选、9阶段测试，共82项；17份PDF完整性、post-release状态及独立patch archive校验通过。正式16项套件本次未在执行时间片内完整结束，因此不计入本次本地通过数；最终HEAD CI已独立完成正式构建、测试和归档门禁。此前PR记录的98项结果保留为历史，不冒称本次全数重跑。

## 阶段状态

M1=completed；E001—E004=resolved；M2=in_progress。M3/Q1仍planned，v0.5.0的final_release_eligible=false，candidate=null。原17份PDF、manifest条目、201项规范数据和既有QA记录未改。

M2入口工作是固定逐字段集合并开始来源资格审计，不授予任何字段reviewed。前言孤行、技术标识断行和儿童可读性继续留在M3/Q1处理，不因M1退出宣称整体版式完美。
