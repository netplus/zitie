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

当前`data/book-config.json`和部分脚本仍固定v0.4.0；全书结构为3页前言、2页目录、258页练习、13页卷末，共276页。输出在`build/`，不是新的正式交付。已有缺字勘误尚待M1修复，重建成功不能当作视觉通过。

`--candidate`/`--formal`属于现有全书构建路径；不带模式的旧逐批release仍受独立门禁限制。不要只改文件名或配置版本便宣称得到v0.4.1/v0.5.0：版本参数化、标题页脚、目录、校验器和归档都需要同步。完整旧流水线见`.github/workflows/book-checks.yml`。

正式归档PDF的精确字节由manifest固定。重建产物需要新的视觉记录；字体环境或PDF元数据可能影响字节哈希。M1/M3新PDF使用新版本目录，Q1绑定最终候选SHA256，历史PDF和manifest旧条目不可覆盖。
