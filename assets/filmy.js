/* Filmy z oficjalnego kanału YouTube SCHEDPOL (youtube.com/@schedpol) — ID sprawdzone przez oEmbed 19.11.2026.
   Wybór: tylko filmy o produktach z oferty Schedpol/Sensea w Leroy Merlin albo ogólne szkoleniowe.
   Pominięte celowo: film z logo innej sieci (Castorama), tytuły z twierdzeniami do korekty EmpCo
   („Antibac”, „idealne wygłuszenie”, „najwyższe właściwości izolacyjne”, „ekstremalnie wytrzymały”, DIN 51097),
   serie spoza oferty LM (Etrusco, Kalait, Competia, Medium, New Horizons, Protos, Stabilsound…).
   Pola: id, t (tytuł z YouTube), kind, g (grupa w Akademii), y (rok), fams (serie w portalu), cats (kategorie — film ogólny), short (pionowy 9:16). */
window.SP = window.SP || {};
window.SP.ytChannel = 'https://www.youtube.com/@schedpol';
window.SP.videos = [
  { id: 'Pi-RpbXVFWk', t: 'Docinanie brodzika kompozytowego bez bałaganu! Zobacz, jakie to proste!', kind: 'Montaż', g: 'brodziki', y: 2026, fams: ['Balans'] },
  { id: 'NgdrtUwx9ic', t: 'Montaż i docinanie brodzika kompozytowego w technologii STABILSOUND PLUS® | Schedpol', kind: 'Montaż · technologia Stabilsound Plus', g: 'brodziki', y: 2021, fams: ['Balans', 'Magnetic'] },  // tylko brodziki kompozytowe (wskazanie użytkownika 19.11.2026)
  /* brodziki kompozytowe w technologii Stabilsound Plus (oferta katalogowa Schedpol, nie seria LM) — dodane na prośbę użytkownika 19.11.2026; tylko w Akademii */
  { id: 'H92RaxaBTNI', t: 'Montaż brodzika STABILSOUND PLUS® na nośniku z podcięciem panelu | SCHEDPOL®', kind: 'Montaż · technologia Stabilsound Plus', g: 'brodziki', y: 2022, fams: ['Frigo', 'Sinergid', 'Integral', 'Consist', 'Grawello', 'Dante', 'Go Baby'] },  // brodziki zintegrowane
  { id: 'X-IB6cWoc5Q', t: 'STABILNE BRODZIKI WYSOKIE – DOCINANE NA WYMIAR! ŁATWY MONTAŻ BEZ PODKUWANIA - SCHEDPOL', kind: 'Prezentacja · brodziki wysokie', g: 'brodziki', y: 2023 },
  { id: 'hZ-liL5so1U', t: 'Brodziki w technologii STABILSOUND® - cechy innowacyjnego brodzika. | Schedpol', kind: 'Prezentacja · technologia Stabilsound', g: 'brodziki', y: 2022 },
  { id: '7ZoJDkV-WTA', t: 'Brodziki kompozytowe do nowoczesnych łazienek | SCHEDPOL® | Stabilsound Plus®', kind: 'Prezentacja · technologia Stabilsound Plus', g: 'brodziki', y: 2021 },
  /* Ipsilon (brodziki standardowe Sensea): film z karty produktu leroymerlin.pl (Brightcove LM, oznaczony przez LM jako treść wygenerowana przez AI) */
  { id: 'bc-6375481871112', bc: ['5588818558001', '6375481871112'], poster: 'https://cf-images.eu-west-1.prod.boltdns.net/v1/jit/5588818558001/81dbde50-c3ee-4086-b3bf-040a462b9883/main/1280x720/1m47s114ms/match/image.jpg',
    t: 'Brodzik Sensea Ipsilon — montaż', kind: 'Montaż · treść wygenerowana przez AI', ai: 1, g: 'brodziki', y: 2026, fams: ['Ipsilon'] },
  { id: 'IJ9kaWSjZfI', t: 'Najazd do brodzików podpłytkowych przeznaczony do zabudowy płytkami - montaż', kind: 'Montaż', g: 'brodziki', y: 2026, fams: ['Najazd'] },
  { id: 'MroB--d6IdE', t: 'Montaż odpływu liniowego Schedpol bezkołnierzowego w podłodze – krok po kroku', kind: 'Montaż', g: 'odplywy', y: 2026, cats: ['odpływ liniowy'] },
  { id: '_cToQnNQMiA', t: 'Montaż odpływu liniowego | SCHEDPOL®', kind: 'Montaż', g: 'odplywy', y: 2019, cats: ['odpływ liniowy'] },
  { id: 'f3jGsJc4k28', t: 'Brodzik podpłytkowy vs Odpływ liniowy - porównanie montażu', kind: 'Szkolenie', g: 'odplywy', y: 2019, cats: ['odpływ liniowy'] },
  { id: 'Uk9nFp8DQM8', t: 'Metamorfoza łazienki w 8h z systemem Wall comfort Schedpol', kind: 'Montaż · prezentacja', g: 'sciany', y: 2025, fams: ['Wall Comfort'] },
  { id: 'YrQWO6zj9LA', t: 'Metamorfoza łazienki w 8h z systemem Wall comfort Schedpol + Łazienki dla seniora.', kind: 'Montaż · prezentacja', g: 'sciany', y: 2025, fams: ['Wall Comfort'] },
  { id: 'AZpRmR4Mz_4', t: 'Prosta i szybka wymiana wanny na prysznic ze ściankami remontowymi WALL COMFORT | Schedpol®', kind: 'Montaż', g: 'sciany', y: 2022, fams: ['Wall Comfort'] },
  { id: '2P3OgAbFNtA', t: 'Prosty montaż nośnika do wanien prostokątnych | SCHEDPOL®', kind: 'Montaż', g: 'wanny', y: 2022, fams: ['Nośnik'] },
  { id: '2bKzwbdqJ9k', t: 'Nośnik stabilizujący - trwała zabudowa wanien prostokątnych', kind: 'Montaż', g: 'wanny', y: 2018, fams: ['Nośnik'] },
  { id: 'eXR4nlPoDv8', t: 'Jak bardzo wytrzymały jest Nośnik do wanien kąpielowych? Szybki test!', kind: 'Prezentacja', g: 'wanny', y: 2018, fams: ['Nośnik'] },
  { id: 'kbgA3BYcQis', t: 'Nośnik uniwersalny do wanien prostokątnych akrylowych i stalowych', kind: 'Montaż', g: 'wanny', y: 2012, fams: ['Nośnik'] },
  { id: 'TaaInRD35lM', t: 'Nośnik uniwersalny do wanien półokrągłych | Schedpol®', kind: 'Montaż', g: 'wanny', y: 2012, fams: ['Nośnik'] },
  { id: '_r7dOWAKAhE', t: 'Obudowa uniwersalna do wanien Schedpol - łatwy i szybki montaż!', kind: 'Montaż', g: 'wanny', y: 2022, fams: ['Obudowa uniwersalna'] },
  { id: 'Y6PNf-S1E94', t: 'Prosty montaż obudowy do wanien | SCHEDPOL®', kind: 'Montaż', g: 'wanny', y: 2022, fams: ['Obudowa uniwersalna'] },
  { id: 's7E3R-jkGJg', t: 'Zestaw naprawczy powierzchni brodzików i wanien Schedpol', kind: 'Serwis', g: 'serwis', y: 2023 },
  { id: '8f6ZambCwZc', t: 'Jaki brodzik wybrać do łazienki marzeń? Poradnik', kind: 'Poradnik', g: 'serwis', y: 2018 },
  { id: '-dXUx7hlCXg', t: 'Schedpol - Poznaj nas!', kind: 'O firmie', g: 'firma', y: 2025 },
  { id: '9e9Rp8cNWB0', t: 'SCHEDPOL FIRMA 2021', kind: 'O firmie', g: 'firma', y: 2021 }
];
window.SP.videoGroups = [
  { k: 'brodziki', l: 'Montaż brodzików' }, { k: 'odplywy', l: 'Odpływy liniowe' }, { k: 'wanny', l: 'Wanny: nośniki i obudowy' },
  { k: 'sciany', l: 'Panele ścienne Wall Comfort' }, { k: 'serwis', l: 'Poradniki i serwis' }, { k: 'firma', l: 'O firmie' }
];
/* prezentacje i katalog do Akademii — pliki w assets/akademia/ (ok = gotowe do publikacji) */
window.SP.academyDocs = [
  { k: 'przeglad', t: 'Przegląd Produktów LM', d: 'Katalog produktów Schedpol i Sensea w ofercie Leroy Merlin — serie, wymiary, kolory, numery ref. LM, gwarancje z zakresem. Wydanie 11.2026 · PDF, 28 stron, 18 MB.',
    f: 'Przeglad-Produktow-LM_2026.11.pdf', ok: true },
  { k: 'prezentacja', kind: 'Prezentacja PDF', t: 'Prezentacja LM PRO', d: 'Schedpol dla Leroy Merlin: firma, współpraca, technologie brodzików, oferta w LM i rynek PRO. Wydanie 19.11.2026 · PDF, 42 slajdy, 13 MB.',
    f: 'Prezentacja-LM-PRO_2026.11.pdf', ok: true }
];
