# 内容优先工作流

本工程从2026-10-02起采用“内容层先行、图形与发布层后置”的分阶段工作流。目标是先把201个主部首的教学内容和证据链持续铺开，避免单个PDF、矢量或CI问题阻塞后续内容编写。

## 阶段1：内容覆盖

阶段1的目标是完成201个主部首的内容记录。内部仍保持每批10项、最后一批1项；单次运行以40个不同主部首为常规目标，即连续推进四个批次；无真实阻塞时至少实质推进30项，20项仅作为真实阻塞下的退化结果。

阶段1每项至少维护：
- 主项ID、教学字形和目标规范身份状态；
- 结构前提；
- 笔数、笔顺与细笔名；
- 采用读音（适用时）；
- 部首／部件名称；
- 两条教学提示与自查句；
- 整字语境和位置迁移边界；
- 字段级来源、实际页码／字条、冲突和未决项。

阶段1的“content_ready”只表示内容层可以进入后续图形处理，不表示正式发布。全书级阻塞（例如GF0011—2022逐项全文）允许保留为明确pending，不阻止后续批次继续完成其他可独立核验字段。

## 阶段2：图形与版式

阶段2统一处理：
- 固定矢量来源；
- 逐笔路径与规范原图对照；
- 当前笔红色、旧笔深灰的累计示范；
- A4田字格和描红／淡字／独立书写；
- 实际PDF生成与逐页视觉检查。

阶段2不再反向阻塞阶段1内容覆盖。内容发现错误时回写内容层；否则图形问题在artwork/layout状态中单独跟踪。

## 阶段3：归档与发布

阶段3处理：
- deliverables/drafts/真实PDF归档；
- manifest中的pages、bytes、SHA256、source_commit和review_record；
- 目标HEAD CI；
- releases/正式稿；
- 全书201主项、附形／位置变体、原27项回归、目录／索引和全书逐页复核。

正式发布仍要求所有相应门槛闭合；阶段1的content_ready绝不等价于release_eligible。

## 状态模型

每个批次分别记录三条状态，不再用一个长字符串混合所有阶段：

- content_status：planned → in_progress → content_ready
- artwork_status：deferred → in_progress → artwork_ready
- publication_status：deferred → draft_archived → release_ready

内容层优先级最高。第一阶段常规运行不因artwork_status或publication_status为deferred而停止下一批内容编写。

## 仓库约定

- 继续使用data/Bxx.json作为批次内容主记录；B04起允许在尚未制图时先建立内容稿。
- reviews/Bxx-content.md记录人工内容复核。
- data/evidence/Bxx-content.json记录机器可读字段级证据。
- sources/catalog.json只登记实际取得／实际审读的来源事实。
- artwork、layout、PDF和manifest在阶段2/3再补齐，不把缺失视为阶段1失败。
- 不为“通过测试”伪造review、evidence、页码、原件审读或source_commit。
- scripts/和.github/workflows/在阶段1原则上保持稳定，除非存在阻止内容数据入库的结构性问题；工程重构集中到独立维护窗口，避免每个批次都修改CI。

## 当前批次

- B01、B02：已有内容和练习页。
- B03：内容层已基本完成；PDF归档和hard-gate属于阶段2/3尾项，不再阻塞B04/B05内容推进。
- B04：干、寸、夕、广、门、尸、己、弓、飞、马。
- B05：无、犬、歹、车、牙、戈、瓦、止、贝、见。

B04/B05当前只是阶段1内容范围，不代表正式发布范围已经通过GF0011—2022逐项核验。
