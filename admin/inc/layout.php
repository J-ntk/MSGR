<?php
declare(strict_types=1);

function page_start(string $title, string $active = '', bool $bare = false): void
{
    $u = current_user();
    $new = 0;
    if ($u) $new = (int) db()->query("SELECT COUNT(*) FROM leads WHERE status = 'new'")->fetchColumn();
    $nav = [
        ['dashboard', 'Обзор', '◫'],
        ['leads', 'Заявки' . ($new ? ' <span class="badge">' . $new . '</span>' : ''), '✉'],
    ];
    foreach (content_collections() as $k => $c) $nav[] = ['edit:' . $k, e($c['title']), $c['icon']];
    $nav[] = ['history', 'История изменений', '↺'];
    if ($u && $u['role'] === 'admin') $nav[] = ['users', 'Пользователи', '☺'];
    ?><!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title><?= e($title) ?> — Админ-панель MSGR</title>
<link rel="icon" href="/assets/img/favicon.jpg">
<link rel="stylesheet" href="/admin/assets/admin.css?v=1">
</head>
<body class="<?= $bare ? 'bare' : '' ?>">
<?php if (!$bare && $u): ?>
<header class="top">
  <button class="top__menu" type="button" data-menu aria-label="Меню">☰</button>
  <a class="top__brand" href="/admin/"><img src="/assets/img/logo.png" alt="" width="34" height="34"><span>MY STUDY IN GREECE<small>админ-панель</small></span></a>
  <div class="top__right">
    <a class="top__site" href="/" target="_blank" rel="noopener">Открыть сайт ↗</a>
    <a class="top__user" href="/admin/?p=account"><?= e($u['display_name'] ?: $u['username']) ?></a>
    <form method="post" action="/admin/?p=logout"><?= csrf_field() ?><button class="linkbtn" type="submit">Выйти</button></form>
  </div>
</header>
<div class="shell">
<nav class="side" data-side>
<?php foreach ($nav as [$key, $label, $icon]):
    $href = str_starts_with($key, 'edit:') ? '/admin/?p=edit&c=' . substr($key, 5) : '/admin/?p=' . $key; ?>
  <a href="<?= $href ?>" class="<?= $active === $key ? 'on' : '' ?>"><i><?= $icon ?></i><?= $label ?></a>
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
