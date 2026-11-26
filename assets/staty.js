/* Statystyki portalu — Umami Cloud (bez ciasteczek, bez banera zgody). Wdrożone 24.11.2026.
   Zlicza: odsłony podstron (także adresy z „#/” — katalog, karta produktu…), pobrania plików, wyszukiwania,
   filmy, kontakt z BOK (tel./mail), dodanie do teczki. Nie zbiera danych osobowych ani treści formularzy poza frazą wyszukiwania.
   Identyfikator strony z panelu Umami: Settings → Websites → Website ID. Pusty = statystyki wyłączone. */
(function () {
  var WEBSITE_ID = 'df4ffe92-0510-43c8-8db9-a02e0fff826a';                                   // ← wpisać Website ID z Umami
  var HOST = 'bartek-schedpol.github.io';                // zliczamy tylko stronę publiczną (nie podgląd lokalny)
  if (!WEBSITE_ID || location.hostname !== HOST) return;

  var s = document.createElement('script');
  s.defer = true;
  s.src = 'https://cloud.umami.is/script.js';
  s.setAttribute('data-website-id', WEBSITE_ID);
  s.setAttribute('data-auto-track', 'false');            // odsłony wysyłamy sami — portal ma podstrony na „#/”
  s.setAttribute('data-domains', HOST);
  document.head.appendChild(s);

  var queue = [];
  function send(fn) { if (window.umami && window.umami.track) fn(window.umami); else queue.push(fn); }
  s.onload = function () { while (queue.length) queue.shift()(window.umami); };

  /* czytelny adres odsłony: /v2/start, /v2/katalog, /v2/produkt/89189407, /v1/akademia … */
  function pageUrl() {
    var lm = location.pathname.match(/\/(v2|en|ro)\//), ver = lm ? lm[1] : (/v1\.html/.test(location.pathname) ? 'v1' : 'v2');   // 26.11: PL w katalogu głównym liczona jako v2   // 25.11: także /en/ i /ro/
    var h = location.hash || '', m = h.match(/^#\/([a-z]+)/), scr = m ? m[1] : 'start';
    if (/podstrony\.html/.test(location.pathname) && !m) scr = 'katalog';
    var ref = (h.match(/ref=(\d+)/) || [])[1];
    return '/' + ver + '/' + scr + (scr === 'produkt' && ref ? '/' + ref : '');
  }
  var last = '';
  function pageview() {
    var u = pageUrl(); if (u === last) return; last = u;
    send(function (um) { um.track(function (p) { p.url = u; p.title = document.title; return p; }); });
  }
  window.addEventListener('hashchange', function () { setTimeout(pageview, 50); });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', pageview); else pageview();

  function ev(name, data) { send(function (um) { um.track(name, data); }); }

  /* kliknięcia: pobrania, kontakt, filmy, teczka */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a, button');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var file = href.split('?')[0].split('/').pop();
    if (a.hasAttribute('download') || /\/assets\/(karty|cad|dokumenty|akademia)\//.test(href) || /\.(pdf|dwg|zip|obj|3ds|jpg|png)$/i.test(file)) {
      var typ = (file.match(/\.([a-z0-9]+)$/i) || [])[1] || 'plik';
      ev('pobranie', { plik: decodeURIComponent(file).slice(0, 120), typ: typ.toLowerCase(), strona: pageUrl() });
      return;
    }
    if (/^tel:/.test(href)) { ev('telefon', { numer: href.slice(4), strona: pageUrl() }); return; }
    if (/^mailto:/.test(href)) { ev('e-mail', { adres: href.slice(7), strona: pageUrl() }); return; }
    if (/youtube\.com|youtu\.be/.test(href) || a.closest('.yt')) { ev('film', { tytul: (a.closest('.yt') || a).textContent.trim().slice(0, 100), strona: pageUrl() }); return; }
    var act = a.getAttribute('data-act') || '';
    if (/^add-/.test(act)) { ev('teczka', { akcja: act, strona: pageUrl() }); return; }
  }, true);

  /* wyszukiwania: pole w Katalogu, wyszukiwarka na Starcie V2, paleta „/” — fraza po 1,5 s bez pisania */
  var tmr;
  document.addEventListener('submit', function (e) {     // Enter w wyszukiwarce na Starcie — wysyłka od razu, przed przejściem do Katalogu
    var t = e.target && e.target.querySelector && e.target.querySelector('input[type=search]');
    var q = t && (t.value || '').trim();
    if (q) { clearTimeout(tmr); ev('wyszukiwanie', { fraza: q.slice(0, 60), pole: 'start', strona: pageUrl() }); }
  }, true);
  document.addEventListener('input', function (e) {
    var t = e.target;
    if (!t || t.type !== 'search') return;
    clearTimeout(tmr);
    tmr = setTimeout(function () {
      var q = (t.value || '').trim();
      if (q.length >= 2) ev('wyszukiwanie', { fraza: q.slice(0, 60), pole: t.id || t.name || 'szukaj', strona: pageUrl() });
    }, 1500);
  }, true);
})();
