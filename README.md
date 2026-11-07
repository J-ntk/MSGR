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
├─ api/lead.php               form/quiz → Telegram + email (PHP)
├─ api/config.example.php     copy to api/config.php and fill in
├─ sitemap.xml, robots.txt, .htaccess
├─ assets/
│  ├─ css/tokens.css          design tokens (colours, type, spacing, motion)
│  ├─ css/main.css            components (header, hero, card, pkg, compare, form, footer…)
│  ├─ js/config.js            site settings (form endpoint)
│  ├─ js/main.js              menu, reveal, tabs, cookies, floating button, forms, quiz, FAQ search
│  └─ img/logo.png, favicon.jpg   (original files from the current site)
├─ data/packages.json         the 5 service packages — single source of truth
└─ tools/build_pages.py       regenerates all 5 pages from shared header/footer
```

## Edit & rebuild

Shared parts (header, footer, contact block) and page text live in `tools/build_pages.py`.
Edit there and rebuild, so every page stays in sync:

```
python tools/build_pages.py
```

Prices and package contents are read from `data/packages.json`, so to change a price,
edit the JSON and rebuild.

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

- **Static hosting (Hostinger, Netlify, Cloudflare Pages…):** upload the folder contents to the site root.
  The server must serve the Cyrillic folder `услуги/` (all common hosts do).
- **Staying on WordPress/Elementor:** use the pages as the visual reference and rebuild them in Elementor
  with the values from `tokens.css`.

## Contact form & quiz → Telegram / email

Both forms POST JSON to `assets/js/config.js → leadEndpoint` (default `/api/lead.php`).
1. Copy `api/config.example.php` → `api/config.php`.
2. Telegram: create a bot with @BotFather, put the token and your chat id in config.php.
3. Email: set `mail_to`; `mail_from` should be a mailbox on mystudygr.com (Hostinger → Emails).
4. Done. The endpoint validates input, has a spam trap, a rate limit (5 per 10 min per IP) and accepts only requests from mystudygr.com.
If the endpoint is missing or fails, the site falls back to opening the visitor's mail app, so no enquiry is lost.
`config.php` is blocked from the web by `api/.htaccess`; never commit it to Git.

## Cookies & GDPR

- Google Tag Manager runs in **Consent Mode v2**: analytics/ads storage is denied until the visitor clicks "Принять все".
  In GTM, make sure tags use the built-in consent checks (Admin → Container settings → Enable consent overview).
- Choice is stored in `localStorage` (`msgr-consent`); the footer link "Настройки cookies" reopens the banner.
- `/privacy/` is a **draft**: fill in [company name], [ΑΦΜ], [address], [retention period] and have a lawyer review it.

## Content that must be kept up to date

- **Calendar** (`/calendar/`, `CALENDAR` in tools/build_pages.py): 2026 dates from the Ministry of Education. Update when 2027 dates are announced (usually late spring).
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
- Rebuild docs after changes (PowerShell):
  ```
  $env:MSGR_OUT="docs"; $env:MSGR_BASE="/MSGR"; python tools/build_pages.py
  ```
  then copy `assets/` and `data/` into `docs/` (already there after the first build).
- GitHub → Settings → Pages → Source: *Deploy from a branch*, Branch: `main`, Folder: `/docs`.
