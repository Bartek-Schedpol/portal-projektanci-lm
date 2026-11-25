# -*- coding: utf-8 -*-
"""Słownik wersji językowych portalu (25.11.2026): PL | EN | RO  ->  assets/i18n-en.js, assets/i18n-ro.js
Tłumaczenie AI (decyzja użytkownika 25.11.2026) — bez weryfikacji native speakera. Dane PL (kontakty, warunki, nr ref. LM) zostają.
EXACT: dokładny tekst albo wzorzec z liczbami {n} (silnik: assets/i18n.js). PHRASES: frazy podmieniane w tekstach złożonych.
Dopisywanie: uruchom portal w wersji EN z ?debug=1 -> window.I18N_MISS w konsoli pokazuje brakujące teksty.
"""
import io, json, os

HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(os.path.dirname(HERE), 'assets')

EXACT = r"""
Start | Home | Acasă
Katalog | Catalogue | Catalog
Pliki | Files | Fișiere
Akademia | Academy | Academie
Kontakt | Contact | Contact
Centrum plików | File centre | Centru de fișiere
Portal architekta i projektanta | Portal for architects and designers | Portal pentru arhitecți și designeri
Strefa projektanta Schedpol | Schedpol designer zone | Zona designerului Schedpol
Katalog — Strefa projektanta Schedpol | Catalogue — Schedpol designer zone | Catalog — Zona designerului Schedpol
Karta produktu — Strefa projektanta Schedpol | Product page — Schedpol designer zone | Pagină produs — Zona designerului Schedpol
Centrum plików — Strefa projektanta Schedpol | File centre — Schedpol designer zone | Centru de fișiere — Zona designerului Schedpol
Akademia — Strefa projektanta Schedpol | Academy — Schedpol designer zone | Academie — Zona designerului Schedpol
Start — Strefa projektanta Schedpol | Home — Schedpol designer zone | Acasă — Zona designerului Schedpol
Projektuj łazienki z produktami Schedpol i Sensea | Design bathrooms with Schedpol and Sensea products | Proiectează băi cu produse Schedpol și Sensea
Rysunki techniczne, modele {n}D i karty produktów do każdej pozycji z oferty Leroy Merlin — wyszukasz je po numerze ref. LM. | Technical drawings, 3D models and product sheets for every item in the Leroy Merlin range — find them by LM reference number. | Desene tehnice, modele 3D și fișe de produs pentru fiecare articol din oferta Leroy Merlin — le găsești după numărul de referință LM.
Przejdź do katalogu | Go to catalogue | Mergi la catalog
Akademia projektanta | Designer academy | Academia designerului
{n} produktów | {n} products | {n} produse
{n} serie | {n} series | {n} serii
{n} serii | {n} series | {n} serii
{n} seria | {n} series | {n} serie
Pliki bez logowania | Files without logging in | Fișiere fără autentificare
Znajdź produkt po numerze ref. LM | Find a product by LM ref. number | Găsește un produs după nr. ref. LM
Wpisz nr ref. LM, kod EAN albo wymiar brodzika — od razu zobaczysz komplet plików. | Enter the LM ref. number, EAN code or tray size — you'll see the full set of files right away. | Introdu nr. ref. LM, codul EAN sau dimensiunea cădiței — vei vedea imediat setul complet de fișiere.
Szukaj | Search | Caută
Szukaj w katalogu | Search the catalogue | Caută în catalog
np. {n}, EAN lub {n} × {n} | e.g. {n}, EAN or {n} × {n} | ex. {n}, EAN sau {n} × {n}
Szukaj po nr ref. LM, kodzie EAN lub wymiarze | Search by LM ref. number, EAN code or size | Caută după nr. ref. LM, cod EAN sau dimensiune
Karta PDF | PDF sheet (PL) | Fișă PDF (PL)
{n} lat współpracy z Leroy Merlin | {n} years of cooperation with Leroy Merlin | {n} de ani de colaborare cu Leroy Merlin
Razem od {n} roku | Together since {n} | Împreună din {n}
kompletność dostaw w {n} r. | delivery completeness in {n} | completitudinea livrărilor în {n}
dnia | days | zile
średni czas realizacji zamówień w {n} r. | average order lead time in {n} | timp mediu de livrare a comenzilor în {n}
netto | net | net
minimum zakupowe | minimum order | comandă minimă
minimum logistyczne | logistics minimum | minim logistic
netto dopłaty | net surcharge | net suprataxă
dropshipping od {n} produktu | dropshipping from {n} product | dropshipping de la {n} produs
Jedno miejsce na pliki do projektu | One place for all project files | Un singur loc pentru fișierele de proiect
Wszystko, czego potrzebujesz, żeby wstawić produkt do projektu łazienki | Everything you need to place a product in a bathroom design | Tot ce ai nevoie pentru a include un produs în proiectul băii
Rysunek, model {n}D i karta PDF — pobierasz osobno albo wszystko naraz w ZIP | Drawing, 3D model and PDF sheet — download separately or all at once as a ZIP | Desen, model 3D și fișă PDF — descarci separat sau totul odată în ZIP
Strefa projektanta zbiera w jednym miejscu dane techniczne produktów Schedpol i Sensea dostępnych w Leroy Merlin. | The designer zone brings together technical data for Schedpol and Sensea products available at Leroy Merlin. | Zona designerului reunește datele tehnice ale produselor Schedpol și Sensea disponibile la Leroy Merlin.
Każda pozycja ma numer ref. LM, wymiary, rysunek z pozycją odpływu i model {n}D. | Every item has an LM ref. number, dimensions, a drawing with the drain position and a 3D model. | Fiecare articol are nr. ref. LM, dimensiuni, desen cu poziția scurgerii și model 3D.
Pliki wybrane z różnych kart odkładasz do Plików i pobierasz razem, gotowe do przekazania klientowi albo wykonawcy. | Collect files from different products in Files and download them together, ready to hand over to a client or contractor. | Adaugi fișiere din diferite produse în Fișiere și le descarci împreună, gata de predat clientului sau constructorului.
O portalu | About the portal | Despre portal
Doradca techniczny Schedpol | Schedpol technical advisor | Consultant tehnic Schedpol
pomoc przy doborze produktu | help choosing a product | ajutor la alegerea produsului
Numer ref. LM i gama przy każdej pozycji | LM ref. number and range for every item | Nr. ref. LM și gama pentru fiecare articol
Modele {n}D z odpływem w miejscu jak w produkcie | 3D models with the drain where it is in the product | Modele 3D cu scurgerea poziționată ca în produs
Karty produktów PDF do wydruku A{n} | PDF product sheets for A4 printing (PL) | Fișe de produs PDF pentru imprimare A4 (PL)
produktów w ofercie LM | products in the LM range | produse în oferta LM
serie Schedpol i Sensea | Schedpol and Sensea series | serii Schedpol și Sensea
brodzików | shower trays | cădițe de duș
odpływów liniowych | linear drains | rigole liniare
Nowości {n} | New in {n} | Noutăți {n}
Nowe serie w ofercie Leroy Merlin | New series in the Leroy Merlin range | Serii noi în oferta Leroy Merlin
Cały katalog | Full catalogue | Tot catalogul
Nowość | New | Nou
Nowość {n} | New {n} | Nou {n}
Oferta w Leroy Merlin | Range at Leroy Merlin | Oferta la Leroy Merlin
Kategorie | Categories | Categorii
Kategoria | Category | Categorie
Kategoria: | Category: | Categorie:
maskownica | drain cover | capac de scurgere
panel do brodzika | tray panel | panou de cădiță
nogi do brodzika | tray legs | picioare pentru cădiță
najazd | ramp | rampă
Wsparcie techniczne | Technical support | Asistență tehnică
Brakuje pliku albo wymiaru? | Missing a file or a dimension? | Lipsește un fișier sau o dimensiune?
Biuro Obsługi Klienta Schedpol odpowiada na pytania o montaż, dobór produktu i materiały do projektu. Zadzwoń do działu obsługującego Twój region. | Schedpol Customer Service answers questions about installation, product selection and project materials (in Polish). Call the team for your region. | Serviciul Clienți Schedpol răspunde la întrebări despre montaj, alegerea produsului și materialele de proiect (în limba poloneză). Sună echipa pentru regiunea ta.
pon.–pt. {n}:{n}–{n}:{n} | Mon–Fri {n}:{n}–{n}:{n} (CET) | Lun–Vin {n}:{n}–{n}:{n} (CET)
BOK {n} · Zachód | Customer Service {n} · West | Serviciul Clienți {n} · Vest
BOK {n} · Wschód | Customer Service {n} · East | Serviciul Clienți {n} · Est
BOK {n} · Południe | Customer Service {n} · South | Serviciul Clienți {n} · Sud
Polska zachodnia | Western Poland | Polonia de vest
Polska wschodnia i północna | Eastern and northern Poland | Polonia de est și de nord
Polska południowa | Southern Poland | Polonia de sud
Doradca techniczny — klient indywidualny i inwestycje | Technical advisor — private customers and projects | Consultant tehnic — clienți individuali și investiții
Regiony Biura Obsługi Klienta | Customer Service regions | Regiunile Serviciului Clienți
Brodzik Schedpol Balans w aranżacji łazienki | Schedpol Balans shower tray in a bathroom setting | Cădiță de duș Schedpol Balans într-un decor de baie
Zamówienie przez BOK | Order via Customer Service | Comandă prin Serviciul Clienți
Nie ma tego produktu na stanie? Zamów! | Not in stock? Order it! | Produsul nu este în stoc? Comandă-l!
Biuro Obsługi Klienta Schedpol · pon.–pt. {n}:{n}–{n}:{n} | Schedpol Customer Service · Mon–Fri {n}:{n}–{n}:{n} (CET) | Serviciul Clienți Schedpol · Lun–Vin {n}:{n}–{n}:{n} (CET)
Numer referencyjny Leroy Merlin | Leroy Merlin reference number (Poland) | Număr de referință Leroy Merlin (Polonia)
Podgląd karty A{n} przed pobraniem | Preview the A4 sheet before downloading (PL) | Previzualizează fișa A4 înainte de descărcare (PL)
Cena i dostępność: w systemie sklepu Leroy Merlin. | Price and availability: in the Leroy Merlin store system. | Preț și disponibilitate: în sistemul magazinului Leroy Merlin.
Gwarancja | Warranty | Garanție
Warunek: montaż zgodnie z instrukcją, przez osobę o odpowiednich kwalifikacjach. Zakres i terytorium — karta gwarancyjna Stabilsafe v{n}. Gwarancja nie ogranicza ustawowych praw kupującego. | Condition: installation according to the instructions by a suitably qualified person. Scope and territory — Stabilsafe warranty card v{n} (PL). The warranty does not limit the buyer's statutory rights. | Condiție: montaj conform instrucțiunilor, de către o persoană calificată. Domeniu și teritoriu — certificatul de garanție Stabilsafe v{n} (PL). Garanția nu limitează drepturile legale ale cumpărătorului.
Centrum plików cyfrowych | Digital file centre | Centru de fișiere digitale
Materiały do pobrania dla architekta i projektanta | Downloads for architects and designers | Materiale de descărcat pentru arhitecți și designeri
Pobierz całą paczkę (.ZIP · {n} MB) | Download the whole package (.ZIP · {n} MB) | Descarcă tot pachetul (.ZIP · {n} MB)
Modele {n}D i CAD | 3D models and CAD | Modele 3D și CAD
Dokumentacja | Documentation | Documentație
Packshoty i aranżacje | Packshots and room settings | Packshot-uri și amenajări
Udostępnij zestaw inwestorowi | Share the set with your client | Trimite setul investitorului
Skopiuj link do tej karty produktu — pliki i dokumentacja są dostępne bez logowania. | Copy the link to this product page — files and documentation are available without logging in. | Copiază linkul acestei pagini de produs — fișierele și documentația sunt disponibile fără autentificare.
Kopiuj link do karty | Copy link to page | Copiază linkul paginii
Okruszki | Breadcrumbs | Navigare
Galeria produktu | Product gallery | Galerie produs
Poprzednie miniatury | Previous thumbnails | Miniaturile anterioare
Następne miniatury | Next thumbnails | Miniaturile următoare
Kolor | Colour | Culoare
Wymiar | Size | Dimensiune
Kształt | Shape | Formă
Seria | Series | Serie
Marka | Brand | Marcă
Gama | Range | Gamă
Gama LM | LM range | Gama LM
Technologia | Technology | Tehnologie
Wersja | Version | Versiune
Dostępne wersje | Available versions | Versiuni disponibile
{n} wersje | {n} versions | {n} versiuni
EAN | EAN | EAN
Rysunek techniczny | Technical drawing | Desen tehnic
Rysunek techniczny · wymiary w mm | Technical drawing · dimensions in mm | Desen tehnic · dimensiuni în mm
Rysunek techniczny, wymiary w mm | Technical drawing, dimensions in mm | Desen tehnic, dimensiuni în mm
wymiary w mm | dimensions in mm | dimensiuni în mm
wymiary w cm | dimensions in cm | dimensiuni în cm
Gotowe w programie (baza {n}) | Ready in the software (library {n}) | Gata în program (bibliotecă {n})
Wstaw | Insert | Inserează
Format wymiarowy | Sizes | Dimensiuni
Filmy | Videos | Videoclipuri
Montaż i prezentacja produktu. | Installation and product presentation (in Polish). | Montaj și prezentarea produsului (în limba poloneză).
Wszystkie w Akademii | All in the Academy | Toate în Academie
Wizualizacja poglądowa | Illustrative visualisation | Vizualizare orientativă
Wizualizacja poglądowa · inny wariant kolorystyczny | Illustrative visualisation · another colour variant | Vizualizare orientativă · altă variantă de culoare
Inne produkty w tym rozmiarze | Other products in this size | Alte produse cu această dimensiune
Wszystkie w katalogu | All in the catalogue | Toate în catalog
Gwarancja producenta — zakres niżej | Manufacturer's warranty — scope below | Garanția producătorului — detalii mai jos
{n} lat | {n} years | {n} ani
{n} lat — stałość barwy | {n} years — colour stability | {n} ani — stabilitatea culorii
{n} lat — wytrzymałość na nacisk wg PN-EN {n} | {n} years — load resistance per PN-EN {n} | {n} ani — rezistență la sarcină conform PN-EN {n}
{n} lat — wg PN-EN {n}-{n} | {n} years — per PN-EN {n}-{n} | {n} ani — conform PN-EN {n}-{n}
{n} lat — trwałość materiału nośnika EPS | {n} years — durability of the EPS support material | {n} ani — durabilitatea materialului suportului EPS
Oglądasz | Viewing | Vizualizezi
Dostępne kolory w tym wymiarze | Colours available in this size | Culori disponibile în această dimensiune
{n} warianty | {n} variants | {n} variante
{n} wariantów | {n} variants | {n} variante
Właściwości powierzchni ograniczają przyleganie zabrudzeń — brodzik łatwo utrzymać w czystości. | The surface limits dirt adhesion — the tray is easy to keep clean. | Suprafața limitează aderența murdăriei — cădița se curăță ușor.
A{n} — parametry, nr ref., EAN, rysunek techniczny, gwarancja | A4 — specifications, ref. no., EAN, technical drawing, warranty (PL) | A4 — parametri, nr. ref., EAN, desen tehnic, garanție (PL)
Karta produktu PDF, A{n} — parametry, nr ref., EAN, rysunek techniczny, gwarancja | Product sheet PDF, A4 — specifications, ref. no., EAN, technical drawing, warranty (PL) | Fișă produs PDF, A4 — parametri, nr. ref., EAN, desen tehnic, garanție (PL)
Karta produktu PDF | Product sheet PDF (PL) | Fișă produs PDF (PL)
Karta produktu | Product sheet (PL) | Fișă produs (PL)
Karty produktów | Product sheets (PL) | Fișe de produs (PL)
Montaż · technologia Stabilsound Plus · YouTube Schedpol | Installation · Stabilsound Plus technology · YouTube Schedpol (PL) | Montaj · tehnologia Stabilsound Plus · YouTube Schedpol (PL)
Montaż · YouTube Schedpol | Installation · YouTube Schedpol (PL) | Montaj · YouTube Schedpol (PL)
Montaż · prezentacja · YouTube Schedpol | Installation · presentation · YouTube Schedpol (PL) | Montaj · prezentare · YouTube Schedpol (PL)
Szkolenie · YouTube Schedpol | Training · YouTube Schedpol (PL) | Instruire · YouTube Schedpol (PL)
Prezentacja · YouTube Schedpol | Presentation · YouTube Schedpol (PL) | Prezentare · YouTube Schedpol (PL)
Serwis · YouTube Schedpol | Service · YouTube Schedpol (PL) | Service · YouTube Schedpol (PL)
Poradnik · YouTube Schedpol | Guide · YouTube Schedpol (PL) | Ghid · YouTube Schedpol (PL)
O firmie · YouTube Schedpol | About the company · YouTube Schedpol (PL) | Despre companie · YouTube Schedpol (PL)
Prezentacja · brodziki wysokie · YouTube Schedpol | Presentation · high shower trays · YouTube Schedpol (PL) | Prezentare · cădițe înalte · YouTube Schedpol (PL)
Prezentacja · technologia Stabilsound · YouTube Schedpol | Presentation · Stabilsound technology · YouTube Schedpol (PL) | Prezentare · tehnologia Stabilsound · YouTube Schedpol (PL)
Prezentacja · technologia Stabilsound Plus · YouTube Schedpol | Presentation · Stabilsound Plus technology · YouTube Schedpol (PL) | Prezentare · tehnologia Stabilsound Plus · YouTube Schedpol (PL)
Montaż · treść wygenerowana przez AI · film Leroy Merlin | Installation · AI-generated content · Leroy Merlin video | Montaj · conținut generat de AI · videoclip Leroy Merlin
Treść wygenerowana przez AI | AI-generated content | Conținut generat de AI
Antypoślizgowość | Slip resistance | Rezistență la alunecare
klasa A — DIN EN {n}:{n} (załącznik A) | class A — DIN EN {n}:{n} (annex A) | clasa A — DIN EN {n}:{n} (anexa A)
Możliwy montaż na posadzce lub zlicowany z posadzką. | Can be installed on the floor or flush with the floor. | Se poate monta pe pardoseală sau la nivelul pardoselii.
Podparcie na całej powierzchni brodzika zapewnia jego stabilność. | Support across the entire tray surface ensures stability. | Sprijinul pe toată suprafața cădiței asigură stabilitatea.
Wielowarstwowa konstrukcja wspiera izolację termiczną i akustyczną. | The multi-layer construction supports thermal and acoustic insulation. | Construcția multistrat contribuie la izolarea termică și acustică.
Syfon i podejście kanalizacyjne mieszczą się w konstrukcji brodzika. | The trap and waste connection fit within the tray construction. | Sifonul și racordul la canalizare se încadrează în construcția cădiței.
Wzmocnione dno zwiększa sztywność konstrukcji: {n} warstwy laminatu żywicznego i płyta drewnopochodna. | Reinforced base increases rigidity: {n} layers of resin laminate and a wood-based board. | Fundul ranforsat crește rigiditatea: {n} straturi de laminat cu rășină și o placă din lemn.
Hydroszczelna warstwa ogranicza przenikanie wilgoci do wnętrza konstrukcji. | A watertight layer limits moisture penetration into the construction. | Un strat hidroizolant limitează pătrunderea umezelii în construcție.
Możliwość docięcia brodzika ułatwia dopasowanie do nietypowych wnęk. | The tray can be cut to size to fit non-standard recesses. | Cădița poate fi tăiată pe dimensiune pentru nișe atipice.
Infografika | Infographic | Infografic
Infografika · cechy serii | Infographic · series features | Infografic · caracteristicile seriei
cechy serii | series features | caracteristicile seriei
Struktura powierzchni | Surface texture | Textura suprafeței
Zbliżenie powierzchni | Surface close-up | Prim-plan al suprafeței
Linie docinania · wizualizacja poglądowa | Cutting lines · illustrative visualisation | Linii de tăiere · vizualizare orientativă
Przekrój — budowa warstwowa brodzika | Cross-section — layered tray construction | Secțiune — construcția stratificată a cădiței
Przekrój — budowa warstwowa brodzika · wizualizacja poglądowa | Cross-section — layered tray construction · illustrative visualisation | Secțiune — construcția stratificată a cădiței · vizualizare orientativă
wizualizacja poglądowa | illustrative visualisation | vizualizare orientativă
przezroczyste tło | transparent background | fundal transparent
Model {n}D · przeciągnij, aby obrócić | 3D model · drag to rotate | Model 3D · trage pentru a roti
Model {n}D dopasowany do wymiaru produktu (bryła serii {n} × {n} cm) · przeciągnij, aby obrócić | 3D model adjusted to the product size (series body {n} × {n} cm) · drag to rotate | Model 3D adaptat la dimensiunea produsului (corp serie {n} × {n} cm) · trage pentru a roti
Model {n}D | 3D model | Model 3D
Packshot | Packshot | Packshot
Packshot {n} z {n} | Packshot {n} of {n} | Packshot {n} din {n}
Aranżacja — wizualizacja poglądowa | Room setting — illustrative visualisation | Amenajare — vizualizare orientativă
Dodaj pliki do Plików | Add files to Files | Adaugă fișierele în Fișiere
Dodaj do Plików | Add to Files | Adaugă în Fișiere
Dodaj pliki produktu {n} do Plików | Add files of product {n} to Files | Adaugă fișierele produsului {n} în Fișiere
Kopiuj nr ref. LM | Copy LM ref. no. | Copiază nr. ref. LM
Typy plików | File types | Tipuri de fișiere
Podgląd przed pobraniem | Preview before downloading | Previzualizare înainte de descărcare
Podgląd | Preview | Previzualizare
Pobierz | Download | Descarcă
Pobierz PDF | Download PDF (PL) | Descarcă PDF (PL)
{n} plik | {n} file | {n} fișier
{n} pliki | {n} files | {n} fișiere
{n} plików | {n} files | {n} fișiere
{n} plików w {n} pozycjach | {n} files in {n} items | {n} fișiere în {n} poziții
{n} pliki w {n} pozycjach | {n} files in {n} items | {n} fișiere în {n} poziții
{n} plik w {n} pozycji | {n} file in {n} item | {n} fișier în {n} poziție
{n} pliki w {n} pozycji | {n} files in {n} item | {n} fișiere în {n} poziție
{n} plików w {n} pozycji | {n} files in {n} item | {n} fișiere în {n} poziție
Karta gwarancyjna | Warranty card (PL) | Certificat de garanție (PL)
Karta gwarancyjna Stabilsafe v{n} | Stabilsafe warranty card v{n} (PL) | Certificat de garanție Stabilsafe v{n} (PL)
Karta gwarancyjna Stabilsound v{n} — marka katalogowa Schedpol, nie dotyczy indeksów LM | Stabilsound warranty card v{n} (PL) — Schedpol catalogue brand, not for LM items | Certificat de garanție Stabilsound v{n} (PL) — marcă de catalog Schedpol, nu se aplică articolelor LM
Instrukcja montażu No{n} — brodziki kompozytowe | Installation manual No{n} — composite shower trays (PL) | Instrucțiuni de montaj No{n} — cădițe de duș compozite (PL)
Instrukcja montażu No{n} — brodziki zintegrowane | Installation manual No{n} — integrated shower trays (PL) | Instrucțiuni de montaj No{n} — cădițe de duș integrate (PL)
Instrukcja montażu No{n} — brodziki laminowane | Installation manual No{n} — laminated shower trays (PL) | Instrucțiuni de montaj No{n} — cădițe de duș laminate (PL)
Instrukcja montażu No{n}A — brodzik standard z nośnikiem | Installation manual No{n}A — standard tray with support (PL) | Instrucțiuni de montaj No{n}A — cădiță standard cu suport (PL)
Instrukcja montażu No{n} — odpływy liniowe | Installation manual No{n} — linear drains (PL) | Instrucțiuni de montaj No{n} — rigole liniare (PL)
Instrukcja montażu No{n}C — odpływy liniowe, posadzka winylowa | Installation manual No{n}C — linear drains, vinyl flooring (PL) | Instrucțiuni de montaj No{n}C — rigole liniare, pardoseală vinil (PL)
Instrukcja montażu No{n} — wanny | Installation manual No{n} — bathtubs (PL) | Instrucțiuni de montaj No{n} — căzi (PL)
Instrukcja montażu No{n} — Wall Comfort | Installation manual No{n} — Wall Comfort (PL) | Instrucțiuni de montaj No{n} — Wall Comfort (PL)
Instrukcja montażu No{n} — nośnik do wanien | Installation manual No{n} — bathtub support (PL) | Instrucțiuni de montaj No{n} — suport pentru căzi (PL)
Instrukcja montażu No{n} — obudowy podpłytkowe | Installation manual No{n} — tileable bath panels (PL) | Instrucțiuni de montaj No{n} — panouri de cadă pentru placare (PL)
Instrukcja montażu No{n} — najazd do brodzików | Installation manual No{n} — shower tray ramp (PL) | Instrucțiuni de montaj No{n} — rampă pentru cădițe (PL)
Instrukcja montażu — obudowa podpłytkowa {n} | Installation manual — tileable bath panel {n} (PL) | Instrucțiuni de montaj — panou de cadă pentru placare {n} (PL)
Instrukcja montażu — Frigo Sensea | Installation manual — Frigo Sensea (PL) | Instrucțiuni de montaj — Frigo Sensea (PL)
Instrukcja montażu — Ipsilon Sensea | Installation manual — Ipsilon Sensea (PL) | Instrucțiuni de montaj — Ipsilon Sensea (PL)
Instrukcja montażu — brodziki Comfo | Installation manual — Comfo shower trays (PL) | Instrucțiuni de montaj — cădițe Comfo (PL)
Komplet plików do projektu: {x}, {d}. Każdy plik można obejrzeć przed pobraniem. | Complete project file set: {x}, {d}. Every file can be previewed before downloading. | Set complet de fișiere pentru proiect: {x}, {d}. Fiecare fișier poate fi previzualizat înainte de descărcare.
brak plików | no files | niciun fișier
Brak plików | No files | Niciun fișier
Brak plików tego typu dla tego indeksu. | No files of this type for this item. | Nu există fișiere de acest tip pentru acest articol.
Pokaż wszystkie ({n}) | Show all ({n}) | Arată toate ({n})
Model {n}D DWG | 3D model DWG | Model 3D DWG
Model {n}D OBJ w archiwum ZIP | 3D model OBJ in a ZIP archive | Model 3D OBJ în arhivă ZIP
Model {n}D {n}DS | 3D model 3DS | Model 3D 3DS
Model {n}D DWG (AutoCAD) | 3D model DWG (AutoCAD) | Model 3D DWG (AutoCAD)
odpływ wg rysunku technicznego | drain per technical drawing | scurgere conform desenului tehnic
bryła serii dopasowana do wymiaru produktu (wzorzec {n} × {n} cm) | series body adjusted to the product size (template {n} × {n} cm) | corp de serie adaptat la dimensiunea produsului (șablon {n} × {n} cm)
bryła Regular Flow (Schedline {n}): długość, położenie syfonu i wykończenie wg rysunku technicznego Harmony | Regular Flow body (Schedline {n}): length, trap position and finish per Harmony technical drawing | corp Regular Flow (Schedline {n}): lungimea, poziția sifonului și finisajul conform desenului tehnic Harmony
AutoCAD {n}D / {n}D | AutoCAD {n}D / {n}D | AutoCAD {n}D / {n}D
Filtry | Filters | Filtre
Rozmiar (długość × szerokość) | Size (length × width) | Dimensiune (lungime × lățime)
Sortowanie | Sort by | Sortare
Seria A–Z | Series A–Z | Serie A–Z
Seria Z–A | Series Z–A | Serie Z–A
Filtruj katalog | Filter the catalogue | Filtrează catalogul
nie podano | not specified | nespecificat
Gama wg eksportu referencji LM z {n}.{n}. | Range per LM reference export of {n}.{n}. | Gama conform exportului de referințe LM din {n}.{n}.
Gama Leroy Merlin wg eksportu referencji z {n}.{n} | Leroy Merlin range per reference export of {n}.{n} | Gama Leroy Merlin conform exportului de referințe din {n}.{n}
Filtruj: nr ref., EAN, seria, wymiar, kolor… | Filter: ref. no., EAN, series, size, colour… | Filtrează: nr. ref., EAN, serie, dimensiune, culoare…
Filtry katalogu | Catalogue filters | Filtrele catalogului
Zamknij filtry | Close filters | Închide filtrele
Wyniki | Results | Rezultate
Widok wyników | Results view | Vizualizare rezultate
Kafle | Tiles | Plăci
Widok kafli | Tile view | Vizualizare plăci
Tabela | Table | Tabel
Widok tabeli | Table view | Vizualizare tabel
Katalog · oferta w Leroy Merlin | Catalogue · Leroy Merlin range | Catalog · oferta Leroy Merlin
Katalog produktów | Product catalogue | Catalog de produse
{n} produktów w {n} seriach. Każda pozycja ma numer ref. LM, wymiary i komplet plików do projektu. Gama wg eksportu referencji LM z {n}.{n}. | {n} products in {n} series. Every item has an LM ref. number, dimensions and a complete set of project files. Range per LM reference export of {n}.{n}. | {n} produse în {n} serii. Fiecare articol are nr. ref. LM, dimensiuni și un set complet de fișiere pentru proiect. Gama conform exportului de referințe LM din {n}.{n}.
Wyświetlono {n} z {n} | Showing {n} of {n} | Afișate {n} din {n}
Pokaż kolejne {n} | Show {n} more | Arată încă {n}
wyników z {n} | results of {n} | rezultate din {n}
Wyczyść wszystko | Clear all | Șterge tot
Wyczyść filtry | Clear filters | Șterge filtrele
Usuń wyszukiwaną frazę | Remove search phrase | Șterge termenul căutat
Brak produktów dla tych kryteriów | No products match these criteria | Niciun produs pentru aceste criterii
Usuń część filtrów albo zmień frazę. Numer ref. LM ma {n} cyfr — wpisz go w całości, np. {n}. | Remove some filters or change the phrase. The LM ref. number has {n} digits — enter it in full, e.g. {n}. | Elimină unele filtre sau schimbă termenul. Nr. ref. LM are {n} cifre — introdu-l complet, ex. {n}.
Szukaj: | Search: | Caută:
Akcja | Action | Acțiune
Rozmiar | Size | Dimensiune
Razem | Total | Total
Razem · {n} serie | Total · {n} series | Total · {n} serii
Razem · {n} serii | Total · {n} series | Total · {n} serii
Razem · {n} seria | Total · {n} series | Total · {n} serie
Zawartość paczki | Package contents | Conținutul pachetului
Paczki plików dla całych serii | File packages for whole series | Pachete de fișiere pentru serii întregi
{n} pliki · {n} MB · {n} serie produktów. Paczkę ZIP serii pobierzesz od razu (strzałka) albo dodasz do Plików i pobierzesz razem z innymi. | {n} files · {n} MB · {n} product series. Download a series ZIP right away (arrow) or add it to Files and download it with others. | {n} fișiere · {n} MB · {n} serii de produse. Descarcă imediat ZIP-ul seriei (săgeata) sau adaugă-l în Fișiere și descarcă-l împreună cu altele.
{n} plików · {n} MB · {n} serii produktów. Paczkę ZIP serii pobierzesz od razu (strzałka) albo dodasz do Plików i pobierzesz razem z innymi. | {n} files · {n} MB · {n} product series. Download a series ZIP right away (arrow) or add it to Files and download it with others. | {n} fișiere · {n} MB · {n} serii de produse. Descarcă imediat ZIP-ul seriei (săgeata) sau adaugă-l în Fișiere și descarcă-l împreună cu altele.
Baza CAD Decor · {n} | CAD Decor library · {n} | Biblioteca CAD Decor · {n}
Baza CAD Decor | CAD Decor library | Biblioteca CAD Decor
Instrukcje i karty gw. | Manuals and warranty cards (PL) | Instrucțiuni și certificate de garanție (PL)
Statusy plików | File status | Starea fișierelor
Publikujemy wyłącznie pliki po weryfikacji treści. Paczki ZIP powstają z aktualnych plików w chwili pobrania. | We only publish files whose content has been verified. ZIP packages are built from the current files when you download. | Publicăm doar fișiere verificate. Pachetele ZIP se creează din fișierele actuale în momentul descărcării.
Zweryfikowano {n} | Verified {n} | Verificat {n}
Baza {n} | Library {n} | Bibliotecă {n}
Wersje | Versions | Versiuni
Po aktualizacji pliku poprzednia wersja znika z biblioteki. Paczki ZIP i linki z Plików zawierają aktualne wersje plików. | When a file is updated, the previous version is removed from the library. ZIP packages and links from Files always contain the current versions. | După actualizarea unui fișier, versiunea anterioară dispare din bibliotecă. Pachetele ZIP și linkurile din Fișiere conțin versiunile actuale.
Nazwy plików | File names | Denumirea fișierelor
Jeden schemat nazw dla wszystkich materiałów: | One naming scheme for all materials: | O singură schemă de denumire pentru toate materialele:
Schedpol_<Seria>_<wymiar>_<typ>.<ext> | Schedpol_<Series>_<size>_<type>.<ext> | Schedpol_<Serie>_<dimensiune>_<tip>.<ext>
Paczki serii | Series packages | Pachete de serii
Typ plików | File type | Tip de fișiere
Pliki do pobrania | Files to download | Fișiere de descărcat
Otwórz listę plików do pobrania | Open the download list | Deschide lista de descărcări
Zamknij listę plików | Close the file list | Închide lista de fișiere
Lista plików jest pusta | Your file list is empty | Lista de fișiere este goală
Dodaj pliki z katalogu, karty produktu albo paczkę całej serii. | Add files from the catalogue, a product page or a whole series package. | Adaugă fișiere din catalog, de pe pagina unui produs sau pachetul unei serii întregi.
Pobierz ZIP | Download ZIP | Descarcă ZIP
Wyślij linki e-mailem | Send links by email | Trimite linkurile pe e-mail
Wyczyść | Clear | Golește
Wszystkie | All | Toate
Modele {n}D | 3D models | Modele 3D
Rysunki techniczne | Technical drawings | Desene tehnice
Packshoty | Packshots | Packshot-uri
Aranżacje | Room settings | Amenajări
Przekroje i infografiki | Cross-sections and infographics | Secțiuni și infografice
{n} karta | {n} sheet | {n} fișă
{n} karty | {n} sheets | {n} fișe
{n} kart | {n} sheets | {n} fișe
{n} model {n}D | {n} 3D model | {n} model 3D
{n} modele {n}D | {n} 3D models | {n} modele 3D
{n} modeli {n}D | {n} 3D models | {n} modele 3D
{n} rysunek | {n} drawing | {n} desen
{n} rysunki | {n} drawings | {n} desene
{n} rysunków | {n} drawings | {n} desene
{n} packshot | {n} packshot | {n} packshot
{n} packshoty | {n} packshots | {n} packshot-uri
{n} packshotów | {n} packshots | {n} packshot-uri
{n} aranżacja | {n} room setting | {n} amenajare
{n} aranżacje | {n} room settings | {n} amenajări
{n} aranżacji | {n} room settings | {n} amenajări
{n} grafika | {n} graphic | {n} grafică
{n} grafiki | {n} graphics | {n} grafice
{n} grafik | {n} graphics | {n} grafice
{n} dokument | {n} document | {n} document
{n} dokumenty | {n} documents | {n} documente
{n} dokumentów | {n} documents | {n} documente
karta | sheet | fișă
karty | sheets | fișe
kart | sheets | fișe
modele {n}D | 3D models | modele 3D
modeli {n}D | 3D models | modele 3D
rysunek | drawing | desen
rysunki | drawings | desene
rysunków | drawings | desene
packshot | packshot | packshot
packshoty | packshots | packshot-uri
packshotów | packshots | packshot-uri
aranżacja | room setting | amenajare
aranżacje | room settings | amenajări
aranżacji | room settings | amenajări
grafiki | graphics | grafice
dokument | document | document
dokumenty | documents | documente
indeksów | items | articole
Dokument | Document | Document
Dotyczy | Applies to | Se aplică la
Wszystkie indeksy w ofercie LM | All items in the LM range | Toate articolele din oferta LM
Nie dotyczy indeksów LM | Not for LM items | Nu se aplică articolelor LM
{n} dokumentów | {n} documents | {n} documente
· instrukcje montażu przypisane do serii, karta gwarancyjna Stabilsafe v{n} do wszystkich indeksów LM | · installation manuals assigned to series, Stabilsafe warranty card v{n} for all LM items (all in Polish) | · instrucțiuni de montaj atribuite seriilor, certificat de garanție Stabilsafe v{n} pentru toate articolele LM (toate în limba poloneză)
{n} strony | {n} pages | {n} pagini
{n} stron | {n} pages | {n} pagini
{n} strona | {n} page | {n} pagină
Filmy, prezentacje i katalog | Videos, presentations and catalogue | Videoclipuri, prezentări și catalog
Materiały szkoleniowe Schedpol dla projektantów i zespołów Leroy Merlin: {n} filmów z kanału YouTube Schedpol, prezentacje i katalog produktów. | Schedpol training materials for designers and Leroy Merlin teams: {n} videos from the Schedpol YouTube channel, presentations and the product catalogue (all in Polish). | Materiale de instruire Schedpol pentru designeri și echipele Leroy Merlin: {n} videoclipuri de pe canalul YouTube Schedpol, prezentări și catalogul de produse (toate în limba poloneză).
Kanał YouTube Schedpol | Schedpol YouTube channel | Canalul YouTube Schedpol
Katalog i prezentacje | Catalogue and presentations | Catalog și prezentări
Katalog PDF | PDF catalogue (PL) | Catalog PDF (PL)
Prezentacja PDF | PDF presentation (PL) | Prezentare PDF (PL)
Przegląd Produktów LM | LM Product Overview | Prezentare generală a produselor LM
Prezentacja LM PRO | LM PRO presentation | Prezentare LM PRO
Katalog produktów Schedpol i Sensea w ofercie Leroy Merlin — serie, wymiary, kolory, numery ref. LM, gwarancje z zakresem. Wydanie {n} · PDF, {n} stron, {n} MB. | Catalogue of Schedpol and Sensea products in the Leroy Merlin range — series, sizes, colours, LM ref. numbers, warranties with scope. Edition {n} · PDF in Polish, {n} pages, {n} MB. | Catalogul produselor Schedpol și Sensea din oferta Leroy Merlin — serii, dimensiuni, culori, nr. ref. LM, garanții cu domeniu. Ediția {n} · PDF în poloneză, {n} pagini, {n} MB.
Katalog produktów Schedpol i Sensea w ofercie Leroy Merlin — serie, wymiary, kolory, numery ref. LM, gwarancje z zakresem. Wydanie {n}.{n} · PDF, {n} stron, {n} MB. | Catalogue of Schedpol and Sensea products in the Leroy Merlin range — series, sizes, colours, LM ref. numbers, warranties with scope. Edition {n}.{n} · PDF in Polish, {n} pages, {n} MB. | Catalogul produselor Schedpol și Sensea din oferta Leroy Merlin — serii, dimensiuni, culori, nr. ref. LM, garanții cu domeniu. Ediția {n}.{n} · PDF în poloneză, {n} pagini, {n} MB.
Schedpol dla Leroy Merlin: firma, współpraca, technologie brodzików, oferta w LM i rynek PRO. Wydanie {n}.{n} · PDF, {n} slajdy, {n} MB. | Schedpol for Leroy Merlin: company, cooperation, shower tray technologies, LM range and the PRO market. Edition {n}.{n} · PDF in Polish, {n} slides, {n} MB. | Schedpol pentru Leroy Merlin: companie, colaborare, tehnologii de cădițe, oferta LM și piața PRO. Ediția {n}.{n} · PDF în poloneză, {n} diapozitive, {n} MB.
Filmy szkoleniowe i montażowe | Training and installation videos | Videoclipuri de instruire și montaj
Kliknij miniaturę, żeby odtworzyć film na stronie. | Click a thumbnail to play the video on the page. Videos are in Polish. | Fă clic pe o miniatură pentru a reda videoclipul pe pagină. Videoclipurile sunt în limba poloneză.
Filmy są osadzone z serwisu YouTube (tryb bez plików cookie do chwili odtworzenia) oraz z odtwarzacza Leroy Merlin. | Videos are embedded from YouTube (no cookies until played) and from the Leroy Merlin player. | Videoclipurile sunt încorporate din YouTube (fără cookie-uri până la redare) și din playerul Leroy Merlin.
Temat filmów | Video topic | Tema videoclipurilor
Montaż brodzików | Shower tray installation | Montajul cădițelor de duș
Wanny: nośniki i obudowy | Bathtubs: supports and panels | Căzi: suporturi și panouri
Panele ścienne Wall Comfort | Wall Comfort wall panels | Panouri de perete Wall Comfort
Poradniki i serwis | Guides and service | Ghiduri și service
O firmie | About the company | Despre companie
Przejdź do treści | Skip to content | Salt la conținut
Szukaj: nr ref., seria, wymiar… | Search: ref. no., series, size… | Caută: nr. ref., serie, dimensiune…
Szukaj: nr ref., seria, wymiar (skrót: ukośnik) | Search: ref. no., series, size (shortcut: slash) | Caută: nr. ref., serie, dimensiune (scurtătură: bară oblică)
Nr ref. LM, EAN, seria, wymiar, kolor… | LM ref. no., EAN, series, size, colour… | Nr. ref. LM, EAN, serie, dimensiune, culoare…
Szukaj w bibliotece | Search the library | Caută în bibliotecă
Wyszukiwarka | Search | Căutare
Nawigacja główna | Main navigation | Navigare principală
Menu | Menu | Meniu
Stopka | Footer | Subsol
Schedpol — Strefa projektanta, strona startowa | Schedpol — designer zone, home page | Schedpol — zona designerului, pagina principală
Anna Nowak · projektantka · LM Poznań | Anna Nowak · designer · LM Poznań | Anna Nowak · designer · LM Poznań
Konto: Anna Nowak, projektantka, LM Poznań | Account: Anna Nowak, designer, LM Poznań | Cont: Anna Nowak, designer, LM Poznań
SCHEDPOL Sp. z o.o. · od {n} | SCHEDPOL Sp. z o.o. · since {n} | SCHEDPOL Sp. z o.o. · din {n}
Pełna oferta — schedpol.pl | Full range — schedpol.pl | Oferta completă — schedpol.pl
Dane produktów: oferta Schedpol i Sensea dostępna w Leroy Merlin. Ceny i dostępność: w systemie sklepu. | Product data: Schedpol and Sensea range available at Leroy Merlin. Prices and availability: in the store system. | Date despre produse: oferta Schedpol și Sensea disponibilă la Leroy Merlin. Prețuri și disponibilitate: în sistemul magazinului.
Często szukane | Frequently searched | Căutate frecvent
Produkty | Products | Produse
Serie | Series | Serii
pokaż wszystkie wyniki | show all results | arată toate rezultatele
{n} wynik | {n} result | {n} rezultat
{n} wyniki | {n} results | {n} rezultate
{n} wyników | {n} results | {n} rezultate
Brak wyników dla „{x}” | No results for “{x}” | Niciun rezultat pentru „{x}”
Numer ref. LM ma {n} cyfr. Możesz też wpisać serię i wymiar, np. Balans {n}×{n}. | The LM ref. number has {n} digits. You can also enter a series and size, e.g. Balans {n}×{n}. | Nr. ref. LM are {n} cifre. Poți introduce și seria și dimensiunea, ex. Balans {n}×{n}.
{n} indeks | {n} item | {n} articol
{n} indeksy | {n} items | {n} articole
{n} indeksów | {n} items | {n} articole
Brak plików do pobrania | No files to download | Nu există fișiere de descărcat
Dodano do Plików | Added to Files | Adăugat în Fișiere
Link do karty skopiowany | Page link copied | Linkul paginii a fost copiat
Lista plików wyczyszczona | File list cleared | Lista de fișiere a fost golită
Nie udało się przygotować paczki ZIP | Couldn't prepare the ZIP package | Pachetul ZIP nu a putut fi pregătit
sprawdź połączenie i spróbuj ponownie | check your connection and try again | verifică conexiunea și încearcă din nou
Paczka ZIP gotowa | ZIP package ready | Pachetul ZIP este gata
Skopiowano nr ref. | Ref. no. copied | Nr. ref. copiat
Trwa przygotowanie poprzedniej paczki | The previous package is still being prepared | Pachetul anterior este încă în pregătire
Zaktualizowano w Plikach | Updated in Files | Actualizat în Fișiere
Zaznacz co najmniej jeden plik | Select at least one file | Selectează cel puțin un fișier
Przygotowanie… | Preparing… | Pregătire…
Paczka ma ok. {n} MB ({n} plików). Przygotowanie może potrwać kilka minut. Kontynuować? | The package is about {n} MB ({n} files). Preparing it may take a few minutes. Continue? | Pachetul are cca {n} MB ({n} fișiere). Pregătirea poate dura câteva minute. Continui?
Paczka ma ok. {n} GB ({n} plików). Przygotowanie może potrwać kilka minut. Kontynuować? | The package is about {n} GB ({n} files). Preparing it may take a few minutes. Continue? | Pachetul are cca {n} GB ({n} fișiere). Pregătirea poate dura câteva minute. Continui?
Pobieranie {n} / {n} | Downloading {n} / {n} | Descărcare {n} / {n}
Pakowanie {n}% | Packing {n}% | Împachetare {n}%
W Plikach | In Files | În Fișiere
Dodaj do Plików | Add to Files | Adaugă în Fișiere
Seria {x} — wszystkie pliki | Series {x} — all files | Seria {x} — toate fișierele
Zamknij podgląd | Close preview | Închide previzualizarea
Zamknij | Close | Închide
Z podcięciem na stopy (LED) | With toe recess (LED) | Cu degajare pentru picioare (LED)
Bez podcięcia na stopy | Without toe recess | Fără degajare pentru picioare
z podcięciem na stopy (LED) | with toe recess (LED) | cu degajare pentru picioare (LED)
bez podcięcia na stopy | without toe recess | fără degajare pentru picioare
front + bok × wysokość | front + side × height | față + lateral × înălțime
rozwinięcie panelu × wysokość | panel developed length × height | lungimea desfășurată a panoului × înălțime
wnęka przy posadzce — miejsce na stopy i taśmę LED | recess at floor level — room for feet and an LED strip | degajare la nivelul pardoselii — loc pentru picioare și bandă LED
panele do samej posadzki, bez wnęki | panels down to the floor, no recess | panouri până la pardoseală, fără degajare
Panele do brodzików półokrągłych Grawello, Dante, Go Baby i Dafne. | Panels for Grawello, Dante, Go Baby and Dafne quadrant trays. | Panouri pentru cădițele semirotunde Grawello, Dante, Go Baby și Dafne.
Wykończenie matowe: biały mat i czarny mat. | Matt finish: white matt and black matt. | Finisaj mat: alb mat și negru mat.
Wąski rant o szerokości {n} cm. | Narrow rim, {n} cm wide. | Margine îngustă, lată de {n} cm.
Wzmocnienia rantów. | Reinforced rims. | Margini ranforsate.
Możliwość bezpośredniego oklejenia płytkami. | Can be tiled directly. | Se poate placa direct cu faianță.
Duży format {n} × {n} cm ogranicza liczbę łączeń. | Large {n} × {n} cm format reduces the number of joints. | Formatul mare {n} × {n} cm reduce numărul de îmbinări.
Dwie grubości: {n} cm oraz {n} cm — wariant {n} cm pozwala ukryć instalację. | Two thicknesses: {n} cm and {n} cm — the {n} cm version can conceal pipework. | Două grosimi: {n} cm și {n} cm — varianta de {n} cm permite ascunderea instalației.
Panele można docinać i montować na klej. | Panels can be cut and installed with adhesive. | Panourile pot fi tăiate și montate cu adeziv.
Cztery wykończenia, w tym o strukturze kamienia. | Four finishes, including stone texture. | Patru finisaje, inclusiv cu textură de piatră.
Długości {n}, {n}, {n} i {n} cm. | Lengths {n}, {n}, {n} and {n} cm. | Lungimi {n}, {n}, {n} și {n} cm.
Maskownica {n}w{n}: gładka lub do zabudowy płytkami. | 2-in-1 cover: plain or tile-in. | Capac 2 în 1: neted sau pentru placare cu faianță.
Regulacja położenia w pionie i poziomie. | Vertical and horizontal adjustment. | Reglare pe verticală și orizontală.
Podparcie wanny na całej powierzchni. | Support across the whole bathtub surface. | Sprijin pe toată suprafața căzii.
Łączone elementy pozwalają dopasować nośnik do rozmiaru wanny. | Connectable elements let you fit the support to the bathtub size. | Elementele îmbinabile permit adaptarea suportului la dimensiunea căzii.
Do wanien akrylowych i stalowych. | For acrylic and steel bathtubs. | Pentru căzi acrilice și din oțel.
Montaż z możliwością późniejszego demontażu. | Installation that can be removed later. | Montaj care permite demontarea ulterioară.
Maskownice do brodzików Balans i Integral: złota polerowana, złota szczotkowana i miedziana. | Covers for Balans and Integral trays: polished gold, brushed gold and copper. | Capace pentru cădițele Balans și Integral: auriu lustruit, auriu periat și cupru.
Najazd {n} lub {n} cm ułatwia wejście do brodzika osobom o ograniczonej sprawności ruchowej. | A {n} or {n} cm ramp makes it easier for people with reduced mobility to step into the tray. | Rampa de {n} sau {n} cm facilitează accesul în cădiță persoanelor cu mobilitate redusă.
Zestaw nóg do brodzików Ipsilon: {n} nóżek i {n} kotwy przyścienne. | Leg kit for Ipsilon trays: {n} legs and {n} wall anchors. | Set de picioare pentru cădițele Ipsilon: {n} picioare și {n} ancore de perete.
Nogi do brodzików Ipsilon, zestaw nóg | Legs for Ipsilon trays, leg kit | Picioare pentru cădițele Ipsilon, set de picioare
— inne serie i kolory o tych samych wymiarach boków i kształcie. | — other series and colours with the same side lengths and shape. | — alte serii și culori cu aceleași dimensiuni și formă.
Brodzik podpłytkowy vs Odpływ liniowy - porównanie montażu | Tile-in shower tray vs linear drain — installation comparison | Cădiță sub gresie vs rigolă liniară — comparație de montaj
Montaż odpływu liniowego | SCHEDPOL® | Linear drain installation | SCHEDPOL® | Montajul rigolei liniare | SCHEDPOL®
Montaż odpływu liniowego Schedpol bezkołnierzowego w podłodze – krok po kroku | Installing a flangeless Schedpol linear drain in the floor — step by step | Montajul în pardoseală al rigolei liniare Schedpol fără flanșă — pas cu pas
Montaż brodzika STABILSOUND PLUS® na nośniku z podcięciem panelu | SCHEDPOL® | Installing a STABILSOUND PLUS® tray on a support with panel recess | SCHEDPOL® | Montajul cădiței STABILSOUND PLUS® pe suport cu degajare de panou | SCHEDPOL®
Montaż i docinanie brodzika kompozytowego w technologii STABILSOUND PLUS® | Schedpol | Installing and cutting a composite STABILSOUND PLUS® tray | Schedpol | Montajul și tăierea cădiței compozite STABILSOUND PLUS® | Schedpol
Docinanie brodzika kompozytowego bez bałaganu! Zobacz, jakie to proste! | Cutting a composite tray without the mess — see how it's done | Tăierea cădiței compozite fără mizerie — vezi cum se face
Brodzik Sensea Ipsilon — montaż | Sensea Ipsilon shower tray — installation | Cădiță de duș Sensea Ipsilon — montaj
Metamorfoza łazienki w {n}h z systemem Wall comfort Schedpol | Bathroom makeover in {n}h with the Schedpol Wall Comfort system | Renovarea băii în {n}h cu sistemul Schedpol Wall Comfort
Metamorfoza łazienki w {n}h z systemem Wall comfort Schedpol + Łazienki dla seniora. | Bathroom makeover in {n}h with the Schedpol Wall Comfort system + bathrooms for seniors | Renovarea băii în {n}h cu sistemul Schedpol Wall Comfort + băi pentru seniori
Prosta i szybka wymiana wanny na prysznic ze ściankami remontowymi WALL COMFORT | Schedpol® | Quick and simple bath-to-shower replacement with WALL COMFORT renovation panels | Schedpol® | Înlocuire simplă și rapidă a căzii cu duș cu panourile de renovare WALL COMFORT | Schedpol®
Prosty montaż nośnika do wanien prostokątnych | SCHEDPOL® | Easy installation of a support for rectangular bathtubs | SCHEDPOL® | Montaj simplu al suportului pentru căzi dreptunghiulare | SCHEDPOL®
Nośnik stabilizujący - trwała zabudowa wanien prostokątnych | Stabilising support — durable enclosure for rectangular bathtubs | Suport stabilizator — închidere durabilă pentru căzi dreptunghiulare
Jak bardzo wytrzymały jest Nośnik do wanien kąpielowych? Szybki test! | How strong is the bathtub support? A quick test | Cât de rezistent este suportul pentru căzi? Un test rapid
Nośnik uniwersalny do wanien prostokątnych akrylowych i stalowych | Universal support for rectangular acrylic and steel bathtubs | Suport universal pentru căzi dreptunghiulare acrilice și din oțel
Nośnik uniwersalny do wanien półokrągłych | Schedpol® | Universal support for corner bathtubs | Schedpol® | Suport universal pentru căzi de colț | Schedpol®
Obudowa uniwersalna do wanien Schedpol - łatwy i szybki montaż! | Schedpol universal bath panel — quick and easy installation | Panou universal de cadă Schedpol — montaj rapid și ușor
Prosty montaż obudowy do wanien | SCHEDPOL® | Easy bath panel installation | SCHEDPOL® | Montaj simplu al panoului de cadă | SCHEDPOL®
Najazd do brodzików podpłytkowych przeznaczony do zabudowy płytkami - montaż | Ramp for tile-in shower trays, for tiling — installation | Rampă pentru cădițe sub gresie, pentru placare — montaj
STABILNE BRODZIKI WYSOKIE – DOCINANE NA WYMIAR! ŁATWY MONTAŻ BEZ PODKUWANIA - SCHEDPOL | Stable high shower trays — cut to size, easy installation without chiselling — Schedpol | Cădițe înalte stabile — tăiate pe dimensiune, montaj ușor fără spargere — Schedpol
Brodziki w technologii STABILSOUND® - cechy innowacyjnego brodzika. | Schedpol | STABILSOUND® shower trays — features of an innovative tray | Schedpol | Cădițe în tehnologia STABILSOUND® — caracteristicile unei cădițe inovatoare | Schedpol
Brodziki kompozytowe do nowoczesnych łazienek | SCHEDPOL® | Stabilsound Plus® | Composite shower trays for modern bathrooms | SCHEDPOL® | Stabilsound Plus® | Cădițe compozite pentru băi moderne | SCHEDPOL® | Stabilsound Plus®
Zestaw naprawczy powierzchni brodzików i wanien Schedpol | Schedpol repair kit for shower tray and bathtub surfaces | Kit de reparație Schedpol pentru suprafețele cădițelor și căzilor
Jaki brodzik wybrać do łazienki marzeń? Poradnik | Which shower tray for your dream bathroom? A guide | Ce cădiță să alegi pentru baia visurilor? Ghid
Schedpol - Poznaj nas! | Schedpol — meet us | Schedpol — cunoaște-ne
SCHEDPOL FIRMA {n} | SCHEDPOL COMPANY {n} | COMPANIA SCHEDPOL {n}
Maskownica do brodzików Balans / Integral | Drain cover for Balans / Integral trays | Capac de scurgere pentru cădițele Balans / Integral
Nogi do brodzików Ipsilon | Legs for Ipsilon trays | Picioare pentru cădițele Ipsilon
Nośnik uniwersalny do wanien | Universal bathtub support | Suport universal pentru căzi
Obudowa podpłytkowa do wanien prostokątnych | Tileable panel for rectangular bathtubs | Panou pentru placare pentru căzi dreptunghiulare
Obudowa podpłytkowa do wanien półokrągłych | Tileable panel for corner bathtubs | Panou pentru placare pentru căzi de colț
Usuń filtr | Remove filter | Elimină filtrul
Kopiuj link | Copy link | Copiază linkul
Link do listy plików skopiowany | File list link copied | Linkul listei de fișiere a fost copiat
Skopiuj link do listy plików: | Copy the file list link: | Copiază linkul listei de fișiere:
Skopiuj link do karty produktu: | Copy the product page link: | Copiază linkul paginii produsului:
Minimum logistyczne | Logistics minimum | Minim logistic
Dropshipping od {n} produktu | Dropshipping from {n} product | Dropshipping de la {n} produs
Produkty możliwe do dobrania | Matching products | Produse compatibile
Produkty z oferty w Leroy Merlin, które można dobrać do tej serii w projekcie. | Products from the Leroy Merlin range that can be combined with this series in a project. | Produse din oferta Leroy Merlin care pot fi combinate cu această serie în proiect.
Strefa prysznica | Shower area | Zona de duș
Wielkoformatowy panel {n} × {n} cm w grubości {n} lub {n} cm. Montaż na klej, bez skuwania płytek. | Large-format {n} × {n} cm panel, {n} or {n} cm thick. Installed with adhesive, without removing tiles. | Panou de format mare {n} × {n} cm, grosime {n} sau {n} cm. Montaj cu adeziv, fără spargerea faianței.
Podparcie wanny | Bathtub support | Sprijinirea căzii
Zabudowa wanny | Bathtub enclosure | Închiderea căzii
Komplet plików do projektu: {x}. Każdy plik można obejrzeć przed pobraniem. | Complete project file set: {x}. Every file can be previewed before downloading. | Set complet de fișiere pentru proiect: {x}. Fiecare fișier poate fi previzualizat înainte de descărcare.
Balans {n}×{n} | Balans {n}×{n} | Balans {n}×{n}
odpływ {n} | drain {n} | scurgere {n}
Seria {x} | Series {x} | Seria {x}
Enter | Enter | Enter
Czarny mat · LM {n} | Black matt · LM {n} | Negru mat · LM {n}
Model {n}D · przeciągnij, aby obrócić; kółko myszy przybliża | 3D model · drag to rotate; scroll to zoom | Model 3D · trage pentru a roti; rotița mouse-ului mărește
Podgląd {n}D — przeciągnij, aby obrócić; kółko myszy przybliża | 3D preview — drag to rotate; scroll to zoom | Previzualizare 3D — trage pentru a roti; rotița mouse-ului mărește
Podgląd rysunku — plik DWG zawiera ten sam widok w wektorze | Drawing preview — the DWG file contains the same view as vectors | Previzualizarea desenului — fișierul DWG conține aceeași vedere vectorială
Rysunek w przygotowaniu — podgląd produktu | Drawing in preparation — product preview | Desen în pregătire — previzualizare produs
Seria {x} — wszystkie pliki | Series {x} — all files | Seria {x} — toate fișierele
Obudowa podpłytkowa do wanien prostokątnych i półokrągłych, do oklejenia płytkami. Dwie wersje: z podcięciem na stopy (wnęka przy posadzce, miejsce na taśmę LED) albo bez podcięcia — panele do samej posadzki. | Tileable panel for rectangular and corner bathtubs. Two versions: with a toe recess (recess at floor level, room for an LED strip) or without — panels down to the floor. | Panou pentru placare pentru căzi dreptunghiulare și de colț. Două versiuni: cu degajare pentru picioare (la nivelul pardoselii, loc pentru bandă LED) sau fără — panouri până la pardoseală.
"""

