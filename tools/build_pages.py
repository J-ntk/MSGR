#!/usr/bin/env python3
"""Generates all static MSGR pages (RU + UA + KZ) with a shared header/footer.
Editable content (packages, FAQ, calendar, universities, articles) lives in content/*.json —
that is what the admin panel edits. Everything else is in this file.
Run:  python tools/build_pages.py   (regenerates all pages, RU + UA + KZ)
GitHub Pages build:  MSGR_OUT=docs MSGR_BASE=/MSGR python tools/build_pages.py
Translations of the fixed texts: tools/i18n/uk.tsv and kk.tsv."""
import os, json, html as _html

_HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.environ.get("MSGR_CONTENT") or next(
    (d for d in (os.path.join(_HERE, "content"), os.path.join(_HERE, "..", "content")) if os.path.isdir(d)), "content")


def _cload(name):
    return json.load(open(os.path.join(CONTENT, name), encoding="utf-8"))


# ---- localized values from content/*.json: {"ru": ..., "uk": ..., "kk": ...} ----
EXTRA = {"uk": {}, "kk": {}}  # RU text -> translation, merged into the page translator


def L(v):
    """Return the Russian text and remember its UA/KZ versions for the translated pages."""
    if v is None or isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        return v
    esc = lambda x: _html.escape((x or "").strip(), quote=False)  # plain text from the admin panel is never HTML
    ru = esc(v.get("ru"))
    for c in ("uk", "kk"):
        t = esc(v.get(c))
        if ru and t and t != ru:
            EXTRA[c][ru] = t
    return ru


TPL = {  # sentence templates with numbers/names inside
    "since": {"ru": "с {n} г.", "uk": "з {n} р.", "kk": "{n} жылдан"},
    "limits": {"ru": "До {w} письменных обращений в месяц и {h} ч. связи",
               "uk": "До {w} письмових звернень на місяць і {h} год зв’язку",
               "kk": "Айына {w} жазбаша өтінішке дейін және {h} сағ байланыс"},
    "readmeta": {"ru": "· {n} мин чтения", "uk": "· {n} хв читання", "kk": "· оқуға {n} мин"},
    "pill": {"ru": "Статья · {n} мин", "uk": "Стаття · {n} хв", "kk": "Мақала · {n} мин"},
    "choose": {"ru": "Выбрать «{x}»", "uk": "Обрати «{x}»", "kk": "«{x}» пакетін таңдау"},
}


def T(key, **kw):
    """Fill a template in all languages; values may themselves be localized dicts."""
    out = {}
    for c in ("ru", "uk", "kk"):
        vals = {k: (v.get(c) or v.get("ru")) if isinstance(v, dict) else v for k, v in kw.items()}
        out[c] = TPL[key][c].format(**vals)
    return L(out)


BODIES = {}  # marker -> {"ru": html, "uk": html, "kk": html} (rich text inserted after translation)


def rich(key, v):
    BODIES[key] = v
    return f"<!--LOC:{key}-->"

