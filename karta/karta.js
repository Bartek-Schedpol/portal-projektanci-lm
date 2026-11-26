/* Karta produktu A4 (1 strona) — Schedpol dla projektantów Leroy Merlin.
   Dane: ../assets/data.js + lm.js (gama, EAN z eksportu LM) + rysunki.js (rysunki techniczne).
   Logika nazw i wariantów jak w a-biblioteka/a.js. */
(function () {
  'use strict';
  const SP = window.SP;
  const DATA_DATE = '11.2026';
  const TITLE = {
    'Nośnik': 'Nośnik uniwersalny do wanien',
    'Obudowa uniwersalna': 'Obudowa uniwersalna do wanien',
    'Maskownica Balans/Integral': 'Maskownica do brodzików Balans / Integral',
    'Najazd': 'Najazd do brodzików',
    'Nogi Ipsilon': 'Nogi do brodzików Ipsilon'
  };
  const EXTRA_SCENES = { 'Balans': ['balans-bs-b'] };
  const SKIP_SCENES = { 'balans-zoom-ws': 1, 'balans-zoom-bs': 1, 'balans-cut': 1, 'wc-przed': 1 };   // zbliżenia/„przed” to nie aranżacje
  const SCENE_COL = { 'najazd-a': '', 'najazd-b': '' };
  /* kadr aranżacji na produkt: [ogniskowa X %, ogniskowa Y %, przybliżenie] — ustawione ręcznie dla każdej sceny */
  const FOCUS = {
    'balans-ws-a': [27, 84, 2.1], 'balans-bs-a': [27, 84, 2.1], 'balans-cas': [22, 96, 2.0], 'balans-gs': [22, 96, 2.0],
    'balans-ws-b': [22, 96, 2.0], 'balans-bs-b': [22, 96, 2.0],
    'ipsilon-sw': [36, 74, 1.5], 'ipsilon-bs': [36, 74, 1.5], 'frigo-sw': [38, 82, 1.8], 'frigo-bs': [30, 80, 1.8],
    'integral-bs': [62, 74, 1.6], 'integral-ws': [72, 80, 1.6], 'consist': [52, 78, 1.7], 'consist-rect': [60, 78, 1.6],
    'tebe': [48, 82, 1.8], 'corrina': [34, 80, 1.4], 'comfo': [42, 46, 1.5], 'grawello': [30, 80, 1.6], 'dante': [42, 76, 1.6],
    'gobaby': [55, 78, 1.6], 'dafne': [46, 80, 1.6], 'torres-w': [40, 56, 1.25], 'torres-b': [40, 56, 1.25],
    'odplyw-scena': [62, 88, 2.4], 'odplyw-detal': [58, 86, 2.0], 'odplyw-black': [70, 80, 1.9], 'odplyw-prime': [72, 82, 2.2],
    'wc-po': [28, 62, 1.35], 'nosnik': [50, 72, 1.3], 'obudowa-led': [50, 72, 1.3], 'obudowa-pol': [50, 72, 1.3],
    'najazd-a': [50, 55, 1], 'najazd-b': [50, 55, 1],
    'unity-aranzacja-steel': [44, 72, 1.7], 'unity-aranzacja-black': [44, 72, 1.7], 'unity-aranzacja-gold': [44, 72, 1.7], 'unity-aranzacja-copper': [44, 72, 1.7], 'unity-aranzacja-graphite': [44, 72, 1.7]
  };
  /* gwarancja wg karty Stabilsafe v15.25 (kanał DIY); znaki: oryginały z etykiet Sensea i z przeglądu oferty Schedpol */
  const GW_TAIL = 'Warunek: montaż zgodnie z instrukcją, przez osobę o odpowiednich kwalifikacjach. Zakres i terytorium — karta gwarancyjna Stabilsafe v15.25. Gwarancja nie ogranicza ustawowych praw kupującego.';
  function gwFor(p) {
    const sensea = p.brand === 'Sensea';
    if (p.tn === 'Stabilsafe') return { badge: sensea ? 'gw-sensea-10' : 'gw-10', lines: ['10 lat — wytrzymałość na nacisk wg PN-EN 14527', '5 lat — stałość barwy'] };
    if (p.tn === 'Standard Plus') return { badge: sensea ? 'gw-sensea-7' : 'gw-7', lines: ['7 lat — stałość barwy'] };
    if (p.fam === 'Nośnik') return { badge: 'gw-31', lines: ['31 lat — trwałość materiału nośnika EPS'] };
    if (p.fam === 'Harmony') return { badge: '', lines: ['5 lat — wg PN-EN 1253-1'] };
    return { badge: '', lines: [] };
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function cap(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : s; }
  function lcFirst(s) { return s ? s.charAt(0).toLowerCase() + s.slice(1) : s; }
  function norm(s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ł/g, 'l'); }
  function serieOf(p) { return SP.serie(p.fam) || { fam: p.fam, type: SP.catLabel(p.cat), files: {}, scenes: [], feats: [], gw: '', lead: '', n: 0 }; }
  function typeShort(p) { return serieOf(p).type.split(' · ')[0]; }
  function variant(p) {
    const d = SP.dims(p);
    if (d) return d.replace(/-/g, '–');
    return p.c || p.shape || lcFirst(typeShort(p));
  }
  function titleOf(p) {
    if (p.fam === 'Panele do brodzików') return 'Panel do brodzika ' + p.s.replace(/^Panel\s+/, '');
    if (p.fam === 'Obudowa uniwersalna') return 'Obudowa podpłytkowa do wanien ' + (p.shape === 'półokrągły' ? 'półokrągłych' : 'prostokątnych');
    if (TITLE[p.fam]) return TITLE[p.fam];
    return typeShort(p) + ' ' + p.brand + ' ' + p.s;
  }
  function sceneCol(key) {
    if (Object.prototype.hasOwnProperty.call(SCENE_COL, key)) return SCENE_COL[key];
    if (/-ws|-sw/.test(key)) return 'w';
    if (/-bs|black/.test(key)) return 'b';
    if (/-cas/.test(key)) return 'c';
    if (/-gs/.test(key)) return 'g';
    if (/-w$/.test(key)) return 'w';
    if (/-b$/.test(key)) return 'b';
    return '';
  }
  function prodCol(p) {
    const c = p.c || '';
    if (/czarn/.test(c)) return 'b';
    if (/kaszmir/.test(c)) return 'c';
    if (/szar|cement/.test(c)) return 'g';
    if (/bia/.test(c)) return 'w';
    return 'x';
  }
  function sceneFor(p) {
    const s = serieOf(p), pc = prodCol(p);
    /* 26.11: aranżacja w kolorze tego wariantu (zdjęcia dodatkowe, np. UNITY — każda maskownica ma własną) */
    const ph = ((SP.extra && SP.extra[p.ref]) || []).filter(function (x) { return x.kind === 'photo' && SP.img[x.k]; })[0];
    if (ph && !(s.scenes || []).length) return { k: ph.k, cap: 'Wizualizacja poglądowa' };
    let all = (s.scenes || []).concat(EXTRA_SCENES[p.fam] || []).filter(function (k) { return SP.img[k] && !SKIP_SCENES[k]; });
    if (p.fam === 'Obudowa uniwersalna') {               // aranżacja tej wersji obudowy (kształt + podcięcie)
      const ob = (p.shape === 'półokrągły' ? 'pol' : 'pr') + (/LED/.test(p.ver || '') ? '-led' : '');
      all = all.filter(function (k) { return k === { 'pr-led': 'obudowa-led', 'pol-led': 'obudowa-pol', 'pr': 'obudowa-pr', 'pol': 'obudowa-pol-bez' }[ob]; });
    }
    let own = all.filter(function (k) { const sc = sceneCol(k); return sc === '' || sc === pc; });
    own.sort(function (a, b) { return (sceneCol(b) === pc ? 1 : 0) - (sceneCol(a) === pc ? 1 : 0); });
    if (own.length) return { k: own[0], cap: 'Wizualizacja poglądowa' };
    if (all.length) return { k: all[0], cap: 'Wizualizacja poglądowa · inny wariant kolorystyczny' };
    return null;
  }
  function zestawFor(p) {
    const r = [];
    if (p.fam === 'Balans' || p.fam === 'Integral') r.push({ fam: 'Maskownica Balans/Integral', why: 'Maskownica odpływu' });
    if (['Grawello', 'Dante', 'Go Baby', 'Dafne'].indexOf(p.fam) !== -1) r.push({ fam: 'Panele do brodzików', why: 'Panel do brodzika', q: p.fam });
    if (p.fam === 'Ipsilon') r.push({ fam: 'Nogi Ipsilon', why: 'Zestaw nóg' });
    if (p.fam === 'Torres') { r.push({ fam: 'Nośnik', why: 'Podparcie wanny' }); r.push({ fam: 'Obudowa uniwersalna', why: 'Zabudowa wanny' }); }
    if (['Balans', 'Frigo', 'Integral'].indexOf(p.fam) !== -1) r.push({ fam: 'Wall Comfort', why: 'Strefa prysznica' });
    return r.filter(function (x) { return SP.serie(x.fam); }).map(function (z) {
      const list = SP.products.filter(function (x) { return x.fam === z.fam && (!z.q || norm(x.s).indexOf(norm(z.q)) !== -1); });
      return { why: z.why, name: z.q && list[0] ? list[0].s : z.fam, refs: list.map(function (x) { return x.ref; }) };
    });
  }
  function img(key, alt) {
    const i = SP.img[key];
    if (!i) return '';
    return '<img' + (i.tb ? '' : ' class="is-mult"') + ' src="' + esc(SP.src(key)) + '" alt="' + esc(alt || '') + '">';
  }
  function dot(hx) { return hx ? '<i class="dot" style="--c:' + esc(hx) + '"></i>' : ''; }

  const BOK_AREA = ['Polska zachodnia', 'Polska wschodnia i północna', 'Polska południowa'];
  function render(p) {
    const s = serieOf(p), sensea = p.brand === 'Sensea';
    const stone = p.cat === 'brodzik' && /kamień/.test(p.c || '');
    const tech = p.tn ? p.tn + (p.tn === 'Stabilsafe' ? '®' : '') + (p.tech ? ' · ' + p.tech : '') : (p.tech || '');
    const params = [
      ['Marka', esc(p.brand)],
      ['Seria', esc(p.s)],
      p.shape ? ['Kształt', esc(cap(p.shape))] : null,
      SP.dims(p) ? ['Wymiar', '<span class="num">' + esc(variant(p)) + '</span>'] : null,
      p.ver ? ['Wersja', esc(p.ver.charAt(0).toUpperCase() + p.ver.slice(1)) + (/LED/.test(p.ver) ? ' — wnęka przy posadzce na stopy i taśmę LED' : ' — panele do samej posadzki')] : null,
      p.c ? ['Kolor', dot(p.hx) + esc(cap(p.c)) + (p.ce || p.ral ? ' <small>' + esc([p.ce, p.ral].filter(Boolean).join(' · ')) + '</small>' : '')] : null,
      tech ? ['Technologia', esc(tech)] : null,
      stone ? ['Antypoślizgowość', 'klasa A <small>DIN EN 16165:2023, zał. A</small>'] : null,
      p.ean ? ['EAN', '<span class="num">' + esc(p.ean) + '</span>'] : null
    ].filter(Boolean);
    const sc = sceneFor(p), fx = sc && (FOCUS[sc.k] || [50, 60, 1.2]);
    const rys = SP.rys && SP.rys[p.ref];
    const gw = gwFor(p), zest = zestawFor(p), feats = s.feats || [];
    const vbits = [];
    if (SP.dims(p)) vbits.push('<span class="num">' + esc(variant(p)) + '</span>');
    if (p.c) vbits.push('<span>' + dot(p.hx) + esc(p.c) + '</span>');

    document.title = 'Karta produktu LM ' + p.ref + ' — ' + titleOf(p);
    document.getElementById('sheet').innerHTML = `
      <header class="hd">
        ${sensea ? '<img class="logo logo-sensea" src="../assets/znaki/sensea.png" alt="Sensea">' : '<img class="logo" src="../assets/logo.svg" alt="Schedpol">'}
        <div class="hd-r"><b>Karta produktu</b><span>dla projektantów Leroy Merlin · stan danych ${DATA_DATE}</span></div>
      </header>

      <section class="ttl">
        <p class="kick">${esc(SP.catLabel(p.cat))} · ${esc(p.brand)}${p.new ? ' · <em>Nowość 2026</em>' : ''}</p>
        <h1>${esc(titleOf(p))}</h1>
        ${vbits.length ? '<p class="var">' + vbits.join('<i class="sep"></i>') + '</p>' : ''}
      </section>

      <section class="main">
        <figure class="pack">${img(p.im, titleOf(p))}
          ${p.g ? '<span class="pk-gama">Gama LM <b>' + esc(p.g) + '</b></span>' : ''}
        </figure>
        <div class="side">
          <div class="refbox">
            <span class="rb-k">Nr ref. Leroy Merlin</span>
            <b class="rb-n">${esc(p.ref)}</b>
            <span class="rb-g">Gama LM: ${p.g ? esc(p.g) : 'brak w eksporcie LM'}</span>
          </div>
          <dl class="params">${params.map(function (a) { return '<div><dt>' + a[0] + '</dt><dd>' + a[1] + '</dd></div>'; }).join('')}</dl>
        </div>
      </section>

      <section class="draw${rys ? '' : ' is-solo'}">
        ${rys ? `<figure class="rys">
          <figcaption><b>Rysunek techniczny</b><span>wymiary w mm</span></figcaption>
          <div class="rys-img"><img src="../assets/img/rys/${esc(rys.f)}" alt="Rysunek techniczny ${esc(titleOf(p))}"></div>
        </figure>` : ''}
        ${sc ? `<figure class="scene">
          <div class="sc-img"><img src="${esc(SP.src(sc.k))}" alt="${esc(sc.cap)}" style="object-position:${fx[0]}% ${fx[1]}%;transform-origin:${fx[0]}% ${fx[1]}%;transform:scale(${fx[2]})"></div>
          <figcaption>${esc(sc.cap)}</figcaption>
        </figure>` : ''}
      </section>

      <section class="low">
        ${gw.lines.length ? `<div class="gw">
          ${gw.badge ? '<img class="gw-badge" src="../assets/znaki/' + gw.badge + '.png" alt="Znak gwarancji">' : ''}
          <div>
            <h2>Gwarancja producenta</h2>
            <ul>${gw.lines.map(function (l) { return '<li>' + esc(l) + '</li>'; }).join('')}</ul>
            <p>${esc(GW_TAIL)}</p>
          </div>
        </div>` : ''}
        <div class="col">
          <h2>${feats.length ? 'Cechy serii ' + esc(p.fam) : 'O produkcie'}</h2>
          ${feats.length ? '<ol class="feats">' + feats.map(function (f, i) { return '<li><span>0' + (i + 1) + '</span>' + esc(f) + '</li>'; }).join('') + '</ol>'
            : '<p class="lead">' + esc(s.lead) + '</p>'}
        </div>
      </section>

      <section class="kont" aria-label="Kontakt Schedpol">
        <div class="kont-h"><b>Zamówienia i pytania o produkt</b><span>Biuro Obsługi Klienta Schedpol · ${esc((SP.contacts && SP.contacts.hours) || '')}</span></div>
        <div class="kont-l">${((SP.contacts && SP.contacts.bok) || []).map(function (b, i) {
          return '<div title="' + esc(BOK_AREA[i] || '') + '"><b>' + esc(b.n) + ' <span class="num">· ' + esc(b.tel) + '</span></b><span>' + esc(b.mail) + '</span></div>';
        }).join('')}
          <div><b>Doradca techniczny <span class="num">· 502 356 267</span></b><span>doradcatechniczny@schedpol.pl</span></div>
        </div>
      </section>

      <footer class="ft">
        <div>
          <b>Kartę przygotował: SCHEDPOL Sp. z o.o.</b>
          <span>${esc((SP.contacts && SP.contacts.company || '').replace(/^SCHEDPOL Sp\. z o\.o\.,\s*/, ''))} · www.schedpol.pl</span>
        </div>
        <p>Karta ma charakter informacyjny i nie stanowi oferty w rozumieniu Kodeksu cywilnego. Cena i dostępność: w systemie sklepu Leroy Merlin.
          Zdjęcia aranżacyjne są wizualizacjami poglądowymi; kolor na wydruku może odbiegać od rzeczywistego.</p>
      </footer>`;
  }

  function bar(p) {
    const b = document.getElementById('bar');
    if (/[?&]druk=1/.test(location.search)) { b.remove(); return; }
    b.innerHTML = '<span>Podgląd karty · LM <b>' + esc(p.ref) + '</b></span>' +
      '<a class="btn" href="../assets/karty/Karta-produktu_LM' + esc(p.ref) + '.pdf" download>Pobierz PDF</a>' +
      '<button class="btn btn-ghost" type="button" onclick="window.print()">Drukuj</button>';
  }

  const m = /[?&]ref=(\d+)/.exec(location.search);
  const p = (m && SP.byRef(m[1])) || SP.byRef('89189409') || SP.products[0];
  render(p);
  bar(p);
  document.documentElement.setAttribute('data-ready', '1');
})();