PHRASES = r"""
Brodzik głęboki zintegrowany | Deep integrated shower tray | Cădiță de duș adâncă integrată
Brodzik głęboki laminowany | Deep laminated shower tray | Cădiță de duș adâncă laminată
brodzik głęboki zintegrowany | deep integrated shower tray | cădiță de duș adâncă integrată
brodzik głęboki laminowany | deep laminated shower tray | cădiță de duș adâncă laminată
Brodzik kompozytowy | Composite shower tray | Cădiță de duș compozită
Brodzik zintegrowany | Integrated shower tray | Cădiță de duș integrată
Brodzik laminowany | Laminated shower tray | Cădiță de duș laminată
brodzik kompozytowy | composite shower tray | cădiță de duș compozită
brodzik zintegrowany | integrated shower tray | cădiță de duș integrată
brodzik laminowany | laminated shower tray | cădiță de duș laminată
Wanna laminowana | Laminated bathtub | Cadă laminată
wanna laminowana | laminated bathtub | cadă laminată
Odpływ liniowy | Linear drain | Rigolă liniară
odpływ liniowy | linear drain | rigolă liniară
Odpływy liniowe | Linear drains | Rigole liniare
Dekoracyjny panel ścienny | Decorative wall panel | Panou de perete decorativ
dekoracyjny panel ścienny | decorative wall panel | panou de perete decorativ
Panele ścienne | Wall panels | Panouri de perete
Panel do brodzika głębokiego | Panel for deep shower tray | Panou pentru cădiță adâncă
Panele do brodzików | Shower tray panels | Panouri pentru cădițe
Panel do brodzika | Panel for shower tray | Panou pentru cădița
Nośnik EPS do wanien | EPS bathtub support | Suport EPS pentru căzi
Nośniki | Supports | Suporturi
Nośnik | Support | Suport
Obudowy wanien | Bath panels | Panouri de cadă
Obudowa do wanien | Bath panel | Panou de cadă
Obudowa uniwersalna | Universal bath panel | Panou de cadă universal
Najazd do brodzików | Shower tray ramp | Rampă pentru cădițe
Najazd | Ramp | Rampă
Maskownica odpływu | Drain cover | Capac de scurgere
Maskownica | Cover | Capac
Zestaw nóg | Leg kit | Set de picioare
Nogi Ipsilon | Ipsilon legs | Picioare Ipsilon
Akcesoria | Accessories | Accesorii
Brodziki | Shower trays | Cădițe de duș
Wanny | Bathtubs | Căzi
Cechy serii | Series features | Caracteristicile seriei
biały kamień | white stone | piatră albă
czarny kamień | black stone | piatră neagră
szary kamień | grey stone | piatră gri
kaszmirowy kamień | cashmere stone | piatră cașmir
cementowy kamień | cement stone | piatră ciment
biały gładki | smooth white | alb neted
biały mat | white matt | alb mat
czarny mat | black matt | negru mat
złota polerowana | polished gold | auriu lustruit
złota szczotkowana | brushed gold | auriu periat
miedziana | copper | cupru
Biały kamień | White stone | Piatră albă
Czarny kamień | Black stone | Piatră neagră
Szary kamień | Grey stone | Piatră gri
Kaszmirowy kamień | Cashmere stone | Piatră cașmir
Cementowy kamień | Cement stone | Piatră ciment
Biały gładki | Smooth white | Alb neted
Biały mat | White matt | Alb mat
Czarny mat | Black matt | Negru mat
Złota polerowana | Polished gold | Auriu lustruit
Złota szczotkowana | Brushed gold | Auriu periat
Miedziana | Copper | Cupru
Stal | Steel | Oțel
stal | steel | oțel
Czarny | Black | Negru
czarny | black | negru
kwadratowy | square | pătrată
prostokątny | rectangular | dreptunghiulară
półokrągły | quadrant | semirotundă
pięciokątny | pentagonal | pentagonală
Kwadratowy | Square | Pătrată
Prostokątny | Rectangular | Dreptunghiulară
Półokrągły | Quadrant | Semirotundă
Pięciokątny | Pentagonal | Pentagonală
półokr. | quadrant | semirot.
pięciok. | pentagonal | pentag.
laminowany | laminated | laminat
laminowana | laminated | laminată
kompozytowy | composite | compozit
zintegrowany | integrated | integrat
Smooth White | Smooth White | Smooth White
Marka | Brand | Marcă
seria | series | seria
packshoty | packshots | packshot-uri
modele 3d | 3D models | modele 3D
rysunki techniczne | technical drawings | desene tehnice
aranżacje | room settings | amenajări
przekroje i infografiki | cross-sections and infographics | secțiuni și infografice
karty produktów | product sheets | fișe de produs
Panel | Panel | Panou
, półokrągły | , quadrant | , semirotundă
Leroy Merlin | Leroy Merlin | Leroy Merlin
wymiary w cm | dimensions in cm | dimensiuni în cm
wymiary w mm | dimensions in mm | dimensiuni în mm
w archiwum ZIP | in a ZIP archive | în arhivă ZIP
"""