OUT = os.environ.get("MSGR_OUT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
BASE = os.environ.get("MSGR_BASE", "").rstrip("/")  # e.g. "/MSGR" for GitHub Pages project sites
SITE = "https://mystudygr.com"
SERV = "/%d1%83%d1%81%d0%bb%d1%83%d0%b3%d0%b8/"  # /услуги/ — exact existing URL
NAV = [("home", "/", "Главная"), ("about", "/about-us/", "О нас"), ("learning", "/learning/", "Образование"),
       ("universities", "/universities/", "Университеты"),
       ("services", SERV, "Услуги"), ("faq", "/faq/", "Вопросы"), ("contacts", "/contacts/", "Контакты")]
USEFUL = [("/quiz/", "Проверить шансы"), ("/calendar/", "Календарь поступления"), ("/universities/", "Университеты Греции"),
          ("/faq/", "Вопросы и ответы"), ("/blog/", "Статьи")]

PHONE_HREF = "tel:+306942770701"
PHONE = "+30 694 277 07 01"
EMAIL = "mystudygr1@gmail.com"
WA = "https://wa.me/306942770701"
VIBER = "viber://chat/?number=306942770701"
TG = "https://t.me/Igor_Toikin"
FB = "https://facebook.com/groups/852853695726219/?ref=share"
IG_HEADER = "https://www.instagram.com/_mystudygr_?igsh=MXByd2FlMWNlNXJmOQ%3D%3D"
IG_CONTACT = IG_HEADER  # the only correct account: _mystudygr_
HOURS = "ПН–ПТ, 08:00 – 20:00"

ICON = {
 "lang": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 5h9M8.5 3v2M6 5c0 4 3 7 6 8M11 5c0 3-3 7-6 8"/><path d="M13 21l4-10 4 10M14.5 17h5"/></svg>',
 "exam": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 3h6l1 4H8z"/><rect x="5" y="7" width="14" height="14" rx="2"/><path d="M9 14l2 2 4-4"/></svg>',
 "grad": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 9l9-5 9 5-9 5z"/><path d="M7 11v5c0 1.5 2.2 3 5 3s5-1.5 5-3v-5M21 9v6"/></svg>',
 "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/><path d="M9 12l2 2 4-4"/></svg>',
 "heart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.8 5.6a5 5 0 0 0-7.1 0L12 7.3l-1.7-1.7a5 5 0 0 0-7.1 7.1L12 21.5l8.8-8.8a5 5 0 0 0 0-7.1z"/></svg>',
 "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
 "home": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/></svg>',
 "coin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M15 9.5c-.6-1-1.7-1.5-3-1.5-1.7 0-3 .9-3 2.2 0 3 6 1.6 6 4.6 0 1.3-1.3 2.2-3 2.2-1.3 0-2.4-.5-3-1.5M12 6v2M12 16v2"/></svg>',
 "globe": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z"/></svg>',
 "users": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.8-3.5 3.4-5.5 6.5-5.5s5.7 2 6.5 5.5"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14.8c2 .7 3.2 2.5 3.6 5.2"/></svg>',
 "book": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5M8 7h7"/></svg>',
 "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
 "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
 "burger": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
}

import math



def _svg(P, label):
    paths = "".join(f'<path class="ha-{c}" d="{d}" pathLength="1"/>' for d, c in P)
    return (f'<svg class="hero__art" data-art="{label}" viewBox="-10 0 620 400" aria-hidden="true" '
            f'focusable="false" preserveAspectRatio="xMaxYMax meet">{paths}</svg>')


def _cypress(P, cx, base=392, h=110):
    top = base - h
    P.append((f"M{cx} {base}V{base-18}M{cx} {base-18}c-14-20-12-{h-30} 0-{h-18}c12 {h-30} 14 {h-38} 0 {h-18}", "t"))


def _olive(P, x0=6, y0=380):
    P.append((f"M{x0} {y0}c40-20 70-28 110-30", "t"))
    for k in range(5):
        x = x0 + 16 + k * 20
        y = y0 - 8 - k * 4
        P.append((f"M{x} {y}c4-10 12-14 20-14c-2 8-10 14-20 14z", "t"))


# 1. HOME — temple (Parthenon-style octastyle)
def temple():
    P = [("M0 392H600", "g")]
    for x, y, w, h in [(40, 372, 520, 20), (56, 356, 488, 16), (72, 342, 456, 14)]:
        P.append((f"M{x} {y}h{w}v{h}h-{w}z", "s"))
    for i in range(8):
        x = 96 + i * 54
        P += [(f"M{x+2} 336L{x+5} 150H{x+25}L{x+28} 336", "c"),
              (f"M{x+11} 334L{x+12} 152M{x+19} 334L{x+18} 152", "f"),
              (f"M{x-3} 342v-6h36v6", "c"),
              (f"M{x+3} 150c0-5 4-8 12-8s12 3 12 8", "c"),
              (f"M{x-4} 142h38v-6h-38z", "c")]
    P += [("M80 136h440v-24H80z", "e"), ("M80 112h440V84H80z", "e")]
    for i in range(17):
        x = 92 + i * 25.5
        P.append((f"M{x:.1f} 88v20M{x+4:.1f} 88v20M{x+8:.1f} 88v20", "f"))
    P += [("M70 84h460v-6H70z", "e"), ("M70 78L300 18L530 78", "p"), ("M104 72L300 30L496 72z", "p"),
          ("M300 18v-12M294 10h12M70 78l-6-10M530 78l6-10", "f"),
          ("M282 58c6-10 30-10 36 0M286 62c5 6 23 6 28 0", "f")]
    _cypress(P, 18, h=118); _cypress(P, 582, h=118); _olive(P)
    return _svg(P, "temple")


# 2. ABOUT — Caryatid porch (Erechtheion-style)
def caryatids():
    P = [("M0 392H600", "g")]
    # main building wall behind, right side, with ashlar courses
    P.append(("M506 392V96H600", "s"))
    for y in range(120, 392, 24):
        P.append((f"M506 {y}H600", "f"))
    for i, y in enumerate(range(120, 392, 24)):
        off = 16 if i % 2 else 48
        for x in range(506 + off, 600, 64):
            P.append((f"M{x} {y}v24", "f"))
    # tall window in the wall
    P.append(("M534 300V172h40v128zM528 172h52l-26-20z", "e"))
    # podium of the porch
    P.append(("M150 392V342H490V392", "s"))
    for y in (356, 370, 384):
        P.append((f"M150 {y}H490", "f"))
    P.append(("M142 342h356v-8H142z", "s"))
    # four maidens
    for cx in (200, 280, 360, 440):
        P += [
            (f"M{cx-18} 334h36v-10h-36z", "c"),                                       # plinth
            (f"M{cx-14} 200C{cx-17} 240 {cx-20} 290 {cx-17} 324H{cx+17}C{cx+20} 290 {cx+17} 240 {cx+14} 200", "c"),  # dress
            (f"M{cx-14} 200Q{cx} 192 {cx+14} 200", "c"),                              # shoulders
            (f"M{cx-8} 214C{cx-9} 260 {cx-10} 296 {cx-9} 322M{cx} 210V322M{cx+8} 214C{cx+12} 250 {cx+5} 284 {cx+10} 322", "f"),  # folds
            (f"M{cx+3} 262c6 8 8 20 7 30", "f"),                                       # bent knee
            (f"M{cx-14} 202c-5 22-5 44-2 64", "c"),                                    # arm
            (f"M{cx-4} 186v8M{cx+4} 186v8", "c"),                                      # neck
            (f"M{cx-10} 176a10 11 0 1 0 20 0a10 11 0 1 0-20 0", "c"),                  # head
            (f"M{cx-10} 180c-2 10-2 16-5 24M{cx+10} 180c2 10 2 16 5 24", "f"),         # braids
            (f"M{cx-12} 165h24l5-9h-34z", "c"),                                        # basket capital
            (f"M{cx-20} 156h40v-6h-40z", "c"),                                         # abacus
        ]
    # entablature over the porch
    P += [("M150 150h340v-22H150z", "e"), ("M150 128h340v-10H150z", "e")]
    for x in range(156, 490, 12):
        P.append((f"M{x} 118v-8h6v8", "f"))                                              # dentils
    P += [("M140 110h360v-8H140z", "p"), ("M140 102h330", "p")]
    _olive(P); _cypress(P, 70, h=150)
    return _svg(P, "caryatids")


# 3. EDUCATION — two-storey ancient library (Celsus-style)
def library():
    P = [("M0 392H600", "g")]
    for x, y, w, h in [(90, 378, 480, 14), (104, 366, 452, 12), (118, 356, 424, 10)]:
        P.append((f"M{x} {y}h{w}v{h}h-{w}z", "s"))
    pairs = (170, 270, 390, 490)
    doors = ((220, 18), (330, 26), (440, 18))
    # back wall
    P.append(("M130 356V96H530V356", "f"))
    # lower doors
    for cx, r in doors:
        P.append((f"M{cx-r} 356V{290-r}a{r} {r} 0 0 1 {2*r} 0V356", "e"))
        P.append((f"M{cx-r-6} {290-r}h{2*r+12}", "f"))
    # lower columns (pairs) with podiums
    for c in pairs:
        P.append((f"M{c-24} 356v-14h48v14", "s"))
        for x in (c - 13, c + 5):
            P += [(f"M{x} 342V236h8V342", "c"), (f"M{x-3} 236h14v-6h-14z", "c")]
    # lower entablature, projecting over pairs
    P.append(("M134 230h392v-18H134z", "e"))
    for c in pairs:
        P.append((f"M{c-28} 212h56v-8h-56z", "e"))
    # upper windows / niches
    for cx, r in doors:
        w = 14 if r < 20 else 18
        P.append((f"M{cx-w} 196V146h{2*w}v50", "e"))
        P.append((f"M{cx-w-6} 146L{cx} 128L{cx+w+6} 146", "p") if r > 20 else (f"M{cx-w-6} 146h{2*w+12}", "f"))
        # a small statue in each niche
        P.append((f"M{cx-5} 192c-1-14 0-24 5-30c5 6 6 16 5 30M{cx-4} 158a4 4 0 1 0 8 0a4 4 0 1 0-8 0", "f"))
    # upper columns (pairs)
    for c in pairs:
        for x in (c - 11, c + 5):
            P += [(f"M{x} 204V126h6V204", "c"), (f"M{x-2} 126h10v-5h-10z", "c")]
    # upper entablature + crowning
    P += [("M134 121h392v-14H134z", "e"), ("M128 107h404v-6H128z", "p"),
          ("M146 101L170 84L194 101M466 101L490 84L514 101", "p"),
          ("M246 101Q330 52 414 101", "p")]
    # open scroll, lower left
    P += [("M10 372c20-8 50-8 74 0", "t"), ("M10 372c-6-4-6-12 0-14c20-8 50-8 74 0c6 2 6 10 0 14", "t"),
          ("M22 362h48M24 366h42", "f")]
    _cypress(P, 584, h=150)
    return _svg(P, "library")


# 4. SERVICES — stoa (two-storey colonnade of the agora)
def stoa():
    P = [("M0 392H600", "g")]
    P += [("M10 392v-10h590v10", "s"), ("M18 382v-10h574v10", "s")]
    xs = list(range(40, 580, 40))
    # back wall with shop doorways
    P.append(("M28 372V244H582V372", "f"))
    for i, x in enumerate(xs[:-1]):
        if i % 2 == 0:
            P.append((f"M{x+12} 372V318h16v54", "f"))
    # lower Doric columns
    for x in xs:
        P += [(f"M{x-6} 372L{x-5} 252H{x+5}L{x+6} 372", "c"), (f"M{x-9} 252h18v-6h-18z", "c")]
    # first-floor slab + balustrade
    P += [("M24 246h562v-16H24z", "e"), ("M28 230V214H582V230", "f")]
    for x in range(36, 580, 10):
        P.append((f"M{x} 228v-12", "f"))
    # upper Ionic columns
    for x in xs:
        P += [(f"M{x-4} 214V160h8V214", "c"), (f"M{x-8} 160c0-4 4-4 4 0M{x+8} 160c0-4-4-4-4 0M{x-8} 160h16", "c")]
    # roof
    P += [("M20 160h570v-12H20z", "e"), ("M12 148L305 116L598 148", "p"), ("M14 148h582", "p")]
    for x in range(40, 580, 28):
        P.append((f"M{x} 152v-4", "f"))
    # amphora on a pedestal, front left
    P += [("M0 392v-20h26v20", "s"),
          ("M7 372c-6-6-6-20 0-30c-2-4-2-8 0-10h12c2 2 2 6 0 10c6 10 6 24 0 30zM6 334c-6 0-6-8 0-8M20 334c6 0 6-8 0-8", "t")]
    _cypress(P, 600, h=128)
    return _svg(P, "stoa")


# 5. CONTACTS — amphitheatre (Epidaurus-style)
def theatre():
    P = []
    # hills behind
    P.append(("M-10 214C60 190 120 200 190 182S330 170 400 186S520 176 610 196", "f"))
    cx, cy = 300, 356
    radii = list(range(86, 290, 17))
    for i, rx in enumerate(radii):
        ry = rx * 0.44
        cls = "p" if i in (0, 7, len(radii) - 1) else ("c" if i % 2 == 0 else "f")
        P.append((f"M{cx-rx} {cy}A{rx} {ry:.1f} 0 0 1 {cx+rx} {cy}", cls))
    # radial aisles (stairs)
    for ang in (18, 40, 62, 90, 118, 140, 162):
        a = math.radians(ang)
        r0, r1 = radii[0], radii[-1]
        x0, y0 = cx + r0 * math.cos(a), cy - r0 * 0.44 * math.sin(a)
        x1, y1 = cx + r1 * math.cos(a), cy - r1 * 0.44 * math.sin(a)
        P.append((f"M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}", "e"))
    # orchestra (circular stage floor) and altar
    P.append((f"M{cx-70} 368a70 24 0 1 0 140 0a70 24 0 1 0-140 0", "s"))
    P.append((f"M{cx-6} 368a6 3 0 1 0 12 0a6 3 0 1 0-12 0", "f"))
    # skene (stage building) in front
    P += [("M150 392v-16h300v16", "s"), ("M150 376h300", "e"), ("M140 392H460", "g")]
    for x in range(166, 450, 24):
        P.append((f"M{x} 392v-14", "f"))
    _cypress(P, -2, h=150); _cypress(P, 602, h=150)
    return _svg(P, "theatre")


ARTS = {"home": temple, "about": caryatids, "learning": library, "services": stoa, "contacts": theatre}


# ---- Extra hero illustrations for the new pages ----
def academy():
    """Universities — Academy of Athens style: temple front flanked by two tall
    columns topped with statues (Athena & Apollo)."""
    P = [("M0 392H600", "g")]
    for x, y, w, h in [(150, 378, 320, 14), (162, 366, 296, 12)]:
        P.append((f"M{x} {y}h{w}v{h}h-{w}z", "s"))
    # central Ionic portico, 6 columns
    for i in range(6):
        x = 190 + i * 46
        P += [(f"M{x} 366V196h14V366", "c"), (f"M{x+5} 362V200M{x+9} 362V200", "f"),
              (f"M{x-6} 196c0-6 6-6 6 0M{x+20} 196c0-6-6-6-6 0M{x-6} 196h26", "c")]
    P += [("M178 190h264v-18H178z", "e"), ("M172 172h276v-8H172z", "e"),
          ("M172 164L310 112L448 164", "p"), ("M200 158L310 122L420 158z", "p"),
          ("M296 150c4-8 24-8 28 0", "f")]
    # two tall free-standing columns with statues
    for cx, spear in ((90, True), (530, False)):
        P += [(f"M{cx-22} 392v-22h44v22", "s"), (f"M{cx-14} 370V150h28v220", "c"),
              (f"M{cx-5} 366V154M{cx+5} 366V154", "f"),
              (f"M{cx-20} 150c0-8 8-8 8 0M{cx+20} 150c0-8-8-8-8 0M{cx-20} 150h40v-8h-40z", "c"),
              # statue: draped standing figure
              (f"M{cx-10} 142c-2-22 0-40 4-52h12c4 12 6 30 4 52z", "c"),
              (f"M{cx-6} 84a6 7 0 1 0 12 0a6 7 0 1 0-12 0", "c"),
              (f"M{cx-3} 140c0-14 1-28 3-40M{cx+4} 140c0-12-1-24-2-36", "f")]
        if spear:
            P += [(f"M{cx+16} 142V62M{cx+12} 66l4-8l4 8", "c"), (f"M{cx-20} 120a10 12 0 1 0 0.1 0", "f")]  # spear + shield
        else:
            P += [(f"M{cx-18} 112c-8-6-8-22 0-26c4 4 4 22 0 26M{cx-22} 92v14", "c")]  # lyre
    _cypress(P, 20, h=120)
    return _svg(P, "academy")


def owl():
    """FAQ — owl of Athena (symbol of wisdom) standing on an Ionic capital."""
    P = [("M0 392H600", "g")]
    cx = 430
    P += [(f"M{cx-60} 392v-16h120v16", "s"), (f"M{cx-46} 376V214h92v162", "c"),
          (f"M{cx-30} 372V218M{cx-10} 372V218M{cx+10} 372V218M{cx+30} 372V218", "f"),
          (f"M{cx-70} 214c0-16 22-16 22 0M{cx+70} 214c0-16-22-16-22 0M{cx-70} 214h140", "c"),
          (f"M{cx-60} 208c0-8 10-8 10 0M{cx+60} 208c0-8-10-8-10 0", "f"),
          (f"M{cx-72} 200h144v-8h-144z", "e")]
    # owl body
    P += [(f"M{cx-34} 192c-10-30-8-70 6-92c6-8 22-8 28 0c14 22 16 62 6 92z", "c"),
          (f"M{cx-26} 108l-6-20l18 12M{cx+26} 108l6-20l-18 12", "c"),           # ear tufts
          (f"M{cx-24} 120a12 12 0 1 0 22 0a12 12 0 1 0-22 0M{cx+2} 120a12 12 0 1 0 22 0a12 12 0 1 0-22 0", "c"),  # eyes
          (f"M{cx-14} 120a3 3 0 1 0 4 0M{cx+12} 120a3 3 0 1 0 4 0", "f"),
          (f"M{cx-4} 132l4 8l4-8", "c"),                                          # beak
          (f"M{cx-20} 150c6 4 34 4 40 0M{cx-22} 164c8 4 36 4 44 0M{cx-20} 178c8 4 32 4 40 0", "f"),  # feathers
          (f"M{cx-34} 150c-10 16-10 32 0 42M{cx+34} 150c10 16 10 32 0 42", "c"),  # wings
          (f"M{cx-14} 192v8M{cx-6} 192v8M{cx+6} 192v8M{cx+14} 192v8", "c")]      # talons
    # olive branch in the beak area / left, plus a small temple far left
    _olive(P, x0=262, y0=214)
    for i in range(4):
        x = 70 + i * 34
        P.append((f"M{x} 392V300h10v92", "f"))
    P += [("M60 300h140v-10H60z", "f"), ("M56 290L130 262L204 290", "f")]
    _cypress(P, 590, h=130)
    return _svg(P, "owl")


def tower():
    """Calendar — Tower of the Winds (ancient Athenian clock tower)."""
    P = [("M0 392H600", "g")]
    cx = 400
    P += [(f"M{cx-110} 392v-14h220v14", "s"),
          (f"M{cx-80} 378V170h160v208", "c"),                 # front face
          (f"M{cx-80} 378l-34-12V178l34-8M{cx+80} 378l34-12V178l-34-8", "c"),  # side faces (octagon)
          (f"M{cx-80} 170h160l-14-14h-132z", "e"),
          (f"M{cx-94} 156L{cx} 92L{cx+94} 156", "p"), (f"M{cx} 92v-14", "p"),
          (f"M{cx-6} 74l12 0l-6-10z", "f")]                   # weather vane (Triton)
    # frieze with wind figures (simplified flowing shapes)
    P.append((f"M{cx-80} 196h160M{cx-80} 214h160", "f"))
    for i in range(4):
        x = cx - 70 + i * 40
        P.append((f"M{x} 210c6-10 14-12 24-10c-6 4-8 8-16 10", "f"))
    # sundial lines on the front
    P.append((f"M{cx} 246v-22M{cx} 246l-30-16M{cx} 246l30-16M{cx} 246l-40 0M{cx} 246l40 0", "f"))
    P.append((f"M{cx-40} 246a40 26 0 0 1 80 0", "f"))
    # door with porch columns
    P += [(f"M{cx-22} 378V300h44v78", "e"), (f"M{cx-40} 378V296h8v82M{cx+32} 378V296h8v82", "c"),
          (f"M{cx-46} 296h92l-46-22z", "p")]
    # calendar stones / sun path
    P.append(("M60 140a46 46 0 1 0 92 0a46 46 0 1 0-92 0", "t"))
    for k in range(12):
        import math as _m
        a = _m.radians(k * 30)
        P.append((f"M{106+52*_m.cos(a):.1f} {140+52*_m.sin(a):.1f}L{106+62*_m.cos(a):.1f} {140+62*_m.sin(a):.1f}", "t"))
    _cypress(P, 590, h=140); _cypress(P, 190, h=110)
    return _svg(P, "tower")


def amphorae():
    """Articles — painted amphorae (ancient storytelling) beside a column."""
    P = [("M0 392H600", "g"), ("M240 392v-18h340v18", "s")]

    def amph(cx, h, w):
        top = 374 - h
        P.append((f"M{cx-w*0.25:.1f} {top}h{w*0.5:.1f}v{h*0.1:.1f}c{w*0.5:.1f} {h*0.12:.1f} {w*0.55:.1f} {h*0.6:.1f} {w*0.12:.1f} {h*0.82:.1f}"
                  f"l-{w*0.07:.1f} {h*0.08:.1f}h-{w*0.6:.1f}l-{w*0.07:.1f}-{h*0.08:.1f}c-{w*0.43:.1f}-{h*0.22:.1f}-{w*0.38:.1f}-{h*0.7:.1f} {w*0.12:.1f}-{h*0.82:.1f}z", "c"))
        P.append((f"M{cx-w*0.25:.1f} {top+h*0.12:.1f}c-{w*0.3:.1f} 0-{w*0.3:.1f} {h*0.22:.1f}-{w*0.05:.1f} {h*0.26:.1f}"
                  f"M{cx+w*0.25:.1f} {top+h*0.12:.1f}c{w*0.3:.1f} 0 {w*0.3:.1f} {h*0.22:.1f} {w*0.05:.1f} {h*0.26:.1f}", "c"))
        P.append((f"M{cx-w*0.42:.1f} {top+h*0.42:.1f}h{w*0.84:.1f}M{cx-w*0.44:.1f} {top+h*0.6:.1f}h{w*0.88:.1f}", "f"))
        # meander band
        y = top + h * 0.44
        x0 = cx - w * 0.38
        n = int(w * 0.76 // 12)
        d = "".join(f"M{x0+i*12:.1f} {y+h*0.14:.1f}v-{h*0.1:.1f}h8v{h*0.05:.1f}h-4" for i in range(n))
        P.append((d, "f"))

    amph(296, 166, 90); amph(430, 206, 108); amph(548, 128, 68)
    # column with open scroll on top
    P += [("M120 392V180h30v212", "c"), ("M128 388V184M142 388V184", "f"),
          ("M108 180c0-8 10-8 10 0M162 180c0-8-10-8-10 0M108 180h54v-8h-54z", "c"),
          ("M96 168c18-10 60-10 78 0c-4 6-4 10 0 14c-18-10-60-10-78 0c4-4 4-8 0-14z", "t"),
          ("M110 168h50M112 174h44", "f")]
    _olive(P, x0=8, y0=388)
    return _svg(P, "amphorae")


def laurel():
    """Quiz — laurel wreath (the prize) with a column."""
    P = [("M0 392H600", "g")]
    import math as _m
    cx, cy, r = 430, 210, 120
    for side in (-1, 1):
        d = f"M{cx} {cy+r}"
        P.append((f"M{cx} {cy+r}" + "".join(
            f"L{cx + side*r*_m.sin(_m.radians(a)):.1f} {cy + r*_m.cos(_m.radians(a)):.1f}" for a in range(10, 171, 10)), "c"))
        for a in range(18, 170, 16):
            t = _m.radians(a)
            x, y = cx + side * r * _m.sin(t), cy + r * _m.cos(t)
            ox, oy = side * 26 * _m.cos(t), -26 * _m.sin(t)
            P.append((f"M{x:.1f} {y:.1f}q{ox*0.5 - side*8:.1f} {oy*0.5:.1f} {ox:.1f} {oy - 10:.1f}q{-side*14:.1f} {6:.1f} {-ox:.1f} {-oy + 10:.1f}z", "t"))
    P.append((f"M{cx-14} {cy+r+6}l14-12l14 12M{cx} {cy+r-6}v24", "t"))
    # a check mark in the centre (passed!)
    P.append((f"M{cx-40} {cy}l26 28l56-60", "c"))
    # small column on the left
    P += [("M140 392V250h24v142", "c"), ("M146 388V254M158 388V254", "f"),
          ("M128 250c0-8 10-8 10 0M176 250c0-8-10-8-10 0M128 250h48v-8h-48z", "c"),
          ("M118 242h68v-6h-68z", "e")]
    _cypress(P, 590, h=120)
    return _svg(P, "laurel")


def ruins():
    """404 — temple ruins: broken columns and fallen drums."""
    P = [("M0 392H600", "g"), ("M120 392v-14h440v14", "s"), ("M134 378v-10h412v10", "s")]
    hs = [200, 120, 210, 70, 160, 40]
    for i, h in enumerate(hs):
        x = 160 + i * 64
        top = 368 - h
        P += [(f"M{x} 368V{top+6}l6-6l8 4l6-6l6 8V368", "c"),
              (f"M{x+10} 364V{top+10}M{x+22} 364V{top+10}", "f")]
        if h > 180:
            P += [(f"M{x-6} {top}c0-6 6-6 6 0M{x+38} {top}c0-6-6-6-6 0", "c")]
    # architrave fragment spanning two columns
    P.append(("M152 168h132v-16H152z", "e"))
    # fallen drums
    P += [("M420 392a18 10 0 1 0 0.1 0M436 382h40v20h-40", "c"),
          ("M500 392c4-14 26-16 34-2", "c"), ("M90 392l20-26l30 8l-6 18z", "c")]
    _cypress(P, 40, h=140)
    return _svg(P, "ruins")


def scroll_doc():
    """Privacy — sealed scroll and a stylus (an ancient document)."""
    P = [("M0 392H600", "g")]
    P += [("M300 120c0-14 20-14 20 0v220c0 14-20 14-20 0zM560 120c0-14 20-14 20 0v220c0 14-20 14-20 0z", "c"),
          ("M310 110h260M310 350h260", "c")]
    for y in range(150, 330, 22):
        P.append((f"M344 {y}h{190 - (y % 3) * 20}", "f"))
    # wax seal
    P += [("M520 300a22 22 0 1 0 0.1 0", "t"), ("M510 300l8 8l14-16", "t"),
          ("M530 318l10 24l-10-6l-6 10z", "t")]
    # stylus + small column
    P += [("M220 380L270 230M266 238l8-14", "c"), ("M90 392V260h24v132M84 260h36v-8H84z", "c"),
          ("M96 388V264M108 388V264", "f")]
    _cypress(P, 30, h=120)
    return _svg(P, "scroll")


ART = {'home': temple(), 'about': caryatids(), 'learn': library(), 'serv': stoa(), 'cont': theatre(),
       'univ': academy(), 'faq': owl(), 'cal': tower(), 'blog': amphorae(), 'quiz': laurel(), 'e404': ruins(), 'priv': scroll_doc()}

CONSENT_DEFAULT = """<script>
window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:'denied',functionality_storage:'granted',security_storage:'granted',wait_for_update:500});
try{if(localStorage.getItem('msgr-consent')==='all'){gtag('consent','update',{ad_storage:'granted',ad_user_data:'granted',ad_personalization:'granted',analytics_storage:'granted'});}}catch(e){}
</script>"""

GREEK_KEY = '''<div class="greek-key" aria-hidden="true"><svg width="2600" height="18"><defs><pattern id="mk-{id}" width="36" height="18" patternUnits="userSpaceOnUse"><path d="M0 17h9V5h15v8h-8V9" fill="none" stroke="{color}" stroke-width="2"/><path d="M24 17h12" stroke="{color}" stroke-width="2"/></pattern></defs><rect width="2600" height="18" fill="url(#mk-{id})"/></svg></div>'''


def head(title, desc, path, noindex=False):
    robots = '<meta name="robots" content="noindex">' if noindex else ''
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="MY STUDY IN GREECE">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/assets/img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="ru_RU">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#13294B">
<link rel="icon" href="/assets/img/favicon.jpg">
<link rel="apple-touch-icon" href="/assets/img/favicon.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&amp;family=Golos+Text:wght@400;500;600;700&amp;display=swap">
<link rel="stylesheet" href="/assets/css/tokens.css">
<link rel="stylesheet" href="/assets/css/main.css">
{CONSENT_DEFAULT}
<!-- Google Tag Manager (kept from the current site). Runs in Consent Mode: analytics only after the visitor accepts. -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','GTM-MCM45RZH');</script>
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"EducationalOrganization","name":"MY STUDY IN GREECE","alternateName":"MSGR","url":SITE+"/","logo":SITE+"/assets/img/logo.png","email":EMAIL,"telephone":"+306942770701","sameAs":[FB,IG_HEADER,TG]}, ensure_ascii=False)}</script>
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-MCM45RZH" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<a class="skip-link" href="#content">Перейти к содержимому</a>
'''


def header(active, cta="#contact"):
    links = "\n".join(f'<a href="{h}"{" aria-current=\"page\"" if k == active else ""}>{t}</a>' for k, h, t in NAV)
    return f'''<header class="header">
