/* A1 offline SVG pen player: median-stroke mask reveals exact audited outline. */
(function (root, factory) {
  const Timeline = typeof module === 'object' && module.exports ?
    require('./timeline.js') : root.ZitieTimeline;
  const api = factory(Timeline);
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.ZitiePlayer = api;
})(typeof window !== 'undefined' ? window : null, function (T) {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  const create = (tag, attrs = {}) => {
    const el = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([key, val]) => el.setAttribute(key, String(val)));
    return el;
  };
  let instanceId = 0;
  function linePath(points) {
    return points.map((p, i) => (i ? 'L' : 'M') + ' ' + p[0] + ' ' + p[1]).join(' ');
  }

  class StrokePlayer {
    constructor({ svg, status, progress, onUpdate } = {}) {
      if (!svg || svg.namespaceURI !== NS) throw new Error('An SVG stage is required');
      this.svg = svg;
      this.status = status || null;
      this.progress = progress || null;
      this.onUpdate = onUpdate || (() => {});
      this.prefix = 'zitie-a1-' + (++instanceId) + '-';
      this.elapsed = 0;
      this.speed = 1;
      this.playing = false;
      this.singleEnd = null;
      this.frameHandle = null;
      this.lastTick = null;
      this.timeline = null;
      this.rows = [];
      this.tip = null;
      this._tick = this._tick.bind(this);
    }

    setGlyph(glyph) {
      // Validate before altering the currently selected glyph.
      const tl = T.buildTimeline(glyph);
      this.pause();
      this.timeline = tl;
      this.elapsed = 0;
      this.svg.replaceChildren();
      this.svg.setAttribute('viewBox', '0 0 1024 1024');
      this.svg.setAttribute('aria-label', glyph.character + '的笔顺轨迹工程预览');
      const defs = create('defs');
      this.svg.appendChild(create('rect', { x: 0, y: 0, width: 1024, height: 1024, fill: '#FFFFFF' }));
      this.svg.appendChild(create('rect', { x: 56, y: 48, width: 912, height: 928,
        fill: 'none', stroke: '#C9979B', 'stroke-width': 2 }));
      for (const [x1, y1, x2, y2] of [[512,48,512,976],[56,512,968,512]]) {
        this.svg.appendChild(create('line', { x1,y1,x2,y2,stroke:'#E2C9CD',
          'stroke-width':2, 'stroke-dasharray':'12 12' }));
      }
      const group = create('g', { transform: 'translate(0 900) scale(1 -1)' });
      this.rows = glyph.strokes.map((s, i) => {
        const id = this.prefix + i;
        const mask = create('mask', { id, maskUnits: 'userSpaceOnUse',
          maskContentUnits: 'userSpaceOnUse', x:-240, y:-240, width:1504, height:1504,
          'mask-type': 'alpha' });
        const brush = create('path', { d: linePath(s.median), fill: 'none',
          stroke: '#FFFFFF', 'stroke-width': 170, 'stroke-linejoin': 'round',
          'stroke-linecap': 'round', 'stroke-dasharray': '0 999999' });
        mask.appendChild(brush);
        defs.appendChild(mask);
        const hint = create('path', { d: s.outline, fill:'#E1E4E7' });
        const solid = create('path', { d: s.outline, fill:'#5C6269' });
        const reveal = create('path', { d: s.outline, fill:'#BD3945',
          mask:'url(#' + id + ')' });
        return { hint, solid, reveal, brush, length: tl.strokes[i].length, id };
      });
      // Layer by paint role, NOT by stroke index: future gray strokes must
      // never obscure the currently written red stroke at intersections.
      for (const row of this.rows) group.appendChild(row.hint);
      for (const row of this.rows) group.appendChild(row.solid);
      for (const row of this.rows) group.appendChild(row.reveal);
      this.tip = create('circle', { cx:0,cy:0,r:12,fill:'#BD3945',
        stroke:'#FFFFFF','stroke-width':4, 'pointer-events':'none' });
      group.appendChild(this.tip);
      this.svg.append(defs, group);
      this.render();
    }

    getState() {
      if (!this.timeline) return null;
      const frame = T.frameAt(this.timeline, this.elapsed);
      return { ...frame, playing:this.playing, speed:this.speed,
        totalMs:this.timeline.totalMs, count:this.rows.length };
    }

    render() {
      if (!this.timeline) return;
      const frame = T.frameAt(this.timeline, this.elapsed);
      this.rows.forEach((r, i) => {
        const finished = frame.phase === 'finished';
        const old = i < frame.index;
        const current = !finished && i === frame.index;
        r.solid.style.display = finished || old ? '' : 'none';
        r.reveal.style.display = current ? '' : 'none';
        if (current) {
          // The unmodified outline is always the final geometry. The median
          // only controls which part of its fill is uncovered at a given time.
          if (frame.progress >= 1) {
            r.reveal.removeAttribute('mask');
          } else {
            r.reveal.setAttribute('mask', 'url(#' + r.id + ')');
            const drawn = Math.max(0, r.length * frame.progress);
            r.brush.setAttribute('stroke-dasharray', drawn + ' ' + (r.length + 1000));
          }
        }
      });
      if (frame.phase === 'writing' && frame.progress > 0 && frame.progress < 1) {
        this.tip.setAttribute('cx', frame.tip[0]);
        this.tip.setAttribute('cy', frame.tip[1]);
        this.tip.style.display = '';
      } else this.tip.style.display = 'none';
      if (this.progress) this.progress.value = this.timeline.totalMs === 0 ?
        0 : Math.round(1000 * this.elapsed / this.timeline.totalMs);
      const stroke = this.timeline.glyph.strokes[frame.index];
      const label = stroke.name_status === 'reviewed' ? stroke.name : '第' + (frame.index + 1) + '笔';
      const mode = frame.phase === 'finished' ? '全部完成' :
        frame.phase === 'pause' ? '笔间停顿' : (this.playing ? '书写中' : '已暂停/待播放');
      if (this.status) this.status.textContent =
        this.timeline.glyph.character + ' · 第 ' + (frame.index + 1) + '/' +
        this.rows.length + ' 笔 · ' + label + ' · ' + mode +
        (frame.phase === 'writing' ? ' ' + Math.round(frame.progress*100) + '%' : '') +
        ' · 轨迹工程预览（未经教学审定）';
      this.onUpdate(this.getState());
    }

    _cancelFrame() {
      if (this.frameHandle !== null) cancelAnimationFrame(this.frameHandle);
      this.frameHandle = null;
      this.lastTick = null;
    }
    pause() {
      this.playing = false;
      this._cancelFrame();
      this.render();
    }
    play() {
      if (!this.timeline) return;
      if (this.elapsed >= this.timeline.totalMs) this.elapsed = 0;
      if (this.playing) return;
      this.playing = true;
      this.lastTick = null;
      this.render();
      this.frameHandle = requestAnimationFrame(this._tick);
    }
    _tick(timestamp) {
      if (!this.playing) return;
      if (this.lastTick !== null) {
        const delta = Math.max(0, timestamp - this.lastTick);
        this.elapsed = Math.min(this.elapsed + delta * this.speed,
          this.singleEnd === null ? this.timeline.totalMs : this.singleEnd);
      }
      this.lastTick = timestamp;
      if (this.elapsed >= (this.singleEnd === null ? this.timeline.totalMs : this.singleEnd)) {
        this.pause();
        this.singleEnd = null;
        return;
      }
      this.render();
      this.frameHandle = requestAnimationFrame(this._tick);
    }
    restart() {
      if (!this.timeline) return;
      this.pause();
      this.singleEnd = null;
      this.elapsed = 0;
      this.play();
    }
    seekStroke(index) {
      if (!this.timeline) return;
      this.pause();
      this.singleEnd = null;
      this.elapsed = T.strokeStart(this.timeline, index);
      this.render();
    }
    previous() {
      if (!this.timeline) return;
      const i = T.frameAt(this.timeline, this.elapsed).index;
      this.seekStroke(Math.max(0, i - 1));
    }
    next() {
      if (!this.timeline) return;
      const i = T.frameAt(this.timeline, this.elapsed).index;
      this.seekStroke(Math.min(this.rows.length - 1, i + 1));
    }
    replayStroke() {
      if (!this.timeline) return;
      const i = T.frameAt(this.timeline, this.elapsed).index;
      this.seekStroke(i);
      this.singleEnd = T.strokeEnd(this.timeline, i);
      this.play();
    }
    showAll() {
      if (!this.timeline) return;
      this.pause();
      this.singleEnd = null;
      this.elapsed = this.timeline.totalMs;
      this.render();
    }
    setSpeed(speed) {
      if (!Number.isFinite(speed) || speed < 0.25 || speed > 4)
        throw new Error('Speed must be within 0.25–4x');
      this.speed = speed;
      this.render();
    }
    destroy() {
      this.pause();
      this.svg.replaceChildren();
      this.timeline = null;
      this.rows = [];
    }
  }

  return { StrokePlayer, linePath };
});
