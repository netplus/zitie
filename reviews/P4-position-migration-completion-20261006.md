# P4 position_migration 全书收口检查点

日期：2026-10-06

## 全书结果

P4 的 position_migration 已覆盖201个主部首：

- reviewed：**198/201**
- conflict_fail_closed：**3/201**
- ordinary pending：**0/201**

3个 fail-closed：
- **屮**：代表整字“屯”GF0023原页已核，但独体屮的完整粗粒度笔顺不能可靠映射到整字；
- **毋**：代表整字“每”GF0023原页已核，但独体毋的完整粗粒度笔顺不能可靠映射到整字；
- **瓦**：代表整字“瓶”GF0023上下文原页已核，但旧持久化整字数字笔顺记录在进入瓦部件前截断，无法可靠恢复瓦的4笔索引/改笔。

## 分轮

1. B06—B11：60/60 reviewed；
2. B12—B19：78 reviewed + 屮、毋2项 fail-closed；
3. B01—B03 + B20/B21：41项 self-context reviewed；
4. B04—B05：19 reviewed + 瓦1项 fail-closed。

## 关键整字时序/改笔

需要完整整字时序或非连续映射的典型：
- 匚→区；
- 弋→式；
- 囗→国；
- 疒、虍包围/半包围语境；
- 尸等包围语境按整字顺序理解。

已记录的典型改笔/位置形态变化：
- 矢→知：末笔捺→点；
- 禾→和：末笔捺→点；
- 疋、竹、足：进入代表整字后的粗粒度笔画类别变化；
- 车→辆：独体粗粒度码 `1512` → 左旁位置形前4笔 `1521`。

## self-context边界

B01—B03和B20/B21共41项复用此前已经实际完成的GF0023原页目标字核验，只关闭“目标本身作为整字时无位置迁移”的self-context。该结论**不外推**任何附形/偏旁行为。

## 与GF0011—2022的关系

position_migration 完成不等于GF0011—2022正式附形身份完成。

当前P4仍有一个独立source blocker：GF0011—2022正式全文/官方逐项数据尚未取得可重复公开通道，因此201项的2022精确：
- 主形字形；
- 正式附形/从属形；
- 常用名称；
- 信息处理国际编码

仍保持pending。

证据：
- `data/evidence/P4-B06-B11-position-migration-whole-character.json`
- `data/evidence/P4-B12-B19-position-migration-whole-character.json`
- `data/evidence/P4-B01-B03-B20-B21-position-migration-self-context.json`
- `data/evidence/P4-B04-B05-position-migration-final.json`