<div class="header__inner">
<a class="logo-tile" href="/" aria-label="MY STUDY IN GREECE — на главную"><img src="/assets/img/logo.png" alt="MSGR — My Study in Greece" width="91" height="42"></a>
<nav class="nav" aria-label="Основное меню">
{links}
</nav>
<div class="header__actions">
<a class="header__phone" href="{PHONE_HREF}">{PHONE}</a>
<a class="btn btn--navy btn--sm header__cta" href="{cta}">Связаться с нами</a>
<button class="burger" type="button" aria-label="Меню" aria-expanded="false" aria-controls="mobile-nav">{ICON["burger"]}</button>
</div>
</div>
<nav class="mobile-nav" id="mobile-nav" aria-label="Мобильное меню">
{links}
<a href="{PHONE_HREF}">{PHONE}</a>
<a class="btn btn--navy" href="{cta}">Связаться с нами</a>
</nav>
</header>
<main id="content">
'''


def socials_all():
    return f'''<div class="socials">
<a href="{FB}">Facebook</a>
<a href="{IG_HEADER}">Instagram</a>
<a href="{TG}">Telegram</a>
<a href="{VIBER}">Viber</a>
<a href="{WA}">WhatsApp</a>
</div>'''


FAB = f"""<div class="fab" data-fab>
<div class="fab__menu" id="fab-menu" hidden>
<a class="fab__link fab__link--wa" href="{WA}">WhatsApp</a>
<a class="fab__link fab__link--tg" href="{TG}">Telegram</a>
<a class="fab__link fab__link--vb" href="{VIBER}">Viber</a>
<a class="fab__link fab__link--ph" href="{PHONE_HREF}">Позвонить</a>
</div>
<button class="fab__btn" type="button" aria-expanded="false" aria-controls="fab-menu" aria-label="Написать нам в мессенджер">
<svg class="fab__icon-open" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a8.5 8.5 0 0 1-12.6 7.4L3 21l1.6-5.2A8.5 8.5 0 1 1 21 12z"/><path d="M8.5 11h.01M12 11h.01M15.5 11h.01"/></svg>
<svg class="fab__icon-close" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
</button>
</div>"""

COOKIE = """<div class="cookie" id="cookie" role="dialog" aria-labelledby="cookie-title" aria-describedby="cookie-text" hidden>
<p class="cookie__title" id="cookie-title">Мы используем cookies</p>
<p class="cookie__text" id="cookie-text">Необходимые cookies нужны для работы сайта. С вашего согласия мы также используем аналитические cookies (Google), чтобы понимать, как улучшить сайт. <a href="/privacy/#cookies">Подробнее</a></p>
<div class="cookie__actions">
<button type="button" class="btn btn--navy btn--sm" data-consent="all">Принять все</button>
<button type="button" class="btn btn--outline btn--sm" data-consent="necessary">Только необходимые</button>
</div>
</div>"""


def footer():
    links = "\n".join(f'<a href="{h}">{t}</a>' for _, h, t in NAV)
    useful = "\n".join(f'<a href="{h}">{t}</a>' for h, t in USEFUL)
    return f'''</main>
