<?php
/**
 * MSGR admin panel — https://mystudygr.com/admin/
 * Leads inbox + editing of website content (published through GitHub → hosting).
 */
declare(strict_types=1);
require __DIR__ . '/inc/core.php';
require __DIR__ . '/inc/content.php';
require __DIR__ . '/inc/layout.php';

if (!msgr_configured()) {
    page_start('Настройка', '', true);
    echo '<div class="card narrow"><h1>Почти готово</h1><p>Создайте файл <code>api/config.php</code> из <code>api/config.example.php</code> и заполните его. Подробности — в README, раздел «Админ-панель».</p></div>';
    page_end();
    exit;
}

$p = $_GET['p'] ?? 'dashboard';
$isPost = $_SERVER['REQUEST_METHOD'] === 'POST';
if ($isPost) csrf_check();

/* ============================== first run: create the first admin ============================== */
if (users_count() === 0) {
    $cfg = msgr_config();
    $err = '';
    if ($isPost && $p === 'setup') {
        if ($cfg['admin_setup_key'] === '' || !hash_equals($cfg['admin_setup_key'], (string) ($_POST['key'] ?? ''))) {
            $err = 'Неверный ключ настройки (секрет ADMIN_SETUP_KEY в GitHub).';
        } else {
            $err = create_user((string) $_POST['username'], (string) $_POST['name'], (string) $_POST['password'], 'admin') ?? '';
            if ($err === '') {
                try_login((string) $_POST['username'], (string) $_POST['password']);
                audit('setup', 'создан первый администратор');
                flash('Аккаунт создан. Теперь удалите секрет ADMIN_SETUP_KEY в GitHub и запустите Build and deploy.', 'warn');
                redirect('/admin/');
            }
        }
    }
    page_start('Первый вход', '', true); ?>
    <form class="card narrow" method="post" action="/admin/?p=setup" autocomplete="off">
      <?= brand_tile() ?>
      <h1>Создание администратора</h1>
      <?php if ($cfg['admin_setup_key'] === ''): ?>
        <p class="flash flash--warn">Сначала добавьте в GitHub секрет <code>ADMIN_SETUP_KEY</code> (любой длинный секретный текст) и запустите Build and deploy.</p>
      <?php endif; ?>
      <?php if ($err): ?><p class="flash flash--bad"><?= e($err) ?></p><?php endif; ?>
      <?= csrf_field() ?>
      <label>Ключ настройки<input type="password" name="key" required></label>
      <label>Ваше имя<input name="name" required value="<?= e($_POST['name'] ?? '') ?>"></label>
      <label>Логин (латиницей)<input name="username" required pattern="[a-zA-Z0-9._\-]{3,32}" value="<?= e($_POST['username'] ?? '') ?>"></label>
      <label>Пароль (мин. 10 символов)<input type="password" name="password" required minlength="10" autocomplete="new-password"></label>
      <button class="btn btn--primary" type="submit">Создать и войти</button>
    </form>
    <?php page_end();
    exit;
}

/* ============================== login / logout ============================== */
if ($p === 'login') {
    if (current_user()) redirect('/admin/');
    $err = '';
    if ($isPost) {
        if (login_blocked()) $err = 'Слишком много попыток. Подождите 15 минут.';
        elseif (try_login((string) ($_POST['username'] ?? ''), (string) ($_POST['password'] ?? ''))) { audit('login'); redirect('/admin/'); }
        else $err = 'Неверный логин или пароль.';
    }
    page_start('Вход', '', true); ?>
    <form class="card narrow" method="post" action="/admin/?p=login">
      <?= brand_tile() ?>
      <h1>Вход в админ-панель</h1>
      <?php if ($err): ?><p class="flash flash--bad"><?= e($err) ?></p><?php endif; ?>
      <?= csrf_field() ?>
      <label>Логин<input name="username" required autocomplete="username" autofocus></label>
      <label>Пароль<input type="password" name="password" required autocomplete="current-password"></label>
      <button class="btn btn--primary" type="submit">Войти</button>
    </form>
    <?php page_end();
    exit;
}
if ($p === 'logout' && $isPost) {
    audit('logout');
    $_SESSION = [];
    session_destroy();
    redirect('/admin/?p=login');
}

$me = require_login();

