# A3 — 正式 zitie PDF 同源毛笔笔顺动画

状态：2026-10-11 工程开发候选；跟踪 [Issue #120](https://github.com/netplus/zitie/issues/120)。用户决定**恢复毛笔默认**，冻结硬笔改良，仅保留过去的可选硬笔实验。

## 什么叫 PDF 是源

正式发布的 299 页 A4 文件位于 deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf。PDF 是出版后的视觉和教学内容基准；但静态 PDF 并不包含完整的人体书写时序。A3 不 OCR 识别 PDF 图片来臆造中线/先后，而是复用创建该 PDF 的同套数据：

- data/B01.json 至 data/B21.json：201 主部首 ID、字、先后、细笔名、提示和证据；
- data/teaching-source-policy.json 与 scripts/m3_model.py 的 display_entry：不允许公布的细笔名/读音继续留空/显示序数；
- 固定 Hanzi Writer / Make Me a Hanzi 68d10a4b21150cae5e1ebbd223eed289cf32d90c 修订版：各笔 strokes、medians 与 Arphic PL 许可；
- scripts/apply_artwork.py 和 SHA锁定的 terminal-overrides-v1.json：在正式 PDF 中已经执行的源轮廓修正。

生成器将 201 主项与 PDF 原有 ID001—ID201 书签逐项对应，强制核对 PDF 文件 SHA256、字节数与正式 deliverables/manifest.json。已发布 PDF 保持字节不变。动画使用相同已应用覆写的原始 SVG 轮廓，不能切换成系统字体字形。

## 构建

    python -m pip install -r requirements.txt
    BATCHES="$(printf 'B%02d ' {1..21})"
    python scripts/acquire_vectors.py --batches $BATCHES
    python scripts/build_a3_animation.py --vectors build/vectors --output build/a3/book-pack.js
    node --test animation/tests/a3-book.test.cjs

检查书签和 B01—B21 完整性、201个唯一主项、各笔 SVG/median 数量、笔画编码、六步一页、已登记覆写与14个细笔名限制、读音限制。任何不一致 fail closed。

A3 独立页面是 animation/book.html：201字搜索、按批次过滤、逐笔步骤、暂停/快慢/跳笔/进度拖动、PDF页码直接跳转，以及原书的书写提示与写完检查。GitHub Pages 根路径将指向这一完整字帖页面，并提供 v0.5.1 原 PDF 只读副本；不要求学员运行时联网下载字形。

历史 animation/index.html 仍保留9字 A1.3毛笔回归及模拟笔压、可选硬笔实验，不过毛笔恢复默认，不再以硬笔作为主方向。

## 严格区分审核层级

可以称为“和 PDF 一样的笔顺与字形轮廓”，但**不能称为经过真实手写验证的运笔轨迹**。供应商 medians、计时器、速度与笔尖方向仍是工程演示，未获得人体运动数据与专家运动学认定；也不能把原始2009部首集合冒充 GF0011—2022 的精确逐项形态正式证据。此限制在 UI 和数据中必须可见。

## 验收

- Book CI 重建全201资源 + 元数据、版权、正式PDF哈希/书签限制；
- A1 CI 检查传统九字回归、毛笔默认、硬笔仅可选的功能连续性；对 A3 检查201字SVG加载及54帧实际Chromium单调落墨，0像素消失、390px布局和17笔龠的3页联动；
- Pages 重新生成静态离线资源，复制正式 PDF，原始许可随页附带；
- 只有 PR 精确HEAD的动画/Book均通过，合入后核验实际Pages Deploy，才算上线；
- 不修改正式 v0.5.1 PDF、manifest、201规范教案记录和原始许可素材。

A3.5 人体动作自然度优化需独立真实参考与人工视觉验收，目前不据静态PDF虚构。
