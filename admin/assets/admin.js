/* MSGR admin panel — small helpers + the content editor (builds forms from a schema). */
(function () {
  'use strict';

  /* ---------- general UI ---------- */
  var menu = document.querySelector('[data-menu]');
  if (menu) menu.addEventListener('click', function () { document.body.classList.toggle('side-open'); });

  document.addEventListener('click', function (ev) {
    var c = ev.target.closest('[data-confirm]');
    if (c && !window.confirm(c.getAttribute('data-confirm'))) { ev.preventDefault(); ev.stopPropagation(); }
  }, true);

  var all = document.querySelector('[data-checkall]');
  if (all) all.addEventListener('change', function () {
    document.querySelectorAll('input[name="ids[]"]').forEach(function (b) { b.checked = all.checked; });
  });
  document.querySelectorAll('tr[data-href]').forEach(function (tr) {
    tr.addEventListener('click', function (ev) {
      if (ev.target.closest('a, input, button, label, select')) return;
      window.location = tr.getAttribute('data-href');
    });
  });

  /* ---------- content editor ---------- */
  var root = document.querySelector('[data-editor]');
  if (!root) return;
  var form = document.querySelector('[data-editor-form]');
  var out = document.querySelector('[data-editor-out]');
  var schema = JSON.parse(document.querySelector('[data-editor-schema]').textContent);
  var data = JSON.parse(document.querySelector('[data-editor-data]').textContent);
  var LANGS = [['ru', 'RU'], ['uk', 'UA'], ['kk', 'KZ']];
  var dirty = false, dirtyEl = document.querySelector('[data-dirty]');
  function touch() { dirty = true; if (dirtyEl) dirtyEl.hidden = false; }
  window.addEventListener('beforeunload', function (e) { if (dirty) { e.preventDefault(); e.returnValue = ''; } });

  function h(tag, attrs, kids) {
    var el = document.createElement(tag);
    for (var k in (attrs || {})) {
      if (k === 'text') el.textContent = attrs[k];
      else if (k === 'html') el.innerHTML = attrs[k];
      else if (k.slice(0, 2) === 'on') el.addEventListener(k.slice(2), attrs[k]);
      else if (attrs[k] !== false && attrs[k] != null) el.setAttribute(k, attrs[k] === true ? '' : attrs[k]);
    }
    (kids || []).forEach(function (c) { if (c) el.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return el;
  }
  function isLoc(t) { return t === 'L' || t === 'LT' || t === 'LH'; }
  function today() { var d = new Date(); return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }

  function makeDefault(s, sibling) {
    switch (s.type) {
      case 'L': case 'LT': case 'LH': return { ru: '', uk: '', kk: '' };
      case 'number': return s.min > 0 ? s.min : 0;
      case 'date': return today();
      case 'bool': return false;
      case 'select': return Object.keys(s.options)[0];
      case 'text': return '';
      case 'list':
        if (s.fixed && Array.isArray(sibling)) return sibling.map(function () { return makeDefault(s.item); });
        return [];
      case 'obj':
        var o = {};
        Object.keys(s.fields).forEach(function (k) {
          var f = s.fields[k];
          if (f.optional && f.type === 'obj') return;
          o[k] = makeDefault(f, sibling ? sibling[k] : undefined);
        });
        return o;
    }
    return null;
  }

  function titleOf(item, s) {
    if (!s.itemTitle || !item) return '';
    var t = item[s.itemTitle];
    if (t && typeof t === 'object') t = t.ru;
    return (t || '').toString().replace(/<[^>]+>/g, '').slice(0, 90);
  }

  /* --- localized field with RU / UA / KZ tabs --- */
  function locField(get, set, s) {
    var v = get();
    if (!v || typeof v !== 'object') { v = { ru: typeof v === 'string' ? v : '', uk: '', kk: '' }; set(v); }
    var wrap = h('div', { class: 'loc' });
    var tabs = h('div', { class: 'loc__tabs', role: 'tablist' });
    var panes = [];
    LANGS.forEach(function (lg, i) {
      var code = lg[0];
      var btn = h('button', { type: 'button', class: 'loc__tab' + (i === 0 ? ' on' : ''), text: lg[1] });
      function mark() { btn.classList.toggle('missing', code !== 'ru' && !!(v.ru || '').trim() && !(v[code] || '').replace(/<[^>]+>/g, '').trim()); }
      var input;
      if (s.type === 'LH') input = richEditor(v[code] || '', function (html) { v[code] = html; mark(); touch(); });
      else {
        input = h(s.type === 'LT' ? 'textarea' : 'input', {
          rows: s.type === 'LT' ? 3 : null, maxlength: s.max || null, lang: code === 'uk' ? 'uk' : code,
          placeholder: code === 'ru' ? '' : 'Перевод (' + lg[1] + ') — если пусто, будет показан русский текст',
          oninput: function () { v[code] = input.value; mark(); touch(); count(); }
        });
        input.value = v[code] || '';
        if (s.type === 'LT') autosize(input);
      }
      var counter = s.max ? h('span', { class: 'loc__count muted small' }) : null;
      function count() { if (counter) counter.textContent = (input.value || '').length + ' / ' + s.max; }
      count();
      var pane = h('div', { class: 'loc__pane', hidden: i !== 0 }, [input, counter]);
      panes.push(pane);
      btn.addEventListener('click', function () {
        tabs.querySelectorAll('.loc__tab').forEach(function (b) { b.classList.remove('on'); });
        btn.classList.add('on');
        panes.forEach(function (p, j) { p.hidden = j !== i; });
      });
      mark();
      tabs.appendChild(btn);
    });
    wrap.appendChild(tabs);
    panes.forEach(function (p) { wrap.appendChild(p); });
    return wrap;
  }

  function autosize(t) {
    function fit() { t.style.height = 'auto'; t.style.height = Math.min(t.scrollHeight + 2, 600) + 'px'; }
    t.addEventListener('input', fit);
    setTimeout(fit, 0);
  }

  /* --- simple rich text editor (headings, bold, lists, links, note box) --- */
  var ALLOWED = { P: 1, H2: 1, H3: 1, UL: 1, OL: 1, LI: 1, STRONG: 1, B: 1, EM: 1, I: 1, A: 1, BR: 1, DIV: 1, BLOCKQUOTE: 1 };
  function cleanHTML(html) {
    var box = document.createElement('div');
    box.innerHTML = html;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (c) {
        if (c.nodeType === 8) { node.removeChild(c); return; }
        if (c.nodeType !== 1) return;
        walk(c);
        if (!ALLOWED[c.tagName]) {
          if (/^(SCRIPT|STYLE|IFRAME|OBJECT)$/.test(c.tagName)) { node.removeChild(c); return; }
          while (c.firstChild) node.insertBefore(c.firstChild, c);
          node.removeChild(c);
          return;
        }
        Array.prototype.slice.call(c.attributes).forEach(function (a) {
          var keep = (c.tagName === 'A' && a.name === 'href') || (a.name === 'class' && /\b(lead|note|note--warn)\b/.test(a.value));
          if (!keep) c.removeAttribute(a.name);
        });
      });
    })(box);
    return box.innerHTML;
  }

  function richEditor(value, onChange) {
    var area = h('div', { class: 'rte__area prose', contenteditable: 'true' });
    area.innerHTML = value;
    var src = h('textarea', { class: 'rte__src', hidden: true, rows: 14 });
    function emit() { onChange(cleanHTML(area.innerHTML)); }
    function cmd(c, arg) { area.focus(); document.execCommand(c, false, arg); emit(); }
    var tools = [
      ['Абзац', function () { cmd('formatBlock', 'p'); }],
      ['Заголовок', function () { cmd('formatBlock', 'h2'); }],
      ['Подзаголовок', function () { cmd('formatBlock', 'h3'); }],
      ['Ж', function () { cmd('bold'); }, 'Жирный'],
      ['К', function () { cmd('italic'); }, 'Курсив'],
      ['• Список', function () { cmd('insertUnorderedList'); }],
      ['1. Список', function () { cmd('insertOrderedList'); }],
      ['Ссылка', function () {
        var url = window.prompt('Адрес ссылки (https://… или /страница/):', 'https://');
        if (url && /^(https?:\/\/|\/|mailto:|tel:)/.test(url)) cmd('createLink', url);
      }],
      ['Убрать ссылку', function () { cmd('unlink'); }],
      ['Блок «Важно»', function () { cmd('insertHTML', '<div class="note"><b>Важно.</b> Текст…</div><p></p>'); }],
      ['HTML', function () {
        if (src.hidden) { src.value = cleanHTML(area.innerHTML); src.hidden = false; area.hidden = true; }
        else { area.innerHTML = cleanHTML(src.value); src.hidden = true; area.hidden = false; emit(); }
      }, 'Править код (для опытных)']
    ];
    var bar = h('div', { class: 'rte__bar' }, tools.map(function (t) {
      return h('button', { type: 'button', title: t[2] || t[0], text: t[0], onmousedown: function (e) { e.preventDefault(); }, onclick: t[1] });
    }));
    area.addEventListener('input', emit);
    area.addEventListener('paste', function (e) {
      e.preventDefault();
      var cd = e.clipboardData;
      var html = cd.getData('text/html');
      if (html) document.execCommand('insertHTML', false, cleanHTML(html));
      else document.execCommand('insertText', false, cd.getData('text/plain'));
      emit();
    });
    src.addEventListener('input', function () { onChange(cleanHTML(src.value)); });
    return h('div', { class: 'rte' }, [bar, area, src]);
  }

  /* --- transliteration for article addresses --- */
  var TR = { а: 'a', б: 'b', в: 'v', г: 'g', д: 'd', е: 'e', ё: 'e', ж: 'zh', з: 'z', и: 'i', й: 'y', к: 'k', л: 'l', м: 'm', н: 'n', о: 'o', п: 'p', р: 'r', с: 's', т: 't', у: 'u', ф: 'f', х: 'h', ц: 'ts', ч: 'ch', ш: 'sh', щ: 'sch', ъ: '', ы: 'y', ь: '', э: 'e', ю: 'yu', я: 'ya', і: 'i', ї: 'yi', є: 'ye', ґ: 'g' };
  function slugify(s) {
    return (s || '').toLowerCase().split('').map(function (ch) { return TR[ch] != null ? TR[ch] : ch; }).join('')
      .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 70).replace(/-+$/, '');
  }

  /* --- render any value by schema --- */
  function render(get, set, s, parentObj) {
    switch (s.type) {
      case 'L': case 'LT': case 'LH': return locField(get, set, s);
      case 'text': {
        var inp = h('input', { type: 'text', pattern: s.pattern || null, oninput: function () { set(inp.value); touch(); } });
        inp.value = get() || '';
        if (s.slugFrom && parentObj) {
          var b = h('button', { type: 'button', class: 'btn btn--sm', text: 'Из заголовка', onclick: function () {
            var t = parentObj[s.slugFrom]; inp.value = slugify(t && t.ru); set(inp.value); touch();
          } });
          return h('div', { class: 'row' }, [inp, b]);
        }
        return inp;
      }
      case 'number': {
        var n = h('input', { type: 'number', min: s.min != null ? s.min : null, step: 'any', oninput: function () { set(n.value === '' ? 0 : Number(n.value)); touch(); } });
        n.value = get() != null ? get() : 0;
        return n;
      }
      case 'date': {
        var d = h('input', { type: 'date', oninput: function () { set(d.value); touch(); } });
        d.value = get() || today();
        return d;
      }
      case 'bool': {
        var c = h('input', { type: 'checkbox', onchange: function () { set(c.checked); touch(); } });
        c.checked = !!get();
        return h('label', { class: 'check' }, [c, ' Да']);
      }
      case 'select': {
        var sel = h('select', { onchange: function () { set(sel.value); touch(); } }, Object.keys(s.options).map(function (k) {
          return h('option', { value: k, text: s.options[k] });
        }));
        sel.value = get() || Object.keys(s.options)[0];
        return sel;
      }
      case 'obj': return renderObj(get, set, s);
      case 'list': return renderList(get, set, s);
    }
    return h('span', { text: '?' });
  }

  function renderObj(get, set, s) {
    var box = h('div', { class: 'obj' });
    function draw() {
      box.innerHTML = '';
      var o = get();
      if (o == null) {
        if (s.optional) {
          box.appendChild(h('button', { type: 'button', class: 'btn btn--sm', text: '+ Добавить «' + (s.label || '') + '»', onclick: function () { set(makeDefault(s)); touch(); draw(); } }));
          return;
        }
        o = makeDefault(s); set(o);
      }
      Object.keys(s.fields).forEach(function (k) {
        var f = s.fields[k];
        var field = h('div', { class: 'field field--' + f.type });
        var lab = h('div', { class: 'field__label' }, [f.label || k]);
        field.appendChild(lab);
        if (f.type === 'obj' && f.optional && o[k] != null) {
          lab.appendChild(h('button', { type: 'button', class: 'linkbtn small', text: 'убрать', onclick: function () { o[k] = null; touch(); draw(); } }));
        }
        field.appendChild(render(function () { return o[k]; }, function (v) { o[k] = v; }, f, o));
        box.appendChild(field);
      });
    }
    draw();
    return box;
  }

  function renderList(get, set, s) {
    var box = h('div', { class: 'list' });
    var simple = isLoc(s.item.type) || ['text', 'number'].indexOf(s.item.type) >= 0;
    function draw(openIndex) {
      box.innerHTML = '';
      var arr = get();
      if (!Array.isArray(arr)) { arr = []; set(arr); }
      arr.forEach(function (item, i) {
        var controls = h('span', { class: 'item__ctl' }, [
          !s.fixed || true ? h('button', { type: 'button', title: 'Выше', text: '↑', disabled: i === 0, onclick: function (e) { e.preventDefault(); move(i, -1); } }) : null,
          h('button', { type: 'button', title: 'Ниже', text: '↓', disabled: i === arr.length - 1, onclick: function (e) { e.preventDefault(); move(i, 1); } }),
          s.fixed ? null : h('button', { type: 'button', title: 'Удалить', class: 'del', text: '✕', onclick: function (e) {
            e.preventDefault();
            if (window.confirm('Удалить этот элемент?')) { arr.splice(i, 1); touch(); draw(); }
          } })
        ]);
        var body = render(function () { return arr[i]; }, function (v) { arr[i] = v; }, s.item);
        if (simple) {
          box.appendChild(h('div', { class: 'item item--simple' }, [h('span', { class: 'item__n', text: (i + 1) + '.' }), body, controls]));
        } else {
          var sum = h('summary', {}, [h('span', { class: 'item__title', text: (i + 1) + '. ' + (titleOf(item, s) || 'Новый элемент') }), controls]);
          var det = h('details', { class: 'item', open: openIndex === i }, [sum, body]);
          body.addEventListener('input', function () { sum.firstChild.textContent = (i + 1) + '. ' + (titleOf(arr[i], s) || 'Новый элемент'); });
          box.appendChild(det);
        }
      });
      if (!s.fixed) {
        box.appendChild(h('button', { type: 'button', class: 'btn btn--add', text: '+ Добавить', onclick: function () {
          var item = makeDefault(s.item, arr[0]);
          if (s.newFirst) { arr.unshift(item); touch(); draw(0); }
          else { arr.push(item); touch(); draw(arr.length - 1); }
        } }));
      }
    }
    function move(i, d) {
      var arr = get(), j = i + d;
      if (j < 0 || j >= arr.length) return;
      var t = arr[i]; arr[i] = arr[j]; arr[j] = t; touch(); draw(j);
    }
    draw(-1);
    return box;
  }

  var holder = { v: data };
  var top = render(function () { return holder.v; }, function (v) { holder.v = v; }, schema);
  root.appendChild(top);

  form.addEventListener('submit', function () {
    out.value = JSON.stringify(holder.v);
    dirty = false;
    var b = form.querySelector('button[type=submit]');
    if (b) { b.disabled = true; b.textContent = 'Сохраняю…'; }
  });
})();