def rows(block):
    out = []
    for ln in block.strip().splitlines():
        if not ln.strip(): continue
        p = [x.strip() for x in ln.split(' | ')]
        if len(p) != 3:                                 # teksty z „ | ” w środku (tytuły filmów): podział na trzy równe części
            n = len(p) // 3
            if len(p) % 3: raise SystemExit('Zły wiersz: ' + ln)
            p = [' | '.join(p[:n]), ' | '.join(p[n:2 * n]), ' | '.join(p[2 * n:])]
        out.append(p)
    return out


def norm_key(s):
    import re
    return re.sub(r'\d+(?:[  ]\d{3})*(?:[.,]\d+)?', '{n}', s) if '{n}' not in s and '{x}' not in s and '{d}' not in s else s


ex, ph = rows(EXACT), rows(PHRASES)
for li, lang in ((1, 'en'), (2, 'ro')):
    exact = {}
    for r in ex:
        v = r[li]
        # liczby z klucza muszą trafić na swoje miejsca: „{n}D” (3D) i „A{n}” (A4) zostają jako wzorzec w tłumaczeniu
        if '{n}D' in r[0] and '{n}D' not in v and '3D' in v: v = v.replace('3D', '{n}D', 1)
        if 'A{n}' in r[0] and 'A{n}' not in v and 'A4' in v: v = v.replace('A4', 'A{n}', 1)
        exact[r[0]] = v
    js = ('/* Wygenerowano (_narzedzia/18_slownik.py): słownik %s portalu — tłumaczenie AI, 25.11.2026. Silnik: assets/i18n.js */\n'
          'window.I18N = ' % lang.upper() + json.dumps({'lang': lang, 'exact': exact, 'phrases': [[r[0], r[li]] for r in ph]}, ensure_ascii=False, indent=0) + ';\n')
    io.open(os.path.join(A, 'i18n-%s.js' % lang), 'w', encoding='utf-8').write(js)
print('wpisów dokładnych:', len(ex), ' fraz:', len(ph))
