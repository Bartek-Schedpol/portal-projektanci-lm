/* ==========================================================================
   Koncepcja A — „Biblioteka” · logika makiety (czysty JS, bez zależności)
   Ekrany: #/start · #/katalog · #/produkt?ref=… · #/pliki
   ========================================================================== */
(function () {
  'use strict';

  // Diagnostyka makiety: błąd JS zostawia ślad w atrybucie <html data-js-error>.
  window.addEventListener('error', function (e) {
    document.documentElement.setAttribute('data-js-error', (e.message || 'błąd') + ' @' + (e.lineno || '?'));
  });

  const SP = window.SP, SPI = window.SPI, SPProto = window.SPProto;
  const app = document.getElementById('app');
  if (!SP || !SPI || !SPProto) {
    app.innerHTML = '<p class="noscript">Nie udało się wczytać zasobów makiety (folder assets).</p>';
    return;
  }

  /* ---------- stałe ---------- */
  const DEFAULT_REF = '89189409';
  const CAD = { name: 'Schedpol & Sensea', date: '04.2026', mb: 55.2 };
  /* baza producenta w katalogu CAD Projekt K&A (sprawdzone 25.11.2026: „SCHEDPOL & SCHEDLINE”, kwiecień 2026, 55.2 MB, bez logowania) */
  const CAD_URL = 'https://www.cadprojekt.com.pl/category/baza-modele3d/';
  const CAD_DOC = 'https://cadprojekt.com.pl/instrukcje-cad-decor-pro/';
  const VERIFIED = '11.2026';
  const HINTS = ['89189406', 'Balans 80×100', 'czarny kamień', 'odpływ 80'];
  const FT = [
    { k: 'packshot', l: 'Packshoty' }, { k: 'aranżacja', l: 'Aranżacje' }, { k: 'rysunek', l: 'Rysunki' },
    { k: 'infografika', l: 'Infografiki' }, { k: 'opis', l: 'Opisy' }, { k: 'instrukcja', l: 'Instrukcje' },
    { k: 'zdjęcie dodatkowe', l: 'Zdjęcia dodatkowe' }, { k: 'film', l: 'Film' }, { k: 'karta', l: 'Karty produktów' }
  ];
  /* karta produktu PDF jest dla każdego indeksu — dopisz do liczników serii (ok. 0,2 MB na kartę) */
  SP.series.forEach(function (s) {
    if (!s.files) s.files = {};
    if (!s.files.karta) { s.files.karta = s.n; s.mb = (s.mb || 0) + s.n * 0.2; }
  });
  const FT_MAIN = ['packshot', 'aranżacja', 'rysunek', 'infografika', 'opis'];
  const CAT_REP = {
    'brodzik': 'p-balans-ws', 'wanna': 'p-torres-w', 'odpływ liniowy': 'p-harmony', 'panel ścienny': 'p-wall6-sw',
    'nośnik': 'p-nosnik-wanna', 'obudowa': 'p-obudowa', 'akcesoria': 'p-maskownica-zlota'
  };
  /* Start → Kategorie: przykładowe aranżacje produktów zamiast packshotów */
  const CAT_SCENE = {
    'brodzik': ['balans-ws-a', 30, 80], 'wanna': ['torres-w', 40, 55], 'odpływ liniowy': ['odplyw-detal', 60, 80],
    'panel ścienny': ['wc-po', 25, 55], 'nośnik': ['nosnik', 50, 70], 'obudowa': ['obudowa-led', 50, 70], 'akcesoria': ['balans-zoom-bs', 50, 50]
  };
  const TITLE = {
    'Nośnik': 'Nośnik uniwersalny do wanien',
    'Obudowa uniwersalna': 'Obudowa uniwersalna do wanien',
    'Maskownica Balans/Integral': 'Maskownica do brodzików Balans / Integral',
    'Najazd': 'Najazd do brodzików',
    'Nogi Ipsilon': 'Nogi do brodzików Ipsilon'
  };

  /* ---------- pomocnicze ---------- */
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function ic(n, size, sw) { return SPI.icon(n, { size: size || 18, sw: sw || 1.5 }); }
  function H(screen, params) { return esc(SPProto.href(screen, params || {})); }
  function nf(n, d) {
    const k = d == null ? 1 : d;
    return Number(n).toLocaleString('pl-PL', { minimumFractionDigits: k, maximumFractionDigits: k });
  }
  function plural(n, one, few, many) {
    n = Math.abs(n);
    if (n === 1) return one;
    const d = n % 10, h = n % 100;
    return (d >= 2 && d <= 4 && !(h >= 12 && h <= 14)) ? few : many;
  }
  function pliki(n) { return n + ' ' + plural(n, 'plik', 'pliki', 'plików'); }
  function indeksy(n) { return n + ' ' + plural(n, 'indeks', 'indeksy', 'indeksów'); }
  function cap(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : s; }
  function lcFirst(s) { return s ? s.charAt(0).toLowerCase() + s.slice(1) : s; }
  function norm(s) {
    return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ł/g, 'l');
  }
  function mbLabel(mb) {
    if (!mb) return '0 MB';
    if (mb >= 1000) return nf(mb / 1000, 1) + ' GB';
    if (mb < 0.1) return Math.max(1, Math.round(mb * 1000)) + ' KB';
    return nf(mb, 1) + ' MB';
  }
  function hash(str) {
    let h = 2166136261;
    for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  }
  function rnd(seed, min, max) { return min + (hash(seed) % 1000) / 1000 * (max - min); }
  function typeMb(s, k) {             // karta PDF ~0,2 MB; reszta — średnia z paczki serii
    if (k === 'karta') return (s.files.karta || 0) * 0.2;
    const other = sumFiles(s) - (s.files.karta || 0);
    return other ? ((s.mb || 0) - (s.files.karta || 0) * 0.2) * (s.files[k] || 0) / other : 0;
  }
  function sumFiles(s) { return Object.keys(s.files || {}).reduce(function (a, k) { return a + s.files[k]; }, 0); }

  /* ---------- model produktu ---------- */
  function serieOf(p) {
    return SP.serie(p.fam) || { fam: p.fam, type: SP.catLabel(p.cat), files: {}, scenes: [], feats: [], gw: '', lead: '', n: 0 };
  }
  function typeShort(p) { return serieOf(p).type.split(' · ')[0]; }
  function dimsTxt(p) { const d = SP.dims(p); return d ? d.replace(/-/g, '–') : ''; }
  function variant(p) {
    const d = SP.dims(p);
    if (p.ver) return (d ? d.replace(/-/g, '–') + ' · ' : '') + p.ver;      // obudowy: wersja z podcięciem / bez
    if (d) return d.replace(/-/g, '–');
    return p.c || p.shape || lcFirst(typeShort(p));
  }
  function titleOf(p) {
    if (p.fam === 'Panele do brodzików') return 'Panel do brodzika ' + p.s.replace(/^Panel\s+/, '');
    if (p.fam === 'Obudowa uniwersalna') return 'Obudowa podpłytkowa do wanien ' + (p.shape === 'półokrągły' ? 'półokrągłych' : 'prostokątnych');
    if (TITLE[p.fam]) return TITLE[p.fam];
    return typeShort(p) + ' ' + p.brand + ' ' + p.s;
  }
  function kickerHTML(p) {
    const t = typeShort(p);
    if (p.fam === 'Panele do brodzików') return esc(p.s);
    if (norm(t).split(' ')[0] === norm(p.s).split(' ')[0]) return esc(p.s.length >= t.length ? p.s : t);
    return esc(p.s) + ' <span>· ' + esc(lcFirst(t)) + '</span>';
  }
  function metaLine(p) { return [p.c, p.shape].filter(Boolean).join(' · ') || p.brand; }
  function fileBase(p) {
    const clean = function (s) { return String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ł/g, 'l').replace(/Ł/g, 'L'); };
    const ser = clean(p.s).replace(/[^A-Za-z0-9]+/g, ' ').trim().split(' ').map(cap).join('');
    let dim = '';
    if (p.a != null && p.b != null) dim = p.a + 'x' + p.b + (p.cat === 'panel ścienny' && p.h ? 'x' + p.h : '');
    else if (p.a != null) dim = p.a + 'cm';
    else if (p.c) dim = clean(p.c).replace(/\s+/g, '-');
    const ver = p.ver ? (/LED/.test(p.ver) ? '_podciecie-LED' : '_bez-podciecia') : '';     // obudowy: dwie wersje tego samego wymiaru
    return p.brand + '_' + ser + (dim ? '_' + dim : '') + ver;
  }
  /* karta produktu PDF: prawdziwe pliki z _narzedzia/7_karty_pdf.py (szablon ../karta/index.html) */
  const KARTY_V = '20261126i';   // wersja kart PDF — po każdym przegenerowaniu zmień, żeby przeglądarki nie podawały starych plików z pamięci podręcznej
  /* 26.11: prefiks ścieżek — '../' dla stron w podfolderach (v2/, en/, ro/, a-biblioteka/), '' dla wersji PL w katalogu głównym (window.SP_UP) */
  const UP = window.SP_UP != null ? window.SP_UP : '../';
  function kartaPdf(p) { return UP + 'assets/karty/Karta-produktu_LM' + p.ref + '.pdf?v=' + KARTY_V; }
  function kartaView(p) { return UP + 'karta/index.html?ref=' + encodeURIComponent(p.ref); }
  /* karty gwarancyjne i instrukcje montażu przypisane do indeksu (assets/dokumenty.js) */
  const DOC_BASE = UP + 'assets/dokumenty/';
  function docsFor(p) {
    return ((SP.docMap && SP.docMap[p.ref]) || []).map(function (k) { return SP.docs[k]; }).filter(Boolean);
  }
  /* modele 3D (assets/modele3d.js) i podgląd w przeglądarce (<model-viewer>, ładowany przy pierwszym użyciu) */
  const CAD_BASE = UP + 'assets/cad/';
  const CAD_Q = '?v=20261125c';   // wersja modeli 3D — zmień po przebudowie brył (pamięć podręczna przeglądarek)
  function cadFor(p) { return SP.cad && SP.cad[p.ref]; }
  function glbFor(p) { const c = cadFor(p); const g = c && c.files.filter(function (x) { return x.ext === 'GLB'; })[0]; return g ? CAD_BASE + g.f + CAD_Q : ''; }
  let mvLoading = null;
  function loadMV() {
    if (window.customElements && customElements.get('model-viewer')) return;
    if (mvLoading) return;
    mvLoading = document.createElement('script'); mvLoading.type = 'module';
    mvLoading.src = 'https://cdn.jsdelivr.net/npm/@google/model-viewer@3.5.0/dist/model-viewer.min.js';
    document.head.appendChild(mvLoading);
  }
  /* wykończenie modelu wg wariantu: kolor RAL z danych produktu; struktura kamienia = relief (normal map z próbki kamienia)
     + subtelna faktura barwy; mat/połysk. Zmienia się tylko materiał „akryl” — maskownice i pokrywy odpływu („metal”) zostają stalowe. */
  function finishFor(p) {
    const c = (p && p.c || '').toLowerCase();
    const stone = /kamie/.test(c);
    /* jasne barwy kamienne w oświetleniu podglądu wypadają zbyt blado — korekta pod packshot (kaszmir) */
    const HX3D = { 'kaszmirowy kamień': '#D3C3A8', 'cementowy kamień': '#A9ACA7' };
    return { hx: HX3D[c] || (p && p.hx ? p.hx : '#F4F4F2'), stone: stone, rough: stone ? 0.86 : (/mat/.test(c) ? 0.7 : 0.22) };
  }
  let stoneTex = null;
  async function applyFinish(mv) {
    const p = SP.byRef(mv.getAttribute('data-ref') || '');
    if (!p || !mv.model) return;
    const f = finishFor(p);
    let nrm = null, det = null;
    if (f.stone) {
      try { nrm = await mv.createTexture(UP + 'assets/img/stone-normal.jpg'); det = await mv.createTexture(UP + 'assets/img/stone-detail.jpg'); } catch (e) { nrm = det = null; }
    }
    mv.model.materials.forEach(function (m) {
      if (m.name !== 'akryl') return;   // kolor wariantu tylko dla bryły; maskownice, mata, nośnik EPS, spód skorupy bez zmian
      const pbr = m.pbrMetallicRoughness;
      pbr.setMetallicFactor(0);
      pbr.setRoughnessFactor(f.rough);
      pbr.setBaseColorFactor(f.hx);
      if (det) pbr.baseColorTexture.setTexture(det);
      if (nrm && m.normalTexture) { m.normalTexture.setTexture(nrm); try { m.normalTexture.setScale && m.normalTexture.setScale(1); } catch (e) { /* starsze API */ } }
    });
  }
  document.addEventListener('load', function (e) {
    if (e.target && e.target.tagName === 'MODEL-VIEWER') applyFinish(e.target);
  }, true);
  function mvHTML(src, alt, ref) {
    loadMV();
    return '<model-viewer src="' + esc(src) + '" data-ref="' + esc(ref || '') + '" alt="' + esc(alt) + '" camera-controls touch-action="pan-y" auto-rotate auto-rotate-delay="800" rotation-per-second="18deg" ' +
      'shadow-intensity="1.4" shadow-softness="0.6" exposure="0.78" tone-mapping="neutral" environment-image="neutral" camera-orbit="35deg 62deg auto" ar ar-modes="webxr scene-viewer quick-look"></model-viewer>';
  }
  /* 25.11.2026: wyłącznie pliki, które są na serwerze (wcześniej część pozycji była atrapą makiety).
     typ = grupa w Centrum plików i folder w paczce ZIP; rozmiary z assets/rozmiary.js (16_rozmiary_plikow.py). */
  const FTYP = [
    { k: 'karta', l: 'Karty produktów', dir: 'Karty produktow PDF' },
    { k: 'model', l: 'Modele 3D', dir: 'Modele 3D' },
    { k: 'rysunek', l: 'Rysunki techniczne', dir: 'Rysunki techniczne' },
    { k: 'packshot', l: 'Packshoty', dir: 'Packshoty' },
    { k: 'aranzacja', l: 'Aranżacje', dir: 'Aranzacje' },
    { k: 'grafika', l: 'Przekroje i infografiki', dir: 'Przekroje i infografiki' },
    { k: 'dokument', l: 'Instrukcje i karty gwarancyjne', dir: 'Instrukcje i karty gwarancyjne' }
  ];
  function kbOf(href) { const k = String(href || '').split('?')[0].replace(/^\.\.\/assets\//, ''); return (SP.kb && SP.kb[k]) || 0; }
  function extOfPath(path) { return ((String(path).split('?')[0].match(/\.([a-z0-9]+)$/i) || [])[1] || '').toUpperCase(); }
  function filesFor(p) {
    const f = [], base = fileBase(p);
    const add = function (o) { o.mb = kbOf(o.href) / 1024 || o.mb || 0; f.push(o); };
    add({ ext: 'PDF', name: 'Karta-produktu_LM' + p.ref + '.pdf', desc: 'Karta produktu PDF, A4 — parametry, nr ref., EAN, rysunek techniczny, gwarancja', href: kartaPdf(p), view: kartaView(p), karta: true, typ: 'karta' });
    const cad = cadFor(p);
    if (cad) {                                      // prawdziwe modele: assets/cad (10_modele_3d.py)
      const glb = (cad.files.filter(function (x) { return x.ext === 'GLB'; })[0] || {}).f;
      const CADD = { DWG: 'Model 3D DWG (AutoCAD)', OBJ: 'Model 3D OBJ w archiwum ZIP (SketchUp, Blender, 3ds Max)', '3DS': 'Model 3D 3DS (3ds Max, CAD Decor)' };
      cad.files.filter(function (x) { return x.ext !== 'GLB'; }).forEach(function (x) {
        add({ ext: x.ext, name: x.f, desc: CADD[x.ext] + ' · wymiary w cm' + (cad.approx && cad.from ? ' · bryła serii dopasowana do wymiaru produktu (wzorzec ' + String(cad.from[0]).replace('.', ',') + ' × ' + String(cad.from[1]).replace('.', ',') + ' cm)' : '') + (cad.fix ? ' · odpływ wg rysunku technicznego' : '') + (cad.note ? ' · ' + cad.note : ''), mb: x.kb / 1024, href: CAD_BASE + x.f + CAD_Q, glb: glb ? CAD_BASE + glb + CAD_Q : '', typ: 'model' });
      });
    }
    if (['brodzik', 'wanna', 'panel ścienny', 'odpływ liniowy'].indexOf(p.cat) !== -1 && !p.noCadDecor) {   // UNITY (06.2026) nie ma w bazie CAD Decor 04.2026
      f.push({ ext: '3D', name: 'Baza CAD Decor — ' + CAD.name, desc: 'Model 3D w bazie CAD Decor (aktualizacja ' + CAD.date + ')', mb: 0, cad: true });
    }
    /* obrazy = to samo, co w galerii produktu (packshot, zdjęcia dodatkowe, aranżacje, rysunek, przekrój) */
    const seen = {}, nTyp = {};
    galleryFor(p).forEach(function (g) {
      if (g.kind === '3d' || seen[g.k]) return;
      seen[g.k] = 1;
      const im = SP.img[g.k]; if (!im) return;
      const href = SP.src(g.k), e = extOfPath(href);
      const typ = g.kind === 'pack' ? 'packshot' : g.kind === 'scene' ? 'aranzacja' : (/^rys:|^draw-/.test(g.k) ? 'rysunek' : 'grafika');
      nTyp[typ] = (nTyp[typ] || 0) + 1;
      const suf = { packshot: 'packshot', aranzacja: 'aranzacja', rysunek: 'rysunek-techniczny', grafika: 'grafika' }[typ];
      const lab = { packshot: 'Packshot', aranzacja: 'Aranżacja — wizualizacja poglądowa', rysunek: 'Rysunek techniczny, wymiary w mm', grafika: g.cap || 'Grafika' }[typ];
      add({ ext: e, name: base + '_' + suf + (nTyp[typ] > 1 ? '-' + nTyp[typ] : '') + '.' + e.toLowerCase(), desc: lab + ' · ' + im.w + ' × ' + im.h + ' px' + (im.tb ? ' · przezroczyste tło' : ''),
        href: href, typ: typ, pv: { t: 'img', src: href, tb: typ === 'packshot', note: typ === 'aranzacja' ? 'Wizualizacja poglądowa' : '' } });
    });
    docsFor(p).forEach(function (d) {              // prawdziwe pliki: assets/dokumenty (8_zasoby_kart.py)
      add({ ext: 'PDF', name: d.f, desc: d.t + ' · ' + d.str + ' ' + plural(d.str, 'strona', 'strony', 'stron'), mb: d.mb, href: DOC_BASE + d.f, doc: d.typ, t: d.t, typ: 'dokument' });
    });
    f.forEach(function (x) { if (!x.pv) x.pv = previewOf(p, x); });
    return f;
  }
  /* podgląd pliku przed pobraniem: PDF w ramce, obrazy w lightboksie, opis jako tekst */
  function previewOf(p, f) {
    const s = serieOf(p), n = f.name || '';
    const rys = SP.rys && SP.rys[p.ref];
    const rysSrc = rys ? SP.base + 'rys/' + rys.f : (p.fam === 'Balans' ? SP.src(p.shape === 'prostokątny' ? 'draw-balans-rect' : 'draw-balans-sq') : '');
    if (f.glb) return { t: '3d', src: f.glb, note: 'Podgląd 3D — przeciągnij, aby obrócić; kółko myszy przybliża' };
    if (f.karta) return { t: 'pdf', src: f.view };
    if (f.doc) return { t: 'pdf', src: f.href };
    if (/_packshot\./.test(n)) return { t: 'img', src: SP.src(p.im), tb: true };
    if (/_aranzacja/.test(n)) { const k = (galleryFor(p).filter(function (x) { return x.kind === 'scene'; })[0] || {}).k; return k ? { t: 'img', src: SP.src(k), note: 'Wizualizacja poglądowa' } : { t: 'img', src: SP.src(p.im), tb: true }; }
    if (/_rysunek/.test(n)) return rysSrc ? { t: 'img', src: rysSrc, note: f.ext === 'DWG' ? 'Podgląd rysunku — plik DWG zawiera ten sam widok w wektorze' : 'Wymiary w mm' } : { t: 'img', src: SP.src(p.im), tb: true, note: 'Rysunek w przygotowaniu — podgląd produktu' };
    if (f.cad) return { t: 'img', src: SP.src(p.im), tb: true, note: 'Model 3D jest w bazie CAD Decor „' + CAD.name + '” — podgląd produktu' };
    if (/_cechy/.test(n)) return p.fam === 'Balans' && SP.img['info-balans'] ? { t: 'img', src: SP.src('info-balans') } : { t: 'text', html: '<ol>' + (s.feats || []).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ol>' };
    if (/_opis/.test(n)) return { t: 'text', html: '<p>' + esc(s.lead) + '</p>' + ((s.feats || []).length ? '<ul>' + s.feats.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' : '') };
    return { t: 'img', src: SP.src(p.im), tb: true };
  }

  /* Karta produktu → „Centrum plików cyfrowych”: trzy kolumny (modele 3D i CAD / dokumentacja / packshoty i prezentacje) */

  /* Karta produktu: kafelki „Format wymiarowy” — wymiary tej serii w tym samym kolorze (zastępują dolną tabelę „Inne rozmiary”) */
  function pdSizes(p) {
    const seen = {}, opts = [];
    SP.products.filter(function (x) {
      return x.fam === p.fam && serieBase(x.s) === serieBase(p.s) && (x.c || '') === (p.c || '') && (x.ver || '') === (p.ver || '') && sizeKey(x);
    }).sort(function (a, b) { return area(a) - area(b) || String(a.shape).localeCompare(String(b.shape)); }).forEach(function (x) {
      const key = sizeKey(x) + '|' + (x.shape || '');
      if (seen[key]) { if (x.ref === p.ref) opts[seen[key] - 1] = x; return; }
      opts.push(x); seen[key] = opts.length;
    });
    if (opts.length < 2) return '';
    const lab = function (x) {
      return (x.b != null ? x.a + ' × ' + x.b + ' cm' : x.a + ' cm') + (x.shape === 'półokrągły' ? ' · półokr.' : x.shape === 'pięciokątny' ? ' · pięciok.' : '');
    };
    return '<div class="pds"><div class="pds-sizes" aria-label="Format wymiarowy">' +
      opts.map(function (x) {
        const on = x.ref === p.ref;
        return '<a class="pds-o' + (on ? ' is-on' : '') + '" href="' + H('produkt', { ref: x.ref }) + '"' + (on ? ' aria-current="true"' : '') + ' title="LM ' + esc(x.ref) + '">' + esc(lab(x)) + '</a>';
      }).join('') + '</div></div>';
  }
  function pfCols(p, all) {
    const groups = [
      { k: 'cad', t: 'Modele 3D i CAD', ic: 'cube', test: function (f) { return f.cad || ['DWG', 'OBJ', '3DS', 'GLB'].indexOf(f.ext) !== -1; } },
      { k: 'doc', t: 'Dokumentacja', ic: 'file', test: function (f) { return f.ext === 'PDF' || f.typ === 'rysunek' || f.typ === 'grafika'; } },
      { k: 'img', t: 'Packshoty i aranżacje', ic: 'image', test: function (f) { return f.typ === 'packshot' || f.typ === 'aranzacja'; } }
    ];
    const used = {};
    return groups.map(function (g) {
      const fs = all.map(function (f, i) { return { f: f, i: i }; }).filter(function (x) { return !used[x.i] && g.test(x.f) && (used[x.i] = 1); });
      const rows = fs.map(function (x) {
        const f = x.f, parts = String(f.desc || '').split(' · ');
        const CADT = { DWG: 'AutoCAD 2D / 3D', OBJ: 'SketchUp · Blender · 3ds Max', '3DS': '3ds Max · CAD Decor' };
        let head = f.t || parts[0], more = '';
        const cm = head.indexOf(', '), pa = head.indexOf('(');
        if (!f.t && cm !== -1 && !(pa !== -1 && pa < cm)) { more = head.slice(cm + 2); head = head.slice(0, cm); }   // „Packshot JPG, 2500 px”
        if (CADT[f.ext] && !f.t) { more = 'Model 3D ' + f.ext + (f.ext === 'OBJ' ? ' w archiwum ZIP' : ''); head = CADT[f.ext]; }
        const sub = [f.cad ? 'Gotowe w programie (baza ' + CAD.date + ')' : [more].concat(f.t ? [] : parts.slice(1)).filter(Boolean).join(' · '),
                     f.mb ? mbLabel(f.mb) : ''].filter(Boolean).join(' · ');
        if (f.cad) {
          return '<div class="pf-row is-cad">' + extBadge('CD3D') + '<div class="pf-t"><b>CAD Decor PRO · ' + esc(CAD.name) + '</b><small>' + esc(sub) + '</small></div>' +
            '<a class="btn btn-sm" href="' + H('start', { sek: 'cad', keep: 1 }) + '">Wstaw</a></div>';
        }
        return '<div class="pf-row">' + extBadge(f.ext) + '<div class="pf-t"><b>' + esc(head) + '</b><small title="' + esc(f.name) + '">' + esc(sub || f.name) + '</small></div>' +
          '<div class="pf-act"><button class="icon-btn" type="button" data-act="preview-all" data-file="' + x.i + '" aria-label="Podgląd: ' + esc(f.name) + '" title="Podgląd przed pobraniem">' + ic('eye', 16) + '</button>' +
          (f.href ? '<a class="icon-btn" href="' + esc(f.href) + '" download aria-label="Pobierz: ' + esc(f.name) + '" title="Pobierz">' + ic('download', 16) + '</a>'
                  : '<button class="icon-btn" type="button" data-act="demo" data-msg="Makieta: pobieranie pliku" data-detail="' + esc(f.name) + '" aria-label="Pobierz: ' + esc(f.name) + '">' + ic('download', 16) + '</button>') + '</div></div>';
      }).join('');
      const extra = g.k === 'img' ? '<div class="pf-share"><b>' + ic('send', 16) + ' Udostępnij zestaw inwestorowi</b><p>Skopiuj link do tej karty produktu — pliki i dokumentacja są dostępne bez logowania.</p>' +
        '<button class="btn btn-sm pf-copy" type="button" data-act="pf-copy">' + ic('copy', 15) + ' Kopiuj link do karty</button></div>' : '';
      const n = fs.length;
      return '<div class="pf-col"><div class="pf-col-h"><span class="pf-ic">' + ic(g.ic, 18) + '</span><b>' + g.t + '</b><span class="pf-n">' + (n ? pliki(n) : 'brak plików') + '</span></div>' +
        (rows || '<p class="pf-empty">Brak plików tego typu dla tego indeksu.</p>') + extra + '</div>';
    }).join('');
  }
  function pvBtn(i, name) {
    return '<button class="icon-btn" type="button" data-act="preview" data-file="' + i + '" aria-label="Podgląd: ' + esc(name) + '" title="Podgląd przed pobraniem">' + ic('eye', 16) + '</button>';
  }
  function openPreview(f) {
    if (!f || !f.pv) return;
    let box = $('#pv');
    if (!box) {
      box = document.createElement('div'); box.id = 'pv'; box.className = 'pv'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-modal', 'true');
      document.body.appendChild(box);
      box.addEventListener('click', function (e) { if (e.target === box || e.target.closest('[data-pv-close]')) closePreview(); });
    }
    const v = f.pv;
    const body = v.t === '3d' ? '<div class="pv-3d">' + mvHTML(v.src, f.desc, PD.p && PD.p.ref) + '</div>'
      : v.t === 'pdf' ? '<iframe src="' + esc(v.src) + '" title="Podgląd: ' + esc(f.name) + '"></iframe>'
      : v.t === 'text' ? '<div class="pv-text">' + v.html + '</div>'
      : '<div class="pv-img' + (v.tb ? ' is-pack' : '') + '"><img src="' + esc(v.src) + '" alt="' + esc(f.desc) + '"></div>';
    const dl = f.href ? '<a class="btn btn-sm btn-primary" href="' + esc(f.href) + '" download>' + ic('download', 15) + ' Pobierz</a>'
      : '<button class="btn btn-sm btn-primary" type="button" data-act="demo" data-msg="Makieta: pobieranie pliku" data-detail="' + esc(f.name) + '">' + ic('download', 15) + ' Pobierz</button>';
    box.innerHTML = '<div class="pv-card"><header class="pv-h">' + extBadge(f.ext) + '<div><b>' + esc(f.name) + '</b><small>' + esc(f.desc) + (v.note ? ' · ' + esc(v.note) : '') + '</small></div>' + dl +
      '<button class="icon-btn" type="button" data-pv-close aria-label="Zamknij podgląd">' + ic('x', 18) + '</button></header><div class="pv-b is-' + v.t + '">' + body + '</div></div>';
    box.classList.add('is-open'); document.documentElement.classList.add('pv-lock');
    const c = $('[data-pv-close]', box); if (c) c.focus({ preventScroll: true });
  }
  function closePreview() {
    const box = $('#pv'); if (!box) return;
    box.classList.remove('is-open'); box.innerHTML = ''; document.documentElement.classList.remove('pv-lock');
  }
  function extList(p) {
    const seen = {}, out = [];
    filesFor(p).forEach(function (f) { if (!seen[f.ext]) { seen[f.ext] = 1; out.push(f.ext); } });
    return ['JPG', 'PNG', 'PDF', 'DWG', '3D'].filter(function (e) { return out.indexOf(e) !== -1; });
  }
  function zestawFor(p) {
    const r = [];
    if (p.fam === 'Balans' || p.fam === 'Integral') r.push({ fam: 'Maskownica Balans/Integral', why: 'Maskownica odpływu' });
    if (['Grawello', 'Dante', 'Go Baby', 'Dafne'].indexOf(p.fam) !== -1) r.push({ fam: 'Panele do brodzików', why: 'Panel do brodzika', q: p.fam });
    if (p.fam === 'Ipsilon') r.push({ fam: 'Nogi Ipsilon', why: 'Zestaw nóg' });
    if (p.fam === 'Torres') {
      r.push({ fam: 'Nośnik', why: 'Podparcie wanny' });
      r.push({ fam: 'Obudowa uniwersalna', why: 'Zabudowa wanny' });
    }
    if (['Balans', 'Frigo', 'Integral'].indexOf(p.fam) !== -1) r.push({ fam: 'Wall Comfort', why: 'Strefa prysznica' });
    return r.filter(function (x) { return SP.serie(x.fam); });
  }

  /* ---------- komponenty ---------- */
  function dot(hx, cls) { return hx ? '<span class="dot' + (cls ? ' ' + cls : '') + '" style="--c:' + esc(hx) + '"></span>' : ''; }
  function pimg(key, alt) {
    const i = SP.img[key];
    if (!i) return '';
    return '<img' + (i.tb ? '' : ' class="is-mult"') + ' src="' + esc(SP.src(key)) + '" alt="' + esc(alt || '') + '" width="' + i.w +
      '" height="' + i.h + '" decoding="async">';
  }
  function refChip(p, big) {
    return '<button type="button" class="ref' + (big ? ' ref-lg' : '') + '" data-act="copy-ref" data-ref="' + esc(p.ref) +
      '" title="Kopiuj nr ref. LM" aria-label="Kopiuj nr ref. LM ' + esc(p.ref) + '"><span class="ref-k">LM</span><span class="ref-n">' +
      esc(p.ref) + '</span>' + ic('copy', big ? 16 : 13) + '</button>';
  }
  function refStatic(p) { return '<span class="ref"><span class="ref-k">LM</span><span class="ref-n">' + esc(p.ref) + '</span></span>'; }
  function extBadge(ext) { return '<span class="f-ext x-' + esc(String(ext).toLowerCase()) + '">' + esc(ext) + '</span>'; }
  function ftsHTML(p) {
    return '<span class="fts" aria-label="Typy plików">' + extList(p).map(function (e) {
      return '<span class="ft' + (e === '3D' ? ' ft-3d' : '') + '">' + e + '</span>';
    }).join('') + '</span>';
  }
  /* flaga marki na zdjęciu w katalogu: oryginalne logo Sensea (z etykiety) lub Schedpol (logotyp korporacyjny 2016) */
  const BRAND_LOGO = { 'Sensea': UP + 'assets/znaki/sensea.png', 'Schedpol': UP + 'assets/znaki/schedpol.svg' };
  /* gama LM z eksportu referencji (26.11.2026) — flaga na zdjęciu, jak logo marki */
  function gamaFlag(p, cls) {
    return p.g ? '<span class="flag flag-gama' + (cls ? ' ' + cls : '') + '" title="Gama Leroy Merlin wg eksportu referencji z 26.11.2026">Gama <b>' + esc(p.g) + '</b></span>' : '';
  }
  function brandFlag(p) {
    const src = BRAND_LOGO[p.brand];
    return src ? '<span class="flag flag-' + esc(p.brand.toLowerCase()) + '"><img src="' + src + '" alt="' + esc(p.brand) + '"></span>' : '';
  }
  function cardHTML(p, i) {
    const href = H('produkt', { ref: p.ref }), inT = inTeczka('p:' + p.ref);
    return `<article class="card" style="--i:${Math.min(i, 14)}">
      <a class="card-media" href="${href}" tabindex="-1" aria-hidden="true">
        ${pimg(p.im, '')}
        ${p.new ? '<span class="tag">Nowość</span>' : ''}
        ${brandFlag(p)}${gamaFlag(p)}
      </a>
      <button type="button" class="card-add${inT ? ' is-in' : ''}" data-act="add-product" data-ref="${esc(p.ref)}" aria-label="Dodaj pliki produktu ${esc(p.ref)} do Plików" title="Dodaj pliki do Plików">${ic(inT ? 'check' : 'plus', 16, 1.8)}</button>
      <div class="card-body">
        <p class="card-kicker">${kickerHTML(p)}</p>
        <h3 class="card-title"><a href="${href}">${esc(variant(p))}</a></h3>
        <p class="card-meta">${dot(p.hx)}${esc(metaLine(p))}</p>
        <div class="card-foot">${refChip(p)}${ftsHTML(p)}</div>
      </div>
    </article>`;
  }
  function rowHTML(p) {
    const href = H('produkt', { ref: p.ref });
    return `<tr data-href="${href}">
      <td>${refChip(p)}</td>
      <td><a class="t-prod" href="${href}"><span class="t-thumb">${pimg(p.im, '')}</span><span><b>${esc(p.s)}</b><small>${esc(typeShort(p))} · ${esc(p.brand)}</small></span></a></td>
      <td>${p.shape ? esc(p.shape) : '<span class="muted">—</span>'}</td>
      <td class="mono">${SP.dims(p) ? esc(variant(p)) : '<span class="muted">—</span>'}</td>
      <td>${p.c ? '<span class="t-col">' + dot(p.hx) + esc(p.c) + '</span>' : '<span class="muted">—</span>'}</td>
      <td class="mono">${p.g ? esc(p.g) : '<span class="muted">—</span>'}</td>
      <td>${ftsHTML(p)}</td>
      <td><div class="t-act">
        <a class="icon-btn" href="${esc(kartaPdf(p))}" download aria-label="Pobierz kartę produktu PDF ${esc(p.ref)}" title="Karta produktu PDF">${ic('file', 16)}</a>
        <button type="button" class="icon-btn" data-act="add-product" data-ref="${esc(p.ref)}" aria-label="Dodaj pliki produktu ${esc(p.ref)} do Plików" title="Dodaj pliki do Plików">${ic(inTeczka('p:' + p.ref) ? 'check' : 'plus', 16)}</button>
        <a class="icon-btn" href="${href}" aria-label="Otwórz kartę produktu ${esc(p.ref)}" title="Karta produktu">${ic('arrow-right', 16)}</a>
      </div></td>
    </tr>`;
  }

  /* ---------- tosty i schowek ---------- */
  function toast(msg, detail, icon) {
    const box = $('#toasts'), t = document.createElement('div');
    t.className = 'toast';
    t.innerHTML = ic(icon || 'check', 16, 1.8) + '<span>' + esc(msg) + (detail ? ' <span class="mono">' + esc(detail) + '</span>' : '') + '</span>';
    box.appendChild(t);
    while (box.children.length > 3) box.removeChild(box.firstChild);
    setTimeout(function () {
      t.classList.add('out');
      setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 420);
    }, 2800);
  }
  function legacyCopy(text) {
    try {
      const ta = document.createElement('textarea');
      ta.value = text; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;left:-9999px;top:0;opacity:0';
      document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta);
    } catch (e) { /* schowek niedostępny — makieta pokazuje samo potwierdzenie */ }
  }
  function copyRef(ref, btn) {
    let viaApi = false;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(ref).catch(function () { legacyCopy(ref); });
        viaApi = true;
      }
    } catch (e) { /* przejście do metody zapasowej */ }
    if (!viaApi) legacyCopy(ref);
    toast('Skopiowano nr ref.', ref, 'copy');
    if (btn && btn.classList.contains('ref')) {
      btn.classList.add('is-copied');
      setTimeout(function () { btn.classList.remove('is-copied'); }, 1400);
    }
  }

  /* ---------- teczka ---------- */
  const TZ_KEY = 'sp-a-teczka';
  let teczka = (function () {
    try {
      const v = JSON.parse(localStorage.getItem(TZ_KEY) || '[]');
      return Array.isArray(v) ? v.filter(function (x) { return x && x.id && x.title; }) : [];
    } catch (e) { return []; }
  })();
  function tzSave() { try { localStorage.setItem(TZ_KEY, JSON.stringify(teczka)); } catch (e) { /* brak dostępu do pamięci */ } }
  function inTeczka(id) { return teczka.some(function (x) { return x.id === id; }); }
  /* 25.11.2026: pozycje listy „Pliki” wskazują paczkę (p: produkt, s: seria, t: seria + typ), pliki i rozmiary liczone na żywo
     z prawdziwych plików — ZIP składa przeglądarka (JSZip z cdnjs, ładowany przy pierwszym pobraniu). */
  teczka = teczka.filter(function (x) { return /^(p|s|t):/.test(x.id); });          // stare pozycje makiety (np. „cad”) — usunięte
  const PKG = {};
  function seriesFiles(fam) {
    if (PKG[fam]) return PKG[fam];
    const seen = {}, out = [];
    SP.products.filter(function (p) { return p.fam === fam; }).forEach(function (p) {
      filesFor(p).forEach(function (f) {
        if (!f.href) return;
        const u = f.href.split('?')[0];
        if (seen[u]) return;
        seen[u] = 1; out.push(f);
      });
    });
    return (PKG[fam] = out);
  }
  function typOf(k) { return FTYP.filter(function (t) { return t.k === k; })[0]; }
  function itemFiles(x) {
    const m = /^(p|s|t):(.+)$/.exec(x.id || '');
    if (!m) return [];
    if (m[1] === 'p') {
      const p = SP.byRef(m[2]);
      if (!p) return [];
      const fs = filesFor(p).filter(function (f) { return f.href; });
      return x.names ? fs.filter(function (f) { return x.names.indexOf(f.name) !== -1; }) : fs;
    }
    const part = m[2].split(':'), fs = seriesFiles(part[0]);
    return m[1] === 't' ? fs.filter(function (f) { return f.typ === part[1]; }) : fs;
  }
  function itemStats(x) { return itemFiles(x).reduce(function (a, f) { return { n: a.n + 1, mb: a.mb + (f.mb || 0) }; }, { n: 0, mb: 0 }); }
  function zipSafe(s) { return String(s).replace(/[<>:"\/\\|?*]+/g, '-').replace(/\s+/g, ' ').trim(); }
  function itemDir(x, f) {
    if (x.id.charAt(0) === 'p') return zipSafe('LM ' + x.id.slice(2) + ' ' + x.title);
    const t = typOf(f.typ);
    return zipSafe(x.id.slice(2).split(':')[0]) + '/' + (t ? t.dir : 'Inne');
  }
  function zipList(items) {
    const seen = {}, list = [];
    items.forEach(function (x) {
      itemFiles(x).forEach(function (f) {
        const u = f.href.split('?')[0];
        if (seen[u]) return;
        seen[u] = 1; list.push({ href: f.href, path: itemDir(x, f) + '/' + zipSafe(f.name), mb: f.mb || 0 });
      });
    });
    return list;
  }
  function tzTotals() { return teczka.reduce(function (a, x) { const t = itemStats(x); return { n: a.n + t.n, mb: a.mb + t.mb }; }, { n: 0, mb: 0 }); }
  function tzAdd(item) {
    const i = teczka.findIndex(function (x) { return x.id === item.id; });
    if (i >= 0) { teczka[i] = item; toast('Zaktualizowano w Plikach', item.title); }
    else { teczka.unshift(item); toast('Dodano do Plików', item.title + ' · ' + pliki(itemStats(item).n)); }
    tzSave(); tzPaint(true);
  }
  function tzRemove(id) { teczka = teczka.filter(function (x) { return x.id !== id; }); tzSave(); tzPaint(); }
  function addProduct(ref, files) {
    const p = SP.byRef(ref);
    if (!p) return;
    const all = filesFor(p).filter(function (f) { return f.href; });
    const fs = (files || all).filter(function (f) { return f && f.href; });
    if (!fs.length) { toast('Zaznacz co najmniej jeden plik', '', 'info'); return; }
    const item = { id: 'p:' + ref, title: p.s + ' ' + variant(p), sub: 'LM ' + ref, im: p.im };
    if (fs.length < all.length) item.names = fs.map(function (f) { return f.name; });
    tzAdd(item);
  }
  function addSeries(fam) {
    const s = SP.serie(fam);
    if (!s) return;
    tzAdd({ id: 's:' + fam, title: 'Seria ' + fam + ' — wszystkie pliki', sub: indeksy(s.n), im: s.pack });
  }
  function addType(fam, type) {
    const s = SP.serie(fam), t = typOf(type);
    if (!s || !t) return;
    tzAdd({ id: 't:' + fam + ':' + type, title: fam + ' — ' + t.l.toLowerCase(), sub: indeksy(s.n), im: s.pack });
  }
  /* pakowanie ZIP w przeglądarce */
  let jszipP = null, zipBusy = false;
  function loadZip() {
    if (window.JSZip) return Promise.resolve(window.JSZip);
    if (!jszipP) {
      jszipP = new Promise(function (res, rej) {
        const sc = document.createElement('script');
        sc.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
        sc.onload = function () { res(window.JSZip); };
        sc.onerror = function () { jszipP = null; rej(new Error('JSZip')); };
        document.head.appendChild(sc);
      });
    }
    return jszipP;
  }
  function zipDownload(list, zipName, btn) {
    if (zipBusy) { toast('Trwa przygotowanie poprzedniej paczki', '', 'info'); return; }
    if (!list.length) { toast('Brak plików do pobrania', '', 'info'); return; }
    const tot = list.reduce(function (a, x) { return a + x.mb; }, 0);
    if (tot > 300 && !window.confirm('Paczka ma ok. ' + mbLabel(tot) + ' (' + pliki(list.length) + '). Przygotowanie może potrwać kilka minut. Kontynuować?')) return;
    zipBusy = true;
    const lab = btn ? btn.innerHTML : '';
    const set = function (t) { if (btn) { btn.disabled = true; btn.textContent = t; } };
    set('Przygotowanie…');
    loadZip().then(function (JSZip) {
      const zip = new JSZip(), failed = [];
      let i = 0, done = 0;
      const worker = function () {
        if (i >= list.length) return Promise.resolve();
        const x = list[i++];
        return fetch(x.href).then(function (r) { if (!r.ok) throw new Error(r.status); return r.arrayBuffer(); })
          .then(function (b) { zip.file(x.path, b, { binary: true }); }, function () { failed.push(x.path); })
          .then(function () { done++; set('Pobieranie ' + done + ' / ' + list.length); return worker(); });
      };
      return Promise.all([worker(), worker(), worker(), worker()]).then(function () {
        if (failed.length === list.length) throw new Error('brak plików');
        if (failed.length) zip.file('BRAKUJACE_PLIKI.txt', 'Tych plików nie udało się pobrać — spróbuj ponownie albo pobierz je z karty produktu:\r\n' + failed.join('\r\n'));
        return zip.generateAsync({ type: 'blob', compression: 'STORE' }, function (m) { set('Pakowanie ' + Math.round(m.percent) + '%'); });
      });
    }).then(function (blob) {
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = zipName;
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 60000);
      toast('Paczka ZIP gotowa', zipName + ' · ' + mbLabel(blob.size / 1048576), 'download');
      if (window.umami && window.umami.track) window.umami.track('pobranie', { plik: zipName, typ: 'zip', pliki: list.length });
    }, function () {
      toast('Nie udało się przygotować paczki ZIP', 'sprawdź połączenie i spróbuj ponownie', 'info');
    }).then(function () {
      zipBusy = false;
      if (btn) { btn.disabled = false; btn.innerHTML = lab; }
    });
  }
  function today() { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
  function zipItem(id, btn) {
    const m = /^(s|t):([^:]+)(?::(.+))?$/.exec(id || '');
    if (!m) return;
    const t = m[3] ? typOf(m[3]) : null;
    zipDownload(zipList([{ id: id, title: '' }]), zipSafe('Schedpol_' + m[2] + (t ? '_' + t.dir : '') + '_' + today()).replace(/ /g, '-') + '.zip', btn);
  }
  /* 25.11: „Kopiuj link” — adres, który po otwarciu odtwarza tę samą listę plików (#/pliki?lista=…) */
  function tzItem(id) {
    const m = /^(p|s|t):([^:]+)(?::(.+))?$/.exec(id || '');
    if (!m) return null;
    if (m[1] === 'p') { const p = SP.byRef(m[2]); return p ? { id: id, title: p.s + ' ' + variant(p), sub: 'LM ' + p.ref, im: p.im } : null; }
    const s = SP.serie(m[2]); if (!s) return null;
    if (m[1] === 's') return { id: id, title: 'Seria ' + s.fam + ' — wszystkie pliki', sub: indeksy(s.n), im: s.pack };
    const t = typOf(m[3]); return t ? { id: id, title: s.fam + ' — ' + t.l.toLowerCase(), sub: indeksy(s.n), im: s.pack } : null;
  }
  function tzImport(list) {
    let n = 0;
    String(list || '').split('|').forEach(function (id) {
      if (inTeczka(id)) return;
      const it = tzItem(id); if (it) { teczka.push(it); n++; }
    });
    if (n) { tzSave(); toast('Dodano do Plików', pliki(tzTotals().n), 'folder'); }
  }
  function tzLink() {
    const url = location.href.split('#')[0] + '#/pliki?lista=' + encodeURIComponent(teczka.map(function (x) { return x.id; }).join('|'));
    (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(function () { toast('Link do listy plików skopiowany', '', 'copy'); },
      function () { window.prompt('Skopiuj link do listy plików:', url); });
  }
  function tzMail() {
    const base = location.href.split('#')[0];
    const lines = teczka.map(function (x) {
      const m = /^(p|s|t):([^:]+)/.exec(x.id);
      const url = m[1] === 'p' ? base + '#/produkt?ref=' + m[2] : base + '#/katalog?seria=' + encodeURIComponent(m[2]);
      return '• ' + x.title + (x.sub ? ' (' + x.sub + ')' : '') + '\n  ' + url;
    });
    const body = 'Dzień dobry,\n\nprzesyłam linki do plików produktów Schedpol w ofercie Leroy Merlin (karty produktów, modele 3D, rysunki, instrukcje):\n\n' + lines.join('\n') + '\n\nPliki są dostępne bez logowania.';
    location.href = 'mailto:?subject=' + encodeURIComponent('Pliki produktów Schedpol — Leroy Merlin') + '&body=' + encodeURIComponent(body);
  }
  function tzListHTML() {
    if (!teczka.length) {
      return '<div class="tz-empty"><div class="empty-ic">' + ic('folder', 24) + '</div><b>Lista plików jest pusta</b>' +
        '<span>Dodaj pliki z katalogu, karty produktu albo paczkę całej serii.</span></div>';
    }
    return teczka.map(function (x) {
      const t = itemStats(x);
      return `<div class="tz-item">
        <span class="tz-ic">${x.im && SP.img[x.im] ? pimg(x.im, '') : ic(x.icon || 'zip', 20)}</span>
        <span class="tz-main"><span class="tz-t">${esc(x.title)}</span><span class="tz-s">${x.sub ? esc(x.sub) + ' · ' : ''}${pliki(t.n)} · ${mbLabel(t.mb)}</span></span>
        <button class="icon-btn" type="button" data-act="tz-remove" data-id="${esc(x.id)}" aria-label="Usuń z Plików: ${esc(x.title)}">${ic('x', 16)}</button>
      </div>`;
    }).join('');
  }
  function tzFootHTML() {
    const t = tzTotals(), dis = teczka.length ? '' : ' disabled';
    return `<div class="tz-total"><span>${pliki(t.n)} w ${teczka.length} ${plural(teczka.length, 'pozycji', 'pozycjach', 'pozycjach')}</span><b>${mbLabel(t.mb)}</b></div>
      <button class="btn btn-primary btn-block" type="button" data-act="tz-zip"${dis}>Pobierz ZIP <span class="btn-ic">${ic('download', 16)}</span></button>
      <div class="tz-row2">
        <button class="btn btn-block" type="button" data-act="tz-link"${dis}>${ic('copy', 16)} Kopiuj link</button>
        <button class="btn" type="button" data-act="tz-clear"${dis}>Wyczyść</button>
      </div>`;
  }
  function tzPaint(bump) {
    const t = tzTotals(), c = $('#teczkaCount');
    c.textContent = t.n;
    c.classList.toggle('is-zero', !t.n);
    if (bump) { c.classList.remove('bump'); void c.offsetWidth; c.classList.add('bump'); }
    $('#teczkaSum').textContent = teczka.length ? pliki(t.n) + ' · ' + mbLabel(t.mb) : 'Brak plików';
    $('#teczkaBody').innerHTML = tzListHTML();
    $('#teczkaFoot').innerHTML = tzFootHTML();
    const inl = $('#tzInline');
    if (inl) {
      $('#tzInSum').textContent = teczka.length ? pliki(t.n) + ' · ' + mbLabel(t.mb) : 'Brak plików';
      $('#tzInList').innerHTML = tzListHTML();
      $('#tzInFoot').innerHTML = tzFootHTML();
      paintPlikiTable();
    }
    $$('[data-act="add-product"]').forEach(function (b) {
      const on = inTeczka('p:' + b.getAttribute('data-ref'));
      if (b.classList.contains('card-add')) { b.classList.toggle('is-in', on); b.innerHTML = ic(on ? 'check' : 'plus', 16, 1.8); }
      else if (b.classList.contains('icon-btn')) b.innerHTML = ic(on ? 'check' : 'plus', 16);
    });
  }

  /* ---------- wyszukiwarka z podpowiedziami ---------- */
  function sgProduct(p) {
    return `<a class="sg-item" href="${H('produkt', { ref: p.ref })}">
      <span class="sg-thumb">${pimg(p.im, '')}</span>
      <span class="sg-main"><span class="sg-t">${esc(p.s)}<span class="mono">${esc(variant(p))}</span></span>
      <span class="sg-s">${dot(p.hx)}${esc([p.c, p.shape, p.brand].filter(Boolean).join(' · '))}</span></span>
      ${refStatic(p)}
    </a>`;
  }
  function sgSerie(s) {
    return `<a class="sg-item" href="${H('katalog', { seria: s.fam })}">
      <span class="sg-thumb">${pimg(s.pack, '')}</span>
      <span class="sg-main"><span class="sg-t">Seria ${esc(s.fam)}</span><span class="sg-s">${indeksy(s.n)} · ${esc(s.type)}</span></span>
      ${ic('arrow-right', 16)}
    </a>`;
  }
  function suggHTML(q) {
    q = String(q || '').trim();
    if (!q) {
      return '<div class="sg-h">Często szukane</div>' + HINTS.map(function (h) {
        return `<a class="sg-item" href="${H('katalog', { q: h })}"><span class="sg-thumb">${ic('search', 18)}</span><span class="sg-main"><span class="sg-t mono">${esc(h)}</span></span>${ic('arrow-right', 16)}</a>`;
      }).join('') + '<div class="sg-h">Kategorie</div>' + SP.cats.slice(0, 4).map(function (c) {
        const n = SP.products.filter(function (p) { return p.cat === c.id; }).length;
        return `<a class="sg-item" href="${H('katalog', { cat: c.id })}"><span class="sg-thumb">${pimg(CAT_REP[c.id], '')}</span><span class="sg-main"><span class="sg-t">${esc(c.label)}</span><span class="sg-s">${indeksy(n)}</span></span>${ic('arrow-right', 16)}</a>`;
      }).join('');
    }
    const res = SP.search(q), nq = norm(q);
    const fams = SP.series.filter(function (s) { return norm(s.fam).indexOf(nq) !== -1; }).slice(0, 3);
    if (!res.length && !fams.length) {
      return '<div class="sg-empty"><b>Brak wyników dla „' + esc(q) + '”</b>Numer ref. LM ma 8 cyfr. Możesz też wpisać serię i wymiar, np. Balans 80×100.</div>';
    }
    let h = '';
    if (res.length) h += '<div class="sg-h">Produkty</div>' + res.slice(0, 6).map(sgProduct).join('');
    if (fams.length) h += '<div class="sg-h">Serie</div>' + fams.map(sgSerie).join('');
    h += '<div class="sg-foot"><span><kbd>Enter</kbd> pokaż wszystkie wyniki</span><span class="mono">' + res.length + ' ' + plural(res.length, 'wynik', 'wyniki', 'wyników') + '</span></div>';
    return h;
  }
  function mountSearch(input, list, opts) {
    opts = opts || {};
    let active = -1;
    const items = function () { return $$('.sg-item', list); };
    const paint = function () { list.innerHTML = suggHTML(input.value); active = -1; };
    const setActive = function (i) {
      const it = items();
      if (!it.length) return;
      active = i < 0 ? it.length - 1 : (i >= it.length ? 0 : i);
      it.forEach(function (el, k) { el.classList.toggle('is-active', k === active); });
      it[active].scrollIntoView({ block: 'nearest' });
    };
    const submit = function () {
      const q = input.value.trim(), res = q ? SP.search(q) : [];
      if (opts.onClose) opts.onClose();
      if (/^(\d{8}|\d{13})$/.test(q) && res.length === 1) SPProto.go('produkt', { ref: res[0].ref });
      else SPProto.go('katalog', q ? { q: q } : {});
    };
    input.addEventListener('input', function () { paint(); if (opts.onOpen) opts.onOpen(); });
    input.addEventListener('focus', function () { paint(); if (opts.onOpen) opts.onOpen(); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); setActive(active + 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(active - 1); }
      else if (e.key === 'Enter') {
        e.preventDefault();
        const it = items();
        if (active >= 0 && it[active]) it[active].click(); else submit();
      } else if (e.key === 'Escape') { e.stopPropagation(); if (opts.onClose) opts.onClose(); input.blur(); }
    });
    return { paint: paint, submit: submit };
  }

  /* ==========================================================================
     Ekran: Start
     ========================================================================== */
  let packFam = 'Balans';
  let bigSearch = null;

  function packHTML(fam) {
    const s = SP.serie(fam) || SP.series[0];
    const n = sumFiles(s);
    const types = FT.filter(function (t) { return s.files[t.k]; }).sort(function (a, b) { return s.files[b.k] - s.files[a.k]; });
    const max = types.length ? s.files[types[0].k] : 1;
    return `<div class="pack-top">
        <span class="pack-thumb">${pimg(s.pack, '')}</span>
        <div><p class="pack-title">${esc(s.fam)}</p><p class="pack-meta">${pliki(n)} · ${mbLabel(s.mb)}</p></div>
      </div>
      <p class="pack-lead">${esc(s.type)} · ${indeksy(s.n)}</p>
      <div class="bars">${types.map(function (t) {
        return `<div class="bar"><em>${esc(t.l)}</em><i style="--w:${(s.files[t.k] / max).toFixed(3)}"></i><b>${s.files[t.k]}</b></div>`;
      }).join('')}</div>
      <div class="pack-foot">
        <button class="btn btn-primary btn-block" type="button" data-act="add-series" data-fam="${esc(s.fam)}">Dodaj serię do Plików <span class="btn-ic">${ic('plus', 16)}</span></button>
        <a class="link" href="${H('katalog', { seria: s.fam })}">Zobacz ${indeksy(s.n)} w katalogu ${ic('arrow-right', 14)}</a>
      </div>`;
  }

  /* Start → Nowości: kafle jak w Kategoriach [seria, obraz, x%, y%, podpis] */
  const NEWS = [
    ['Balans', 'balans-cas', 30, 75, 'Balans'], ['Harmony', 'odplyw-black', 55, 60], ['Consist', 'consist', 50, 60],
    ['Tebe', 'tebe', 50, 60], ['Najazd', 'najazd-a', 50, 60, 'Najazd do brodzików']
  ];
  /* Start → współpraca z LM (dane od użytkownika, 19.11.2026) */
  const COOP = [
    { l: 'Kompletność dostaw w 2025 r.', v: '99,53%', i: 'box-check' },
    { l: 'Średni czas realizacji zamówień w 2025 r.', v: '6,31', u: 'dnia', i: 'clock' },
    { l: 'Dropshipping od 1 produktu · realizacja do 4 dni', v: '+45 zł', u: 'netto dopłaty', i: 'truck' }   // 26.11: bez minimum zakupowego
  ];
  /* doradca techniczny — dane ze schedpol.pl/kontakt (sprawdzone 19.11.2026) */
  const TECH = { n: 'Maciej Naskręt', role: 'Doradca techniczny — klient indywidualny i inwestycje', tel: '502 356 267', mail: 'doradcatechniczny@schedpol.pl' };
  const BOK_AREA = { '1': 'Polska zachodnia', '2': 'Polska wschodnia i północna', '3': 'Polska południowa' };
  function bokMapSVG(k) {
    const m = SP.bokMap; if (!m) return '';
    return '<svg class="bok-map" viewBox="' + m.vb + '" role="img" aria-label="Region ' + esc(BOK_AREA[k] || '') + '">' +
      Object.keys(m.r).map(function (r) { return '<path class="' + (r === k ? 'on' : '') + '" d="' + m.r[r] + '"/>'; }).join('') + '</svg>';
  }

  /* Start → Kategorie (wariant hybrydowy 20.11.2026): aranżacja albo kolaż + pasek informacji dla projektanta */
  const CAT_V = {   // z = przybliżenie, f = punkt produktu [x, y] w kaflu (0–1), który trafia na środek kadru
    'brodzik': { img: 'integral-ws', z: 1.5, f: [0.6, 0.8] },
    'wanna': { img: 'torres-b', pos: '50% 62%' },
    'odpływ liniowy': { img: 'odplyw-black', pos: '50% 100%', z: 1.8, f: [0.66, 0.7] },
    'panel ścienny': { img: 'wc-po', z: 1.8, f: [0.36, 0.52] },
    'nośnik': { img: 'nosnik', z: 1.6, f: [0.42, 0.66] },
    'obudowa': { img: 'obudowa-pol', pos: '50% 68%' },
    'akcesoria': { noCols: 1, col: [['p-maskownica-zlota', 'maskownica'], ['pk-packshot-panel-do-brodzika-dante-2500x25-08d42a', 'panel do brodzika'], ['p-nogi', 'nogi do brodzika'], ['p-najazd', 'najazd']] }
  };
  const SHAPE_SVG = [
    [/kwadr/, 'kwadratowy', '<rect x="3" y="3" width="14" height="14"/>'],
    [/prostok/, 'prostokątny', '<rect x="1" y="5" width="18" height="10"/>'],
    [/półokr|polokr|łuk|R55/i, 'półokrągły', '<path d="M3 3h14v14H3A14 14 0 0 1 3 3z" transform="matrix(-1 0 0 1 20 0)"/>'],
    [/pięciok|pieciok/, 'pięciokątny', '<path d="M3 3h14v14H9L3 11z"/>']
  ];
  function catTile(c, i) {
    const ps = SP.products.filter(function (p) { return p.cat === c.id; });
    const v = CAT_V[c.id] || {};
    const seen = {}, cols = [];
    ps.forEach(function (p) { if (p.hx && !seen[p.hx]) { seen[p.hx] = 1; cols.push([p.hx, p.c || '']); } });
    const shp = SHAPE_SVG.filter(function (s) { return ps.some(function (p) { return s[0].test(p.shape || ''); }); });
    const nCad = ps.filter(function (p) { return cadFor(p); }).length;
    const meta = [];
    if (cols.length > 1 && !v.noCols) meta.push('<span class="cm-cols">' + cols.slice(0, 6).map(function (x) { return '<i style="background:' + esc(x[0]) + '" title="' + esc(x[1]) + '"></i>'; }).join('') + (cols.length > 6 ? '<em>+' + (cols.length - 6) + '</em>' : '') + '</span>');
    if (shp.length > 1) meta.push('<span class="cm-shp">' + shp.map(function (s) { return '<svg viewBox="0 0 20 20" aria-label="' + s[1] + '"><title>' + s[1] + '</title>' + s[2] + '</svg>'; }).join('') + '</span>');
    if (nCad) meta.push('<span class="cm-cad">DWG · 3D</span>');
    const metaH = meta.length ? '<span class="cat-meta">' + meta.join('') + '</span>' : '';
    const body = v.col
      ? '<span class="hcat-col n' + v.col.length + '">' + v.col.map(function (x) { return '<span><img src="' + esc(SP.src(x[0])) + '" alt="" decoding="async"><small>' + esc(x[1]) + '</small></span>'; }).join('') + '</span>'
      : '<img src="' + esc(SP.src(v.img || CAT_REP[c.id])) + '" alt="" decoding="async" style="object-position:' + (v.pos || '50% 50%') + (v.z ? (function () { const m = (1 - 1 / v.z) / 2, cl = function (d) { return Math.max(-m, Math.min(m, d)) * 100; }; return ';--z:' + v.z + ';--tx:' + cl(0.5 - v.f[0]).toFixed(1) + '%;--ty:' + cl(0.5 - v.f[1]).toFixed(1) + '%'; })() : '') + '">';
    return `<a class="hcat ${v.col ? 'is-col' : 'is-scene'} hcat-${i} rv" style="--d:${i * 40}ms" href="${H('katalog', { cat: c.id })}">
            ${body}
            <span class="hcat-go">${ic('arrow-up-right', 18)}</span>
            <span class="hcat-txt"><b>${esc(c.label)}</b><span>${indeksy(ps.length)}</span>${metaH}</span>
          </a>`;
  }
  function renderStart(params) {
    const total = SP.products.length;
    const nFiles = SP.series.reduce(function (a, s) { return a + sumFiles(s); }, 0);
    const mb = SP.series.reduce(function (a, s) { return a + (s.mb || 0); }, 0);
    const tiles = [
      { ic: 'grid', t: 'Katalog z filtrami', d: 'Szukaj po nr. ref. LM, serii, wymiarze, kolorze i kształcie — ' + total + ' indeksów Schedpol i Sensea.', href: H('katalog') },
      { ic: 'zip', t: 'Paczki plików serii', d: 'Packshoty, aranżacje, rysunki i karty produktów całej serii w jednym pliku ZIP.', href: H('pliki') },
      { ic: 'cube', t: 'Baza CAD Decor', d: 'Modele 3D „' + CAD.name + '” — aktualizacja ' + CAD.date + ', ' + mbLabel(CAD.mb) + '.', href: H('start', { sek: 'cad', keep: 1 }) },
      { ic: 'clipboard', t: 'Instrukcje i karty gwarancyjne', d: 'Instrukcja montażu i karta gwarancyjna Stabilsafe przypisane do indeksu — do pobrania w PDF.', href: H('pliki', { typ: 'dokumenty' }) }
    ];

    app.innerHTML = `
    <div class="home">
      <section class="home-hero" aria-labelledby="heroT">
        <div class="wrap home-hero-in">
          <div class="home-copy">
            <div class="hero-partner rv"><img class="lm-logo" src="${UP}assets/znaki/leroy-merlin.svg" alt="Leroy Merlin" width="79" height="48"><span>Strefa architekta i projektanta</span></div>
            <h1 class="home-title rv" id="heroT" style="--d:60ms">Projektuj łazienki z produktami Schedpol i Sensea</h1>
            <p class="hero-lead rv" style="--d:120ms">Karty produktów PDF, rysunki techniczne, packshoty, instrukcje montażu i modele 3D w bazie CAD Decor — dla ${total} indeksów z oferty Leroy Merlin.</p>
            <div class="bigsearch rv" id="bigBox" style="--d:180ms" role="search">
              ${ic('search', 22)}
              <input id="bigSearch" type="search" placeholder="Nr ref. LM, EAN, seria, wymiar, kolor…" autocomplete="off" spellcheck="false" aria-label="Szukaj w bibliotece" aria-controls="bigList">
              <kbd>/</kbd>
              <button class="btn btn-primary" type="button" data-act="big-submit">Szukaj <span class="btn-ic">${ic('arrow-right', 16)}</span></button>
              <div class="sugg" id="bigList"></div>
            </div>
            <div class="hints rv" style="--d:240ms"><span>Popularne:</span>${HINTS.map(function (h) {
              return '<button class="hint" type="button" data-act="hint" data-q="' + esc(h) + '">' + esc(h) + '</button>';
            }).join('')}</div>
          </div>
          <div class="hcoop rv" style="--d:200ms" aria-labelledby="coopT">
            <div class="hcoop-h"><span class="home-k">30 lat współpracy z Leroy Merlin</span><h2 id="coopT">Razem od 1997 roku</h2></div>
            <dl class="hcoop-l">${COOP.map(function (c) {
              return '<div class="hco' + (c.wide ? ' is-wide' : '') + '">' + (c.i ? '<span class="hco-ic" aria-hidden="true">' + ic(c.i, 24) + '</span>' : '') + '<dt>' + esc(c.l) + '</dt><dd><b>' + esc(c.v) + '</b>' + (c.u ? '<span>' + esc(c.u) + '</span>' : '') + '</dd></div>';
            }).join('')}</dl>
          </div>
</div>
        </div>
      </section>

      <div class="wrap">
          <section class="home-block hnews-box" aria-labelledby="newsT">
            <div class="home-h home-h-row"><div><span class="home-k">Nowości 2026</span><h2 id="newsT">Nowe serie w ofercie Leroy Merlin</h2></div>
              <a class="link" href="${H('katalog')}">Cały katalog ${ic('arrow-right', 14)}</a></div>
            <div class="hnews">${NEWS.map(function (x, i) {
              const s = SP.serie(x[0]); if (!s) return '';
              const n = SP.products.filter(function (p) { return p.fam === x[0]; }).length;
              const pack = !SP.img[x[1]] || SP.img[x[1]].k === 'pack' || /^p-|^pk-/.test(x[1]);
              return `<a class="hcat hnew rv hnew-${i}${pack ? ' is-pack' : ''}" href="${H('katalog', { seria: x[0] })}">
                <img src="${esc(SP.src(x[1]))}" alt="" decoding="async" style="object-position:${x[2]}% ${x[3]}%">
                ${pack ? '' : '<span class="hnew-tag">Nowość</span>'}
                <span class="hcat-go">${ic('arrow-up-right', 16)}</span>
                <span class="hcat-txt"><b>${esc(x[4] || x[0])}</b><span>${esc(typeShort({ fam: x[0] }))} · ${indeksy(n)}</span></span>
              </a>`;
            }).join('')}</div>
          </section>

      <section class="home-block" aria-labelledby="catT">
        <div class="home-h home-h-row"><div><span class="home-k">Oferta w Leroy Merlin</span><h2 id="catT">Kategorie</h2></div>
          <a class="link" href="${H('katalog')}">Cały katalog ${ic('arrow-right', 14)}</a></div>
        <div class="hcats hcats-v2">${SP.cats.map(function (c, i) { return catTile(c, i); }).join('')}</div>
      </section>

      <section class="home-block panel hcad rv" id="sek-cad">
        <div class="hcad-l">
          <span class="cad-ic">${ic('cube', 24)}</span>
          <div>
            <h2>Baza CAD Decor</h2>
            <div class="cad-chips"><span class="chip">${esc(CAD.name)}</span><span class="chip mono">aktualizacja ${CAD.date}</span><span class="chip mono">${mbLabel(CAD.mb)}</span></div>
          </div>
        </div>
        <ol class="steps">
          <li>Pobierz bazę „${esc(CAD.name)}” — stąd albo przez aktualizator baz w programie.</li>
          <li>Zainstaluj bazę w CAD Decor lub CAD Decor PRO.</li>
          <li>Wstaw model do projektu i potwierdź nr ref. LM na karcie produktu w portalu.</li>
        </ol>
        <div class="cad-foot">
          <a class="btn btn-dark" href="${CAD_URL}" target="_blank" rel="noopener">${ic('download', 16)} Pobierz bazę</a>
          <a class="btn" href="${CAD_DOC}" target="_blank" rel="noopener">${ic('file', 16)} Instrukcje CAD Decor PRO</a>
        </div>
      </section>

      <section class="home-block hsupport rv" id="sek-kontakt" aria-labelledby="supT">
        <div class="hsupport-intro">
          <span class="home-k">Wsparcie techniczne</span>
          <h2 id="supT">Brakuje pliku albo wymiaru?</h2>
          <p>Biuro Obsługi Klienta Schedpol odpowiada na pytania o montaż, dobór produktu i materiały do projektu.</p>
          <span class="chip">${ic('clock', 14)} ${esc(SP.contacts.hours)}</span>
        </div>
        <div class="bok-grid">${SP.contacts.bok.map(function (b, i) {
          return `<div class="sb bok">
            ${bokMapSVG(String(i + 1))}
            <div class="bok-txt"><b>${esc(b.n)}</b>
            <small>${esc(BOK_AREA[String(i + 1)] || '')}</small>
            <a class="mono" href="tel:+48${esc(b.tel.replace(/\s/g, ''))}">${ic('phone', 15)} ${esc(b.tel)}</a>
            <a href="mailto:${esc(b.mail)}">${ic('mail', 15)} ${esc(b.mail)}</a></div></div>`;
        }).join('')}
        ${TECH ? `<div class="sb bok bok-tech">
            <span class="bok-ic">${ic('user', 30)}</span>
            <div class="bok-txt"><b>${esc(TECH.n)}</b><small>${esc(TECH.role)}</small>
            <a class="mono" href="tel:+48${esc(TECH.tel.replace(/\s/g, ''))}">${ic('phone', 15)} ${esc(TECH.tel)}</a>
            <a href="mailto:${esc(TECH.mail)}">${ic('mail', 15)} ${esc(TECH.mail)}</a></div></div>` : ''}</div>
      </section>

      <section class="home-block" aria-labelledby="toolT">
        <div class="home-h"><span class="home-k">Narzędzia pracy</span><h2 id="toolT">Szybkie akcje projektowe</h2></div>
        <div class="tiles tiles-4">${tiles.map(function (t, i) {
          return `<a class="tile rv" style="--d:${i * 50}ms" href="${t.href}">
            <span class="tile-top"><span class="tile-ic">${ic(t.ic, 22)}</span><span class="tile-go">${ic('arrow-up-right', 18)}</span></span>
            <b>${esc(t.t)}</b><p>${esc(t.d)}</p>
          </a>`;
        }).join('')}</div>
      </section>
      </div>
    </div>`;

    const box = $('#bigBox'), input = $('#bigSearch');
    bigSearch = mountSearch(input, $('#bigList'), {
      onOpen: function () { box.classList.add('is-open'); },
      onClose: function () { box.classList.remove('is-open'); }
    });
    box.addEventListener('focusout', function (e) {
      if (!box.contains(e.relatedTarget)) setTimeout(function () { if (!box.contains(document.activeElement)) box.classList.remove('is-open'); }, 140);
    });
    if (params && params.sek) scrollToSek(params.sek);
  }
  function scrollToSek(sek) {
    requestAnimationFrame(function () {
      const el = document.getElementById('sek-' + sek);
      if (!el) return;
      el.classList.add('in');
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  }

  /* ==========================================================================
     Ekran: Katalog
     ========================================================================== */
  const PARAM = { cat: 'cat', fam: 'seria', shape: 'ksztalt', size: 'rozmiar', color: 'kolor', brand: 'marka', gama: 'gama' };
  const C = { q: '', f: { cat: [], fam: [], shape: [], size: [], color: [], brand: [], gama: [] }, sort: 'seria', view: 'grid', limit: 24, open: {} };
  const COLORS = (function () {
    const m = {};
    SP.products.forEach(function (p) { if (p.c) { m[p.c] = m[p.c] || { v: p.c, l: p.c, hx: p.hx, n: 0 }; m[p.c].n++; } });
    return Object.keys(m).map(function (k) { return m[k]; }).sort(function (a, b) { return a.l.localeCompare(b.l, 'pl'); });   // alfabetycznie
  })();
  /* rozmiar: długość × szerokość (większy wymiar pierwszy), np. „100 × 80 cm”; odpływy — sama długość */
  function sizeKey(p) {
    const a = typeof p.a === 'number' ? p.a : null, b = typeof p.b === 'number' ? p.b : null;
    if (a != null && b != null) return Math.max(a, b) + ' × ' + Math.min(a, b) + ' cm';
    if (p.a != null && p.b != null) return String(p.a).replace(/-/g, '–') + ' × ' + p.b + ' cm';
    if (p.a != null) return String(p.a).replace(/-/g, '–') + ' cm';
    return '';
  }
  const SIZES = (function () {
    const m = {};
    SP.products.forEach(function (p) { const k = sizeKey(p); if (k) { m[k] = m[k] || { v: k, l: k, n: 0, s: 0 }; m[k].n++; } });
    return Object.keys(m).map(function (k) {
      const nums = k.match(/\d+/g).map(Number);
      m[k].s = nums[0] * 1000 + (nums[1] || 0);
      return m[k];
    }).sort(function (a, b) { return a.s - b.s; });
  })();
  const GAMY = ['A', 'B', 'C', 'L', 'M', 'X', 'brak'];   // wg eksportu referencji LM z 26.11.2026 (nowa gama M; assets/aktualizacja-lm.js)
  const FACETS = [
    { id: 'brand', label: 'Marka', get: function (p) { return p.brand; }, opts: [{ v: 'Schedpol', l: 'Schedpol' }, { v: 'Sensea', l: 'Sensea' }] },
    { id: 'cat', label: 'Kategoria', get: function (p) { return p.cat; }, opts: SP.cats.map(function (c) { return { v: c.id, l: c.label }; }) },
    { id: 'fam', label: 'Seria', get: function (p) { return p.fam; }, opts: SP.series.map(function (s) { return { v: s.fam, l: s.fam, n: SP.products.filter(function (p) { return p.fam === s.fam; }).length }; }).sort(function (a, b) { return b.n - a.n || a.l.localeCompare(b.l, 'pl'); }), collapse: 8 },   // najwięcej produktów u góry
    { id: 'shape', label: 'Kształt', get: function (p) { return p.shape; }, opts: ['kwadratowy', 'prostokątny', 'półokrągły', 'pięciokątny'].map(function (v) { return { v: v, l: cap(v) }; }) },
    { id: 'size', label: 'Rozmiar (długość × szerokość)', get: function (p) { return sizeKey(p); }, opts: SIZES, collapse: 10, mono: true, hideZero: true },
    { id: 'color', label: 'Kolor', get: function (p) { return p.c; }, opts: COLORS, collapse: 7 },
    { id: 'gama', label: 'Gama LM', get: function (p) { return p.g || 'brak'; }, opts: GAMY.map(function (g) { return { v: g, l: g === 'brak' ? 'nie podano' : g, mono: g !== 'brak' }; }),
      hint: 'Gama wg eksportu referencji LM z 26.11.2026.' }
  ];
  function facetById(id) { return FACETS.filter(function (F) { return F.id === id; })[0]; }
  function optLabel(F, v) { const o = F.opts.filter(function (x) { return x.v === v; })[0]; return o ? o.l : v; }

  function catFromParams(params) {
    C.q = params.q || '';
    Object.keys(PARAM).forEach(function (k) {
      C.f[k] = params[PARAM[k]] ? String(params[PARAM[k]]).split('|').filter(Boolean) : [];
    });
    C.sort = ['seria-za', 'nowe'].indexOf(params.sort) !== -1 ? params.sort : 'seria';
    C.view = params.widok === 'tabela' ? 'table' : 'grid';
    C.limit = 24;
  }
  function catParams() {
    const o = {};
    if (C.q) o.q = C.q;
    Object.keys(PARAM).forEach(function (k) { if (C.f[k].length) o[PARAM[k]] = C.f[k].join('|'); });
    if (C.sort !== 'seria') o.sort = C.sort;
    if (C.view === 'table') o.widok = 'tabela';
    return o;
  }
  function syncUrl() { try { history.replaceState(null, '', SPProto.href('katalog', catParams())); } catch (e) { /* file:// bez historii */ } }
  function pass(p, skip) {
    for (let i = 0; i < FACETS.length; i++) {
      const F = FACETS[i];
      if (F.id === skip) continue;
      const sel = C.f[F.id];
      if (sel.length && sel.indexOf(F.get(p)) === -1) return false;
    }
    return true;
  }
  function area(p) {
    const a = typeof p.a === 'number' ? p.a : (parseFloat(p.a) || 0);
    const b = typeof p.b === 'number' ? p.b : 0;
    return a * (b || 1);
  }
  function sortList(list) {
    const idx = {};
    SP.series.forEach(function (s, i) { idx[s.fam] = i; });
    const l = list.slice();
    if (C.sort === 'nowe') {
      l.sort(function (x, y) { return (y.new ? 1 : 0) - (x.new ? 1 : 0) || idx[x.fam] - idx[y.fam] || area(x) - area(y); });
    } else {
      const dir = C.sort === 'seria-za' ? -1 : 1;     // Seria Z–A: odwrotna kolejność serii, w serii bez zmian
      l.sort(function (x, y) {
        return dir * String(x.fam).localeCompare(String(y.fam), 'pl') || String(x.s).localeCompare(String(y.s), 'pl') ||
          String(x.c).localeCompare(String(y.c), 'pl') || area(x) - area(y);
      });
    }
    return l;
  }
  function facetsHTML(base) {
    let h = '<div class="facets-head"><span>Filtry</span><button class="icon-btn" type="button" data-act="close-all" aria-label="Zamknij filtry">' + ic('x', 18) + '</button></div>';
    FACETS.forEach(function (F) {
      const cnt = {};
      base.forEach(function (p) { if (pass(p, F.id)) { const v = F.get(p); cnt[v] = (cnt[v] || 0) + 1; } });
      const sel = C.f[F.id], open = !!C.open[F.id];
      let shown = 0, hidden = 0, body = '';
      let vis = 0;
      F.opts.forEach(function (o) {
        const on = sel.indexOf(o.v) !== -1, n = cnt[o.v] || 0;
        if (F.hideZero && n === 0 && !on) return;      // rozmiar: tylko wymiary obecne w bieżącym wyborze
        const i = vis++;
        if (F.collapse && !open && i >= F.collapse && !on) { hidden++; return; }
        shown++;
        body += '<label class="fopt' + (n === 0 && !on ? ' is-zero' : '') + '"><input type="checkbox" data-facet="' + F.id + '" value="' + esc(o.v) + '"' + (on ? ' checked' : '') + '>' +
          '<span class="fbox">' + ic('check', 12, 2.2) + '</span><span class="fl' + (o.mono ? ' mono' : '') + '">' + (o.hx ? dot(o.hx) : '') + esc(o.l) + '</span><span class="fc">' + n + '</span></label>';
      });
      h += '<div class="fg" role="group" aria-label="' + esc(F.label) + '"><div class="fg-h">' + esc(F.label) + (sel.length ? '<span>' + sel.length + '</span>' : '') + '</div>' + body;
      const total = F.hideZero ? vis : F.opts.length;
      if (F.collapse && total > F.collapse) {
        h += '<button class="fmore" type="button" data-act="facet-more" data-facet="' + F.id + '" aria-expanded="' + open + '">' +
          (open ? 'Pokaż mniej' : 'Pokaż wszystkie (' + total + ')') + ic('chevron-down', 14) + '</button>';
      }
      if (F.hint) h += '<p class="fhint">' + esc(F.hint) + '</p>';
      h += '</div>';
    });
    return h;
  }
  function toolbarHTML(n) {
    let chips = '';
    if (C.q) chips += '<span class="chip"><span class="chip-k">Szukaj:</span> ' + esc(C.q) + '<button class="chip-x" type="button" data-act="rm-q" aria-label="Usuń wyszukiwaną frazę">' + ic('x', 12, 2) + '</button></span>';
    FACETS.forEach(function (F) {
      C.f[F.id].forEach(function (v) {
        chips += '<span class="chip"><span class="chip-k">' + esc(F.label) + ':</span> ' + esc(optLabel(F, v)) +
          '<button class="chip-x" type="button" data-act="rm-filter" data-facet="' + F.id + '" data-value="' + esc(v) + '" aria-label="Usuń filtr: ' + esc(optLabel(F, v)) + '">' + ic('x', 12, 2) + '</button></span>';
      });
    });
    if (chips) chips += '<button class="chip-clear" type="button" data-act="clear-filters">Wyczyść wszystko</button>';
    const all = n === SP.products.length && !chips;
    return `<div class="tb-count" aria-live="polite"><b>${n}</b> ${all ? plural(n, 'indeks', 'indeksy', 'indeksów') : plural(n, 'wynik', 'wyniki', 'wyników') + ' z ' + SP.products.length}</div>
      <div class="tb-chips">${chips}</div>
      <div class="tb-tools">
        <button class="btn btn-sm only-m" type="button" data-act="open-facets">${ic('filter', 16)} Filtry</button>
        <label class="select"><span class="sr">Sortowanie</span>
          <select id="sortSel" aria-label="Sortowanie">
            <option value="seria"${C.sort === 'seria' ? ' selected' : ''}>Seria A–Z</option>
            <option value="seria-za"${C.sort === 'seria-za' ? ' selected' : ''}>Seria Z–A</option>
            <option value="nowe"${C.sort === 'nowe' ? ' selected' : ''}>Nowość</option>
          </select>${ic('chevron-down', 16)}
        </label>
        <div class="seg" role="group" aria-label="Widok wyników">
          <button type="button" data-act="view" data-view="grid" aria-pressed="${C.view === 'grid'}" aria-label="Widok kafli" title="Kafle">${ic('grid', 16)}</button>
          <button type="button" data-act="view" data-view="table" aria-pressed="${C.view === 'table'}" aria-label="Widok tabeli" title="Tabela">${ic('list', 16)}</button>
        </div>
      </div>`;
  }
  function resultsHTML(list) {
    if (!list.length) {
      return `<div class="empty"><div class="empty-ic">${ic('search', 24)}</div><h3>Brak produktów dla tych kryteriów</h3>
        <p>Usuń część filtrów albo zmień frazę. Numer ref. LM ma 8 cyfr — wpisz go w całości, np. 89189406.</p>
        <button class="btn btn-dark" type="button" data-act="clear-filters">Wyczyść filtry</button></div>`;
    }
    const part = list.slice(0, C.limit);
    let h;
    if (C.view === 'table') {
      h = '<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Ref LM</th><th>Seria</th><th>Kształt</th><th>Wymiar</th><th>Kolor</th><th>Gama</th><th>Pliki</th><th><span class="sr">Akcje</span></th></tr></thead><tbody>' +
        part.map(rowHTML).join('') + '</tbody></table></div>';
    } else {
      h = '<div class="grid">' + part.map(cardHTML).join('') + '</div>';
    }
    h += '<div class="more">' + (list.length > part.length ? '<button class="btn" type="button" data-act="more">Pokaż kolejne ' + Math.min(24, list.length - part.length) + '</button>' : '') +
      '<span class="more-info">Wyświetlono ' + part.length + ' z ' + list.length + '</span></div>';
    return h;
  }
  function paintCatalog(focusKey) {
    const base = C.q ? SP.search(C.q) : SP.products;
    const list = sortList(base.filter(function (p) { return pass(p); }));
    const fa = $('#facets');
    if (!fa) return;
    const st = fa.scrollTop;
    fa.innerHTML = facetsHTML(base);
    fa.scrollTop = st;
    $('#tb').innerHTML = toolbarHTML(list.length);
    $('#res').innerHTML = resultsHTML(list);
    if (focusKey) {
      const el = $$('input[data-facet]', fa).filter(function (i) { return i.getAttribute('data-facet') + '|' + i.value === focusKey; })[0];
      if (el) el.focus({ preventScroll: true });
    }
  }
  function renderKatalog(params) {
    catFromParams(params || {});
    app.innerHTML = `
    <div class="wrap">
      <header class="page-head">
        <div>
          <span class="eyebrow">Katalog · oferta w Leroy Merlin</span>
          <h1 class="page-title" style="margin-top:18px">Katalog produktów</h1>
          <p class="page-sub">${SP.products.length} produktów w ${SP.series.length} seriach. Każda pozycja ma numer ref. LM, wymiary i komplet plików do projektu. Gama wg eksportu referencji LM z 26.11.2026.</p>
        </div>
        <label class="cat-search">${ic('search', 18)}<span class="sr">Filtruj katalog</span>
          <input id="catQ" type="search" placeholder="Filtruj: nr ref., EAN, seria, wymiar, kolor…" value="${esc(C.q)}" autocomplete="off" spellcheck="false"><kbd>/</kbd>
        </label>
      </header>
      <div class="cat-layout">
        <aside class="facets" id="facets" aria-label="Filtry katalogu"></aside>
        <section aria-label="Wyniki">
          <div class="tb" id="tb"></div>
          <div id="res"></div>
        </section>
      </div>
    </div>`;
    paintCatalog();

    let timer = null;
    $('#catQ').addEventListener('input', function (e) {
      clearTimeout(timer);
      const v = e.target.value;
      timer = setTimeout(function () { C.q = v.trim(); C.limit = 24; paintCatalog(); syncUrl(); }, 140);
    });
    $('#facets').addEventListener('change', function (e) {
      const inp = e.target.closest('input[data-facet]');
      if (!inp) return;
      const id = inp.getAttribute('data-facet'), arr = C.f[id], i = arr.indexOf(inp.value);
      if (inp.checked && i === -1) arr.push(inp.value);
      if (!inp.checked && i !== -1) arr.splice(i, 1);
      C.limit = 24;
      paintCatalog(id + '|' + inp.value);
      syncUrl();
    });
    $('#tb').addEventListener('change', function (e) {
      if (e.target.id === 'sortSel') { C.sort = e.target.value; paintCatalog(); syncUrl(); }
    });
  }

  /* ==========================================================================
     Ekran: Karta produktu
     ========================================================================== */
  let PD = { p: null, files: [], gal: [] };

  const EXTRA_SCENES = { 'Balans': ['balans-bs-b', 'balans-zoom-bs'] };
  const SCENE_COL = { 'balans-cut': 'w', 'balans-zoom-ws': 'w', 'balans-zoom-bs': 'b', 'najazd-a': '', 'najazd-b': '' };
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
  function galleryFor(p) {
    const s = serieOf(p), pc = prodCol(p), docs = [];
    const ex = (SP.extra && SP.extra[p.ref]) || [];          // zdjęcia dodatkowe z paczki e-commerce (packshoty.js)
    const rys = SP.rys && SP.rys[p.ref];                     // rysunek techniczny tego indeksu (rysunki.js)
    if (rys) {
      const rk = 'rys:' + rys.f;
      SP.img[rk] = SP.img[rk] || { f: 'rys/' + rys.f, w: rys.w, h: rys.h, tb: false };
      docs.push({ k: rk, kind: 'doc', cap: 'Rysunek techniczny · wymiary w mm' });
    } else if (p.fam === 'Balans') {
      docs.push({ k: p.shape === 'prostokątny' ? 'draw-balans-rect' : 'draw-balans-sq', kind: 'doc', cap: 'Rysunek techniczny · wymiary w mm' });
    }
    /* przekrój z paczki e-commerce — bez podpisów (oryginał: „Antibac”, „ochrona przed pleśnią” — twierdzenia biobójcze, EmpCo/BPR) */
    if (p.fam === 'Balans' && /biały/.test(p.c || '')) docs.push({ k: 'balans-przekroj', kind: 'doc', cap: 'Przekrój — budowa warstwowa brodzika · wizualizacja poglądowa' });
    if (p.fam === 'Balans') docs.push({ k: 'info-balans', kind: 'doc', cap: 'Infografika · cechy serii' });
    /* info-frigo / info-ipsilon celowo pominięte: grafiki zawierają „Ponad 45 lat doświadczenia” i goły badge gwarancji — do korekty przed publikacją */
    const exPack = ex.filter(function (x) { return x.kind === 'pack'; }).map(function (x) { return { k: x.k, kind: 'pack', cap: x.cap }; });
    const exPhoto = ex.filter(function (x) { return x.kind !== 'pack'; }).map(function (x) { return { k: x.k, kind: 'scene', cap: x.cap }; });
    const dup = ex.length ? { 'balans-zoom-ws': 1, 'balans-zoom-bs': 1, 'balans-cut': 1 } : {};
    let all = (s.scenes || []).concat(EXTRA_SCENES[p.fam] || []).filter(function (k) { return SP.img[k] && !dup[k]; });
    if (p.fam === 'Obudowa uniwersalna') {               // aranżacja tej wersji (kształt + podcięcie), nie pozostałych
      const ob = (p.shape === 'półokrągły' ? 'pol' : 'pr') + (/LED/.test(p.ver || '') ? '-led' : '');
      all = all.filter(function (k) { return k === { 'pr-led': 'obudowa-led', 'pol-led': 'obudowa-pol', 'pr': 'obudowa-pr', 'pol': 'obudowa-pol-bez' }[ob]; });
    }
    let own = all.filter(function (k) { const sc = sceneCol(k); return sc === '' || sc === pc; });
    own.sort(function (a, b) { return (sceneCol(b) === pc ? 1 : 0) - (sceneCol(a) === pc ? 1 : 0); });
    let cap = 'Wizualizacja poglądowa';
    if (!own.length && all.length) { own = all; cap = 'Wizualizacja poglądowa · inny wariant kolorystyczny'; }
    const scenes = own.slice(0, Math.max(2, 9 - docs.length - ex.length)).map(function (k) { return { k: k, kind: 'scene', cap: cap }; });
    const cad3 = cadFor(p);
    const g3 = glbFor(p) ? [{ k: p.im, kind: '3d', glb: glbFor(p),
      cap: cad3.approx && cad3.from ? 'Model 3D dopasowany do wymiaru produktu (bryła serii ' + cad3.from[0] + ' × ' + cad3.from[1] + ' cm) · przeciągnij, aby obrócić' : 'Model 3D · przeciągnij, aby obrócić' }] : [];
    return [{ k: p.im, kind: 'pack', cap: '' }].concat(g3, exPack, scenes, exPhoto, docs).filter(function (x) { return SP.img[x.k]; });
  }
  function stageInner(item, alt) {
    if (item.kind === '3d') return mvHTML(item.glb, 'Model 3D: ' + alt, PD.p && PD.p.ref) + '<span class="gal-cap">' + esc(item.cap) + '</span>';
    const i = SP.img[item.k];
    return '<img' + (item.kind === 'pack' && !i.tb ? ' class="is-mult"' : '') + ' src="' + esc(SP.src(item.k)) + '" alt="' + esc(alt) + '" width="' + i.w + '" height="' + i.h + '">' +
      (item.cap ? '<span class="gal-cap">' + esc(item.cap) + '</span>' : '');
  }
  function galAlt(item, p) {
    return item.kind === 'pack' ? titleOf(p) + ', ' + variant(p) : (item.kind === 'scene' ? 'Aranżacja z produktem ' + p.s + ' — wizualizacja poglądowa' : item.cap);
  }
  function setStage(idx) {
    const item = PD.gal[idx], st = $('#galStage');
    if (!item || !st) return;
    st.className = 'core gal-stage is-' + item.kind;
    st.innerHTML = stageInner(item, galAlt(item, PD.p));
    $$('.gal-thumb').forEach(function (b, i) { b.classList.toggle('is-on', i === idx); b.setAttribute('aria-pressed', i === idx); });
  }
  function filesSummary() {
    const on = $$('.files-tbl input[data-file]').filter(function (i) { return i.checked; });
    const mb = on.reduce(function (a, i) { return a + (PD.files[+i.getAttribute('data-file')].mb || 0); }, 0);
    const sum = $('#fSum'), all = $('#fAll');
    if (sum) sum.textContent = pliki(on.length) + ' · ' + mbLabel(mb);
    if (all) { all.checked = on.length === PD.files.length; all.indeterminate = on.length > 0 && on.length < PD.files.length; }
    $$('.files-tbl tbody tr').forEach(function (tr) { const inp = $('input[data-file]', tr); tr.classList.toggle('is-off', !inp.checked); });
  }

  /* gwarancja producenta wg karty Stabilsafe v15.25 (kanał DIY); znaki: oryginały z etykiet Sensea i przeglądu oferty Schedpol */
  const GW_TAIL = 'Warunek: montaż zgodnie z instrukcją, przez osobę o odpowiednich kwalifikacjach. Zakres i terytorium — karta gwarancyjna Stabilsafe v15.25. Gwarancja nie ogranicza ustawowych praw kupującego.';
  function gwFor(p) {
    const sensea = p.brand === 'Sensea';
    if (p.tn === 'Stabilsafe') return { badge: sensea ? 'gw-sensea-10' : 'gw-10', lines: ['10 lat — wytrzymałość na nacisk wg PN-EN 14527', '5 lat — stałość barwy'] };
    if (p.tn === 'Standard Plus') return { badge: sensea ? 'gw-sensea-7' : 'gw-7', lines: ['7 lat — stałość barwy'] };
    if (p.fam === 'Nośnik') return { badge: 'gw-31', lines: ['31 lat — trwałość materiału nośnika EPS'] };
    if (p.fam === 'Harmony') return { badge: '', lines: ['5 lat — wg PN-EN 1253-1'] };
    return { badge: '', lines: [] };
  }
  /* ten sam wymiar i kształt, inny kolor — w tej samej serii */
  /* „Harmony” i „Harmony Black” to ta sama seria w dwóch kolorach (nazwa koloru w nazwie serii) */
  function serieBase(s) { return String(s || '').replace(/\s+Black$/i, ''); }
  function colorVariants(p) {
    const k = sizeKey(p);
    if (!k || !p.c) return [];
    return SP.products.filter(function (x) {
      return x.ref !== p.ref && x.fam === p.fam && serieBase(x.s) === serieBase(p.s) && x.c && x.c !== p.c && sizeKey(x) === k && (x.shape || '') === (p.shape || '');
    }).sort(function (a, b) { return a.c.localeCompare(b.c, 'pl'); });
  }
  /* inne produkty o tych samych wymiarach boków (inne serie / kolory), ta sama kategoria */
  function sameSize(p, excl) {
    const k = sizeKey(p); if (!k || p.cat === 'odpływ liniowy') return [];
    const seen = {};
    return SP.products.filter(function (x) {
      return x.ref !== p.ref && !excl[x.ref] && sizeKey(x) === k && x.cat === p.cat && (x.shape || '') === (p.shape || '');   // ten sam wymiar i kształt
    }).sort(function (a, b) {
      return ((a.fam === p.fam ? 1 : 0) - (b.fam === p.fam ? 1 : 0)) || a.s.localeCompare(b.s, 'pl');
    }).filter(function (x) { const kk = x.fam + '|' + x.c + '|' + x.shape; if (seen[kk]) return false; seen[kk] = 1; return true; });
  }
  /* filmy z kanału YouTube Schedpol (assets/filmy.js) przypisane do serii / kategorii */
  function videosFor(p) {
    const own = function (v) { return (v.fams || []).indexOf(p.fam) !== -1 ? 1 : 0; };
    return (SP.videos || []).filter(function (v) {
      if ((v.c && v.c !== p.c) || (v.shape && v.shape !== p.shape)) return false;     // 360°: tylko film tego koloru i kształtu
      return own(v) || (v.cats || []).indexOf(p.cat) !== -1;
    }).sort(function (a, b) { return own(b) - own(a); });
  }
  /* film: YouTube Schedpol albo odtwarzacz Brightcove Leroy Merlin (v.bc = [konto, id filmu]) */
  function videoSrc(v) {
    return v.bc ? 'https://players.brightcove.net/' + v.bc[0] + '/default_default/index.html?videoId=' + v.bc[1] + '&autoplay=true'
      : 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(v.id) + '?autoplay=1&rel=0';
  }
  function ytHTML(v, lazy) {
    const poster = v.poster || ('https://i.ytimg.com/vi/' + v.id + (v.short ? '/oardefault.jpg' : '/hqdefault.jpg'));   // shorts: hqdefault bywa czarnym kadrem
    return '<figure class="yt"><div class="yt-frame">' +
      '<button type="button" class="yt-poster" data-act="yt" data-src="' + esc(videoSrc(v)) + '" aria-label="Odtwórz film: ' + esc(v.t) + '">' +
      '<img src="' + esc(poster) + '" alt="" loading="' + (lazy ? 'lazy' : 'eager') + '"><span class="yt-play">' + ic('play', 26) + '</span>' +
      (v.ai ? '<span class="yt-ai">Treść wygenerowana przez AI</span>' : '') + '</button></div>' +
      '<figcaption><b>' + esc(v.t) + '</b><small>' + esc(v.kind || 'Film') + ' · ' + esc(v.bc ? 'film Leroy Merlin' : 'YouTube Schedpol') + '</small></figcaption></figure>';
  }
  function renderProdukt(params) {
    const p = SP.byRef((params && params.ref) || DEFAULT_REF) || SP.byRef(DEFAULT_REF) || SP.products[0];
    const s = serieOf(p), allFiles = filesFor(p), gal = galleryFor(p);
    const files = allFiles.filter(function (f) { return !f.doc; });
    const docFiles = allFiles.filter(function (f) { return f.doc; });
    PD = { p: p, files: files, docs: docFiles, all: allFiles, gal: gal };
    const stone = p.cat === 'brodzik' && /kamień/.test(p.c || '');
    const tech = p.tn ? p.tn + (p.tn === 'Stabilsafe' ? '®' : '') + (p.tech ? ' · ' + p.tech : '') : (p.tech || '');
    const attrs = [
      ['Marka', esc(p.brand)],
      ['Seria', '<a class="link" style="font-size:inherit;color:inherit" href="' + H('katalog', { seria: p.fam }) + '">' + esc(p.s) + ' ' + ic('arrow-right', 13) + '</a>'],
      p.shape ? ['Kształt', esc(cap(p.shape))] : null,
      SP.dims(p) ? ['Wymiar', '<span class="mono">' + esc(dimsTxt(p)) + '</span>' + (p.fam === 'Obudowa uniwersalna' ? ' <small>' + (p.shape === 'półokrągły' ? 'rozwinięcie panelu × wysokość' : 'front + bok × wysokość') + '</small>' : '')] : null,
      p.ver ? ['Wersja', esc(cap(p.ver)) + ' <small>' + (/LED/.test(p.ver) ? 'wnęka przy posadzce — miejsce na stopy i taśmę LED' : 'panele do samej posadzki, bez wnęki') + '</small>'] : null,
      p.c ? ['Kolor', dot(p.hx, 'lg') + esc(cap(p.c)) + (p.ce || p.ral ? ' <small>' + esc([p.ce, p.ral].filter(Boolean).join(' · ')) + '</small>' : '')] : null,
      tech ? ['Technologia', esc(tech)] : null,
      ['Gama LM', p.g ? '<span class="mono">' + esc(p.g) + '</span>' : '<small>brak w eksporcie LM</small>'],
      p.ean ? ['EAN', '<span class="mono">' + esc(p.ean) + '</span>'] : null,
      stone ? ['Antypoślizgowość', 'klasa A — DIN EN 16165:2023 (załącznik A)'] : null
    ].filter(Boolean);
    const sibs = SP.products.filter(function (x) { return x.fam === p.fam && x.s === p.s && x.c === p.c && x.ref !== p.ref; })
      .sort(function (a, b) { return area(a) - area(b); });
    const zest = zestawFor(p), gw = gwFor(p), cvar = colorVariants(p), vids = videosFor(p);
    const vvar = p.ver ? SP.products.filter(function (x) { return x.ref !== p.ref && x.fam === p.fam && x.shape === p.shape && x.ver && x.ver !== p.ver; }) : [];
    const same = sameSize(p, cvar.reduce(function (a, x) { a[x.ref] = 1; return a; }, {})).slice(0, 12);
    const pdBits = [];
    if (SP.dims(p)) pdBits.push('<span class="mono">' + esc(variant(p)) + '</span>');
    if (p.c) pdBits.push('<span>' + dot(p.hx, 'lg') + esc(p.c) + '</span>');
    if (!pdBits.length && p.shape) pdBits.push('<span>' + esc(p.shape) + '</span>');
    const pdVar = pdBits.join('<i class="sep" aria-hidden="true"></i>');
    const mbAll = files.reduce(function (a, f) { return a + (f.mb || 0); }, 0);

    app.innerHTML = `
    <div class="wrap pd">
      <nav class="crumbs" aria-label="Okruszki">
        <a href="${H('katalog')}">Katalog</a>${ic('chevron-right', 14)}
        <a href="${H('katalog', { cat: p.cat })}">${esc(SP.catLabel(p.cat))}</a>${ic('chevron-right', 14)}
        <a href="${H('katalog', { seria: p.fam })}">${esc(p.fam)}</a>${ic('chevron-right', 14)}
        <span class="mono" aria-current="page">LM ${esc(p.ref)}</span>
      </nav>

      <div class="pd-top">
        <section class="gal" aria-label="Galeria produktu">
          <div class="bezel gal-bezel"><div class="core gal-stage is-pack" id="galStage">${stageInner(gal[0], galAlt(gal[0], p))}</div>
            <div class="gal-marks">
              ${gw.badge ? '<a class="gal-gw" href="#gT" title="Gwarancja producenta — zakres niżej"><img src="' + UP + 'assets/znaki/' + gw.badge + '.png" alt="Znak gwarancji producenta: ' + esc(gw.lines[0] ? gw.lines[0].split(' — ')[0] : '') + '"></a>' : ''}
              ${BRAND_LOGO[p.brand] ? '<span class="gal-brand gal-brand-' + esc(p.brand.toLowerCase()) + '"><img src="' + BRAND_LOGO[p.brand] + '" alt="Marka ' + esc(p.brand) + '"></span>' : ''}
              ${gamaFlag(p, 'gal-gama')}
            </div></div>
          ${gal.length > 1 ? '<div class="gal-thumbs">' + gal.map(function (g, i) {
            return '<button type="button" class="gal-thumb is-' + g.kind + (i === 0 ? ' is-on' : '') + '" data-act="gal" data-idx="' + i + '" aria-pressed="' + (i === 0) + '" aria-label="' +
              esc(g.kind === 'pack' ? 'Packshot' : g.cap) + ' ' + (i + 1) + ' z ' + gal.length + '"><img' + (g.kind === 'pack' && !SP.img[g.k].tb ? ' class="is-mult"' : '') + ' src="' + esc(SP.src(g.k)) + '" alt=""></button>';
          }).join('') + '</div>' : ''}
          <div class="pd-order" aria-labelledby="ordT">
            <h2 id="ordT">Nie ma tego produktu na stanie? Zamów!</h2>
            <p class="pd-order-sub">${ic('clock', 14)} Biuro Obsługi Klienta Schedpol · ${esc(SP.contacts.hours)}</p>
            <div class="pd-order-l">${SP.contacts.bok.map(function (b, i) {
              return `<div class="sb bok">
                ${bokMapSVG(String(i + 1))}
                <div class="bok-txt"><b>${esc(b.n)}</b>
                <small>${esc(BOK_AREA[String(i + 1)] || '')}</small>
                <a class="mono" href="tel:+48${esc(b.tel.replace(/\s/g, ''))}">${ic('phone', 15)} ${esc(b.tel)}</a>
                <a href="mailto:${esc(b.mail)}">${ic('mail', 15)} ${esc(b.mail)}</a></div></div>`;
            }).join('')}</div>
            <dl class="pd-order-terms">
              <div><dt>Dropshipping od 1 produktu · realizacja do 4 dni</dt><dd><b>${esc(COOP[2].v)}</b> ${esc(COOP[2].u)}</dd></div>
            </dl>
          </div>
        </section>

        <section class="pd-info" aria-labelledby="pdT">
          <p class="kicker">${esc(SP.catLabel(p.cat))} · ${esc(p.brand)}${p.new ? ' · <span style="color:var(--brand)">Nowość 2026</span>' : ''}</p>
          <h1 class="pd-title" id="pdT">${esc(titleOf(p))}</h1>
          ${pdVar ? '<p class="pd-var">' + pdVar + '</p>' : ''}
          <div class="pd-ref">${refChip(p, true)}<span>Numer referencyjny Leroy Merlin</span></div>
          ${cvar.length ? '<div class="pd-colors"><div class="pd-colors-h">' + ic('drop', 16) + '<b>Dostępne kolory w tym wymiarze</b><span>' + (cvar.length + 1) + ' ' + plural(cvar.length + 1, 'wariant', 'warianty', 'wariantów') + '</span></div><div class="pd-colors-l">' + [p].concat(cvar).map(function (x) {
            const on = x.ref === p.ref;
            return '<a class="cvar' + (on ? ' is-on' : '') + '" href="' + H('produkt', { ref: x.ref }) + '"' + (on ? ' aria-current="true"' : '') + ' title="' + esc(cap(x.c)) + ' · LM ' + esc(x.ref) + '"><span class="cvar-img">' + pimg(x.im, '') + '</span><span class="cvar-n">' + dot(x.hx) + esc(cap(x.c)) + '</span><small class="mono">LM ' + esc(x.ref) + '</small>' + (on ? '<span class="cvar-tag">Oglądasz</span>' : '') + '</a>';
          }).join('') + '</div></div>' : ''}
          <div class="pd-act">
          <div class="pd-cta">
            <button class="btn btn-primary" type="button" data-act="add-product-sel">Dodaj do Plików <span class="btn-ic">${ic('arrow-right', 16)}</span></button>
            <a class="btn btn-primary btn-karta" href="${esc(kartaPdf(p))}" download>${ic('file', 16)} Karta produktu PDF</a>
          </div>
          <p class="pd-karta"><a class="link" href="${esc(kartaView(p))}" target="_blank" rel="noopener">${ic('eye', 15)} Podgląd karty A4 przed pobraniem</a></p>
          <p class="pd-note">${ic('info', 16)} Cena i dostępność: w systemie sklepu Leroy Merlin.</p>
          </div>
          ${pdSizes(p)}
          ${vvar.length ? '<div class="pd-colors"><div class="pd-colors-h">' + ic('layers', 16) + '<b>Dostępne wersje</b><span>' + (vvar.length + 1) + ' ' + plural(vvar.length + 1, 'wersja', 'wersje', 'wersji') + '</span></div><div class="pd-colors-l">' + [p].concat(vvar).map(function (x) {
            const on = x.ref === p.ref;
            return '<a class="cvar' + (on ? ' is-on' : '') + '" href="' + H('produkt', { ref: x.ref }) + '"' + (on ? ' aria-current="true"' : '') + ' title="' + esc(cap(x.ver)) + ' · LM ' + esc(x.ref) + '"><span class="cvar-img">' + pimg(x.im, '') + '</span><span class="cvar-n">' + esc(cap(x.ver)) + '</span><small class="mono">LM ' + esc(x.ref) + '</small>' + (on ? '<span class="cvar-tag">Oglądasz</span>' : '') + '</a>';
          }).join('') + '</div></div>' : ''}
          <dl class="attrs">${attrs.map(function (a) { return '<div><dt>' + a[0] + '</dt><dd>' + a[1] + '</dd></div>'; }).join('')}</dl>
        </section>
      </div>


      <div class="pd-two">
        <section class="panel" aria-labelledby="cT">
          <div class="panel-h"><h2 id="cT">Cechy serii ${esc(p.fam)}</h2><span class="kicker">${esc(s.type.split(' · ')[0])}</span></div>
          ${s.feats && s.feats.length ? '<ol class="feats">' + s.feats.map(function (f, i) { return '<li><span>0' + (i + 1) + '</span>' + esc(f) + '</li>'; }).join('') + '</ol>' : '<p class="feats-lead">' + esc(s.lead) + '</p>'}
        </section>
        <section class="panel gw" aria-labelledby="gT"${gw.lines.length || docsFor(p).length ? '' : ' hidden'}>
          <h2 class="gw-h" id="gT">${ic('shield', 20)} ${gw.lines.length ? 'Gwarancja' : 'Dokumenty'}</h2>
          ${gw.lines.length ? '<ul class="gw-lines">' + gw.lines.map(function (l) { return '<li>' + esc(l) + '</li>'; }).join('') + '</ul><p>' + esc(GW_TAIL) + '</p>' : ''}
          ${docsFor(p).map(function (d) {
            return '<a class="link" href="' + esc(DOC_BASE + d.f) + '" target="_blank" rel="noopener">' + ic('file', 15) + ' ' + esc(d.t) + ' <small>(PDF, ' + esc(nf(d.mb, 1)) + ' MB)</small></a>';
          }).join('')}
        </section>
      </div>

      <section class="pd-sec pf" aria-labelledby="fT">
        <div class="pf-h">
          <div><span class="home-k">${ic('folder', 14)} Centrum plików cyfrowych</span>
            <h2 id="fT">Materiały do pobrania dla architekta i projektanta</h2>
            <p>Komplet plików do projektu: ${esc(titleOf(p))}${SP.dims(p) ? ', ' + esc(variant(p)) : ''}. Każdy plik można obejrzeć przed pobraniem.</p></div>
          <button class="btn pf-zip" type="button" data-act="add-product-sel">${ic('download', 16)} Pobierz całą paczkę (.ZIP · ${mbLabel(allFiles.reduce(function (a, f) { return a + (f.mb || 0); }, 0))})</button>
        </div>
        <div class="pf-cols">${pfCols(p, allFiles)}</div>
      </section>




      ${zest.length ? `<section class="pd-sec" aria-labelledby="zT">
        <div class="sec-h"><div><h2 id="zT">Produkty możliwe do dobrania</h2><p>Produkty z oferty w Leroy Merlin, które można dobrać do tej serii w projekcie.</p></div></div>
        <div class="zestaw">${zest.map(function (z) {
          const zs = SP.serie(z.fam);
          const zp = z.q ? SP.products.filter(function (x) { return x.fam === z.fam && norm(x.s).indexOf(norm(z.q)) !== -1; })[0] : null;
          return `<a class="zcard" href="${H('katalog', z.q ? { seria: z.fam, q: z.q } : { seria: z.fam })}">
            <span class="zcard-thumb">${pimg(zp ? zp.im : zs.pack, '')}</span>
            <span class="zcard-main"><span class="kicker">${esc(z.why)}</span><b>${esc(zp ? zp.s : zs.fam)}</b><p>${esc(zs.lead)}</p><span class="mono">${indeksy(zs.n)}</span></span>
          </a>`;
        }).join('')}</div>
      </section>` : ''}

      ${same.length ? `<section class="pd-sec" aria-labelledby="ssT">
        <div class="sec-h"><div><h2 id="ssT">Inne produkty w tym rozmiarze</h2><p><span class="mono">${esc(sizeKey(p))}</span> ${p.shape ? ' · ' + esc(p.shape) : ''} — inne serie i kolory o tych samych wymiarach boków i kształcie.</p></div>
          <a class="link" href="${H('katalog', p.shape ? { cat: p.cat, ksztalt: p.shape, rozmiar: sizeKey(p) } : { cat: p.cat, rozmiar: sizeKey(p) })}">Wszystkie w katalogu ${ic('arrow-right', 14)}</a></div>
        <div class="grid same-grid">${same.map(function (x, i) { return cardHTML(x, i); }).join('')}</div>
      </section>` : ''}

      ${vids.length ? `<section class="pd-sec" aria-labelledby="vT">
        <div class="sec-h"><div><h2 id="vT">Filmy</h2><p>Montaż i prezentacja produktu.</p></div>
          <a class="link" href="${H('akademia')}">Wszystkie w Akademii ${ic('arrow-right', 14)}</a></div>
        <div class="yt-grid">${vids.slice(0, 6).map(function (v) { return ytHTML(v, true); }).join('')}</div>
      </section>` : ''}
    </div>`;

    const tbl = $('.files-tbl');
    if (tbl) {
      tbl.addEventListener('change', function (e) { if (e.target.matches('input[data-file]')) filesSummary(); });
      $('#fAll').addEventListener('change', function (e) {
        $$('.files-tbl input[data-file]').forEach(function (i) { i.checked = e.target.checked; });
        filesSummary();
      });
    }
  }

  /* ==========================================================================
     Ekran: Centrum plików
     ========================================================================== */
  const P = { tab: 'all' };
  const TABS = [{ k: 'all', l: 'Wszystkie' }].concat(FTYP.map(function (t) { return { k: t.k, l: t.k === 'dokument' ? 'Instrukcje i karty gw.' : t.l }; }));

  /* biblioteka dokumentów: wszystkie instrukcje montażu i karty gwarancyjne z materiałów (assets/dokumenty.js) */
  function docsLibraryHTML() {
    const D = SP.docs || {};
    const keys = Object.keys(D).sort(function (a, b) {
      const x = D[a], y = D[b];
      return (y.lm - x.lm) || ((x.typ === 'gw' ? 0 : 1) - (y.typ === 'gw' ? 0 : 1)) || x.t.localeCompare(y.t, 'pl');
    });
    const mbAll = keys.reduce(function (a, k) { return a + D[k].mb; }, 0);
    return `<div class="tbl-wrap"><table class="tbl docs-tbl">
      <thead><tr><th>Dokument</th><th>Dotyczy</th><th style="text-align:right">Rozmiar</th><th><span class="sr">Pobierz</span></th></tr></thead>
      <tbody>${keys.map(function (k) {
        const d = D[k], href = DOC_BASE + d.f;
        const fams = d.lm ? (d.fams.length > 6 && d.typ === 'gw' ? 'Wszystkie indeksy w ofercie LM' : d.fams.join(', ')) : 'Nie dotyczy indeksów LM';
        return `<tr${d.lm ? '' : ' class="is-off"'}>
          <td><div class="f-file">${extBadge('PDF')}<div><b>${esc(d.t)}</b><small>${esc(d.f)} · ${d.str} ${plural(d.str, 'strona', 'strony', 'stron')}</small></div></div></td>
          <td>${d.typ === 'gw' ? '<span class="st st-ok">' + ic('shield', 12, 1.8) + ' Karta gwarancyjna</span> ' : ''}<small class="docs-fams">${esc(fams)}</small></td>
          <td class="num">${nf(d.mb, 1)} MB</td>
          <td><div class="t-act">
            <button class="icon-btn" type="button" data-act="preview-url" data-src="${esc(href)}" data-name="${esc(d.f)}" data-desc="${esc(d.t)}" aria-label="Podgląd: ${esc(d.t)}" title="Podgląd przed pobraniem">${ic('eye', 16)}</button>
            <a class="icon-btn" href="${esc(href)}" download aria-label="Pobierz: ${esc(d.t)}" title="Pobierz PDF">${ic('download', 16)}</a>
          </div></td>
        </tr>`;
      }).join('')}</tbody>
      <tfoot><tr><td colspan="2"><b>${keys.length} ${plural(keys.length, 'dokument', 'dokumenty', 'dokumentów')}</b> · instrukcje montażu przypisane do serii, karta gwarancyjna Stabilsafe v15.25 do wszystkich indeksów LM</td><td class="num"><b>${nf(mbAll, 1)} MB</b></td><td></td></tr></tfoot>
    </table></div>`;
  }

  function famStats(fam) {
    const st = { n: 0, mb: 0 };
    seriesFiles(fam).forEach(function (f) {
      const t = st[f.typ] || (st[f.typ] = { n: 0, mb: 0 });
      t.n++; t.mb += f.mb || 0; st.n++; st.mb += f.mb || 0;
    });
    return st;
  }
  function plikiTableHTML() {
    const tab = P.tab, all = tab === 'all';
    if (tab === 'dokument') return docsLibraryHTML();
    const fams = SP.series.map(function (s) { return { s: s, st: famStats(s.fam) }; })
      .filter(function (x) { return all ? x.st.n : x.st[tab]; });
    const seriaCell = function (s) {
      return '<a class="t-prod" href="' + H('katalog', { seria: s.fam }) + '"><span class="t-thumb">' + pimg(s.pack, '') + '</span><span><b>' + esc(s.fam) + '</b><small>' + esc(s.type.split(' · ')[0]) + ' · ' + indeksy(s.n) + '</small></span></a>';
    };
    const num = function (v) { return '<td class="num">' + (v ? '<b>' + v + '</b>' : '<span class="zero">—</span>') + '</td>'; };
    const acts = function (id, fam, lab) {
      const inT = inTeczka(id);
      return '<td><div class="t-act">' +
        '<button class="icon-btn" type="button" data-act="zip-pkg" data-id="' + esc(id) + '" title="Pobierz ZIP: ' + esc(lab) + '" aria-label="Pobierz ZIP: ' + esc(lab) + '">' + ic('download', 16) + '</button>' +
        (inT ? '<span class="icon-btn is-done" title="W Plikach" aria-label="' + esc(lab) + ' jest w Plikach">' + ic('check', 16, 2) + '</span>'
             : '<button class="icon-btn is-add" type="button" data-act="' + (id.charAt(0) === 's' ? 'add-series' : 'add-type') + '" data-fam="' + esc(fam) + '"' + (id.charAt(0) === 't' ? ' data-type="' + esc(tab) + '"' : '') + ' title="Dodaj do Plików" aria-label="Dodaj do Plików: ' + esc(lab) + '">' + ic('plus', 16, 1.8) + '</button>') +
        '</div></td>';
    };
    /* 25.11: zamiast 9 kolumn — jedna kolumna „Zawartość” (liczby wg typu zawijają się), przyciski zawsze widoczne */
    const ABBR = { karta: ['karta', 'karty', 'kart'], model: ['model 3D', 'modele 3D', 'modeli 3D'], rysunek: ['rysunek', 'rysunki', 'rysunków'],
      packshot: ['packshot', 'packshoty', 'packshotów'], aranzacja: ['aranżacja', 'aranżacje', 'aranżacji'], grafika: ['grafika', 'grafiki', 'grafik'],
      dokument: ['dokument', 'dokumenty', 'dokumentów'] };
    if (all) {
      const tot = { n: 0, mb: 0 };
      const body = fams.map(function (x) {
        const st = x.st;
        tot.n += st.n; tot.mb += st.mb;
        const mix = FTYP.filter(function (t) { return st[t.k]; }).map(function (t) {
          const n = st[t.k].n; return '<span class="fl-chip"><b>' + n + '</b> ' + plural(n, ABBR[t.k][0], ABBR[t.k][1], ABBR[t.k][2]) + '</span>';
        }).join('');
        return '<tr><td>' + seriaCell(x.s) + '</td><td class="fl-mix">' + mix + '</td><td class="num fl-mb"><b>' + pliki(st.n) + '</b><small>' + mbLabel(st.mb) + '</small></td>' + acts('s:' + x.s.fam, x.s.fam, 'seria ' + x.s.fam) + '</tr>';
      }).join('');
      return '<div class="tbl-wrap"><table class="tbl fl-tbl fl-all"><thead><tr><th>Seria</th><th>Zawartość paczki</th><th style="text-align:right">Razem</th><th><span class="sr">Akcja</span></th></tr></thead><tbody>' + body +
        '<tr class="fl-sum"><td><b>Razem · ' + fams.length + ' ' + plural(fams.length, 'seria', 'serie', 'serii') + '</b></td><td></td><td class="num fl-mb"><b>' + pliki(tot.n) + '</b><small>' + mbLabel(tot.mb) + '</small></td><td></td></tr></tbody></table></div>';
    }
    const T = typOf(tab);
    let tn = 0, tmb = 0;
    const body = fams.map(function (x) {
      const st = x.st[tab];
      tn += st.n; tmb += st.mb;
      return '<tr><td>' + seriaCell(x.s) + '</td>' + num(st.n) + '<td class="num">' + mbLabel(st.mb) + '</td>' +
        acts('t:' + x.s.fam + ':' + tab, x.s.fam, x.s.fam + ' — ' + T.l.toLowerCase()) + '</tr>';
    }).join('');
    return '<div class="tbl-wrap"><table class="tbl fl-tbl"><thead><tr><th>Seria</th><th style="text-align:right">' + esc(T.l) + '</th><th style="text-align:right">Rozmiar</th><th><span class="sr">Akcja</span></th></tr></thead><tbody>' +
      body + '<tr><td><b>Razem · ' + fams.length + ' ' + plural(fams.length, 'seria', 'serie', 'serii') + '</b></td>' + num(tn) + '<td class="num"><b>' + mbLabel(tmb) + '</b></td><td></td></tr></tbody></table></div>';
  }
  function allStats() {
    const seen = {}, st = { n: 0, mb: 0 };
    SP.series.forEach(function (s) {
      seriesFiles(s.fam).forEach(function (f) {
        const u = f.href.split('?')[0];
        if (seen[u]) return;
        seen[u] = 1;
        const t = st[f.typ] || (st[f.typ] = { n: 0, mb: 0 });
        t.n++; st.n++; t.mb += f.mb || 0; st.mb += f.mb || 0;
      });
    });
    return st;
  }
  function tabsHTML() {
    const st = allStats();
    return TABS.map(function (t) {
      const n = t.k === 'dokument' ? Object.keys(SP.docs || {}).length : t.k === 'all' ? st.n : (st[t.k] ? st[t.k].n : 0);
      return '<button class="tab' + (P.tab === t.k ? ' is-on' : '') + '" type="button" role="tab" aria-selected="' + (P.tab === t.k) + '" data-act="ftab" data-tab="' + esc(t.k) + '">' + esc(t.l) + '<small>' + n.toLocaleString('pl-PL') + '</small></button>';
    }).join('');
  }
  function paintPlikiTable() {
    const box = $('#flTable'), tabs = $('#flTabs');
    if (!box || !tabs) return;
    tabs.innerHTML = tabsHTML();
    box.innerHTML = plikiTableHTML();
  }
  /* ==========================================================================
     Ekran: Akademia — filmy szkoleniowe (YouTube Schedpol), prezentacje, katalog
     ========================================================================== */
  function renderAkademia(params) {
    const V = SP.videos || [], G = (SP.videoGroups || []).filter(function (g) { return V.some(function (v) { return v.g === g.k; }); });
    const grp = G.some(function (g) { return g.k === (params && params.g); }) ? params.g : 'all';
    const docs = SP.academyDocs || [];
    const shown = V.filter(function (v) { return grp === 'all' || v.g === grp; });
    app.innerHTML = `
    <div class="wrap ak">
      <header class="page-head">
        <div>
          <span class="eyebrow">Akademia</span>
          <h1 class="page-title" style="margin-top:18px">Filmy, prezentacje i katalog</h1>
          <p class="page-sub">Materiały szkoleniowe Schedpol dla projektantów i zespołów Leroy Merlin: ${V.length} ${plural(V.length, 'film', 'filmy', 'filmów')} z kanału YouTube Schedpol, prezentacje i katalog produktów.</p>
        </div>
        <a class="btn" href="${esc(SP.ytChannel || 'https://www.youtube.com/@schedpol')}" target="_blank" rel="noopener">${ic('play', 16)} Kanał YouTube Schedpol ${ic('external', 14)}</a>
      </header>

      <section class="ak-docs" aria-labelledby="akDocT">
        <h2 class="sr" id="akDocT">Katalog i prezentacje</h2>
        ${docs.map(function (d) {
          return `<article class="ak-doc${d.ok ? '' : ' is-soon'}">
            <span class="ak-doc-ic">${ic('book', 26)}</span>
            <div class="ak-doc-t"><span class="home-k">${esc(d.kind || 'Katalog PDF')}</span><h3>${esc(d.t)}</h3><p>${esc(d.d)}</p>${d.ok ? '' : '<p class="ak-soon">' + ic('clock', 14) + ' ' + esc(d.note) + '</p>'}</div>
            <div class="ak-doc-a">${d.ok
              ? '<button class="btn" type="button" data-act="preview-url" data-src="' + UP + 'assets/akademia/' + esc(d.f) + '" data-name="' + esc(d.f) + '" data-desc="' + esc(d.t) + '">' + ic('eye', 16) + ' Podgląd</button><a class="btn btn-primary" href="' + UP + 'assets/akademia/' + esc(d.f) + '" download>' + ic('download', 16) + ' Pobierz PDF</a>'
              : '<button class="btn" type="button" disabled>' + ic('download', 16) + ' Wkrótce</button>'}</div>
          </article>`;
        }).join('')}
      </section>

      <section class="pd-sec ak-vids" aria-labelledby="akVT">
        <div class="sec-h"><div><h2 id="akVT">Filmy szkoleniowe i montażowe</h2><p>Kliknij miniaturę, żeby odtworzyć film na stronie.</p></div></div>
        <div class="tabs ak-tabs" role="tablist" aria-label="Temat filmów">
          <a class="tab${grp === 'all' ? ' is-on' : ''}" href="${H('akademia', { keep: 1 })}" role="tab" aria-selected="${grp === 'all'}">Wszystkie<small>${V.length}</small></a>
          ${G.map(function (g) {
            const n = V.filter(function (v) { return v.g === g.k; }).length;
            return '<a class="tab' + (grp === g.k ? ' is-on' : '') + '" href="' + H('akademia', { g: g.k, keep: 1 }) + '" role="tab" aria-selected="' + (grp === g.k) + '">' + esc(g.l) + '<small>' + n + '</small></a>';
          }).join('')}
        </div>
        ${G.filter(function (g) { return grp === 'all' || g.k === grp; }).map(function (g) {
          const vs = shown.filter(function (v) { return v.g === g.k; });
          return `<div class="ak-grp"><h3>${esc(g.l)}</h3><div class="yt-grid${g.k === '360' ? ' is-short' : ''}">${vs.map(function (v) { return ytHTML(v, true); }).join('')}</div></div>`;
        }).join('')}
        <p class="hcats-note">Filmy są osadzone z serwisu YouTube (tryb bez plików cookie do chwili odtworzenia) oraz z odtwarzacza Leroy Merlin.</p>
      </section>
    </div>`;
  }

  function renderPliki(params) {
    if (params && params.lista) {                              // link z „Kopiuj link”: odtwórz listę i usuń parametr z adresu
      tzImport(params.lista);
      try { history.replaceState(null, '', SPProto.href('pliki', {})); } catch (e) { /* bez historii */ }
    }
    const typ = params && params.typ === 'dokumenty' ? 'dokument' : params && params.typ;      // stare linki ?typ=dokumenty
    P.tab = TABS.some(function (t) { return t.k === typ; }) ? typ : 'all';
    const st = allStats(), nFiles = st.n, mb = st.mb;
    const nSer = SP.series.filter(function (s) { return famStats(s.fam).n; }).length;
    app.innerHTML = `
    <div class="wrap">
      <header class="page-head">
        <div>
          <span class="eyebrow">Centrum plików</span>
          <h1 class="page-title" style="margin-top:18px">Paczki plików dla całych serii</h1>
          <p class="page-sub">${nFiles.toLocaleString('pl-PL')} ${plural(nFiles, 'plik', 'pliki', 'plików')} · ${mbLabel(mb)} · ${nSer} ${plural(nSer, 'seria', 'serie', 'serii')} produktów. Paczkę ZIP serii pobierzesz od razu (strzałka) albo dodasz do Plików i pobierzesz razem z innymi.</p>
        </div>
        <a class="btn" href="${CAD_URL}" target="_blank" rel="noopener">${ic('cube', 16)} Baza CAD Decor · ${CAD.date}</a>
      </header>
      <div class="fl-layout">
        <section aria-label="Paczki serii">
          <div class="tabs" id="flTabs" role="tablist" aria-label="Typ plików"></div>
          <div id="flTable"></div>
          <div class="notes">
            <div class="note"><h3>${ic('shield', 18)} Statusy plików</h3><p>Publikujemy wyłącznie pliki po weryfikacji treści. Paczki ZIP powstają z aktualnych plików w chwili pobrania.</p>
              <div class="sts"><span class="st st-ok">${ic('check', 12, 2)} Zweryfikowano ${VERIFIED}</span><span class="st st-cad">${ic('cube', 12, 1.8)} Baza ${CAD.date}</span></div></div>
            <div class="note"><h3>${ic('layers', 18)} Wersje</h3><p>Po aktualizacji pliku poprzednia wersja znika z biblioteki. Paczki ZIP i linki z Plików zawierają aktualne wersje plików.</p></div>
            <div class="note"><h3>${ic('file', 18)} Nazwy plików</h3><p>Jeden schemat nazw dla wszystkich materiałów:</p><p><code>Schedpol_&lt;Seria&gt;_&lt;wymiar&gt;_&lt;typ&gt;.&lt;ext&gt;</code></p></div>
          </div>
        </section>
        <aside class="bezel fl-side" id="tzInline" aria-label="Pliki do pobrania">
          <div class="core">
            <div class="panel-h" style="margin-bottom:0"><h2>Pliki</h2><span class="kicker">ZIP</span></div>
            <p class="mono" id="tzInSum" style="margin-top:2px;font-size:12.5px;color:var(--ink-2)"></p>
            <div class="tz-list" id="tzInList"></div>
            <div class="drawer-foot" id="tzInFoot" style="padding:16px 0 0;margin-top:12px"></div>
          </div>
        </aside>
      </div>
    </div>`;
    tzPaint();
  }

  /* ==========================================================================
     Nakładki, nawigacja, zdarzenia globalne
     ========================================================================== */
  let lastFocus = null, cmdSearch = null, firstRender = true, current = '';

  function scrim(on) { $('#scrim').classList.toggle('is-on', !!on); }
  function openTeczka() {
    closeAll();
    lastFocus = document.activeElement;
    const d = $('#teczka');
    d.classList.add('is-open'); d.setAttribute('aria-hidden', 'false'); scrim(true);
    setTimeout(function () { const b = $('.icon-btn', d); if (b) b.focus(); }, 80);
  }
  function openFacets() {
    closeAll();
    lastFocus = document.activeElement;
    const f = $('#facets');
    if (!f) return;
    f.classList.add('is-open'); scrim(true);
  }
  function openSearch() {
    closeAll();
    lastFocus = document.activeElement;
    const c = $('#cmd'), inp = $('#cmdInput');
    c.hidden = false; inp.value = '';
    cmdSearch.paint();
    setTimeout(function () { inp.focus(); }, 30);
  }
  function closeMenu() {
    $('#navLinks').classList.remove('is-open');
    const b = $('.nav-burger');
    b.classList.remove('is-open'); b.setAttribute('aria-expanded', 'false');
  }
  function closeAll(restore) {
    const d = $('#teczka'), f = $('#facets'), c = $('#cmd');
    const wasOpen = d.classList.contains('is-open') || (f && f.classList.contains('is-open')) || !c.hidden;
    d.classList.remove('is-open'); d.setAttribute('aria-hidden', 'true');
    if (f) f.classList.remove('is-open');
    c.hidden = true;
    closeMenu(); scrim(false);
    if (restore && wasOpen && lastFocus && document.contains(lastFocus)) lastFocus.focus({ preventScroll: true });
  }
  function setNav(screen, params) {
    let key = screen === 'produkt' ? 'katalog' : screen;
    if (screen === 'start' && params && params.sek) key = params.sek;
    $$('#navLinks a').forEach(function (a) {
      const on = a.getAttribute('data-nav') === key;
      a.classList.toggle('is-on', on);
      if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
  }
  let io = null;
  function observeReveals() {
    const els = $$('.rv:not(.in)');
    if (!('IntersectionObserver' in window)) { els.forEach(function (el) { el.classList.add('in'); }); return; }
    if (!io) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
      }, { rootMargin: '0px 0px -6% 0px', threshold: 0.04 });
    }
    els.forEach(function (el) { io.observe(el); });
    // Zabezpieczenie dla podglądów i wydruku: po chwili odsłoń wszystko, czego obserwator nie złapał.
    setTimeout(function () { $$('.rv:not(.in)').forEach(function (el) { el.classList.add('in'); }); }, 3200);
  }

  function render(route) {
    const screen = ['start', 'katalog', 'produkt', 'pliki', 'akademia'].indexOf(route.screen) !== -1 ? route.screen : 'start';
    const params = route.params || {};
    closeAll();
    if (screen === 'start' && current === 'start' && params.sek && $('#sek-' + params.sek)) {
      scrollToSek(params.sek);                       // ta sama strona — tylko przewiń do sekcji
    } else if (screen === 'katalog') renderKatalog(params);
    else if (screen === 'produkt') renderProdukt(params);
    else if (screen === 'pliki') renderPliki(params);
    else if (screen === 'akademia') renderAkademia(params);
    else renderStart(params);
    current = screen;
    app.setAttribute('data-screen', screen);
    setNav(screen, params);
    tzPaint();
    observeReveals();
    document.title = ({ start: 'Start', katalog: 'Katalog', produkt: 'Karta produktu', pliki: 'Centrum plików', akademia: 'Akademia' })[screen] + ' — Strefa projektanta Schedpol';
    if (!firstRender) app.focus({ preventScroll: true });
    firstRender = false;
  }

  document.addEventListener('click', function (e) {
    const sg = e.target.closest('.sg-item');
    if (sg) { closeAll(); return; }
    const navA = e.target.closest('#navLinks a, .foot-links a');
    if (navA) {
      closeMenu();
      const m = /[?&]sek=(\w+)/.exec(navA.getAttribute('href') || '');
      if (m && current === 'start' && $('#sek-' + m[1])) { e.preventDefault(); scrollToSek(m[1]); setNav('start', { sek: m[1] }); }
      return;
    }
    const t = e.target.closest('[data-act]');
    if (!t) {
      const tr = e.target.closest('tr[data-href]');
      if (tr && !e.target.closest('a, button, input, label')) location.hash = tr.getAttribute('data-href');
      return;
    }
    const act = t.getAttribute('data-act');
    if (act === 'open-search') openSearch();
    else if (act === 'open-teczka') openTeczka();
    else if (act === 'cmd-go') cmdSearch.submit();
    else if (act === 'open-facets') openFacets();
    else if (act === 'close-all') closeAll(true);
    else if (act === 'toggle-menu') {
      const open = !$('#navLinks').classList.contains('is-open');
      $('#navLinks').classList.toggle('is-open', open);
      t.classList.toggle('is-open', open); t.setAttribute('aria-expanded', String(open));
    }
    else if (act === 'hint') {
      const inp = $('#bigSearch');
      if (inp) { inp.value = t.getAttribute('data-q'); inp.focus(); if (bigSearch) bigSearch.paint(); $('#bigBox').classList.add('is-open'); }
    }
    else if (act === 'big-submit') { if (bigSearch) bigSearch.submit(); }
    else if (act === 'copy-ref') copyRef(t.getAttribute('data-ref'), t);
    else if (act === 'add-product') addProduct(t.getAttribute('data-ref'));
    else if (act === 'add-product-sel') {
      if (!PD.p) return;
      const cb = $$('.files-tbl input[data-file]');            // bez tabeli z zaznaczaniem: cała paczka
      const sel = cb.length ? cb.filter(function (i) { return i.checked; }).map(function (i) { return PD.files[+i.getAttribute('data-file')]; }) : PD.files.slice();
      addProduct(PD.p.ref, sel.concat(PD.docs || []));
    }
    else if (act === 'add-series') addSeries(t.getAttribute('data-fam'));
    else if (act === 'add-type') addType(t.getAttribute('data-fam'), t.getAttribute('data-type'));
    else if (act === 'add-cad') window.open(CAD_URL, '_blank', 'noopener');
    else if (act === 'zip-pkg') zipItem(t.getAttribute('data-id'), t);
    else if (act === 'tz-remove') tzRemove(t.getAttribute('data-id'));
    else if (act === 'tz-clear') { teczka = []; tzSave(); tzPaint(); toast('Lista plików wyczyszczona', '', 'folder'); }
    else if (act === 'tz-zip') zipDownload(zipList(teczka), 'Schedpol_pliki_' + today() + '.zip', t);
    else if (act === 'tz-link') tzLink();
    else if (act === 'demo') toast(t.getAttribute('data-msg') || 'Makieta', t.getAttribute('data-detail') || '', 'download');
    else if (act === 'gal') setStage(+t.getAttribute('data-idx'));
    else if (act === 'preview') openPreview(PD.files && PD.files[+t.getAttribute('data-file')]);
    else if (act === 'preview-all') openPreview(PD.all && PD.all[+t.getAttribute('data-file')]);
    else if (act === 'pf-copy') {
      const url = location.href.split('#')[0] + '#/produkt?ref=' + (PD.p ? PD.p.ref : '');
      (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(function () { toast('Link do karty skopiowany', url, 'copy'); },
        function () { window.prompt('Skopiuj link do karty produktu:', url); });
    }
    else if (act === 'preview-url') openPreview({ ext: t.getAttribute('data-ext') || 'PDF', name: t.getAttribute('data-name') || '', desc: t.getAttribute('data-desc') || '', href: t.getAttribute('data-src'), pv: { t: 'pdf', src: t.getAttribute('data-src') } });
    else if (act === 'yt') { const fr = t.closest('.yt-frame'), src = t.getAttribute('data-src') || ''; if (fr && /^https:\/\/(www\.youtube-nocookie\.com|players\.brightcove\.net)\//.test(src)) fr.innerHTML = '<iframe src="' + esc(src) + '" title="Film" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>'; }
    else if (act === 'more') { C.limit += 24; paintCatalog(); }
    else if (act === 'view') { C.view = t.getAttribute('data-view'); paintCatalog(); syncUrl(); }
    else if (act === 'facet-more') { const id = t.getAttribute('data-facet'); C.open[id] = !C.open[id]; paintCatalog(); }
    else if (act === 'rm-q') { C.q = ''; const q = $('#catQ'); if (q) q.value = ''; C.limit = 24; paintCatalog(); syncUrl(); }
    else if (act === 'rm-filter') {
      const arr = C.f[t.getAttribute('data-facet')], i = arr.indexOf(t.getAttribute('data-value'));
      if (i !== -1) arr.splice(i, 1);
      C.limit = 24; paintCatalog(); syncUrl();
    }
    else if (act === 'clear-filters') {
      Object.keys(C.f).forEach(function (k) { C.f[k] = []; });
      C.q = ''; const q2 = $('#catQ'); if (q2) q2.value = '';
      C.limit = 24; paintCatalog(); syncUrl();
    }
    else if (act === 'ftab') {
      P.tab = t.getAttribute('data-tab'); paintPlikiTable();
      try { history.replaceState(null, '', SPProto.href('pliki', P.tab === 'all' ? {} : { typ: P.tab })); } catch (err) { /* bez historii */ }
    }
  });

  document.addEventListener('keydown', function (e) {
    const typing = /^(input|textarea|select)$/i.test(e.target.tagName || '');
    if (e.key === 'Escape') { if ($('#pv.is-open')) { closePreview(); return; } closeAll(true); return; }
    if (e.key === '/' && !typing && !e.ctrlKey && !e.metaKey && !e.altKey) {
      e.preventDefault();
      const big = $('#bigSearch'), cq = $('#catQ');
      if (big && big.getBoundingClientRect().bottom > 80) big.focus();
      else if (cq && cq.getBoundingClientRect().bottom > 80) cq.focus();
      else openSearch();
    }
  });

  // Paleta wyszukiwania
  cmdSearch = mountSearch($('#cmdInput'), $('#cmdList'), { onClose: function () { closeAll(true); } });
  $('#cmd').addEventListener('click', function (e) { if (e.target === e.currentTarget) closeAll(true); });

  // Cień wyspy nawigacji po przewinięciu
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (en) { $('#nav').classList.toggle('is-scrolled', !en[0].isIntersecting); }).observe($('#topSentinel'));
  }

  SPI.hydrate(document);
  SPProto.init({
    concept: 'A', name: 'Biblioteka',
    screens: [
      { id: 'start', label: 'Start' },
      { id: 'katalog', label: 'Katalog' },
      { id: 'produkt', label: 'Karta produktu' },
      { id: 'pliki', label: 'Pliki' },
      { id: 'akademia', label: 'Akademia' }
    ],
    render: render
  });
})();