<footer class="footer">
<div class="container footer__grid">
<div class="footer__brand">
<a href="/" aria-label="На главную"><img src="/assets/img/logo.png" alt="MSGR — My Study in Greece" width="104" height="48"></a>
<p>Поступление в университеты Греции для студентов из России, Украины и стран СНГ.</p>
</div>
<nav class="footer__col" aria-label="Разделы сайта"><p class="footer__h">Разделы</p>{links}</nav>
<nav class="footer__col" aria-label="Полезное"><p class="footer__h">Полезное</p>{useful}</nav>
<div class="footer__col"><p class="footer__h">Контакты</p>
<a href="{PHONE_HREF}">{PHONE}</a>
<a href="mailto:{EMAIL}">{EMAIL}</a>
<span>{HOURS}</span>
</div>
</div>
<div class="container footer__bottom">
<span>Copyright © <span data-year>2026</span> Учеба и высшее образование в Греции</span>
<div class="footer__legal"><a href="/privacy/">Политика конфиденциальности</a><button type="button" class="footer__linkbtn" data-cookie-settings>Настройки cookies</button></div>
{socials_all()}
</div>
</footer>
{FAB}
{COOKIE}
<script src="/assets/js/config.js"></script>
<script src="/assets/js/site-data.js"></script>
<script src="/assets/js/main.js" defer></script>
</body>
</html>
'''


def contact_section(title="Заинтересовались? Начните сейчас", eyebrow="Контакты", h="h2"):
    return f'''<section id="contact" class="section section--navy" aria-labelledby="contact-title">
<div class="container contact">
<div class="contact__info reveal">
<span class="eyebrow">{eyebrow}</span>
<{h} id="contact-title" class="h2">{title}</{h}>
<p class="lead">Всё можно сделать из дома — без поездок, переводчиков и туров.</p>
<div class="contact__lines">
<a class="contact__phone" href="{PHONE_HREF}">{PHONE}</a>
<a class="contact__mail" href="mailto:{EMAIL}">{EMAIL}</a>
<span class="contact__hours">{HOURS}</span>
</div>
<div class="messengers">
<a class="btn btn--gold" href="{WA}">WhatsApp</a>
<a class="btn btn--white" href="{TG}">Telegram</a>
<a class="btn btn--white" href="{VIBER}">Viber</a>
</div>
<div class="socials">
<a href="{IG_CONTACT}">Instagram</a>
<a href="{FB}">Facebook</a>
</div>
</div>
<form class="form reveal" data-contact-form data-source="Форма связи" novalidate>
<p class="form__title">Форма связи</p>
<div class="form__row">
<label>Имя<input type="text" name="name" autocomplete="given-name" required></label>
<label>Фамилия<input type="text" name="lastname" autocomplete="family-name"></label>
</div>
<div class="form__row">
<label>Email<input type="email" name="email" autocomplete="email" required></label>
<label>Телефон / мессенджер <span class="form__opt">(необязательно)</span><input type="tel" name="phone" autocomplete="tel"></label>
</div>
<label>Сообщение<textarea name="message" rows="4"></textarea></label>
<label class="form__hp" aria-hidden="true">Ваш сайт<input type="text" name="website" tabindex="-1" autocomplete="off"></label>
<label class="form__check"><input type="checkbox" name="consent" required> <span>Я согласен(на) на обработку данных согласно <a href="/privacy/">политике конфиденциальности</a></span></label>
<button type="submit" class="btn btn--navy">Отправить</button>
<p class="form__status" role="status" aria-live="polite"></p>
</form>
</div>
</section>
'''


def cta_band(title, text):
    return f'''<section id="contact" class="section section--navy">
<div class="container cta-band">
<div class="cta-band__text reveal">
<span class="eyebrow">Консультация</span>
<h2 class="h2">{title}</h2>
<p class="lead">{text} {HOURS}.</p>
<div class="socials" style="font-size:1rem">
<a href="{PHONE_HREF}" style="color:#fff;font-weight:700;text-decoration:none">{PHONE}</a>
<a href="mailto:{EMAIL}">{EMAIL}</a>
</div>
</div>
<div class="messengers reveal">
<a class="btn btn--gold" href="{WA}">WhatsApp</a>
<a class="btn btn--white" href="{TG}">Telegram</a>
<a class="btn btn--white" href="{VIBER}">Viber</a>
<a class="btn btn--outline-light" href="/contacts/">Форма связи</a>
</div>
</div>
</section>
'''


def hero_simple(pill, h1, lead, key_id):
    return f'''<section class="hero">
{ART[key_id]}
<div class="container hero__inner--simple" style="position:relative">
<span class="pill fu d1"><span class="pill__dot"></span>{pill}</span>
<h1 class="fu d2" style="font-family:var(--font-display);font-size:var(--fs-h1);line-height:1.08;max-width:900px">{h1}</h1>
<p class="hero__lead fu d3">{lead}</p>
</div>
{GREEK_KEY.format(id=key_id, color="#1D5A7A")}
</section>
'''


def card(icon, tone, title, text, accent=True, delay=""):
    acc = f" card--accent-{tone}" if accent else ""
    ic = f'<span class="icon-tile icon-tile--{tone}">{ICON[icon]}</span>' if icon else ""
    return f'<article class="card lift reveal{acc}">{ic}<h3>{title}</h3><p>{text}</p></article>'


def num_rows(rows):
    tones = ["aegean", "gold", "navy", "soft"]
    out = []
    for i, (t, p) in enumerate(rows):
        out.append(f'<div class="num-row reveal"><span class="num-tile num-tile--{tones[i % 4]}">{i+1:02d}</span><h3>{t}</h3><p>{p}</p></div>')
    return '<div class="num-rows">' + "\n".join(out) + "</div>"


def steps(items):
    out = []
    for i, (t, p) in enumerate(items):
        final = " step--final" if i == len(items) - 1 else ""
        out.append(f'<div class="step lift reveal{final}"><span class="step__num">{i+1:02d}</span><h3>{t}</h3><p>{p}</p></div>')
    return '<div class="grid" style="--min:230px">' + "\n".join(out) + "</div>"


def fmt(n):
    return "€" + f"{n:,}".replace(",", " ")


_PKDATA = _cload("packages.json")
PK = _PKDATA["packages"]
CLS = {"bronze": "bronze", "silver": "silver", "silver-plus": "silverplus", "gold": "gold", "brilliant": "brilliant"}
BTN = {"bronze": "btn--outline-navy", "silver": "btn--aegean", "silver-plus": "btn--outline-navy", "gold": "btn--gold", "brilliant": "btn--gold"}


def _short(label):
    """Stage label without the bracketed detail: 'Аванс (сборы…)' -> 'Аванс'."""
    return L({c: (label.get(c) or label.get("ru")).split(" (")[0] for c in ("ru", "uk", "kk")})


def pkg_cards():
    out = []
    for i, p in enumerate(PK):
        badge = f'<span class="pkg__badge">{L(p["badge"])}</span>' if p.get("badge") and L(p["badge"]) else ""
        stages = "".join(f'<div class="pkg__stage"><span>{_short(s["label"])}</span><b>{fmt(s["amount"])}</b></div>' for s in p["stages"])
        feats = "".join(f"<li>{L(f)}</li>" for f in p["features"])
        c = p.get("consultant")
        limits = f'<p class="pkg__limits">{T("limits", w=c["writtenPerMonth"], h=c["hoursTotal"])}</p>' if c else ""
        out.append(f'''<article class="pkg pkg--{CLS[p["id"]]} lift fu d{i+3}" id="pkg-{p["id"]}">
{badge}
<div><p class="pkg__name">{L(p["name"])}</p><p class="pkg__price">{fmt(p["price"])}</p><p class="pkg__desc">{L(p["summary"])}</p></div>
<div class="pkg__stages">{stages}</div>
<ul class="pkg__list">{feats}</ul>
{limits}
<a class="btn {BTN[p["id"]]}" href="{WA}">Выбрать</a>
</article>''')
    return '<div class="pkg-grid">' + "\n".join(out) + "</div>"


COMPARE_ROWS = [(r["label"], r["values"]) for r in _PKDATA.get("compare", [])]
_OLD_COMPARE_ROWS = [
    ("Подбор вуза", ["✓", "✓", "✓", "✓", "✓"]),
    ("Переводы и заверение документов", ["инструкции", "✓", "✓", "✓", "✓"]),
    ("Подача заявки представителем", ["—", "✓", "✓", "✓", "✓"]),
    ("Поддержка в сложных ситуациях", ["—", "—", "✓", "✓", "✓"]),
    ("Жильё, встреча, трансфер", ["—", "доп. услуга", "доп. услуга", "✓", "✓"]),
    ("Языковые курсы и страховка", ["инструкции", "помощь", "помощь", "✓", "✓"]),
    ("ВНЖ через юриста", ["—", "консультация", "консультация", "✓", "✓ лично"]),
    ("Бесплатная повторная подача", ["—", "—", "—", "—", "✓"]),
]
_cmp_n = [0]


def compare_table():
    _cmp_n[0] += 1
    uid = f"cmp{_cmp_n[0]}"
    colcls = ["", "col-silver", "", "col-gold", "col-brilliant"]
    heads = []
    for i, p in enumerate(PK):
        tag = ""
        if p["id"] == "silver": tag = '<span class="tag tag--aegean">Рекомендуем</span>'
        if p["id"] == "gold": tag = '<span class="tag tag--gold">Популярный</span>'
        heads.append(f'<th scope="col" class="{colcls[i % len(colcls)]}">{tag}<small>{L(p["name"])}</small><span class="price">{fmt(p["price"])}</span></th>')
    body = ""
    for label, vals in COMPARE_ROWS:
        vals = [L(v) for v in vals]
        tds = "".join(f'<td{" class=\"no\"" if not v.startswith("✓") else ""}>{v}</td>' for v in vals)
        body += f'<tr><th scope="row" style="font-weight:400;text-align:left;padding-left:20px">{L(label)}</th>{tds}</tr>\n'
    table = f'''<div class="table-wrap compare-desktop reveal"><table class="compare">
<caption class="sr-only">Сравнение пакетов услуг</caption>
<thead><tr><th scope="col">Что входит</th>{"".join(heads)}</tr></thead>
<tbody>
{body}</tbody></table></div>'''

    # Phone & tablet: package switcher + vertical checklist
    tabs, panels = [], []
    for i, p in enumerate(PK):
        sel = "true" if p["id"] == "silver" else "false"
        tabs.append(f'<button type="button" class="cm-tab cm-tab--{CLS[p["id"]]}" role="tab" id="{uid}-t-{p["id"]}" aria-controls="{uid}-p-{p["id"]}" aria-selected="{sel}" tabindex="{0 if sel == "true" else -1}"><span class="cm-tab__name">{L(p["name"])}</span><span class="cm-tab__price">{fmt(p["price"])}</span></button>')
        items = []
        for label, vals in COMPARE_ROWS:
            v = L(vals[i])
            if v.startswith("✓"):
                state, txt = "yes", ("Включено" + (" · лично" if "лично" in v else ""))
            elif v == "—":
                state, txt = "no", "Не входит"
            else:
                state, txt = "part", L({c: (vals[i].get(c) or v)[:1].upper() + (vals[i].get(c) or v)[1:] for c in ("ru", "uk", "kk")})
            icon = {"yes": "✓", "no": "—", "part": "+"}[state]
            items.append(f'<li class="cm-item cm-item--{state}"><span class="cm-item__icon" aria-hidden="true">{icon}</span><span class="cm-item__label">{L(label)}</span><span class="cm-item__state">{txt}</span></li>')
        badge = f'<span class="cm-panel__badge">{L(p["badge"])}</span>' if p.get("badge") and L(p["badge"]) else ""
        hidden = "" if p["id"] == "silver" else " hidden"
        panels.append(f'''<div class="cm-panel cm-panel--{CLS[p["id"]]}" role="tabpanel" id="{uid}-p-{p["id"]}" aria-labelledby="{uid}-t-{p["id"]}"{hidden}>
