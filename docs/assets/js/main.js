/* MSGR — site behaviour (no dependencies).
   Each block is independent so it can move into a component later. */
(function () {
  document.documentElement.classList.add('js');
  var CFG = window.MSGR_CONFIG || {};
  /* ---------- UI texts per language (ru = root, uk = /ua/, kk = /kz/) ---------- */
  var LANG = (document.documentElement.lang || 'ru').slice(0, 2);
  var T = {
    ru: {
      needConsent: 'Пожалуйста, подтвердите согласие на обработку данных.',
      needName: 'Пожалуйста, укажите имя и корректный email.',
      sending: 'Отправляем…',
      sent: 'Спасибо! Заявка отправлена — мы свяжемся с вами в рабочее время.',
      failed: 'Не удалось отправить автоматически — открываем вашу почту. Также можно написать нам в WhatsApp.',
      next: 'Далее', result: 'Показать результат',
      masterT: 'Магистратура в Греции — реальный вариант',
      masterX: 'В магистратуру документы подаются напрямую в вуз. Мы подберём программы под ваш диплом и проверим требования и стоимость.',
      goodT: 'Шансы хорошие',
      goodX: 'Поступление по квоте для иностранцев идёт по среднему баллу аттестата — с вашими оценками выбор факультетов будет широким.',
      midT: 'Шансы есть — важна стратегия',
      midX: 'Со средним баллом ниже конкурс на популярные факультеты выше, но правильный выбор вузов и порядка приоритетов заметно повышает шансы.',
      eu: ' Для выпускников школ ЕС действует отдельная категория — уточним условия.',
      noGreek: ' Знать греческий для подачи не нужно — на язык будет год после зачисления.',
      tNext: 'Заявки иностранцев принимаются раз в год, обычно в начале июля. Начните готовить документы сейчас — на апостиль и переводы уходит несколько месяцев.',
      tLater: 'Отлично — есть время спокойно подготовить документы и выбрать программы. Начните за 6–8 месяцев до подачи.',
      tExplore: 'Начните с консультации: разберём варианты и сроки, без обязательств.',
      pk: {
        bronze: ['Бронзовый · €1 300', 'Подбор вуза и пошаговые инструкции — для тех, кто готов действовать сам.'],
        silver: ['Серебряный · €2 500', 'Документы, переводы и подача заявки — полностью за вас.'],
        gold: ['Золотой · €5 000', 'Поступление плюс переезд: жильё, встреча, страховка, ВНЖ через юриста.'],
        brilliant: ['Бриллиантовый · €5 700', 'Всё под ключ с гарантиями — родители следят за процессом.']
      }
    },
    uk: {
      needConsent: 'Будь ласка, підтвердьте згоду на обробку даних.',
      needName: 'Будь ласка, вкажіть ім’я та коректний email.',
      sending: 'Надсилаємо…',
      sent: 'Дякуємо! Заявку надіслано — ми зв’яжемося з вами в робочий час.',
      failed: 'Не вдалося надіслати автоматично — відкриваємо вашу пошту. Також можна написати нам у WhatsApp.',
      next: 'Далі', result: 'Показати результат',
      masterT: 'Магістратура в Греції — реальний варіант',
      masterX: 'До магістратури документи подаються безпосередньо до вишу. Ми підберемо програми під ваш диплом і перевіримо вимоги та вартість.',
      goodT: 'Шанси добрі',
      goodX: 'Вступ за квотою для іноземців відбувається за середнім балом атестата — з вашими оцінками вибір факультетів буде широким.',
      midT: 'Шанси є — важлива стратегія',
      midX: 'З нижчим середнім балом конкурс на популярні факультети вищий, але правильний вибір вишів і порядку пріоритетів помітно підвищує шанси.',
      eu: ' Для випускників шкіл ЄС діє окрема категорія — уточнимо умови.',
      noGreek: ' Знати грецьку для подачі не потрібно — на мову буде рік після зарахування.',
      tNext: 'Заявки іноземців приймають раз на рік, зазвичай на початку липня. Почніть готувати документи вже зараз — на апостиль і переклади йде кілька місяців.',
      tLater: 'Чудово — є час спокійно підготувати документи та обрати програми. Почніть за 6–8 місяців до подачі.',
      tExplore: 'Почніть із консультації: розберемо варіанти та строки, без зобов’язань.',
      pk: {
        bronze: ['Бронзовий · €1 300', 'Підбір вишу та покрокові інструкції — для тих, хто готовий діяти сам.'],
        silver: ['Срібний · €2 500', 'Документи, переклади та подача заявки — повністю за вас.'],
        gold: ['Золотий · €5 000', 'Вступ плюс переїзд: житло, зустріч, страховка, посвідка через юриста.'],
        brilliant: ['Діамантовий · €5 700', 'Усе під ключ із гарантіями — батьки стежать за процесом.']
      }
    },
    kk: {
      needConsent: 'Деректерді өңдеуге келісіміңізді растаңыз.',
      needName: 'Атыңызды және дұрыс email көрсетіңіз.',
      sending: 'Жіберілуде…',
      sent: 'Рақмет! Өтінім жіберілді — жұмыс уақытында сізбен байланысамыз.',
      failed: 'Автоматты түрде жіберу мүмкін болмады — поштаңызды ашамыз. Бізге WhatsApp арқылы да жаза аласыз.',
      next: 'Әрі қарай', result: 'Нәтижені көрсету',
      masterT: 'Грекиядағы магистратура — нақты мүмкіндік',
      masterX: 'Магистратураға құжаттар тікелей ЖОО-ға тапсырылады. Дипломыңызға сай бағдарламаларды таңдап, талаптар мен құнын тексереміз.',
      goodT: 'Мүмкіндігіңіз жақсы',
      goodX: 'Шетелдіктерге арналған квота бойынша қабылдау аттестаттың орташа балы бойынша жүреді — сіздің бағаларыңызбен факультет таңдауы кең болады.',
      midT: 'Мүмкіндік бар — стратегия маңызды',
      midX: 'Орташа балл төмен болса, танымал факультеттерге бәсеке жоғары, бірақ ЖОО мен басымдық ретін дұрыс таңдау мүмкіндікті айтарлықтай арттырады.',
      eu: ' ЕО мектептерінің түлектері үшін жеке санат бар — шарттарын нақтылаймыз.',
      noGreek: ' Өтінім беру үшін грек тілін білу қажет емес — қабылданғаннан кейін тіл үйренуге бір жыл беріледі.',
      tNext: 'Шетелдіктердің өтінімдері жылына бір рет, әдетте шілденің басында қабылданады. Құжаттарды қазірден дайындай бастаңыз — апостиль мен аудармаға бірнеше ай кетеді.',
      tLater: 'Тамаша — құжаттарды асықпай дайындап, бағдарламаларды таңдауға уақыт бар. Өтінім беруден 6–8 ай бұрын бастаңыз.',
      tExplore: 'Кеңестен бастаңыз: нұсқалар мен мерзімдерді міндеттемесіз талдаймыз.',
      pk: {
        bronze: ['Қола · €1 300', 'ЖОО таңдау және қадамдық нұсқаулық — өзі әрекет етуге дайындарға.'],
        silver: ['Күміс · €2 500', 'Құжаттар, аударма және өтінім беру — толығымен біз жасаймыз.'],
        gold: ['Алтын · €5 000', 'Түсу және көшу: тұрғын үй, қарсы алу, сақтандыру, заңгер арқылы ықтиярхат.'],
        brilliant: ['Бриллиант · €5 700', 'Барлығы кепілдікпен толық — ата-аналар процесті бақылайды.']
      }
    }
  };
  var L = T[LANG] || T.ru;

  function $all(sel, root) { return [].slice.call((root || document).querySelectorAll(sel)); }

  /* ---------- Mobile menu ---------- */
  var burger = document.querySelector('.burger');
  var mobileNav = document.getElementById('mobile-nav');
  if (burger && mobileNav) {
    var closeMenu = function () { mobileNav.classList.remove('is-open'); burger.setAttribute('aria-expanded', 'false'); };
    burger.addEventListener('click', function () {
      var open = mobileNav.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    $all('a', mobileNav).forEach(function (a) { a.addEventListener('click', closeMenu); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && mobileNav.classList.contains('is-open')) { closeMenu(); burger.focus(); }
    });
  }

  /* ---------- Scroll reveal ---------- */
  var items = $all('.reveal');
  window.__reveal = function (root) { $all('.reveal', root).forEach(function (el) { if (window.__io) window.__io.observe(el); else el.classList.add('is-visible'); }); };
  if ('IntersectionObserver' in window) {
    var io = window.__io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ---------- Tabs (package switcher) ---------- */
  $all('[data-tabs]').forEach(function (root) {
    var tabs = $all('[role=tab]', root);
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.getAttribute('aria-controls'));
        if (panel) panel.hidden = !on;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(t); });
      t.addEventListener('keydown', function (e) {
        var n = null;
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') n = tabs[(i + 1) % tabs.length];
        if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (e.key === 'Home') n = tabs[0];
        if (e.key === 'End') n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
  });

  /* ---------- Footer year ---------- */
  $all('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---------- Cookie consent (Google Consent Mode v2) ---------- */
  var cookie = document.getElementById('cookie');
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function setCookieOffset() {
    if (!cookie) return;
    document.body.style.setProperty('--cookie-h', cookie.hidden ? '0px' : (cookie.offsetHeight + 16) + 'px');
    document.body.classList.toggle('has-cookie', !cookie.hidden);
  }
  function showCookie(show) { if (!cookie) return; cookie.hidden = !show; setCookieOffset(); }
  if (cookie) {
    if (!store('msgr-consent')) showCookie(true);
    $all('[data-consent]', cookie).forEach(function (b) {
      b.addEventListener('click', function () {
        var all = b.getAttribute('data-consent') === 'all';
        store('msgr-consent', all ? 'all' : 'necessary');
        if (typeof window.gtag === 'function') {
          var v = all ? 'granted' : 'denied';
          window.gtag('consent', 'update', { ad_storage: v, ad_user_data: v, ad_personalization: v, analytics_storage: v });
        }
        showCookie(false);
      });
    });
    window.addEventListener('resize', setCookieOffset);
  }
  $all('[data-cookie-settings]').forEach(function (b) { b.addEventListener('click', function () { showCookie(true); var f = cookie && cookie.querySelector('button'); if (f) f.focus(); }); });

  /* ---------- Floating messenger button ---------- */
  $all('[data-fab]').forEach(function (fab) {
    var btn = fab.querySelector('.fab__btn'), menu = fab.querySelector('.fab__menu');
    function set(open) { fab.classList.toggle('is-open', open); menu.hidden = !open; btn.setAttribute('aria-expanded', open ? 'true' : 'false'); }
    btn.addEventListener('click', function () { set(menu.hidden); });
    document.addEventListener('click', function (e) { if (!fab.contains(e.target)) set(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !menu.hidden) { set(false); btn.focus(); } });
  });

  /* ---------- Filter chips (universities) ---------- */
  $all('[data-filter]').forEach(function (bar) {
    var target = document.querySelector('[data-filter-target]');
    $all('.chip', bar).forEach(function (chip) {
      chip.addEventListener('click', function () {
        $all('.chip', bar).forEach(function (c) { c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
        var v = chip.getAttribute('data-value');
        $all('[data-group]', target).forEach(function (card) {
          card.hidden = !(v === 'all' || card.getAttribute('data-group') === v);
          if (!card.hidden) card.classList.add('is-visible');
        });
      });
    });
  });

  /* ---------- FAQ search ---------- */
  var fs = document.querySelector('[data-faq-search]');
  if (fs) {
    var empty = document.querySelector('[data-faq-empty]');
    fs.addEventListener('input', function () {
      var q = fs.value.trim().toLowerCase(), any = false;
      $all('.faq__group').forEach(function (g) {
        var groupHas = false;
        $all('.faq__item', g).forEach(function (it) {
          var hit = !q || it.textContent.toLowerCase().indexOf(q) > -1;
          it.hidden = !hit; if (hit) groupHas = true;
          if (q && hit) it.open = true; else if (!q) it.open = false;
        });
        g.hidden = !groupHas; if (groupHas) { any = true; g.classList.add('is-visible'); }
      });
      if (empty) empty.hidden = any;
    });
  }

  /* ---------- Leads: contact form + quiz ---------- */
  function mailtoFallback(d) {
    var to = CFG.fallbackEmail || 'mystudygr1@gmail.com';
    var name = ((d.name || '') + ' ' + (d.lastname || '')).trim();
    var subject = 'Заявка с сайта mystudygr.com' + (name ? ' — ' + name : '');
    var body = 'Источник: ' + d.source + '\nИмя: ' + name + '\nEmail: ' + (d.email || '') + '\nТелефон/мессенджер: ' + (d.phone || '') + '\n\n' + (d.message || '');
    window.location.href = 'mailto:' + to + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  }
  $all('form[data-contact-form]').forEach(function (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var status = form.querySelector('.form__status');
      var nameEl = form.querySelector('[name=name]'), mailEl = form.querySelector('[name=email]'), cons = form.querySelector('[name=consent]');
      var bad = [];
      [nameEl, mailEl, cons].forEach(function (el) { if (el) el.removeAttribute('aria-invalid'); });
      if (nameEl && !nameEl.value.trim()) bad.push(nameEl);
      if (mailEl && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(mailEl.value.trim())) bad.push(mailEl);
      if (cons && !cons.checked) bad.push(cons);
      function say(msg, cls) { if (!status) return; status.className = 'form__status' + (cls ? ' ' + cls : ''); status.textContent = msg; }
      if (bad.length) {
        bad.forEach(function (el) { el.setAttribute('aria-invalid', 'true'); });
        say(cons && bad.indexOf(cons) > -1 && bad.length === 1 ? L.needConsent : L.needName, 'is-error');
        bad[0].focus();
        return;
      }
      var fd = new FormData(form);
      if (fd.get('website')) return; // bot
      var d = { source: form.getAttribute('data-source') || 'Сайт', page: location.pathname, lang: LANG };
      fd.forEach(function (v, k) { if (k !== 'website') d[k] = v; });
      var btn = form.querySelector('[type=submit]');
      if (btn) btn.disabled = true;
      say(L.sending);
      var done = function () {
        say(L.sent, 'is-ok');
        form.reset(); if (btn) btn.disabled = false;
        if (window.dataLayer) window.dataLayer.push({ event: 'lead_submit', lead_source: d.source });
      };
      var fail = function () {
        if (btn) btn.disabled = false;
        say(L.failed, 'is-error');
        mailtoFallback(d);
      };
      if (!CFG.leadEndpoint || !window.fetch) { fail(); return; }
      fetch(CFG.leadEndpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) })
        .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
        .then(function (j) { if (j && j.ok) done(); else fail(); })
        .catch(fail);
    });
  });

  /* ---------- Quiz "Проверить шансы" ---------- */
  $all('[data-quiz]').forEach(function (quiz) {
    var steps = $all('.quiz__step', quiz), i = 0;
    var next = quiz.querySelector('[data-quiz-next]'), back = quiz.querySelector('[data-quiz-back]');
    var bar = quiz.querySelector('[data-quiz-progress]'), form = quiz.querySelector('[data-quiz-form]'), res = quiz.querySelector('[data-quiz-result]');
    function answered(n) { return !!steps[n].querySelector('input:checked'); }
    function render() {
      steps.forEach(function (s, k) { s.hidden = k !== i; });
      back.hidden = i === 0;
      next.disabled = !answered(i);
      next.textContent = i === steps.length - 1 ? L.result : L.next;
      bar.style.width = (i / steps.length * 100) + '%';
    }
    steps.forEach(function (s) {
      s.addEventListener('change', function () {
        next.disabled = false;
        setTimeout(function () { if (i < steps.length - 1 && answered(i)) { i++; render(); var f = steps[i].querySelector('input'); if (f) f.focus(); } }, 260);
      });
    });
    back.addEventListener('click', function () { if (i > 0) { i--; render(); } });
    next.addEventListener('click', function () { if (!answered(i)) return; if (i < steps.length - 1) { i++; render(); } else { show(); } });
    var restart = quiz.querySelector('[data-quiz-restart]');
    if (restart) restart.addEventListener('click', function () { form.reset(); i = 0; res.hidden = true; form.hidden = false; render(); });

    function val(n) { var el = form.querySelector('[name=' + n + ']:checked'); return el ? el.value : ''; }
    function label(n) { var el = form.querySelector('[name=' + n + ']:checked'); return el ? el.parentNode.textContent.trim() : ''; }
    var PKID = { bronze: 'pkg-bronze', silver: 'pkg-silver', gold: 'pkg-gold', brilliant: 'pkg-brilliant' };
    // live prices/names from the admin panel (assets/js/site-data.js); falls back to the built-in texts
    function fmtEur(n) { return '€' + String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ' '); }
    function pkInfo(pk, lang) {
      var d = (window.MSGR_DATA && window.MSGR_DATA.packages || []).filter(function (p) { return p.id === pk; })[0];
      var fb = (T[lang] || T.ru).pk[pk];
      if (!d) return fb;
      return [(d.name[lang] || d.name.ru) + ' · ' + fmtEur(d.price), d.quiz[lang] || d.quiz.ru || fb[1]];
    }
    function show() {
      bar.style.width = '100%';
      var level = val('level'), grade = val('grade'), school = val('school'), help = val('help'), when = val('when');
      var title, text;
      if (level === 'master') { title = L.masterT; text = L.masterX; }
      else if (grade === 'high' || grade === 'mid') { title = L.goodT; text = L.goodX; }
      else { title = L.midT; text = L.midX; }
      if (school === 'eu') text += L.eu;
      if (val('greek') === 'none') text += L.noGreek;
      var pk = help === 'self' ? 'bronze' : help === 'docs' ? 'silver' : help === 'full' ? 'gold' : 'brilliant';
      var time = when === 'next' ? L.tNext : when === 'later' ? L.tLater : L.tExplore;
      res.querySelector('[data-r-title]').textContent = title;
      res.querySelector('[data-r-text]').textContent = text;
      var info = pkInfo(pk, T[LANG] ? LANG : 'ru');
      res.querySelector('[data-r-pkg]').textContent = info[0];
      res.querySelector('[data-r-pkgtext]').textContent = info[1];
      var link = res.querySelector('[data-r-pkglink]'); link.setAttribute('href', link.getAttribute('href').split('#')[0] + '#' + PKID[pk]);
      res.querySelector('[data-r-time]').textContent = time;
      var summary = ['level', 'school', 'grade', 'greek', 'when', 'help'].map(function (k) { return '• ' + label(k); }).join('\n');
      res.querySelector('[data-r-summary]').value = 'Ответы теста:\n' + summary + '\nРекомендация: ' + pkInfo(pk, 'ru')[0] + ' (язык сайта: ' + LANG + ')';
      form.hidden = true; res.hidden = false; res.focus();
      if (window.dataLayer) window.dataLayer.push({ event: 'quiz_complete', quiz_package: pk });
    }
    render();
  });
})();