/* ============================== leads: actions ============================== */
function leads_where(array $q, array &$args): string
{
    $w = ['1=1'];
    if (!empty($q['status']) && isset(LEAD_STATUSES[$q['status']])) { $w[] = 'status = ?'; $args[] = $q['status']; }
    elseif (empty($q['status'])) { $w[] = "status != 'spam'"; }
    if (!empty($q['lang']) && isset(LANG_NAMES[$q['lang']])) { $w[] = 'lang = ?'; $args[] = $q['lang']; }
    if (!empty($q['from'])) { $w[] = 'created_at >= ?'; $args[] = $q['from'] . ' 00:00:00'; }
    if (!empty($q['to'])) { $w[] = 'created_at <= ?'; $args[] = $q['to'] . ' 23:59:59'; }
    if (!empty($q['q'])) {
        $w[] = '(name LIKE ? OR lastname LIKE ? OR email LIKE ? OR phone LIKE ? OR message LIKE ? OR notes LIKE ?)';
        $like = '%' . str_replace(['%', '_'], ['\%', '\_'], (string) $q['q']) . '%';
        array_push($args, $like, $like, $like, $like, $like, $like);
    }
    return implode(' AND ', $w);
}

if ($p === 'leads-export') {
    $args = [];
    $st = db()->prepare('SELECT * FROM leads WHERE ' . leads_where($_GET, $args) . ' ORDER BY created_at DESC');
    $st->execute($args);
    audit('export', 'выгрузка заявок');
    header('Content-Type: text/csv; charset=utf-8');
    header('Content-Disposition: attachment; filename="msgr-zayavki-' . date('Y-m-d') . '.csv"');
    $f = fopen('php://output', 'w');
    fwrite($f, "\xEF\xBB\xBF"); // Excel: UTF-8
    fputcsv($f, ['№', 'Дата', 'Статус', 'Имя', 'Фамилия', 'Email', 'Телефон', 'Источник', 'Язык', 'Сообщение', 'Заметки', 'Страница'], ';');
    foreach ($st as $r) {
        fputcsv($f, [$r['id'], fmt_dt($r['created_at']), LEAD_STATUSES[$r['status']] ?? $r['status'], $r['name'], $r['lastname'], $r['email'],
                     $r['phone'], $r['source'], LANG_NAMES[$r['lang']] ?? $r['lang'], $r['message'], $r['notes'], $r['page']], ';');
    }
    exit;
}

if ($p === 'lead' && $isPost) {
    $id = (int) ($_POST['id'] ?? 0);
    if (($_POST['action'] ?? '') === 'delete') {
        if ($me['role'] !== 'admin') { flash('Удалять заявки может только администратор.', 'bad'); redirect('/admin/?p=lead&id=' . $id); }
        db()->prepare('DELETE FROM leads WHERE id = ?')->execute([$id]);
        audit('lead.delete', "#$id");
        flash("Заявка №$id удалена.");
        redirect('/admin/?p=leads');
    }
    $status = (string) ($_POST['status'] ?? 'new');
    if (!isset(LEAD_STATUSES[$status])) $status = 'new';
    db()->prepare('UPDATE leads SET status = ?, notes = ?, updated_at = ? WHERE id = ?')
        ->execute([$status, clean_str($_POST['notes'] ?? '', 5000), now_str(), $id]);
    audit('lead.update', "#$id → $status");
    flash('Сохранено.');
    redirect('/admin/?p=lead&id=' . $id);
}

if ($p === 'leads' && $isPost) {
    $ids = array_map('intval', (array) ($_POST['ids'] ?? []));
    $status = (string) ($_POST['bulk'] ?? '');
    if ($ids && isset(LEAD_STATUSES[$status])) {
        $in = implode(',', array_fill(0, count($ids), '?'));
        db()->prepare("UPDATE leads SET status = ?, updated_at = ? WHERE id IN ($in)")->execute(array_merge([$status, now_str()], $ids));
        audit('lead.bulk', count($ids) . ' → ' . $status);
        flash('Обновлено заявок: ' . count($ids));
    }
    redirect('/admin/?' . http_build_query(array_merge(['p' => 'leads'], array_intersect_key($_GET, array_flip(['status', 'lang', 'q', 'from', 'to'])))));
}

/* ============================== content: save / restore ============================== */
$cols = content_collections();

