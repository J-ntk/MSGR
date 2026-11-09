<?php
/**
 * MSGR lead endpoint — receives the contact form / quiz (JSON POST).
 * 1) saves the lead in the database (admin panel → Заявки), so nothing is ever lost;
 * 2) forwards it to Telegram and/or email.
 * Settings: api/config.php (copy from config.example.php).
 */
declare(strict_types=1);
require __DIR__ . '/inc/bootstrap.php';
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('X-Robots-Tag: noindex');

function out(int $code, array $body): void { http_response_code($code); echo json_encode($body, JSON_UNESCAPED_UNICODE); exit; }

if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(405, ['ok' => false, 'error' => 'method']);
if (!msgr_configured()) out(500, ['ok' => false, 'error' => 'not_configured']);
$cfg = msgr_config();

// Only accept requests from our own site
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if ($origin && !in_array($origin, $cfg['allowed_origins'], true)) out(403, ['ok' => false, 'error' => 'origin']);

$raw = file_get_contents('php://input', false, null, 0, 20000);
$d = json_decode($raw ?: '[]', true);
if (!is_array($d)) $d = $_POST;

// Honeypot: bots fill the hidden "website" field
if (!empty($d['website'])) out(200, ['ok' => true]);

$lang = clean_str($d['lang'] ?? 'ru', 5);
$lead = [
    'name'     => clean_str($d['name'] ?? '', 120),
    'lastname' => clean_str($d['lastname'] ?? '', 120),
    'email'    => clean_str($d['email'] ?? '', 200),
    'phone'    => clean_str($d['phone'] ?? '', 80),
    'message'  => clean_str($d['message'] ?? '', 3000),
    'source'   => clean_str($d['source'] ?? 'Сайт', 80),
    'page'     => clean_str($d['page'] ?? '', 200),
    'lang'     => isset(LANG_NAMES[$lang]) ? $lang : 'ru',
];
if ($lead['name'] === '' || !filter_var($lead['email'], FILTER_VALIDATE_EMAIL) || empty($d['consent'])) {
    out(422, ['ok' => false, 'error' => 'validation']);
}

$saved = false;
try {
    $pdo = db();
    // Rate limit: 5 leads / 10 minutes per visitor
    $ih = ip_hash();
    $st = $pdo->prepare('SELECT COUNT(*) FROM leads WHERE ip_hash = ? AND created_at > ?');
    $st->execute([$ih, date('Y-m-d H:i:s', time() - 600)]);
    if ((int) $st->fetchColumn() >= 5) out(429, ['ok' => false, 'error' => 'rate']);

    $st = $pdo->prepare('INSERT INTO leads (created_at, name, lastname, email, phone, message, source, page, lang, ip_hash)
                         VALUES (?,?,?,?,?,?,?,?,?,?)');
    $st->execute([now_str(), $lead['name'], $lead['lastname'], $lead['email'], $lead['phone'], $lead['message'],
                  $lead['source'], $lead['page'], $lead['lang'], $ih]);
    $lead['id'] = (int) $pdo->lastInsertId();
    $saved = true;
} catch (Throwable $e) {
    error_log('MSGR lead DB error: ' . $e->getMessage());
}

$sent = notify_lead($lead);
if ($saved && $sent) {
    db()->prepare('UPDATE leads SET notified = 1 WHERE id = ?')->execute([$lead['id']]);
}

// The visitor sees success if the lead is safely stored OR was delivered.
out(($saved || $sent) ? 200 : 502, ['ok' => $saved || $sent]);
