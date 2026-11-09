# MSGR — mystudygr.com (redesign)

New version of **MY STUDY IN GREECE** (mystudygr.com) in the approved "Hybrid" style
(Classic + Minimal: navy/gold, Playfair Display + Golos Text, subtle motion).
The original logo is unchanged, and every page URL and external link is the same as on the live site.

## Structure

```
MSGR/
├─ index.html                 → https://mystudygr.com/
├─ about-us/index.html        → /about-us/
├─ learning/index.html        → /learning/
├─ услуги/index.html          → /%d1%83%d1%81%d0%bb%d1%83%d0%b3%d0%b8/  (same URL as today)
├─ contacts/index.html        → /contacts/
├─ universities/  faq/  calendar/  quiz/  blog/  privacy/   (new pages)
├─ blog/<article>/index.html  articles
├─ 404.html                   "page not found"
├─ admin/                     admin panel (PHP): leads inbox + content editor → /admin/
├─ api/lead.php               form/quiz → saved to the database + Telegram + email (PHP)
├─ api/inc/bootstrap.php      shared code (database, notifications) for api/ and admin/
├─ api/config.example.php     copy to api/config.php and fill in
├─ content/*.json             EDITABLE CONTENT: packages, FAQ, calendar, universities, articles (RU/UA/KZ)
├─ .github/workflows/         build + deploy automation (GitHub Actions)
├─ MIGRATION.md               step-by-step plan for moving mystudygr.com from WordPress
├─ sitemap.xml, robots.txt, .htaccess
├─ assets/
│  ├─ css/tokens.css          design tokens (colours, type, spacing, motion)
│  ├─ css/main.css            components (header, hero, card, pkg, compare, form, footer…)
│  ├─ js/config.js            site settings (form endpoint)
│  ├─ js/main.js              menu, reveal, tabs, cookies, floating button, forms, quiz, FAQ search
│  └─ img/logo.png, favicon.jpg   (original files from the current site)
├─ data/packages.json         generated copy of the packages (for the future web app)
└─ tools/build_pages.py       regenerates every page (RU + UA + KZ) from content/ + shared header/footer
```

## Edit & rebuild

Shared parts (header, footer, contact block) and page text live in `tools/build_pages.py`.
Edit there and rebuild, so every page stays in sync:

```
python tools/build_pages.py
```

Prices, packages, FAQ, calendar, universities and articles are read from `content/*.json`.
Normally they are edited in the **admin panel** (below); after a save, GitHub Actions rebuilds the site by itself.

## Preview locally

Links are root-relative (`/about-us/`) so they match the live URLs exactly.
That's why you need a small local server; opening files by double-click won't follow the links.

```
cd MSGR
python -m http.server 8000      # then open http://localhost:8000
# or:  npx serve .
```

## Kept from the current site

- Google Tag Manager `GTM-MCM45RZH`
- Phone `tel:306942770701`, WhatsApp, Viber, Telegram (`t.me/Igor_Toikin`), Facebook group
- Instagram: `instagram.com/_mystudygr_` (confirmed correct; the old `_u/mystudygr.com` link was removed)
- Email `mystudygr1@gmail.com` (now clickable)

## Going live

The live site is on **Beget** (Apache + PHP 8.2). Follow **MIGRATION.md** step by step — it keeps the Google ranking
(301 redirects for every old WordPress URL are already in `.htaccess`).

## Admin panel (`/admin/`)

What it does:
- **Заявки** — every form/quiz request is saved in a database (SQLite) *before* Telegram/email, so nothing is lost.
  Statuses (новая → в работе → стал клиентом / закрыта / спам), notes, search, filters by language/date, export for Excel.
- **Цены и пакеты, Вопросы, Календарь, Университеты, Статьи** — forms with RU / UA / KZ tabs
  (an orange dot = translation missing; the site then shows Russian). Articles have a simple text editor.
- **Сохранить и опубликовать** commits the change to GitHub → GitHub Actions rebuilds all pages and uploads them
  to the hosting (≈1–2 min). **История изменений** shows every version and can roll back with one click.
- Users: administrator (everything) and editor (leads + content). Login protection: hashed passwords,
  lock after 8 wrong attempts, CSRF protection, 8-hour sessions, hidden from Google.

Setup (once, on the server):
1. `api/config.php` (from `config.example.php`): fill `admin_setup_key` (any long secret), `github_token`, Telegram.
2. Open `https://mystudygr.com/admin/` → enter the setup key → create your account → then **clear `admin_setup_key`**.
3. Create the owner's account in **Пользователи**.
4. GitHub token: github.com → Settings → Developer settings → Fine-grained tokens → repository **J-ntk/MSGR** only,
   permissions **Contents: Read and write**, **Actions: Read-only**. Paste into `github_token`.