if ($p === 'save' && $isPost) {
    $key = (string) ($_POST['c'] ?? '');
    if (!isset($cols[$key])) redirect('/admin/');
    $col = $cols[$key];
    try {
        if (!gh_ready()) throw new RuntimeException('Публикация ещё не подключена — см. инструкцию на этой странице.');
        $data = json_decode((string) ($_POST['data'] ?? ''), true);
        if (!is_array($data)) throw new RuntimeException('Не удалось прочитать данные формы.');
        [$old] = gh_read_json($col['file']);
        $errs = [];
        $clean = validate_collection($key, $data, $old, $errs);
        if ($errs) {
            $_SESSION['draft'][$key] = $data;
            foreach (array_slice(array_unique($errs), 0, 8) as $er) flash($er, 'bad');
            redirect('/admin/?p=edit&c=' . $key . '&draft=1');
        }
        if ($clean == $old) { flash('Изменений нет — сохранять нечего.', 'warn'); redirect('/admin/?p=edit&c=' . $key); }
        $note = trim(clean_str($_POST['note'] ?? '', 120));
        gh_write_json($col['file'], $clean, (string) $_POST['sha'], 'Админ-панель: ' . $col['title'] . ($note ? " — $note" : '') . ' (' . $me['username'] . ')');
        unset($_SESSION['draft'][$key]);
        audit('content.save', $col['title'] . ($note ? " — $note" : ''));
        flash('Сохранено. Сайт обновится автоматически примерно через 1–2 минуты — статус на странице «Обзор».');
    } catch (Throwable $ex) {
        if (isset($data) && is_array($data)) $_SESSION['draft'][$key] = $data;
        flash($ex->getMessage(), 'bad');
        redirect('/admin/?p=edit&c=' . $key . (isset($data) && is_array($data) ? '&draft=1' : ''));
    }
    redirect('/admin/?p=edit&c=' . $key);
}

if ($p === 'restore' && $isPost) {
    $key = (string) ($_POST['c'] ?? '');
    $sha = preg_replace('/[^a-f0-9]/', '', (string) ($_POST['sha'] ?? ''));
    if (!isset($cols[$key]) || !$sha) redirect('/admin/?p=history');
    try {
        [$version] = gh_read_json($cols[$key]['file'], $sha);
        [, $curSha] = gh_read_json($cols[$key]['file']);
        gh_write_json($cols[$key]['file'], $version, $curSha, 'Админ-панель: откат «' . $cols[$key]['title'] . '» к версии ' . substr($sha, 0, 7) . ' (' . $me['username'] . ')');
        audit('content.restore', $cols[$key]['title'] . ' → ' . substr($sha, 0, 7));
        flash('Версия восстановлена. Сайт обновится через 1–2 минуты.');
    } catch (Throwable $ex) {
        flash($ex->getMessage(), 'bad');
    }
    redirect('/admin/?p=history&c=' . $key);
}

/* ============================== users ============================== */
if ($p === 'users' && $isPost) {
    require_login('admin');
    $a = $_POST['action'] ?? '';
    if ($a === 'add') {
        $err = create_user((string) $_POST['username'], (string) $_POST['name'], (string) $_POST['password'], (string) $_POST['role']);
        $err ? flash($err, 'bad') : (flash('Пользователь создан. Передайте логин и пароль лично.') ?? audit('user.add', (string) $_POST['username']));
    } elseif ($a === 'delete') {
        $id = (int) $_POST['id'];
        if ($id === (int) $me['id']) flash('Нельзя удалить самого себя.', 'bad');
        else { db()->prepare('DELETE FROM users WHERE id = ?')->execute([$id]); audit('user.delete', "#$id"); flash('Пользователь удалён.'); }
    } elseif ($a === 'reset') {
        $pw = (string) $_POST['password'];
        if (mb_strlen($pw) < 10) flash('Пароль — минимум 10 символов.', 'bad');
        else { db()->prepare('UPDATE users SET pass_hash = ? WHERE id = ?')->execute([password_hash($pw, PASSWORD_DEFAULT), (int) $_POST['id']]); audit('user.reset', '#' . (int) $_POST['id']); flash('Пароль изменён.'); }
    }
    redirect('/admin/?p=users');
}

if ($p === 'account' && $isPost) {
    $st = db()->prepare('SELECT pass_hash FROM users WHERE id = ?');
    $st->execute([$me['id']]);
    if (!password_verify((string) $_POST['old'], (string) $st->fetchColumn())) flash('Текущий пароль неверный.', 'bad');
    elseif (mb_strlen((string) $_POST['new']) < 10) flash('Новый пароль — минимум 10 символов.', 'bad');
    elseif ($_POST['new'] !== $_POST['new2']) flash('Пароли не совпадают.', 'bad');
    else {
        db()->prepare('UPDATE users SET pass_hash = ?, display_name = ? WHERE id = ?')
            ->execute([password_hash((string) $_POST['new'], PASSWORD_DEFAULT), clean_str($_POST['name'] ?? '', 60) ?: $me['username'], $me['id']]);
        audit('account.password');
        flash('Пароль изменён.');
    }
    redirect('/admin/?p=account');
}

