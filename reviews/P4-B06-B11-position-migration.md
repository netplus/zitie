# P4 position_migration 第一轮：B06—B11

日期：2026-10-06  
范围：B06—B11，共60个不同主部首。

## 方法

使用仓库source-probe已SHA固定的GF0023—2020原件：
- SHA256：`0ff0890afc34c5e486edeebafb05350dec69a7bf0d1d75044d7d3f7b722ec3d0`
- recovery run：`37449756736`
- artifact：`11406995313`

对canonical已选定的59个唯一整字语境逐项：
1. 定位GF0023精确整字目标行；
2. 实际渲染并查看规范原页的跟随式累计笔画图；
3. 保存整字PDF页、原印页、字表序号、UCS和数字笔顺；
4. 把目标部件的每一笔映射到整字笔画索引；
5. 记录是否交错书写、是否改笔，以及包围部件是否必须保存完整整字时序。

secondary数据没有授予position_migration reviewed。

## 结果

- 60/60：`position_migration`在所记录整字语境中reviewed；
- 0普通pending；
- 1项self语境：风→风，无位置迁移；
- 1处canonical位置纠错：**甘→甜由left修正为right**；
- 2处明确细笔改笔：
  - 矢→知：部件第5笔 / 整字第5笔，**捺→点**；
  - 禾→和：部件第5笔 / 整字第5笔，**捺→点**。
- 需要特别保存完整整字时序的代表项：
  - 匚→区: indices [1,4], interleaved_enclosing
  - 凵→凶: indices [3,4], contiguous_written_after_inner
  - 廴→建: indices [7,8], contiguous_written_last
  - 辶→近: indices [5,6,7], contiguous_written_last
  - 弋→式: indices [1,5,6], interleaved_outer
  - 囗→国: indices [1,2,8], interleaved_enclosing

最关键的非连续映射：
- 匚→区：`[1,4]`，先写框首笔，内部两笔后再完成匚；
- 弋→式：`[1,5,6]`，外部部件与内部笔画交错；
- 囗→国：`[1,2,8]`，底横最后封口，绝不能按部件独立三笔连续播放。

## 边界

本轮关闭的是**选定整字语境中的位置迁移写法**。它不等价于：
- GF0011—2022正式附形认定；
- “所有可能整字语境”均已审读；
- 2022精确附形/名称/编码已关闭。

B04/B05当前main没有可复用的权威整字语境evidence，因此这20项没有为了凑80而升级，留待下一轮选取/核验整字目标后处理。

机器证据：
`data/evidence/P4-B06-B11-position-migration-whole-character.json`