The leads database is stored in `msgr-data/` next to `public_html` (not reachable from the web).
Include that folder in hosting backups.

Local testing: in `api/config.php` set `'content_local_dir' => '/path/to/MSGR'` and `'data_dir' => '/tmp/msgr-data'` —
the admin then edits the local `content/` files instead of GitHub.

## Automatic build & deploy (GitHub Actions)

`.github/workflows/build-deploy.yml` runs on every push that touches content, code or assets (including admin saves):
builds the site, refreshes `docs/` (GitHub Pages preview), commits the generated pages, and — when the
secrets `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD` and the variable `FTP_DIR` are set — uploads the site to Beget.
Before those secrets exist it only builds (safe). It never uploads `tools/`, `content/`, `docs/` or `api/config.php`.

## Contact form & quiz → Telegram / email

Both forms POST JSON to `assets/js/config.js → leadEndpoint` (default `/api/lead.php`).
1. Copy `api/config.example.php` → `api/config.php`.
2. Telegram: create a bot with @BotFather, put the token and your chat id in config.php.
3. Email: set `mail_to`; `mail_from` should be a mailbox on mystudygr.com (Beget → Почта).
4. Done. Every lead is first saved to the admin database, then sent. The endpoint validates input, has a spam trap,
   a rate limit (5 per 10 min per visitor) and accepts only requests from mystudygr.com.
If the endpoint is missing or fails, the site falls back to opening the visitor's mail app, so no enquiry is lost.
`config.php` is blocked from the web by `api/.htaccess`; never commit it to Git.

## Cookies & GDPR

- Google Tag Manager runs in **Consent Mode v2**: analytics/ads storage is denied until the visitor clicks "Принять все".
  In GTM, make sure tags use the built-in consent checks (Admin → Container settings → Enable consent overview).
- Choice is stored in `localStorage` (`msgr-consent`); the footer link "Настройки cookies" reopens the banner.
- `/privacy/` is a **draft**: fill in [company name], [ΑΦΜ], [address], [retention period] and have a lawyer review it.

## Content that must be kept up to date

- **Calendar** (`/calendar/`, admin → Календарь): 2026 dates from the Ministry of Education. Update when 2027 dates are announced (usually late spring).
- **Tuition wording**: since law 5094/2024 public universities may also admit foreigners to Greek-taught programmes for a fee; the FAQ explains this. Avoid absolute "always free" claims.
- **Universities** list is informational, not partners.

## Toward the web app

The site was built so it can move into a web app without redesigning:

| Today (static)            | Web app (e.g. Next.js / React + Supabase)              |
|---------------------------|--------------------------------------------------------|
| `tokens.css` variables    | Tailwind theme / CSS variables in the app              |
| BEM-style classes         | Components: `Header`, `Hero`, `PackageCard`, `CompareTable`, `ContactForm`, `Footer` |
| `data/packages.json`      | `packages` table in the database (admin can edit prices) |
| mailto form               | `POST /api/leads` → database + email/Telegram notification |
| Static pages              | Same URLs as SSR/SSG pages (keeps SEO)                 |

Possible app features: a student/parent cabinet with application status (the Brilliant package promises
real-time tracking), document upload and checklist, staged payments for each package,
a lead CRM for the team, and RU/EN/GR languages.

## GitHub repository & GitHub Pages

- Repo root = the site source (paths for the real domain, mystudygr.com).
- `docs/` = the same site built for GitHub Pages at `https://j-ntk.github.io/MSGR/` (all links prefixed with `/MSGR`, forms fall back to email, hidden from Google).
- `docs/` is rebuilt automatically by GitHub Actions after every push.
- GitHub → Settings → Pages → Source: *Deploy from a branch*, Branch: `main`, Folder: `/docs`.

## Языки (RU / UA / KZ)

- Русский — в корне сайта (`/`), украинский — `/ua/`, казахский (кириллица) — `/kz/`.
- Редактируемые тексты (пакеты, FAQ, календарь, вузы, статьи) — в админ-панели, у каждого поля вкладки RU / UA / KZ.
- Постоянные тексты страниц генерируются из `tools/build_pages.py`; их переводы лежат в `tools/i18n/`:
  `strings_ru.json` (исходные русские строки) и `uk.tsv` / `kk.tsv` (строка = `номер<TAB>перевод`).
- Чтобы поправить перевод: измените строку в `uk.tsv` или `kk.tsv` и запустите `python tools/build_pages.py`.
- Заголовки h1 переводятся целиком (словарь `H1` в генераторе) — для правильного порядка слов.
- В каждой странице есть hreflang (ru, uk, kk, x-default), sitemap.xml содержит все 3 версии.
- Заявки с UA/KZ приходят в Telegram/почту с пометкой «Язык сайта».
- Тексты UA и KZ сделаны машинно-экспертным переводом — перед запуском желательна вычитка носителем.