/* ============================== pages ============================== */
switch ($p) {

case 'dashboard':
    $c = msgr_config();
    $cnt = fn(string $sql, array $a = []) => (function () use ($sql, $a) { $s = db()->prepare($sql); $s->execute($a); return (int) $s->fetchColumn(); })();
    $newN = $cnt("SELECT COUNT(*) FROM leads WHERE status='new'");
    $d7 = $cnt("SELECT COUNT(*) FROM leads WHERE status!='spam' AND created_at >= ?", [date('Y-m-d', strtotime('-7 days'))]);
    $d30 = $cnt("SELECT COUNT(*) FROM leads WHERE status!='spam' AND created_at >= ?", [date('Y-m-d', strtotime('-30 days'))]);
    $clients = $cnt("SELECT COUNT(*) FROM leads WHERE status='client'");
    $byLang = db()->query("SELECT lang, COUNT(*) n FROM leads WHERE status!='spam' GROUP BY lang")->fetchAll(PDO::FETCH_KEY_PAIR);
    $recent = db()->query("SELECT * FROM leads WHERE status!='spam' ORDER BY created_at DESC LIMIT 6")->fetchAll();
    $runs = [];
    if (gh_ready()) { try { $runs = gh_last_runs(4); } catch (Throwable $e) {} }
    page_start('Обзор', 'dashboard'); ?>
    <h1>Добрый день, <?= e($me['display_name'] ?: $me['username']) ?></h1>
    <div class="stats">
      <a class="stat stat--hot" href="/admin/?p=leads&status=new"><b><?= $newN ?></b><span>новых заявок</span></a>
      <div class="stat"><b><?= $d7 ?></b><span>за 7 дней</span></div>
      <div class="stat"><b><?= $d30 ?></b><span>за 30 дней</span></div>
      <div class="stat"><b><?= $clients ?></b><span>стали клиентами</span></div>
    </div>
    <div class="cols">
      <section class="card">
        <div class="card__head"><h2>Последние заявки</h2><a href="/admin/?p=leads">Все заявки →</a></div>
        <?php if (!$recent): ?><p class="muted">Заявок пока нет. Они появятся здесь, как только кто-то заполнит форму на сайте.</p><?php endif; ?>
        <ul class="mini">
        <?php foreach ($recent as $l): ?>
          <li><a href="/admin/?p=lead&id=<?= $l['id'] ?>"><b><?= e(trim($l['name'] . ' ' . $l['lastname'])) ?></b> <span class="muted"><?= e($l['source']) ?> · <?= strtoupper(e($l['lang'] === 'uk' ? 'ua' : ($l['lang'] === 'kk' ? 'kz' : 'ru'))) ?></span></a><?= status_badge($l['status']) ?><time><?= fmt_dt($l['created_at']) ?></time></li>
        <?php endforeach; ?>
        </ul>
        <?php if ($byLang): ?><p class="muted small">По языку сайта: <?php foreach ($byLang as $lg => $n) echo e(LANG_NAMES[$lg] ?? $lg) . ' — ' . (int) $n . '; '; ?></p><?php endif; ?>
      </section>
      <section class="card">
        <div class="card__head"><h2>Публикация сайта</h2><a href="/admin/?p=history">История →</a></div>
        <?php if (!gh_ready()): ?>
          <p class="flash flash--warn">Публикация ещё не подключена — заявками можно пользоваться, а для редактирования сайта нужен один шаг настройки. <a href="/admin/?p=edit&c=packages">Как подключить →</a></p>
        <?php elseif (!$runs): ?><p class="muted">Пока нет запусков сборки.</p>
        <?php else: ?>
          <ul class="mini">
          <?php foreach ($runs as $r): ?>
            <li><span><?= e(mb_substr($r['display_title'] ?? $r['name'], 0, 70)) ?></span><?= run_badge($r) ?><time><?= fmt_dt(date('Y-m-d H:i:s', strtotime($r['created_at']))) ?></time></li>
          <?php endforeach; ?>
          </ul>
        <?php endif; ?>
        <h3>Что можно изменить</h3>
        <div class="tiles">
        <?php foreach ($cols as $k => $col): ?>
          <a class="tile" href="/admin/?p=edit&c=<?= $k ?>"><i><?= $col['icon'] ?></i><?= e($col['title']) ?></a>
        <?php endforeach; ?>
        </div>
      </section>
    </div>
    <?php
    $checks = [];
    if ($c['admin_setup_key'] !== '') $checks[] = ['warn', 'Ключ первого входа ещё активен', 'Удалите секрет <code>ADMIN_SETUP_KEY</code> в GitHub и запустите Build and deploy.'];
    $checks[] = gh_ready() ? ['ok', 'Публикация сайта', 'Подключена'] : ['warn', 'Публикация сайта', 'Не подключена — <a href="/admin/?p=edit&c=packages">инструкция</a>'];
    $checks[] = $c['telegram_bot_token'] ? ['ok', 'Telegram', 'Заявки приходят в Telegram'] : ['muted', 'Telegram', 'Не подключён — заявки приходят на почту и сюда'];
    $checks[] = $c['mail_to'] ? ['ok', 'Почта для заявок', e($c['mail_to'])] : ['warn', 'Почта для заявок', 'Не указана'];
    if ($me['role'] === 'admin'): ?>
      <section class="card"><h2>Состояние</h2><ul class="checks"><?php foreach ($checks as [$st, $t, $d]) echo '<li><span class="dot dot--' . $st . '"></span><b>' . e($t) . '</b><span class="muted">' . $d . '</span></li>'; ?></ul></section>
    <?php endif;
    page_end();
    break;

case 'leads':
    $q = array_intersect_key($_GET, array_flip(['status', 'lang', 'q', 'from', 'to']));
    $args = [];
    $where = leads_where($q, $args);
    $page = max(1, (int) ($_GET['n'] ?? 1));
    $per = 50;
    $st = db()->prepare("SELECT COUNT(*) FROM leads WHERE $where");
    $st->execute($args);
    $total = (int) $st->fetchColumn();
    $st = db()->prepare("SELECT * FROM leads WHERE $where ORDER BY created_at DESC LIMIT $per OFFSET " . (($page - 1) * $per));
    $st->execute($args);
    $rows = $st->fetchAll();
    $qs = http_build_query($q);
    page_start('Заявки', 'leads'); ?>
    <div class="head-row"><h1>Заявки <span class="muted">(<?= $total ?>)</span></h1>
      <a class="btn" href="/admin/?p=leads-export&<?= e($qs) ?>">Скачать для Excel</a></div>
    <form class="filters" method="get" action="/admin/">
      <input type="hidden" name="p" value="leads">
      <input type="search" name="q" placeholder="Поиск: имя, email, телефон, текст…" value="<?= e($q['q'] ?? '') ?>">
      <select name="status"><option value="">Все (кроме спама)</option><?php foreach (LEAD_STATUSES as $k => $v): ?><option value="<?= $k ?>" <?= ($q['status'] ?? '') === $k ? 'selected' : '' ?>><?= e($v) ?></option><?php endforeach; ?></select>
      <select name="lang"><option value="">Все языки</option><?php foreach (LANG_NAMES as $k => $v): ?><option value="<?= $k ?>" <?= ($q['lang'] ?? '') === $k ? 'selected' : '' ?>><?= e($v) ?></option><?php endforeach; ?></select>
      <label class="inl">с <input type="date" name="from" value="<?= e($q['from'] ?? '') ?>"></label>
      <label class="inl">по <input type="date" name="to" value="<?= e($q['to'] ?? '') ?>"></label>
      <button class="btn" type="submit">Показать</button>
      <?php if ($q): ?><a href="/admin/?p=leads">Сбросить</a><?php endif; ?>
    </form>
    <form method="post" action="/admin/?<?= e(http_build_query(array_merge(['p' => 'leads'], $q))) ?>">
      <?= csrf_field() ?>
      <div class="table-wrap"><table class="table">
        <thead><tr><th><input type="checkbox" data-checkall aria-label="Выбрать все"></th><th>Дата</th><th>Имя</th><th>Контакты</th><th>Источник</th><th>Язык</th><th>Статус</th></tr></thead>
        <tbody>
        <?php if (!$rows): ?><tr><td colspan="7" class="muted center">Ничего не найдено</td></tr><?php endif; ?>
        <?php foreach ($rows as $l): ?>
          <tr class="<?= $l['status'] === 'new' ? 'is-new' : '' ?>" data-href="/admin/?p=lead&id=<?= $l['id'] ?>">
            <td><input type="checkbox" name="ids[]" value="<?= $l['id'] ?>" aria-label="Выбрать"></td>
            <td class="nowrap"><?= fmt_dt($l['created_at']) ?></td>
            <td><a href="/admin/?p=lead&id=<?= $l['id'] ?>"><b><?= e(trim($l['name'] . ' ' . $l['lastname'])) ?></b></a><?php if ($l['message']): ?><div class="muted clip"><?= e(mb_substr($l['message'], 0, 90)) ?></div><?php endif; ?></td>
            <td><?= e($l['email']) ?><?php if ($l['phone']): ?><br><span class="muted"><?= e($l['phone']) ?></span><?php endif; ?></td>
            <td><?= e($l['source']) ?></td>
            <td><?= e(['ru' => 'RU', 'uk' => 'UA', 'kk' => 'KZ'][$l['lang']] ?? $l['lang']) ?></td>
            <td><?= status_badge($l['status']) ?></td>
          </tr>
        <?php endforeach; ?>
        </tbody>
      </table></div>
      <div class="bulk">Отмеченные: <select name="bulk"><option value="">— изменить статус —</option><?php foreach (LEAD_STATUSES as $k => $v): ?><option value="<?= $k ?>"><?= e($v) ?></option><?php endforeach; ?></select> <button class="btn" type="submit">Применить</button></div>
    </form>
    <?php if ($total > $per): ?><nav class="pager"><?php for ($i = 1; $i <= (int) ceil($total / $per); $i++): ?><a class="<?= $i === $page ? 'on' : '' ?>" href="/admin/?p=leads&<?= e($qs) ?>&n=<?= $i ?>"><?= $i ?></a><?php endfor; ?></nav><?php endif;
    page_end();
    break;

case 'lead':
    $st = db()->prepare('SELECT * FROM leads WHERE id = ?');
    $st->execute([(int) ($_GET['id'] ?? 0)]);
    $l = $st->fetch();
    if (!$l) { flash('Заявка не найдена.', 'bad'); redirect('/admin/?p=leads'); }
    if ($l['status'] === 'new') { // opening a new lead marks it as "in progress"
        db()->prepare("UPDATE leads SET status='progress', updated_at=? WHERE id=?")->execute([now_str(), $l['id']]);
        $l['status'] = 'progress';
    }
    $wa = preg_replace('/\D/', '', $l['phone']);
    page_start('Заявка №' . $l['id'], 'leads'); ?>
    <p><a href="/admin/?p=leads">← Все заявки</a></p>
    <div class="cols">
      <section class="card">
        <h1><?= e(trim($l['name'] . ' ' . $l['lastname'])) ?></h1>
        <dl class="dl">
          <dt>Email</dt><dd><a href="mailto:<?= e($l['email']) ?>"><?= e($l['email']) ?></a></dd>
          <?php if ($l['phone']): ?><dt>Телефон / мессенджер</dt><dd><?= e($l['phone']) ?><?php if (strlen($wa) >= 9): ?> · <a href="https://wa.me/<?= e($wa) ?>" target="_blank" rel="noopener">WhatsApp ↗</a> · <a href="tel:+<?= e($wa) ?>">Позвонить</a><?php endif; ?></dd><?php endif; ?>
          <dt>Источник</dt><dd><?= e($l['source']) ?></dd>
          <dt>Язык сайта</dt><dd><?= e(LANG_NAMES[$l['lang']] ?? $l['lang']) ?></dd>
          <dt>Страница</dt><dd><?= e($l['page']) ?></dd>
          <dt>Получена</dt><dd><?= fmt_dt($l['created_at']) ?><?= $l['notified'] ? '' : ' <span class="st st--bad">уведомление не отправилось</span>' ?></dd>
        </dl>
        <?php if ($l['message']): ?><h3>Сообщение</h3><div class="msg"><?= nl2br(e($l['message'])) ?></div><?php endif; ?>
        <p><a class="btn" href="mailto:<?= e($l['email']) ?>?subject=<?= rawurlencode('MY STUDY IN GREECE — ваша заявка') ?>">Ответить письмом</a></p>
      </section>
      <form class="card" method="post" action="/admin/?p=lead">
        <?= csrf_field() ?><input type="hidden" name="id" value="<?= $l['id'] ?>">
        <h2>Работа с заявкой</h2>
        <label>Статус<select name="status"><?php foreach (LEAD_STATUSES as $k => $v): ?><option value="<?= $k ?>" <?= $l['status'] === $k ? 'selected' : '' ?>><?= e($v) ?></option><?php endforeach; ?></select></label>
        <label>Заметки (видны только в админ-панели)<textarea name="notes" rows="8"><?= e($l['notes']) ?></textarea></label>
        <button class="btn btn--primary" type="submit">Сохранить</button>
        <?php if ($l['updated_at']): ?><p class="muted small">Изменена: <?= fmt_dt($l['updated_at']) ?></p><?php endif; ?>
        <?php if ($me['role'] === 'admin'): ?>
          <hr><button class="btn btn--danger" type="submit" name="action" value="delete" data-confirm="Удалить заявку навсегда?">Удалить заявку</button>
        <?php endif; ?>
      </form>
    </div>
    <?php page_end();
    break;

case 'edit':
    $key = (string) ($_GET['c'] ?? '');
    if (!isset($cols[$key])) redirect('/admin/');
    $col = $cols[$key];
    $data = null; $sha = ''; $err = '';
    if (!gh_ready()) $err = 'setup';
    else { try { [$data, $sha] = gh_read_json($col['file']); } catch (Throwable $ex) { $err = $ex->getMessage(); } }
    if ($data !== null && !empty($_GET['draft']) && isset($_SESSION['draft'][$key])) $data = $_SESSION['draft'][$key];
    page_start($col['title'], 'edit:' . $key); ?>
    <div class="head-row"><h1><?= e($col['title']) ?></h1><a href="/admin/?p=history&c=<?= $key ?>">История и откат →</a></div>
    <p class="muted"><?= e($col['hint']) ?></p>
    <?php if ($err === 'setup') { echo publish_setup_help(); page_end(); break; }
    if ($err): ?><p class="flash flash--bad"><?= e($err) ?></p><?php page_end(); break; endif;
    $miss = missing_translations($data, $col['schema']);
    if ($miss): ?>
      <details class="flash flash--warn"><summary>Нет перевода: <?= count($miss) ?> <?= count($miss) === 1 ? 'поле' : 'полей' ?> — на UA/KZ-версии там будет русский текст</summary><ul class="small"><?php foreach (array_slice($miss, 0, 40) as $m) echo '<li>' . e($m) . '</li>'; ?></ul></details>
    <?php endif; ?>
    <form method="post" action="/admin/?p=save" data-editor-form novalidate>
      <?= csrf_field() ?>
      <input type="hidden" name="c" value="<?= e($key) ?>">
      <input type="hidden" name="sha" value="<?= e($sha) ?>">
      <input type="hidden" name="data" data-editor-out>
      <div data-editor></div>
      <script type="application/json" data-editor-schema><?= json_encode($col['schema'], JSON_UNESCAPED_UNICODE | JSON_HEX_TAG | JSON_HEX_AMP) ?></script>
      <script type="application/json" data-editor-data><?= json_encode($data, JSON_UNESCAPED_UNICODE | JSON_HEX_TAG | JSON_HEX_AMP) ?></script>
      <div class="savebar">
        <input name="note" maxlength="120" placeholder="Что изменили? (необязательно, для истории)">
        <button class="btn btn--primary" type="submit">Сохранить и опубликовать</button>
        <span class="muted small" data-dirty hidden>Есть несохранённые изменения</span>
      </div>
    </form>
    <?php page_end();
    break;

case 'history':
    $key = (string) ($_GET['c'] ?? '');
    page_start('История изменений', 'history'); ?>
    <h1>История изменений</h1>
    <nav class="tabs"><?php foreach ($cols as $k => $col): ?><a class="<?= $k === $key ? 'on' : '' ?>" href="/admin/?p=history&c=<?= $k ?>"><?= e($col['title']) ?></a><?php endforeach; ?><a class="<?= $key === 'audit' ? 'on' : '' ?>" href="/admin/?p=history&c=audit">Журнал действий</a></nav>
    <?php
    if ($key === 'audit') {
        $rows = db()->query('SELECT * FROM audit ORDER BY id DESC LIMIT 200')->fetchAll();
        echo '<div class="table-wrap"><table class="table"><thead><tr><th>Когда</th><th>Кто</th><th>Действие</th><th>Подробности</th></tr></thead><tbody>';
        foreach ($rows as $r) echo '<tr><td class="nowrap">' . fmt_dt($r['ts']) . '</td><td>' . e($r['username']) . '</td><td>' . e($r['action']) . '</td><td>' . e($r['detail']) . '</td></tr>';
        echo '</tbody></table></div>';
    } elseif (!isset($cols[$key])) {
        echo '<p class="muted">Выберите раздел, чтобы увидеть его версии. Любую прошлую версию можно вернуть одной кнопкой.</p>';
        if (gh_ready()) {
            try { $runs = gh_last_runs(10); } catch (Throwable $e) { $runs = []; }
            echo '<h2>Последние публикации</h2><ul class="mini">';
            foreach ($runs as $r) echo '<li><span>' . e(mb_substr($r['display_title'] ?? '', 0, 90)) . '</span>' . run_badge($r) . '<time>' . fmt_dt(date('Y-m-d H:i:s', strtotime($r['created_at']))) . '</time></li>';
            echo '</ul>';
        }
    } elseif (!gh_ready()) {
        echo publish_setup_help();
    } else {
        $commits = gh_history($cols[$key]['file'], 20);
        echo '<div class="table-wrap"><table class="table"><thead><tr><th>Когда</th><th>Изменение</th><th></th></tr></thead><tbody>';
        foreach ($commits as $i => $cm) {
            $when = fmt_dt(date('Y-m-d H:i:s', strtotime($cm['commit']['committer']['date'] ?? 'now')));
            echo '<tr><td class="nowrap">' . $when . '</td><td>' . e(mb_substr(strtok($cm['commit']['message'], "\n"), 0, 140)) . '</td><td>';
            if ($i === 0) echo '<span class="st st--ok">текущая</span>';
            else echo '<form method="post" action="/admin/?p=restore">' . csrf_field() . '<input type="hidden" name="c" value="' . e($key) . '"><input type="hidden" name="sha" value="' . e($cm['sha']) . '"><button class="btn btn--sm" data-confirm="Вернуть «' . e($cols[$key]['title']) . '» к этой версии? Текущая версия останется в истории.">Вернуть эту версию</button></form>';
            echo '</td></tr>';
        }
        if (!$commits) echo '<tr><td colspan="3" class="muted">Нет данных</td></tr>';
        echo '</tbody></table></div>';
    }
    page_end();
    break;

case 'users':
    require_login('admin');
    $rows = db()->query('SELECT id, username, display_name, role, created_at, last_login FROM users ORDER BY id')->fetchAll();
    page_start('Пользователи', 'users'); ?>
    <h1>Пользователи</h1>
    <div class="table-wrap"><table class="table"><thead><tr><th>Имя</th><th>Логин</th><th>Роль</th><th>Последний вход</th><th></th></tr></thead><tbody>
    <?php foreach ($rows as $r): ?>
      <tr><td><?= e($r['display_name']) ?></td><td><?= e($r['username']) ?></td><td><?= $r['role'] === 'admin' ? 'Администратор' : 'Редактор' ?></td><td><?= fmt_dt($r['last_login']) ?></td>
      <td class="actions">
        <form method="post" action="/admin/?p=users" class="inl"><?= csrf_field() ?><input type="hidden" name="action" value="reset"><input type="hidden" name="id" value="<?= $r['id'] ?>"><input type="password" name="password" placeholder="Новый пароль" minlength="10" required autocomplete="new-password"><button class="btn btn--sm">Сменить пароль</button></form>
        <?php if ((int) $r['id'] !== (int) $me['id']): ?><form method="post" action="/admin/?p=users" class="inl"><?= csrf_field() ?><input type="hidden" name="action" value="delete"><input type="hidden" name="id" value="<?= $r['id'] ?>"><button class="btn btn--sm btn--danger" data-confirm="Удалить пользователя <?= e($r['username']) ?>?">Удалить</button></form><?php endif; ?>
      </td></tr>
    <?php endforeach; ?>
    </tbody></table></div>
    <form class="card narrow-left" method="post" action="/admin/?p=users">
      <h2>Добавить пользователя</h2><?= csrf_field() ?><input type="hidden" name="action" value="add">
      <label>Имя<input name="name" required></label>
      <label>Логин (латиницей)<input name="username" required pattern="[a-zA-Z0-9._\-]{3,32}"></label>
      <label>Пароль (мин. 10 символов)<input type="password" name="password" required minlength="10" autocomplete="new-password"></label>
      <label>Роль<select name="role"><option value="editor">Редактор — заявки и контент</option><option value="admin">Администратор — всё, включая пользователей</option></select></label>
      <button class="btn btn--primary">Создать</button>
    </form>
    <?php page_end();
    break;

case 'account':
    page_start('Мой аккаунт', 'account'); ?>
    <h1>Мой аккаунт</h1>
    <form class="card narrow-left" method="post" action="/admin/?p=account">
      <?= csrf_field() ?>
      <label>Имя<input name="name" value="<?= e($me['display_name']) ?>"></label>
      <label>Текущий пароль<input type="password" name="old" required autocomplete="current-password"></label>
      <label>Новый пароль (мин. 10 символов)<input type="password" name="new" required minlength="10" autocomplete="new-password"></label>
      <label>Новый пароль ещё раз<input type="password" name="new2" required minlength="10" autocomplete="new-password"></label>
      <button class="btn btn--primary">Сохранить</button>
    </form>
    <?php page_end();
    break;

default:
    redirect('/admin/');
}