<div class="cm-panel__head"><div><p class="cm-panel__name">{L(p["name"])} {badge}</p><p class="cm-panel__summary">{L(p["summary"])}</p></div><p class="cm-panel__price">{fmt(p["price"])}</p></div>
<ul class="cm-list">{"".join(items)}</ul>
<div class="cm-panel__actions"><a class="btn {BTN[p["id"]]}" href="{WA}">{T("choose", x=p["name"])}</a><a class="more-link" href="{SERV}#pkg-{p["id"]}">Все условия пакета →</a></div>
</div>''')
    mobile = f'''<div class="compare-mobile reveal" data-tabs>
<p class="cm-hint">Выберите пакет, чтобы увидеть, что в него входит:</p>
<div class="cm-tabs" role="tablist" aria-label="Пакеты услуг">{"".join(tabs)}</div>
{"".join(panels)}
</div>'''
    return table + "\n" + mobile


# ---------------- PAGES ----------------
def page_home():
    return head("Учеба и высшее образование в Греции — MY STUDY IN GREECE",
                "Поступление в университеты Греции для студентов из России, Украины и СНГ: подбор вуза, документы, переезд и ВНЖ. Бесплатное обучение, без вступительных экзаменов.", "/") + header("home") + f'''
<section class="hero">
{ART['home']}
<div class="container hero__inner">
<div class="hero__text">
<span class="pill fu d1"><span class="pill__dot"></span>MY STUDY IN GREECE</span>
<h1 class="fu d2">Учёба и высшее образование в <span class="text-aegean">Греции</span></h1>
<p class="hero__lead fu d3">Подбираем вуз, готовим документы, подаём заявку и помогаем с переездом и ВНЖ. Для студентов из России, Украины и стран СНГ — профессионально, недорого, качественно.</p>
<div class="hero__actions fu d4">
<a class="btn btn--gold" href="{WA}">Бесплатная консультация</a>
<a class="btn btn--outline" href="{SERV}">Пакеты услуг</a>
</div>
<a class="hero__quiz fu d5" href="/quiz/">Проверить шансы за 1 минуту <span aria-hidden="true">→</span></a>
</div>
<aside class="fact-card" aria-label="Почему Греция">
<div class="fact-card__body">
<p class="fact-card__title">Почему Греция?</p>
<ul class="fact-list">
<li><span>Стоимость обучения</span><b>бесплатно*</b></li>
<li><span>Вступительные экзамены</span><b>не нужны</b></li>
<li><span>Греческий язык</span><b>12 мес. на изучение</b></li>
<li><span>Наши пакеты</span><b>от €1&nbsp;300</b></li>
</ul>
<p class="fact-card__note">* в государственных вузах по квоте для иностранцев; условия зависят от программы</p>
</div>
{GREEK_KEY.format(id="home", color="#E3C58E")}
</aside>
</div>
</section>

<section class="section section--sky">
<div class="container split">
<div class="section__head reveal" style="margin:0">
<span class="eyebrow">ВУЗы Греции</span>
<h2 class="h2">Почему греческие университеты так популярны</h2>
<p class="lead">Международный диплом ценится работодателями — особенно в Украине и странах СНГ.</p>
</div>
{num_rows([("Это бесплатно или недорого", "Государственные вузы — бесплатно или недорого (условия зависят от программы). Иностранцы могут подать на стипендию."),
           ("Без вступительных", "Зачисление по оценкам школьного аттестата."),
           ("Изучение языка", "Греческий при поступлении не нужен — на изучение не менее 12 месяцев."),
           ("Европейский диплом и ВНЖ", "Путь к международной карьере и легальное проживание на время учёбы.")])}
</div>
</section>

<section class="section">
<div class="container">
<div class="section__head reveal">
<span class="eyebrow">Частые вопросы</span>
<h2 class="h2">Чего боятся абитуриенты — и почему не стоит</h2>
</div>
<div class="grid" style="--min:220px">
{card("lang", "aegean", "«Я не знаю греческого»", "При подаче язык не нужен. После зачисления — год на языковые курсы.")}
{card("exam", "gold", "«Боюсь экзаменов»", "Их нет: поступление проходит по оценкам аттестата.")}
{card("grad", "navy", "«Примут ли бакалавриат из СНГ?»", "Подскажем подходящие магистерские программы и поможем с легализацией диплома.")}
</div>
</div>
</section>

<section class="section" style="padding-top:0">
<div class="container">
<div class="section__head reveal"><h2 class="h2">Как мы работаем</h2></div>
{steps([("Консультация", "Цели и честная оценка шансов."), ("Подбор вуза", "Государственный или частный — под вас."),
        ("Документы и подача", "Переводы, заверения, пересчёт оценок, заявка."), ("Переезд и ВНЖ", "Виза, жильё, курсы, вид на жительство.")])}
</div>
</section>

<section class="section" style="padding-top:0">
<div class="container">
<div class="section__head section__head--row reveal">
<div style="display:flex;flex-direction:column;gap:12px">
<span class="eyebrow">Пакеты услуг</span>
<h2 class="h2">Поддержка под ваш бюджет</h2>
<p class="lead">Оплата поэтапно. Без скрытых платежей и наценок.</p>
</div>
<a class="more-link" href="{SERV}">Подробные условия →</a>
</div>
{compare_table()}
</div>
</section>

<section class="section--aegean">
<div class="container quote reveal">
<p>«Мы сами учились за границей, многие из нас — выпускники греческих вузов. Поэтому знаем систему изнутри.»</p>
<span>Команда MY STUDY IN GREECE</span>
</div>
</section>
''' + useful_section() + contact_section() + footer()


def page_services():
    return head("Услуги и пакеты — MY STUDY IN GREECE",
                "Пять пакетов для поступления в вуз Греции: от €1 300 до €5 700. Оплата поэтапно, без скрытых платежей.", SERV) + header("services") + \
        hero_simple("Наши услуги", 'Пять пакетов для поступления в вуз <span class="text-aegean">Греции</span>',
                    "Выберите вариант под ваш бюджет и потребности. Оплата поэтапно — основная часть после выбора университета и программы. Без скрытых платежей.", "serv") + f'''
<section class="section" style="padding-bottom:48px">
<div class="container">
<h2 class="sr-only">Пакеты</h2>
{pkg_cards()}
</div>
</section>

<section class="section" style="padding-top:40px">
<div class="container">
<div class="section__head reveal"><span class="eyebrow">Сравнение</span><h2 class="h2">Что входит в каждый пакет</h2></div>
{compare_table()}
</div>
</section>

<section class="section section--sky">
<div class="container grid" style="--min:220px">
{card(None, "aegean", "Не входит в стоимость", "Государственные пошлины и сборы, личные поездки. В пакете «Бронзовый» — также отправка и перевод документов.")}
{card(None, "gold", "Доплаты за сроки", "€300 — документы отправлены менее чем за месяц до дедлайна; €400 — менее чем за 14 дней. Смена факультета через год — €300.")}
{card(None, "navy", "Дополнительные услуги", "Помощь со стипендией, апостиль и легализация диплома, программы мобильности и гранты, туры по вузам Греции.")}
</div>
</section>
''' + cta_band("Не знаете, какой пакет выбрать?", "Опишите вашу ситуацию — подскажем лучший вариант.") + footer()


def page_about():
    return head("О нас — MY STUDY IN GREECE",
                "MY STUDY IN GREECE — консалтинговая компания: помогаем выбрать университет в Греции, подготовить документы и обустроиться после переезда.", "/about-us/") + header("about") + \
        hero_simple("О нас", 'Как стать студентом университета в <span class="text-aegean">Греции</span>',
                    "MY STUDY IN GREECE помогает выбрать государственный или частный университет, программу и курсы, выстроить стратегию обучения и подготовить документы для поступления.", "about") + f'''
<section class="section">
<div class="container">
<div class="section__head reveal">
<span class="eyebrow">Основные принципы</span>
<h2 class="h2">Честность, порядочность, надёжность</h2>
<p class="lead">Мы рядом и после зачисления: мотивация, поддержка и адаптация к новой среде.</p>
</div>
<div class="grid" style="--min:220px">
{card("shield", "aegean", "Честность", "Реально оцениваем шансы на поступление и говорим как есть.")}
{card("heart", "gold", "Порядочность", "Отвечаем за каждого клиента — в том числе перед родителями, которые отправляют детей в Грецию.")}
{card("users", "navy", "Надёжность", "Помогаем студенту комфортно устроиться на новом месте.")}
</div>
</div>
</section>

<section class="section section--sky">
<div class="container split">
<div class="section__head reveal" style="margin:0">
<span class="eyebrow">Зачем нужен посредник</span>
<h2 class="h2">Поступить несложно. Но мелкая ошибка может стоить дорого</h2>
<p class="lead">Информацию можно найти в интернете, однако подача в несколько вузов отнимает много времени. С нами проще.</p>
</div>
{num_rows([("Работаем с душой", "Быстро решаем задачи, находимся рядом со студентами и даём практические советы."),
           ("Опыт поступивших", "Команда училась за границей, многие — выпускники греческих вузов."),
           ("Экономия времени и сил", "Подаём документы и подсказываем лучшие варианты поступления."),
           ("Индивидуальные консультации", "Разбираем вашу ситуацию и подбираем подходящий путь.")])}
</div>
</section>

<section class="section">
<div class="container">
<div class="section__head reveal">
<span class="eyebrow">Работаем для вас</span>
<h2 class="h2">MY STUDY IN GREECE</h2>
</div>
<div class="grid" style="--min:220px">
<div class="step lift reveal"><span class="step__num">€</span><h3>Без скрытых платежей</h3><p>Прозрачные цены, без наценок и доплат за «сопровождение».</p></div>
<div class="step lift reveal"><span class="step__num">{ICON["home"].replace('<svg', '<svg width="24" height="24"')}</span><h3>Всё из дома</h3><p>Без поездок, переводчиков и туров.</p></div>
<div class="step step--final lift reveal"><span class="step__num">✓</span><h3>Качество, а не количество</h3><p>Наша цель — ваше успешное поступление.</p></div>
</div>
</div>
</section>

<section class="section--aegean">
<div class="container quote reveal">
<p>«Мы сами учились за границей, многие из нас — выпускники греческих вузов. Поэтому знаем систему изнутри.»</p>
<span>Команда MY STUDY IN GREECE</span>
</div>
</section>
''' + contact_section() + footer()


def page_learning():
    return head("Образование в Греции — MY STUDY IN GREECE",
                "Стоит ли получать диплом в Греции? Преимущества обучения, европейские программы, бесплатные государственные вузы и вид на жительство.", "/learning/") + header("learning") + \
        hero_simple("Образование", 'Диплом вуза <span class="text-aegean">Греции</span> — профессионально, недорого, качественно',
                    "Стоит ли получать диплом в Греции? Полезная информация для абитуриентов от MY STUDY IN GREECE (MSGR).", "learn") + f'''
<section class="section">
<div class="container split">
<div class="section__head reveal" style="margin:0">
<span class="eyebrow">Почему именно эта страна</span>
<h2 class="h2">Европейское образование без лишних барьеров</h2>
<p class="lead">Обучение за рубежом стало почти необходимостью для тех, кто строит карьеру в большом мире. Греческий диплом открывает путь к международной работе.</p>
</div>
{num_rows([("Простое поступление", "Без вступительных экзаменов — по оценкам аттестата. С MSGR — ещё проще."),
           ("Качественное образование", "Европейские программы обучения."),
           ("Доступная стоимость", "По квоте для иностранцев государственные вузы традиционно бесплатны; условия зависят от программы."),
           ("Вид на жительство", "Учёба даёт легальный ВНЖ на срок от 1 до 5 лет.")])}
</div>
</section>

<section class="section section--sky">
<div class="container">
<div class="section__head reveal">
<span class="eyebrow">Новые возможности</span>
<h2 class="h2">Преимущества образования в Греции</h2>
<p class="lead">Высшее образование в Греции не сильно отличается от СНГ, но диплом известного европейского вуза работодатели воспринимают иначе.</p>
</div>
<div class="grid" style="--min:250px">
{card("globe", "aegean", "Иностранные языки", "Погружение в языковую среду — греческий и английский.")}
{card("book", "gold", "Качественные знания", "Сильные языковые навыки помогают в международном бизнесе и работе.")}
{card("grad", "navy", "Европейский диплом", "Ценится работодателями в Европе и за её пределами.")}
{card("users", "aegean", "Новые знакомства", "Студенты быстрее взрослеют и заводят международные контакты.")}
</div>
</div>
</section>

