# 重建B01编写稿

当前生成器落实首批简单独体形，明确限制为每字不超过6笔；复杂字、包围部件与位置变体需要后续扩展分页及整字时序模块，不能直接套本脚本批量标为完成。

```sh
python -m pip install -r requirements.txt
python scripts/validate_project.py
python scripts/test_validation.py
python scripts/acquire_vectors.py
python scripts/build_batch.py --draft --font /path/to/local-chinese-kai.ttf --latin-font /path/to/local-latin.ttf
python scripts/verify_pdf.py
```

字体由运行环境提供，不随仓库或输出包分发。默认路径适用于已配置的Linux环境，也可显式传入。首次取得矢量需要联网；离线时将已经取得的十个JSON及许可放入`build/vectors/`后跳过获取步骤。

输出：`build/preface_v0.1.pdf`、`build/B01_draft_A4.pdf`、`build/B01_with_preface_draft_A4.pdf`、`build/generation.json`。前言在合集练习页之前。

本轮预期为3页前言＋10页练习。生成清单记录的是本次构建信息；`visual_review: pending`表示每次重建默认需要重新视觉检查，并不覆盖`reviews/B01-layout.md`中对已交付版本的历史验收。

不带`--draft`时，来源和审读条件未齐就拒绝正式输出。CI只做结构、生成和预检，不会自动把内容改为核验通过。工作流中间包保存14天；长期成果以可重建源文件和之后的正式版本发布为准。
