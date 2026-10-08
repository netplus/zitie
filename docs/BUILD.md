# 重建与检查

更新：2026-10-07。当前生成器覆盖B01—B21全部201主项；复杂项每页最多6个累计笔顺步骤，自动分页，不限于B01或六笔以内的字。

## 基线完整性

```sh
python -m pip install -r requirements.txt
for N in $(seq -w 1 21); do python scripts/validate_project.py --batch "B$N"; done
python scripts/test_validation.py
python scripts/test_deliverables.py
python scripts/verify_deliverables.py
python scripts/verify_formal_release_gate.py
python scripts/verify_post_release.py --self-test
python scripts/verify_post_release.py
```

归档完整性、正式v0.4.0历史状态与新周期计划一致性是三种不同检查。全部通过仍不代表E001/E002已修复或Q1完成。

## 全书研究稿

以下使用Bash、fontconfig和已安装的可加载中文/拉丁字体。字体由本机提供，不提交字体文件。

```sh
BATCHES="$(printf 'B%02d ' {1..21})"
python scripts/acquire_vectors.py --batches $BATCHES
python scripts/test_artwork.py
FONT="$(fc-match -f '%{file}' 'AR PL KaitiM GB')"
LATIN="$(fc-match -f '%{file}' 'DejaVu Sans')"
for BATCH in $BATCHES; do
  python scripts/build_batch.py --draft --batch "$BATCH" --font "$FONT" --latin-font "$LATIN"
  python scripts/verify_pdf.py --batch "$BATCH"
done
python scripts/build_book_matter.py
python scripts/build_collection.py
python scripts/verify_book_matter.py
```

首次矢量获取需联网；离线时使用已恢复且经过哈希检查的`build/vectors/`材料，不能用未经验证的同名字形代替。

当前`data/book-config.json`和部分脚本仍固定v0.4.0；全书结构为3页前言、2页目录、258页练习、13页卷末，共276页。输出在`build/`，不是新的正式交付。此旧版路径保留历史渲染行为；M1修复在下述新版本入口，重建成功不能当作视觉通过。

`--candidate`/`--formal`属于现有全书构建路径；不带模式的旧逐批release仍受独立门禁限制。不要只改文件名或配置版本便宣称得到v0.4.1/v0.5.0：版本参数化、标题页脚、目录、校验器和归档都需要同步。完整旧流水线见`.github/workflows/book-checks.yml`。

正式归档PDF的精确字节由manifest固定。重建产物需要新的视觉记录；字体环境或PDF元数据可能影响字节哈希。M1/M3新PDF使用新版本目录，Q1绑定最终候选SHA256，历史PDF和manifest旧条目不可覆盖。

## M1隔离候选构建

在既有矢量缓存准备后，安装本机TrueType字体AR PL UMing CN（fonts-arphic-uming）并执行：

```sh
python scripts/build_patch_candidate.py --version 0.4.1
python scripts/verify_patch_candidate.py
python scripts/test_patch_candidate.py
```

输出`build/v0.4.1-rc1/`，不覆盖旧v0.4.0构建路径；`--font`、`--latin-font`、`--variant-font`可指定已安装字体路径，TTC索引用`--variant-subfont`。全部32项form必须通过cmap预检，当前5个缺字token实际用嵌入子集绘制。字体文件不导出。

此CLI只构建RC候选；正式模式使用下面的独立入口，不能改名冒充发布。候选页数/字节/source_commit等写入generation.json；CI产物须按实际哈希归档，而不是从本地合成提交推断来源。

## M1正式勘误预检与归档验证

```sh
python scripts/build_patch_release.py --version 0.4.1
python scripts/verify_patch_release.py
python scripts/test_patch_release.py
python scripts/verify_patch_archive.py
```

正式预检输出`build/v0.4.1/`，与RC输出隔离。前言正文按模式修改；候选原稿和旧v0.4.0渲染路径保持。正式预检metadata仍为release_eligible=false，生成成功不表示允许发布。

归档门禁绑定PDF字节、生成提交、原始generation JSON、影响页QA和manifest。旧v0.4.0门禁与新v0.4.1检查独立，额外未登记release会拒绝。最终归档HEAD CI通过并合入后再记录M1退出；v0.5.0仍必须经过M2/M3/Q1。

## M3内部工程预览（全模块，不冻结候选）

```sh
python scripts/acquire_m3_vectors.py
python scripts/build_m3_preview.py
python scripts/test_m3_migration.py
python scripts/verify_m3_preview.py --self-test
python scripts/verify_m3_preview.py
```

依赖已核验的201主项`build/vectors/`和六个完整整字`build/m3-whole-vectors/`，本机楷体/拉丁/UMing字体保持原要求。首次取得六个整字使用固定upstream提交、SHA256及Git blob双检；离线用`python scripts/acquire_m3_vectors.py --offline`，缺缓存会报错，不换来源猜测。上游radStrokes不是本题教学部件索引。字体文件不导出。

输出`build/v0.5.0-dev2/`：299页，含201主项练习、六组比较/回忆及六例完整整字迁移。迁移10页覆盖44笔，每页最多6个累计步骤，续页保留前序笔画；常规练习4行×8格。配置`data/m3_book.json`，文案`book/front-matter/m3-guidance.json`，迁移证据及绘图摘要`data/artwork/m3-migration.json`。

metadata记录输入及字体哈希、真实checkout与dirty状态、逐项证据判定、完整时序、页码/书签/链接。无阻塞仍须有正面证据；不通过字体的radStrokes或外形推导新规范结论。35项新版测试与34项迁移测试分别运行。

该入口只构建内部工程预览，没有candidate/formal升级参数。五包实现后仍需真实冻结和归档完整候选，绑定实际源码提交与PDF字节，再做独立Q1。旧构建路径、17份历史PDF和manifest保持不变。


## 完整v0.5.0-rc1候选

```sh
python scripts/build_m3_candidate.py
python scripts/test_m3_candidate.py
python scripts/verify_m3_candidate.py
python scripts/verify_m3_archive.py
```

复用已核的主项和六例整字矢量缓存与本机字体，输出`build/v0.5.0-rc1/`。候选使用独立配置`data/m3_candidate.json`和分层说明，不改默认dev2预览模式。生成须clean checkout，metadata绑定实际commit/tree、配置/代码/证据输入、字体、依赖环境和导航。生成metadata保持未归档/未冻结，归档freeze记录另述后续状态。

重建产物不能覆盖已归档候选。新增归档门禁核对原始生成JSON、PDF字节及当前输入哈希，不允许保留旧哈希却替换内容。`data/m3_scope.json`是已冻结的生成输入快照；当前阶段和候选状态在post_release/manifest/freeze记录，不反向改写生成输入。Q1只审指定SHA256的归档候选，计划见`Q1_REVIEW.md`。