<section class="section">
<div class="container">
<div class="section__head reveal">
<span class="eyebrow">Для чего нужен посредник</span>
<h2 class="h2">При поступлении в греческий вуз</h2>
<p class="lead">Информации в интернете много, но небольшие ошибки в документах могут закрыть дорогу в европейский вуз. Мы берём оформление на себя.</p>
</div>
{steps([("Подбор вуза", "Индивидуально, под ваши цели и бюджет."), ("Документы", "Переводы, заверения, пересчёт оценок."),
        ("Подача заявки", "В срок и без ошибок."), ("Вы — студент", "Виза, переезд, курсы и ВНЖ.")])}
<div class="reveal" style="margin-top:36px;display:flex;flex-wrap:wrap;gap:12px">
<a class="btn btn--navy" href="{SERV}">Посмотреть пакеты услуг</a>
<a class="btn btn--outline" href="/calendar/">Календарь поступления</a>
<a class="btn btn--outline" href="/universities/">Университеты Греции</a>
<a class="btn btn--outline" href="{WA}">Задать вопрос</a>
</div>
</div>
</section>
''' + contact_section() + footer()


def page_contacts():
    return head("Контакты — MY STUDY IN GREECE",
                "Свяжитесь с MY STUDY IN GREECE: телефон +30 694 277 07 01, WhatsApp, Viber, Telegram, email mystudygr1@gmail.com. ПН–ПТ 08:00–20:00.", "/contacts/") + header("contacts") + \
        hero_simple("Контакты", 'Свяжитесь с <span class="text-aegean">нами</span>',
                    "Ответим на вопросы о поступлении, документах и пакетах услуг. Пишите в удобный мессенджер или оставьте заявку.", "cont") + f'''
<section class="section">
<div class="container">
<div class="grid" style="--min:240px">
<div class="info-card lift reveal"><span class="icon-tile icon-tile--aegean">{ICON["phone"]}</span><span class="info-card__label">Телефон</span><a class="info-card__value" href="{PHONE_HREF}">{PHONE}</a></div>
<div class="info-card lift reveal"><span class="icon-tile icon-tile--gold">{ICON["mail"]}</span><span class="info-card__label">Email</span><a class="info-card__value" href="mailto:{EMAIL}">{EMAIL}</a></div>
<div class="info-card lift reveal"><span class="icon-tile icon-tile--navy">{ICON["clock"]}</span><span class="info-card__label">Часы работы</span><span class="info-card__value">{HOURS}</span></div>
</div>
<div class="reveal" style="margin-top:36px;display:flex;flex-direction:column;gap:16px">
<h2 style="font-size:1.25rem">Мессенджеры и соц. сети</h2>
<div class="messengers">
<a class="btn btn--gold" href="{WA}">WhatsApp</a>
<a class="btn btn--aegean" href="{TG}">Telegram</a>
<a class="btn btn--navy" href="{VIBER}">Viber</a>
<a class="btn btn--outline" href="{IG_HEADER}">Instagram</a>
<a class="btn btn--outline" href="{FB}">Facebook</a>
</div>
</div>
</div>
</section>
''' + contact_section("Напишите нам — ответим быстро", "Форма связи") + footer()



# ======================= NEW PAGES =======================
MINEDU = "https://www.minedu.gov.gr/"
FOREIGN_PORTAL = "https://exams-foreigner.it.minedu.gov.gr"

# ---- editable collections (content/*.json, edited in the admin panel) ----
UNIVERSITIES = _cload("universities.json")
CALENDAR = _cload("calendar.json")
FAQ = _cload("faq.json")
ARTICLES = sorted(_cload("articles.json"), key=lambda a: a["date"], reverse=True)


def _fdate(d):
    return f"{d[8:10]}.{d[5:7]}.{d[:4]}"


def page_universities():
    cards = []
    for u in UNIVERSITIES:
        cards.append(f'''<article class="uni lift reveal" data-group="{u["group"]}">
<div class="uni__top"><span class="uni__city">{L(u["city"])}</span><span class="uni__year">{T("since", n=u["founded"])}</span></div>
<h3>{L(u["name"])}</h3>
<p class="uni__gr">{_html.escape(u.get("greek", ""))}</p>
<p>{L(u["profile"])}</p>
</article>''')
    return head("Университеты Греции — MY STUDY IN GREECE",
                "Государственные университеты Греции: Афины, Салоники, Патры, Крит и другие города. Поможем выбрать вуз и программу.", "/universities/") + header("universities") + \
        hero_simple("Университеты", 'Государственные университеты <span class="text-aegean">Греции</span>',
                    "Обзор крупнейших государственных вузов страны. Поможем выбрать университет и программу под ваши цели — в любом городе.", "univ") + f'''
<section class="section">
<div class="container">
<div class="filters reveal" role="group" aria-label="Фильтр по городу" data-filter>
<button type="button" class="chip" aria-pressed="true" data-value="all">Все <span>{len(UNIVERSITIES)}</span></button>
<button type="button" class="chip" aria-pressed="false" data-value="athens">Афины и Пирей</button>
<button type="button" class="chip" aria-pressed="false" data-value="thess">Салоники</button>
<button type="button" class="chip" aria-pressed="false" data-value="other">Другие города</button>
</div>
<div class="uni-grid" data-filter-target>
{"".join(cards)}
</div>
<p class="fineprint reveal">Список информационный и не является перечнем партнёров. Год указан по основанию учреждения. Мы помогаем с поступлением в любой государственный вуз Греции.</p>
</div>
</section>
{promo_quiz()}
''' + cta_band("Не знаете, какой вуз выбрать?", "Расскажите о своих целях — подберём университет и программу.") + footer()


def page_calendar():
    items = []
    for c in CALENDAR:
        portal = f'<a class="more-link" href="{FOREIGN_PORTAL}">Портал подачи заявок →</a>' if c.get("portal") else ""
        items.append(f'''<li class="tl__item tl__item--{c.get("kind", "prep")} reveal">
<span class="tl__dot" aria-hidden="true"></span>
<p class="tl__when">{L(c["when"])}</p>
<h3>{L(c["title"])}</h3>
<p>{L(c["text"])}</p>{portal}
</li>''')
    return head("Календарь поступления в вузы Греции — MY STUDY IN GREECE",
                "Сроки поступления иностранцев в государственные вузы Греции: подготовка документов, электронная заявка в июле, зачисление в сентябре.", "/calendar/") + header("") + \
        hero_simple("Календарь", 'Календарь поступления в <span class="text-aegean">Грецию</span>',
                    "Основные этапы и сроки для иностранцев, поступающих в государственные вузы по специальной квоте.", "cal") + f'''
<section class="section">
<div class="container split">
<div class="section__head reveal" style="margin:0">
<span class="eyebrow">Цикл 2026/27</span>
<h2 class="h2">Как это было в 2026 году</h2>
<p class="lead">Министерство образования объявляет точные даты каждый год. На следующий цикл ожидаем похожий график — подача в начале июля, зачисление в сентябре. Как только даты 2027 года будут объявлены, мы обновим календарь.</p>
<div class="legend">
<span><i class="lg lg--prep"></i>Подготовка</span><span><i class="lg lg--key"></i>Ключевые даты</span><span><i class="lg lg--after"></i>После зачисления</span>
</div>
<p class="fineprint">Источник: Министерство образования Греции, <a href="{MINEDU}">minedu.gov.gr</a>.</p>
</div>
<ol class="tl">
{"".join(items)}
</ol>
</div>
</section>
{promo_quiz("Успеваете к следующему циклу?", "Ответьте на 6 вопросов — подскажем, с чего начать и какой пакет подойдёт.")}
''' + cta_band("Хотите успеть к следующему набору?", "Начните подготовку документов заранее — мы составим план под ваши сроки.") + footer()


def page_faq():
    groups, schema = [], []
    for g in FAQ:
        qs = [(L(i["q"]), L(i["a"])) for i in g["items"]]
        items = "".join(f'<details class="faq__item"><summary>{q}</summary><div class="faq__a"><p>{a}</p></div></details>' for q, a in qs)
        groups.append(f'<div class="faq__group reveal"><h2 class="faq__h">{L(g["group"])}</h2>{items}</div>')
        schema += [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qs]
    ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": schema}, ensure_ascii=False)
    return head("Вопросы и ответы — MY STUDY IN GREECE",
                "Частые вопросы о поступлении в вузы Греции: язык, экзамены, стоимость, документы, сроки, виза и ВНЖ, работа во время учёбы.", "/faq/") + header("faq") + \
        hero_simple("Вопросы и ответы", 'Частые <span class="text-aegean">вопросы</span>',
                    "Коротко о главном: язык, экзамены, стоимость, документы, виза и жизнь в Греции.", "faq") + f'''
<section class="section">
<div class="container faq">
<label class="faq__search reveal"><span class="sr-only">Поиск по вопросам</span>
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>
<input type="search" placeholder="Поиск по вопросам…" data-faq-search></label>
<p class="faq__empty" hidden data-faq-empty>Ничего не нашли — <a href="#contact">спросите нас напрямую</a>.</p>
{"".join(groups)}
</div>
</section>
<script type="application/ld+json">{ld}</script>
''' + contact_section("Не нашли ответ? Спросите нас", "Вопрос специалисту") + footer()


QUIZ_Q = [
    ("level", "Куда вы планируете поступать?", [("bach", "Бакалавриат"), ("master", "Магистратура"), ("unsure", "Пока не знаю")]),
    ("school", "Где вы окончили (оканчиваете) школу?", [("ru", "Россия"), ("ua", "Украина"), ("cis", "Другая страна СНГ"), ("eu", "Страна ЕС"), ("other", "Другая страна")]),
    ("grade", "Какой у вас средний балл?", [("high", "Отлично — почти все пятёрки"), ("mid", "Хорошо — четвёрки и пятёрки"), ("low", "Есть тройки")]),
    ("greek", "Как вы знаете греческий?", [("none", "Не знаю"), ("basic", "Начальный уровень"), ("good", "Уверенно")]),
    ("when", "Когда хотите начать учёбу?", [("next", "В ближайший набор"), ("later", "Через год и позже"), ("explore", "Пока изучаю варианты")]),
    ("help", "Какая помощь вам нужна?", [("self", "Только подбор и инструкции — остальное сам"), ("docs", "Документы и подача — за меня"), ("full", "Всё: поступление, переезд, жильё, ВНЖ"), ("vip", "Всё под ключ, срочно, с гарантиями")]),
]


def page_quiz():
    steps_html = []
    for i, (key, q, opts) in enumerate(QUIZ_Q):
        o = "".join(f'<label class="quiz__opt"><input type="radio" name="{key}" value="{v}"><span>{t}</span></label>' for v, t in opts)
        steps_html.append(f'<fieldset class="quiz__step" data-step="{i}"{" hidden" if i else ""}><legend class="quiz__q"><span class="quiz__n">Вопрос {i+1} из {len(QUIZ_Q)}</span>{q}</legend><div class="quiz__opts">{o}</div></fieldset>')
    return head("Проверить шансы на поступление — MY STUDY IN GREECE",
                "Ответьте на 6 вопросов и получите предварительную оценку шансов на поступление в вуз Греции и подходящий пакет услуг.", "/quiz/") + header("", cta="/contacts/") + \
        hero_simple("1 минута", 'Проверьте шансы на поступление в <span class="text-aegean">Грецию</span>',
                    "6 простых вопросов — и вы получите предварительную оценку и рекомендацию, с чего начать.", "quiz") + f'''
