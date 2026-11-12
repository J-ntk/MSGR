<?php
declare(strict_types=1);

function page_start(string $title, string $active = '', bool $bare = false): void
{
    $u = current_user();
    $new = 0;
    if ($u) $new = (int) db()->query("SELECT COUNT(*) FROM leads WHERE status = 'new'")->fetchColumn();
    $nav = [
        ['', 'Работа', ''],
        ['dashboard', 'Обзор', '◫'],
        ['leads', 'Заявки' . ($new ? ' <span class="badge">' . $new . '</span>' : ''), '✉'],
        ['', 'Контент сайта', ''],
    ];
    foreach (content_collections() as $k => $c) $nav[] = ['edit:' . $k, e($c['title']), $c['icon']];
    $nav[] = ['', 'Система', ''];
    $nav[] = ['history', 'История изменений', '↺'];
    if ($u && $u['role'] === 'admin') $nav[] = ['users', 'Пользователи', '☺'];
    $nav[] = ['account', 'Мой аккаунт', '⚙'];
    ?><!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title><?= e($title) ?> — Админ-панель MSGR</title>
<link rel="icon" href="/assets/img/favicon.jpg">
<link rel="stylesheet" href="/admin/assets/admin.css?v=2">
</head>
<body class="<?= $bare ? 'bare' : '' ?>">
<?php if (!$bare && $u): ?>
<header class="top">
  <button class="top__menu" type="button" data-menu aria-label="Меню">☰</button>
  <a class="top__brand" href="/admin/" aria-label="Админ-панель — обзор"><img src="/assets/img/logo.png" alt="MY STUDY IN GREECE" width="87" height="40"><span class="top__tag">Админ-панель</span></a>
  <div class="top__right">
    <a class="top__site" href="/" target="_blank" rel="noopener">Открыть сайт ↗</a>
    <a class="top__user" href="/admin/?p=account"><?= e($u['display_name'] ?: $u['username']) ?></a>
    <form method="post" action="/admin/?p=logout"><?= csrf_field() ?><button class="linkbtn" type="submit">Выйти</button></form>
  </div>
</header>
<div class="shell">
<nav class="side" data-side>
<?php foreach ($nav as [$key, $label, $icon]):
    if ($key === '') { echo '<p class="side__group">' . e($label) . '</p>'; continue; }
    $href = str_starts_with($key, 'edit:') ? '/admin/?p=edit&c=' . substr($key, 5) : '/admin/?p=' . $key; ?>
  <a href="<?= $href ?>" class="<?= $active === $key ? 'on' : '' ?>"><i aria-hidden="true"><?= $icon ?></i><span><?= $label ?></span></a>
<?php endforeach; ?>
</nav>
<main class="main">
<?php else: ?>
<main class="main main--bare">
<?php endif;
    foreach (flash() as [$type, $msg]) echo '<div class="flash flash--' . e($type) . '">' . e($msg) . '</div>';
}

function page_end(): void
{
    $u = current_user();
    echo '</main>' . ($u ? '</div>' : '') . '<script src="/admin/assets/admin.js?v=1"></script></body></html>';
}

function status_badge(string $s): string
{
    return '<span class="st st--' . e($s) . '">' . e(LEAD_STATUSES[$s] ?? $s) . '</span>';
}

function run_badge(?array $run): string
{
    if (!$run) return '<span class="st">нет данных</span>';
    $s = $run['status'] === 'completed' ? ($run['conclusion'] ?? '') : $run['status'];
    $map = ['success' => ['ok', 'Опубликовано'], 'failure' => ['bad', 'Ошибка сборки'], 'cancelled' => ['muted', 'Отменено'],
            'in_progress' => ['wait', 'Публикуется…'], 'queued' => ['wait', 'В очереди…'], 'waiting' => ['wait', 'Ожидает…']];
    [$cls, $txt] = $map[$s] ?? ['muted', $s];
    return '<span class="st st--' . $cls . '">' . e($txt) . '</span>';
}

/** Big logo on a navy tile (the logo itself is white). */
function brand_tile(): string
{
    return '<div class="brand-tile"><img src="/assets/img/logo.png" alt="MY STUDY IN GREECE" width="130" height="60"></div>';
}

/** Friendly explanation + steps when publishing to the site is not connected yet. */
function publish_setup_help(): string
{
    $repo = e(msgr_config()['github_repo']);
    return '<section class="card setup">'
        . '<h2>Подключите публикацию — это делается один раз</h2>'
        . '<p class="muted">Админ-панель сохраняет изменения сайта через GitHub. Для этого ей нужен ключ доступа (токен). Заявками можно пользоваться уже сейчас.</p>'
        . '<ol class="steps">'
        . '<li><b>Создайте токен.</b> Откройте <a href="https://github.com/settings/personal-access-tokens/new" target="_blank" rel="noopener">GitHub → Fine-grained token ↗</a>.'
        . ' Название: <code>MSGR admin</code>, срок: <i>1 год</i>, Repository access: <i>Only select repositories</i> → <code>' . $repo . '</code>.'
        . ' Permissions → Repository: <b>Contents — Read and write</b>, <b>Actions — Read-only</b>. Нажмите <i>Generate token</i> и скопируйте его.</li>'
        . '<li><b>Сохраните его в GitHub как секрет.</b> <a href="https://github.com/' . $repo . '/settings/secrets/actions/new" target="_blank" rel="noopener">Settings → Secrets → New secret ↗</a>, имя <code>ADMIN_GITHUB_TOKEN</code>, значение — токен.</li>'
        . '<li><b>Запустите обновление сайта.</b> <a href="https://github.com/' . $repo . '/actions/workflows/build-deploy.yml" target="_blank" rel="noopener">Actions → Build and deploy → Run workflow ↗</a>. Через 1–2 минуты обновите эту страницу.</li>'
        . '</ol></section>';
}
