/* Wersje językowe portalu (25.11.2026): PL (v2/), EN (en/), RO (ro/).
   Strony EN/RO to te same pliki co V2 — ten skrypt tłumaczy teksty na stronie słownikiem window.I18N
   (assets/i18n-en.js, assets/i18n-ro.js, generowane przez _narzedzia/18_slownik.py):
     1) dokładny tekst, 2) wzorzec z liczbami ({n}), 3) reguły dla tekstów złożonych (prefiks: reszta, segmenty „ · ” / „ — ”),
     4) podmiana znanych fraz. Teksty dorysowane później (katalog, karta produktu, komunikaty) tłumaczy MutationObserver.
   Numery ref. LM, EAN, dane kontaktowe i nazwy plików zostają bez zmian. Przełącznik języka: w nagłówku i w menu mobilnym. */
(function () {
  var D = window.I18N || null;
  if (/[?&]debug=1/.test(location.search)) window.I18N_DEBUG = 1;   // brakujące tłumaczenia -> window.I18N_MISS
  var LANG = (D && D.lang) || 'pl';
  var LANGS = [{ k: 'pl', dir: 'v2', n: 'Polski' }, { k: 'en', dir: 'en', n: 'English' }, { k: 'ro', dir: 'ro', n: 'Română' }];
  try { localStorage.setItem('sp-lang', LANG); } catch (e) { /* bez pamięci */ }

  /* ---------- przełącznik ---------- */
  function hrefFor(k) {
    var L = LANGS.filter(function (x) { return x.k === k; })[0];
    var p = location.pathname.replace(/\/(v2|en|ro)\/([^\/]*)$/, '/' + L.dir + '/$2');
    if (p === location.pathname && !/\/(v2|en|ro)\//.test(p)) p = p.replace(/[^\/]*$/, '') + L.dir + '/index.html';
    return p + location.search + location.hash;
  }
  function switcher() {
    if (document.getElementById('spLang')) return;
    var css = document.createElement('style');
    css.textContent =
      '.sp-lang{position:relative;flex:none}' +
      '.sp-lang>button{display:inline-flex;align-items:center;gap:6px;height:34px;padding:0 11px;border-radius:999px;border:1px solid rgba(255,255,255,.35);background:rgba(255,255,255,.08);color:#fff!important;font:600 12.5px/1 Inter,system-ui,sans-serif;letter-spacing:.04em;cursor:pointer}' +
      '.sp-lang>button:hover{border-color:rgba(255,255,255,.6)}' +
      '.sp-lang svg{width:15px;height:15px;flex:none}' +
      '.sp-lang ul{position:absolute;right:0;top:calc(100% + 8px);min-width:178px;margin:0;padding:6px;list-style:none;background:#fff;color:#141414;border-radius:10px;box-shadow:0 12px 32px rgba(0,0,0,.18),0 0 0 1px rgba(0,0,0,.06);z-index:200}' +
      '.sp-lang ul{display:block!important;flex-direction:column}' +
      '.sp-lang ul[hidden]{display:none!important}' +
      '.sp-lang li{display:block;margin:0;padding:0;list-style:none}' +
      '.sp-lang li a{display:flex;justify-content:space-between;gap:16px;padding:9px 10px;border-radius:7px;color:#141414;text-decoration:none;font:500 13.5px/1.2 Inter,system-ui,sans-serif!important;letter-spacing:0!important;text-transform:none!important}' +
      '.sp-lang li a:hover,.sp-lang li a[aria-current]{background:#f2f2f2}' +
      '.sp-lang li small{font:600 11px/1.2 ui-monospace,monospace;color:#777}' +
      '.sp-lang-m{display:flex;gap:6px;margin-top:14px;padding-top:12px;border-top:1px solid rgba(127,127,127,.25)}' +
      '.sp-lang-m a{flex:1;text-align:center;padding:8px 0;border-radius:7px;border:1px solid rgba(127,127,127,.4);font:600 13px Inter,system-ui,sans-serif;text-decoration:none;color:inherit}' +
      '.sp-lang-m a[aria-current]{background:#fff;color:#141414;border-color:#fff}' +
      '@media (min-width:901px){.sp-lang-m{display:none}}' +
      '@media (max-width:900px){.sp-lang.in-nav{display:none}}';
    document.head.appendChild(css);
    var cur = LANGS.filter(function (x) { return x.k === LANG; })[0];
    var w = document.createElement('div');
    w.className = 'sp-lang in-nav'; w.id = 'spLang'; w.setAttribute('translate', 'no');
    w.innerHTML = '<button type="button" aria-haspopup="true" aria-expanded="false" aria-label="Language / Język / Limba: ' + cur.n + '">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3.6 9h16.8M3.6 15h16.8M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>' +
      cur.k.toUpperCase() + '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" style="width:12px;height:12px"><path d="m6 9 6 6 6-6"/></svg></button>' +
      '<ul hidden>' + LANGS.map(function (l) {
        return '<li><a href="' + hrefFor(l.k) + '" data-lang="' + l.k + '"' + (l.k === LANG ? ' aria-current="true"' : '') + '><span>' + l.n + '</span><small>' + l.k.toUpperCase() + (l.k === LANG ? ' ✓' : '') + '</small></a></li>';
      }).join('') + '</ul>';
    var host = document.querySelector('.nav-tools') || document.querySelector('.mb-nav') || document.querySelector('header nav') || document.querySelector('header');
    var before = host && (host.querySelector('.avatar') || host.querySelector('.mb-cta'));
    if (host) { if (before) before.parentNode.insertBefore(w, before); else host.appendChild(w); }
    var b = w.querySelector('button'), ul = w.querySelector('ul');
    b.addEventListener('click', function (e) { e.stopPropagation(); ul.hidden = !ul.hidden; b.setAttribute('aria-expanded', String(!ul.hidden)); });
    document.addEventListener('click', function () { ul.hidden = true; b.setAttribute('aria-expanded', 'false'); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') ul.hidden = true; });
    /* menu mobilne (podstrony: #navLinks) */
    var nl = document.getElementById('navLinks');
    if (nl && !nl.querySelector('.sp-lang-m')) {
      var m = document.createElement('div'); m.className = 'sp-lang-m'; m.setAttribute('translate', 'no');
      m.innerHTML = LANGS.map(function (l) { return '<a href="' + hrefFor(l.k) + '"' + (l.k === LANG ? ' aria-current="true"' : '') + '>' + l.k.toUpperCase() + '</a>'; }).join('');
      nl.appendChild(m);
    }
    /* linki przełącznika muszą nadążać za zmianą podstrony (#/katalog, #/produkt…) */
    window.addEventListener('hashchange', function () {
      document.querySelectorAll('.sp-lang a[data-lang], .sp-lang-m a').forEach(function (a, i) {
        var k = a.getAttribute('data-lang') || LANGS[i % 3].k; a.setAttribute('href', hrefFor(k));
      });
    });
  }

  if (!D) { document.addEventListener('DOMContentLoaded', switcher); return; }      // PL: tylko przełącznik

  /* ---------- tłumaczenie ---------- */
  var EX = D.exact || {}, PH = (D.phrases || []).slice().sort(function (a, b) { return b[0].length - a[0].length; });
  var NUM = /\d+(?:[  ]\d{3})*(?:[.,]\d+)?/g;
  var PREF = /^(Podgląd|Pobierz|Odtwórz film|Pobierz ZIP|Dodaj do Plików|Usuń z Plików|Usuń filtr|Kopiuj nr ref\. LM|Dodano do Plików|Zaktualizowano w Plikach|Marka|Cechy serii|Kategoria|Szukaj|Konto|Znak gwarancji producenta): (.+)$/;
  var cache = {};
  /* wzorce z wstawką {x} (fraza z wyszukiwarki, nazwa serii) — wstawka zostaje bez zmian */
  var XT = Object.keys(EX).filter(function (k) { return k.indexOf('{x}') !== -1 && k.indexOf('{d}') === -1; }).sort(function (a, b) { return b.length - a.length; }).map(function (k) {
    var re = '^' + k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace('\\{x\\}', '(.+?)').replace(/\\\{n\\\}/g, '(\\d+(?:[.,]\\d+)?)') + '$';
    return [new RegExp(re), EX[k], k];
  });
  var OF = { en: 'of', ro: 'din' }[LANG] || 'z';
  function fill(tpl, nums) { var i = 0; return tpl.replace(/\{n\}/g, function () { return nums[i++] || ''; }); }
  /* frazy tylko jako całe słowa („stal” nie może zmienić „Installation”) */
  var PHR = PH.map(function (p) { return [new RegExp('(^|[^\\p{L}\\d])' + p[0].replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?![\\p{L}\\d])', 'gu'), p[1], p[0]]; });
  function phrases(s) {
    var out = s;
    for (var i = 0; i < PHR.length; i++) if (out.indexOf(PHR[i][2]) !== -1) out = out.replace(PHR[i][0], function (m0, pre) { return pre + PHR[i][1]; });
    return out;
  }
  var FILE = /^[^\s]+\.(pdf|dwg|zip|3ds|glb|png|jpg|jpeg|webp|obj)(\?\S*)?$/i;
  var PL = /[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]|(^|\s)(i|w|z|do|na|dla|lub|oraz|nie|jest|od|się|przez)(\s|$)/;
  function one(s) {                                   // jeden fragment: dokładny -> wzorzec -> null
    if (Object.prototype.hasOwnProperty.call(EX, s)) return EX[s];
    var nums = s.match(NUM);
    if (nums) { var t = s.replace(NUM, '{n}'); if (Object.prototype.hasOwnProperty.call(EX, t)) return fill(EX[t], nums); }
    return null;
  }
  /* tekst złożony: dzielenie stopniowe — najpierw „ · ”, potem „ — ”/„ – ”, na końcu „, ”; liść: wzorzec albo frazy */
  var SEPS = [/( · )/, /( — | – )/, /(, )/];
  function seg(s, lv) {
    var x = one(s); if (x !== null) return x;
    for (var i = lv; i < SEPS.length; i++) {
      if (SEPS[i].test(s)) return s.split(SEPS[i]).map(function (p, k) { return k % 2 ? p : seg(p, i + 1); }).join('');
    }
    return phrases(s);
  }
  function tr(raw) {
    if (!raw) return raw;
    var s = raw.replace(/\s+/g, ' ').trim();
    if (!s || !/[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]{2}/.test(s) || FILE.test(s)) return raw;     // nazwy plików bez zmian
    if (cache[s] !== undefined) return keepWs(raw, cache[s]);
    var r = one(s), m;
    if (r === null && (m = /^Komplet plików do projektu: (.+?), (.+)\. Każdy plik można obejrzeć przed pobraniem\.$/.exec(s)))
      r = (EX['Komplet plików do projektu: {x}, {d}. Każdy plik można obejrzeć przed pobraniem.'] || '{x}, {d}').replace('{x}', tr(m[1])).replace('{d}', m[2]);
    if (r === null) for (var xi = 0; xi < XT.length; xi++) {
      if ((m = XT[xi][0].exec(s))) { var nn = m.slice(1).filter(function (v) { return /^\d+(?:[.,]\d+)?$/.test(v); }), xx = m.slice(1).filter(function (v) { return !/^\d+(?:[.,]\d+)?$/.test(v); })[0]; r = fill(XT[xi][1].replace('{x}', xx ? tr(xx) : ''), nn); break; }
    }
    if (r === null && (m = /^(.+) (\d+) z (\d+)$/.exec(s))) r = tr(m[1]) + ' ' + m[2] + ' ' + OF + ' ' + m[3];   // opis zdjęcia w galerii: „… 3 z 10”
    if (r === null && (m = PREF.exec(s))) r = (one(m[1]) || m[1]) + ': ' + tr(m[2]);
    if (r === null) r = seg(s, 0);
    if (r === s) r = null;
    if (r === null) { var y2 = phrases(s); r = y2 !== s ? y2 : s; if (r === s && window.I18N_DEBUG && PL.test(s)) (window.I18N_MISS = window.I18N_MISS || {})[s.replace(NUM, '{n}')] = s; }
    if (LANG === 'en') r = r.replace(/(\d),(\d)/g, '$1.$2');   // 3,5 cm -> 3.5 cm
    cache[s] = r;
    return keepWs(raw, r);
  }
  function keepWs(raw, r) { var a = /^\s*/.exec(raw)[0], b = /\s*$/.exec(raw)[0]; return a + r + b; }
  window.SP_TR = tr;

  var ATTR = ['placeholder', 'title', 'aria-label', 'alt'];
  var SKIP = 'script,style,svg,code.mono-raw,[translate="no"],textarea';
  var done = new WeakMap();
  function node(n) {
    if (n.nodeType === 3) {
      var p = n.parentElement; if (!p || p.closest(SKIP)) return;
      var v = n.nodeValue; if (done.get(n) === v) return;
      var t = tr(v); if (t !== v) n.nodeValue = t; done.set(n, n.nodeValue);
    } else if (n.nodeType === 1) {
      if (n.closest(SKIP)) return;
      for (var i = 0; i < ATTR.length; i++) { var a = n.getAttribute(ATTR[i]); if (a) { var ta = tr(a); if (ta !== a) n.setAttribute(ATTR[i], ta); } }
      if (n.tagName === 'INPUT' && (n.type === 'button' || n.type === 'submit') && n.value) n.value = tr(n.value);
      var w = document.createTreeWalker(n, 5, null), c;
      while ((c = w.nextNode())) {
        if (c.nodeType === 1) { if (c.closest(SKIP)) continue; for (var j = 0; j < ATTR.length; j++) { var b = c.getAttribute(ATTR[j]); if (b) { var tb = tr(b); if (tb !== b) c.setAttribute(ATTR[j], tb); } } }
        else node(c);
      }
    }
  }
  function title() { var t = tr(document.title); if (t !== document.title) document.title = t; }
  var mo = new MutationObserver(function (list) {
    for (var i = 0; i < list.length; i++) {
      var m = list[i];
      if (m.type === 'childList') { for (var k = 0; k < m.addedNodes.length; k++) node(m.addedNodes[k]); if (m.target.nodeName === 'TITLE') title(); }
      else if (m.type === 'characterData') node(m.target);
      else if (m.type === 'attributes' && ATTR.indexOf(m.attributeName) !== -1) { var v = m.target.getAttribute(m.attributeName); var tv = tr(v); if (tv !== v) m.target.setAttribute(m.attributeName, tv); }
    }
  });
  var nc = window.confirm; window.confirm = function (s) { return nc.call(window, tr(String(s))); };
  var np = window.prompt; window.prompt = function (s, v) { return np.call(window, tr(String(s)), v); };
  document.documentElement.lang = LANG;
  function start() {
    try {
      node(document.body); title();
      try { switcher(); } catch (e) { if (window.console) console.warn('i18n: przełącznik', e); }
      mo.observe(document.documentElement, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTR });
    } finally { document.documentElement.classList.remove('i18n-wait'); }   // strona zawsze się pokaże
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