<section class="section">
<div class="container">
<div class="quiz reveal" data-quiz>
<div class="quiz__bar" aria-hidden="true"><span data-quiz-progress></span></div>
<form class="quiz__form" data-quiz-form novalidate>
{"".join(steps_html)}
<div class="quiz__nav">
<button type="button" class="btn btn--outline" data-quiz-back hidden>Назад</button>
<button type="button" class="btn btn--navy" data-quiz-next disabled>Далее</button>
</div>
</form>
<div class="quiz__result" data-quiz-result hidden tabindex="-1">
<span class="eyebrow">Предварительная оценка</span>
<h2 class="h2" data-r-title></h2>
<p class="lead" data-r-text></p>
<div class="quiz__reco">
<div class="quiz__reco-card"><p class="quiz__reco-label">Подходящий пакет</p><p class="quiz__reco-name" data-r-pkg></p><p data-r-pkgtext></p><a class="more-link" data-r-pkglink href="{SERV}">Подробнее о пакете →</a></div>
<div class="quiz__reco-card"><p class="quiz__reco-label">Сроки</p><p data-r-time></p><a class="more-link" href="/calendar/">Календарь поступления →</a></div>
</div>
<form class="form quiz__lead" data-contact-form data-source="Тест «Проверить шансы»" novalidate>
<p class="form__title">Получить бесплатную консультацию</p>
<p class="form__note">Специалист проверит ваши документы и даст точную оценку.</p>
<div class="form__row">
<label>Имя<input type="text" name="name" autocomplete="given-name" required></label>
<label>Email<input type="email" name="email" autocomplete="email" required></label>
</div>
<label>Телефон / мессенджер <span class="form__opt">(необязательно)</span><input type="tel" name="phone" autocomplete="tel"></label>
<input type="hidden" name="message" data-r-summary>
<label class="form__hp" aria-hidden="true">Ваш сайт<input type="text" name="website" tabindex="-1" autocomplete="off"></label>
<label class="form__check"><input type="checkbox" name="consent" required> <span>Я согласен(на) на обработку данных согласно <a href="/privacy/">политике конфиденциальности</a></span></label>
<button type="submit" class="btn btn--gold">Отправить</button>
<p class="form__status" role="status" aria-live="polite"></p>
</form>
<p class="fineprint">Это предварительная оценка по вашим ответам, а не гарантия поступления. <button type="button" class="linkbtn" data-quiz-restart>Пройти заново</button></p>
</div>
</div>
</div>
</section>
''' + footer()


def page_blog():
    cards = "".join(f'''<article class="post-card lift reveal">
<p class="post-card__meta"><time datetime="{a["date"]}">{_fdate(a["date"])}</time> {T("readmeta", n=a["minutes"])}</p>
<h2><a href="/blog/{a["slug"]}/">{L(a["title"])}</a></h2>
<p>{L(a["desc"])}</p>
<a class="more-link" href="/blog/{a["slug"]}/" aria-hidden="true" tabindex="-1">Читать →</a>
</article>''' for a in ARTICLES)
    return head("Статьи об учёбе в Греции — MY STUDY IN GREECE",
                "Полезные статьи о поступлении в вузы Греции, документах, визе, ВНЖ и жизни студентов.", "/blog/") + header("") + \
        hero_simple("Статьи", 'Полезное об учёбе в <span class="text-aegean">Греции</span>',
                    "Инструкции и разборы от команды MY STUDY IN GREECE.", "blog") + f'''
<section class="section">
<div class="container grid" style="--min:300px">{cards}</div>
</section>
''' + cta_band("Остались вопросы?", "Напишите нам — ответим и поможем составить план поступления.") + footer()


def page_article(a):
    others = "".join(f'<li><a href="/blog/{o["slug"]}/">{L(o["title"])}</a></li>' for o in ARTICLES[:4] if o is not a)
    title, desc = L(a["title"]), L(a["desc"])
    ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc,
                     "datePublished": a["date"], "inLanguage": "ru", "author": {"@type": "Organization", "name": "MY STUDY IN GREECE"},
                     "publisher": {"@type": "Organization", "name": "MY STUDY IN GREECE", "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/logo.png"}},
                     "mainEntityOfPage": f'{SITE}/blog/{a["slug"]}/'}, ensure_ascii=False)
    return head(f'{title} — MY STUDY IN GREECE', desc, f'/blog/{a["slug"]}/') + header("") + \
        hero_simple(T("pill", n=a["minutes"]), title, desc, (a.get("art") if a.get("art") in ART else "blog")) + f'''
<section class="section">
<div class="container article-wrap">
<nav class="crumbs" aria-label="Навигация"><a href="/">Главная</a> / <a href="/blog/">Статьи</a></nav>
<article class="prose">
<p class="post-card__meta">Опубликовано <time datetime="{a["date"]}">{_fdate(a["date"])}</time></p>
{rich("body-" + a["slug"], a["body"])}
</article>
<aside class="article-aside">
<div class="aside-card"><p class="aside-card__h">Проверьте шансы</p><p>6 вопросов — и предварительная оценка за минуту.</p><a class="btn btn--gold btn--sm" href="/quiz/">Пройти тест</a></div>
<div class="aside-card"><p class="aside-card__h">Читайте также</p><ul>{others}<li><a href="/faq/">Вопросы и ответы</a></li><li><a href="/calendar/">Календарь поступления</a></li></ul></div>
</aside>
</div>
</section>
<script type="application/ld+json">{ld}</script>
''' + cta_band("Нужна помощь с поступлением?", "Возьмём на себя документы, подачу и переезд.") + footer()


def page_privacy():
    return head("Политика конфиденциальности — MY STUDY IN GREECE",
                "Как MY STUDY IN GREECE обрабатывает персональные данные и использует cookies.", "/privacy/") + header("", cta="/contacts/") + \
        hero_simple("Документ", 'Политика <span class="text-aegean">конфиденциальности</span>',
                    "Как мы обрабатываем персональные данные посетителей сайта mystudygr.com и используем cookies.", "priv") + f'''
<section class="section">
<div class="container article-wrap article-wrap--single">
<article class="prose">
<p class="post-card__meta">Последнее обновление: 06.11.2026</p>
<div class="note note--warn"><b>Черновик.</b> Перед публикацией замените данные в квадратных скобках и согласуйте текст с юристом.</div>
<h2>1. Кто обрабатывает данные</h2>
<p>Оператор персональных данных — [ЮРИДИЧЕСКОЕ НАЗВАНИЕ КОМПАНИИ], ΑΦΜ [НОМЕР], адрес: [АДРЕС], Греция (далее — «MY STUDY IN GREECE», «мы»). Связаться с нами по вопросам данных: <a href="mailto:{EMAIL}">{EMAIL}</a>, {PHONE}.</p>
<h2>2. Какие данные мы собираем</h2>
<ul>
<li>данные, которые вы указываете в формах: имя, фамилия, email, телефон или мессенджер, текст сообщения, ответы теста «Проверить шансы»;</li>
<li>данные переписки, если вы пишете нам в WhatsApp, Telegram, Viber или по email;</li>
<li>технические данные и cookies — только с вашего согласия (см. раздел 7).</li>
</ul>
<h2>3. Зачем мы используем данные</h2>
<ul>
<li>чтобы ответить на ваш запрос и провести консультацию;</li>
<li>чтобы заключить и исполнить договор об оказании услуг;</li>
<li>с вашего согласия — для анализа посещаемости и улучшения сайта.</li>
</ul>
<h2>4. Правовые основания (GDPR)</h2>
<p>Мы обрабатываем данные на основании вашего согласия (ст. 6(1)(a) GDPR), для заключения и исполнения договора (ст. 6(1)(b)) и для выполнения требований закона (ст. 6(1)(c)). Согласие можно отозвать в любой момент.</p>
<h2>5. Кому передаются данные</h2>
<p>Мы не продаём данные. Для работы сайта и связи с вами мы используем сервисы: хостинг сайта, Google (электронная почта, Google Tag Manager / аналитика — только с согласия), Telegram (уведомления о заявках). Некоторые из них могут обрабатывать данные за пределами ЕС на основании стандартных договорных условий. Для оказания услуг данные могут передаваться университетам, переводчикам, юристам и государственным органам Греции — только в объёме, необходимом для вашего поступления и оформления документов.</p>
<h2>6. Сколько мы храним данные</h2>
<p>Данные заявок храним до [СРОК, например 24 месяца] с последнего контакта, данные клиентов — в течение срока договора и сроков, установленных законом. После этого данные удаляются.</p>
<h2 id="cookies">7. Cookies</h2>
<p><b>Необходимые</b> cookies и локальное хранилище обеспечивают работу сайта и запоминают ваш выбор по cookies. <b>Аналитические</b> cookies (Google через Google Tag Manager) помогают понять, как используется сайт, — они включаются только после нажатия «Принять все». Изменить выбор можно в любой момент: <button type="button" class="linkbtn" data-cookie-settings>открыть настройки cookies</button>.</p>
<h2>8. Ваши права</h2>
<p>Вы можете запросить доступ к своим данным, их исправление или удаление, ограничение обработки, перенос данных, а также возразить против обработки и отозвать согласие. Напишите нам на <a href="mailto:{EMAIL}">{EMAIL}</a>. Вы также вправе подать жалобу в греческий орган по защите данных — Αρχή Προστασίας Δεδομένων Προσωπικού Χαρακτήρα (<a href="https://www.dpa.gr/">dpa.gr</a>).</p>
<h2>9. Изменения</h2>
<p>Мы можем обновлять эту политику. Актуальная версия всегда опубликована на этой странице.</p>
</article>
</div>
</section>
''' + footer()


def page_404():
    return head("Страница не найдена — MY STUDY IN GREECE", "Страница не найдена.", "/404.html", noindex=True) + header("", cta="/contacts/") + f'''
<section class="hero hero--404">
{ART['e404']}
<div class="container hero__inner--simple" style="position:relative">
<span class="pill fu d1"><span class="pill__dot"></span>Ошибка 404</span>
<h1 class="fu d2" style="font-family:var(--font-display);font-size:var(--fs-h1);line-height:1.08">Эта страница <span class="text-aegean">не сохранилась</span></h1>
<p class="hero__lead fu d3">Как древние руины — что-то осталось в истории. Возможно, ссылка устарела или в адресе опечатка.</p>
<div class="hero__actions fu d4">
<a class="btn btn--navy" href="/">На главную</a>
<a class="btn btn--outline" href="/faq/">Вопросы и ответы</a>
<a class="btn btn--outline" href="/contacts/">Контакты</a>
</div>
</div>
{GREEK_KEY.format(id="e404", color="#1D5A7A")}
</section>
''' + footer()


def promo_quiz(title="Проверьте свои шансы за 1 минуту", text="Ответьте на 6 вопросов — получите предварительную оценку и рекомендацию по пакету."):
    return f'''<section class="section" style="padding-top:0">
<div class="container">
<div class="promo reveal">
<div class="promo__text"><span class="eyebrow">Бесплатно</span><h2 class="h2">{title}</h2><p class="lead">{text}</p></div>
<a class="btn btn--gold" href="/quiz/">Проверить шансы →</a>
</div>
</div>
</section>
'''


def useful_section():
    items = [("/quiz/", "Проверить шансы", "6 вопросов — предварительная оценка и подходящий пакет.", "exam", "gold"),
             ("/calendar/", "Календарь поступления", "Ключевые даты: подача в июле, зачисление в сентябре.", "clock", "aegean"),
             ("/universities/", "Университеты Греции", "Афины, Салоники, Патры, Крит и другие города.", "grad", "navy"),
             ("/faq/", "Вопросы и ответы", "Язык, экзамены, стоимость, виза и ВНЖ.", "book", "aegean")]
    cards = "".join(f'<a class="card card--link lift reveal card--accent-{tone}" href="{h}"><span class="icon-tile icon-tile--{tone}">{ICON[ic]}</span><h3>{t}</h3><p>{d}</p><span class="more-link" aria-hidden="true">Открыть →</span></a>' for h, t, d, ic, tone in items)
    return f'''<section class="section">
<div class="container">
<div class="section__head reveal"><span class="eyebrow">Полезное</span><h2 class="h2">Всё для подготовки к поступлению</h2></div>
<div class="grid" style="--min:230px">{cards}</div>
</div>
</section>
'''


import re as _re
def _ext(html):
    html = _re.sub(r'<a ([^>]*?)href="(https?://[^"]+)"', lambda m: f'<a {m.group(1)}href="{m.group(2)}" target="_blank" rel="noopener"', html)
    if BASE:  # prefix root-relative links/assets for a sub-path host (GitHub Pages)
        html = _re.sub(r'(href|src)="/(?!/)', lambda m: f'{m.group(1)}="{BASE}/', html)
    return html

PAGES = {"index.html": page_home, "about-us/index.html": page_about, "learning/index.html": page_learning,
         "universities/index.html": page_universities, "faq/index.html": page_faq, "calendar/index.html": page_calendar,
         "quiz/index.html": page_quiz, "blog/index.html": page_blog, "privacy/index.html": page_privacy, "404.html": page_404,
         "услуги/index.html": page_services, "contacts/index.html": page_contacts}

for _a in ARTICLES:
    PAGES[f"blog/{_a['slug']}/index.html"] = (lambda a=_a: page_article(a))


# =================== MULTILINGUAL (RU root, /ua/ Ukrainian, /kz/ Kazakh) ===================
import re as _re2
_I18N_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "i18n")
LANGS = [  # (html lang, url prefix, og locale, switcher label, native name)
    ("ru", "", "ru_RU", "RU", "Русский"),
    ("uk", "/ua", "uk_UA", "UA", "Українська"),
    ("kk", "/kz", "kk_KZ", "KZ", "Қазақша"),
]
_RU_KEYS = json.load(open(os.path.join(_I18N_DIR, "strings_ru.json"), encoding="utf-8"))


def _load_tsv(code):
    m = {}
    for line in open(os.path.join(_I18N_DIR, f"{code}.tsv"), encoding="utf-8"):
        line = line.rstrip("\n")
        if not line:
            continue
        i, t = line.split("\t", 1)
        m[_RU_KEYS[int(i)]] = t
    return m


H1 = {  # whole-heading translations (word order differs, esp. in Kazakh)
    'Государственные университеты <span class="text-aegean">Греции</span>': (
        'Державні університети <span class="text-aegean">Греції</span>',
        '<span class="text-aegean">Грекияның</span> мемлекеттік университеттері'),
    'Диплом вуза <span class="text-aegean">Греции</span> — профессионально, недорого, качественно': (
        'Диплом вишу <span class="text-aegean">Греції</span> — професійно, недорого, якісно',
        '<span class="text-aegean">Грекия</span> ЖОО дипломы — кәсіби, қолжетімді, сапалы'),
    'Как стать студентом университета в <span class="text-aegean">Греции</span>': (
        'Як стати студентом університету в <span class="text-aegean">Греції</span>',
        '<span class="text-aegean">Грекияда</span> университет студенті болу жолы'),
    'Календарь поступления в <span class="text-aegean">Грецию</span>': (
        'Календар вступу до <span class="text-aegean">Греції</span>',
        '<span class="text-aegean">Грекияға</span> түсу күнтізбесі'),
    'Полезное об учёбе в <span class="text-aegean">Греции</span>': (
        'Корисне про навчання в <span class="text-aegean">Греції</span>',
        '<span class="text-aegean">Грекияда</span> оқу туралы пайдалы ақпарат'),
    'Политика <span class="text-aegean">конфиденциальности</span>': (
        'Політика <span class="text-aegean">конфіденційності</span>',
        'Құпиялылық <span class="text-aegean">саясаты</span>'),
    'Проверьте шансы на поступление в <span class="text-aegean">Грецию</span>': (
        'Перевірте шанси на вступ до <span class="text-aegean">Греції</span>',
        '<span class="text-aegean">Грекияға</span> түсу мүмкіндігіңізді тексеріңіз'),
    'Пять пакетов для поступления в вуз <span class="text-aegean">Греции</span>': (
        'П’ять пакетів для вступу до вишу <span class="text-aegean">Греції</span>',
        '<span class="text-aegean">Грекия</span> ЖОО-сына түсуге арналған бес пакет'),
    'Свяжитесь с <span class="text-aegean">нами</span>': (
        'Зв’яжіться з <span class="text-aegean">нами</span>',
        '<span class="text-aegean">Бізбен</span> байланысыңыз'),
    'Учёба и высшее образование в <span class="text-aegean">Греции</span>': (
        'Навчання та вища освіта в <span class="text-aegean">Греції</span>',
        '<span class="text-aegean">Грекиядағы</span> оқу және жоғары білім'),
    'Частые <span class="text-aegean">вопросы</span>': (
        'Часті <span class="text-aegean">питання</span>',
        'Жиі қойылатын <span class="text-aegean">сұрақтар</span>'),
    'Эта страница <span class="text-aegean">не сохранилась</span>': (
        'Ця сторінка <span class="text-aegean">не збереглася</span>',
        'Бұл бет <span class="text-aegean">сақталмаған</span>'),
}
TR = {"uk": _load_tsv("uk"), "kk": _load_tsv("kk")}


def _translate(html, lang):
    m = TR[lang]
    hi = 0 if lang == "uk" else 1
    # 1) JSON-LD blocks: translate string values
    def ld(mo):
        def walk(o):
            if isinstance(o, dict): return {k: walk(v) for k, v in o.items()}
            if isinstance(o, list): return [walk(v) for v in o]
            if isinstance(o, str): return m.get(o, o)
            return o
        return mo.group(1) + json.dumps(walk(json.loads(mo.group(2))), ensure_ascii=False) + mo.group(3)
    html = _re2.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)', ld, html, flags=_re2.S)
    # 2) protect other scripts/styles
    keep = []
    def stash(mo):
        keep.append(mo.group(0)); return f"\x00{len(keep)-1}\x00"
    html = _re2.sub(r'<(script|style)\b[^>]*>.*?</\1>', stash, html, flags=_re2.S)
    # 3) headings as whole units
    html = _re2.sub(r'(<h1\b[^>]*>)(.*?)(</h1>)', lambda mo: mo.group(1) + (H1[mo.group(2)][hi] if mo.group(2) in H1 else mo.group(2)) + mo.group(3), html, flags=_re2.S)
    # 4) attributes
    html = _re2.sub(r'\b(alt|aria-label|placeholder|title|content)="([^"]*)"', lambda mo: f'{mo.group(1)}="{m.get(mo.group(2), mo.group(2))}"', html)
    # 5) text nodes
    def tn(mo):
        raw = mo.group(1); s = raw.strip()
        if s in m:
            lead = raw[:len(raw) - len(raw.lstrip())]; trail = raw[len(raw.rstrip()):]
            return ">" + lead + m[s] + trail + "<"
        return mo.group(0)
    html = _re2.sub(r'>([^<]+)<', tn, html)
    html = _re2.sub(r'\x00(\d+)\x00', lambda mo: keep[int(mo.group(1))], html)
    return html


def _page_path(rel):
    if rel == "404.html": return "/404.html"
    p = "/" + rel[:-len("index.html")]
    return p.replace("/услуги/", SERV)


def _prefix_links(html, prefix):
    # internal page links only (not assets/api/anchors/external)
    def fix(mo):
        attr, url = mo.group(1), mo.group(2)
        if url.startswith(("/assets/", "/api/", "//")): return mo.group(0)
        return f'{attr}="{prefix}{url}"'
    html = _re2.sub(r'\b(href)="(/[^"]*)"', fix, html)
    html = html.replace(f'"{SITE}/', f'"{SITE}{prefix}/')        # canonical, og:url, JSON-LD urls
    html = html.replace(f'"{SITE}{prefix}/assets/', f'"{SITE}/assets/')  # keep og:image etc.
    return html


def _finalize(html, lang, rel):
    code, prefix, locale, _, _ = [l for l in LANGS if l[0] == lang][0]
    path = _page_path(rel)
    html = html.replace('<html lang="ru">', f'<html lang="{code}">', 1)
    html = html.replace('<meta property="og:locale" content="ru_RU">', f'<meta property="og:locale" content="{locale}">', 1)
    if rel != "404.html":
        alts = "".join(f'<link rel="alternate" hreflang="{c}" href="{SITE}{p}{path}">\n' for c, p, *_ in LANGS)
        alts += f'<link rel="alternate" hreflang="x-default" href="{SITE}{path}">\n'
        html = _re2.sub(r'(<link rel="canonical"[^>]*>\n)', lambda mo: mo.group(1) + alts, html, count=1)
    sw = "".join(
        f'<a class="lang__link" href="{p}{path if rel != "404.html" else "/"}" hreflang="{c}" lang="{c}" aria-label="{n}"'
        + (' aria-current="true"' if c == code else "") + f'>{lab}</a>'
        for c, p, _, lab, n in LANGS)
    switch = f'<nav class="lang" aria-label="Язык / Мова / Тіл">{sw}</nav>'
    html = html.replace('<div class="header__actions">', '<div class="header__actions">\n' + switch, 1)
    html = html.replace('<nav class="mobile-nav" id="mobile-nav"', '<nav class="mobile-nav" id="mobile-nav" data-langs', 1)
    html = html.replace('</nav>\n</header>', f'<div class="mobile-nav__langs">{switch}</div>\n</nav>\n</header>', 1)
    return html


def _bodies(html, lang):
    return _re2.sub(r"<!--LOC:([\w-]+)-->", lambda mo: (BODIES[mo.group(1)].get(lang) or BODIES[mo.group(1)].get("ru") or ""), html)


def build_lang_pages(pages_ru):
    for c in ("uk", "kk"):  # content from the admin panel wins over the old dictionary
        TR[c].update(EXTRA[c])
    out = {}
    for rel, html in pages_ru.items():
        out[rel] = _finalize(_bodies(html, "ru"), "ru", rel)
        for code, prefix, *_ in LANGS[1:]:
            t = _translate(html, code)
            t = _bodies(t, code)
            t = _prefix_links(t, prefix)
            out[prefix.lstrip("/") + "/" + rel] = _finalize(t, code, rel)
    return out


_RU = {rel: fn() for rel, fn in PAGES.items()}
_ALL = build_lang_pages(_RU)
for rel, html in _ALL.items():
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(_ext(html))
print("wrote", len(_ALL), "pages (ru + ua + kz)")

# ---------- sitemap.xml (with language alternates) ----------
import datetime as _dt
_TODAY = os.environ.get("MSGR_DATE") or _dt.date.today().isoformat()
_LASTMOD = {f'/blog/{a["slug"]}/': a.get("updated") or a["date"] for a in ARTICLES}
_urls = []
for rel in PAGES:
    if rel == "404.html":
        continue
    path = _page_path(rel)
    _prio = "1.0" if path == "/" else ("0.6" if path.startswith("/blog/") or path == "/privacy/" else "0.8")
    alts = "".join(f'<xhtml:link rel="alternate" hreflang="{c}" href="{SITE}{px}{path}"/>' for c, px, *_ in LANGS)
    for c, px, *_ in LANGS:
        _urls.append(f"  <url><loc>{SITE}{px}{path}</loc><lastmod>{_LASTMOD.get(path, _TODAY)}</lastmod><priority>{_prio}</priority>{alts}</url>")
open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(_urls) + "\n</urlset>\n")
print("wrote sitemap.xml", len(_urls), "urls")

# ---------- data for scripts + the future web app ----------
_site_data = {"packages": [{"id": p["id"], "price": p["price"],
                            "name": {c: (p["name"].get(c) or p["name"]["ru"]) for c in ("ru", "uk", "kk")},
                            "quiz": {c: ((p.get("quizText") or {}).get(c) or (p.get("quizText") or {}).get("ru") or "") for c in ("ru", "uk", "kk")}}
                           for p in PK]}
os.makedirs(os.path.join(OUT, "assets", "js"), exist_ok=True)
open(os.path.join(OUT, "assets", "js", "site-data.js"), "w", encoding="utf-8").write(
    "window.MSGR_DATA=" + json.dumps(_site_data, ensure_ascii=False) + ";\n")
os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
json.dump({"_comment": "Generated from content/packages.json by tools/build_pages.py — edit in the admin panel, not here.",
           "currency": _PKDATA.get("currency", "EUR"), "packages": PK}, open(os.path.join(OUT, "data", "packages.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("wrote assets/js/site-data.js + data/packages.json")
