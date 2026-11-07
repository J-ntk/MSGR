<?php
/**
 * MSGR lead endpoint — receives the contact form / quiz (JSON POST)
 * and forwards it to Telegram and/or email.
 * Works on any PHP 7.4+ hosting (e.g. Hostinger). Settings: api/config.php
 */
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

function out(int $code, array $body): void { http_response_code($code); echo json_encode($body, JSON_UNESCAPED_UNICODE); exit; }

if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(405, ['ok' => false, 'error' => 'method']);

$cfgFile = __DIR__ . '/config.php';
if (!is_file($cfgFile)) out(500, ['ok' => false, 'error' => 'not_configured']);
$cfg = require $cfgFile;

// Only accept requests from our own site
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if ($origin && !in_array($origin, $cfg['allowed_origins'] ?? [], true)) out(403, ['ok' => false, 'error' => 'origin']);

$raw = file_get_contents('php://input', false, null, 0, 20000);
$d = json_decode($raw ?: '[]', true);
if (!is_array($d)) $d = $_POST;

// Honeypot
if (!empty($d['website'])) out(200, ['ok' => true]);

$clean = function ($v, int $max = 500): string {
  $v = is_string($v) ? trim($v) : '';
  $v = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F]/u', '', $v);
  return mb_substr($v, 0, $max);
};
$name    = $clean($d['name'] ?? '', 120);
$last    = $clean($d['lastname'] ?? '', 120);
$email   = $clean($d['email'] ?? '', 200);
$phone   = $clean($d['phone'] ?? '', 80);
$message = $clean($d['message'] ?? '', 3000);
$source  = $clean($d['source'] ?? 'Сайт', 80);
$page    = $clean($d['page'] ?? '', 200);
$consent = !empty($d['consent']);

if ($name === '' || !filter_var($email, FILTER_VALIDATE_EMAIL) || !$consent) out(422, ['ok' => false, 'error' => 'validation']);

// Simple rate limit: 5 requests / 10 minutes per IP
$ip = $_SERVER['REMOTE_ADDR'] ?? '0';
$rl = sys_get_temp_dir() . '/msgr_rl_' . md5($ip);
$now = time();
$hits = array_filter(is_file($rl) ? (array) json_decode((string) file_get_contents($rl), true) : [], fn($t) => $t > $now - 600);
if (count($hits) >= 5) out(429, ['ok' => false, 'error' => 'rate']);
$hits[] = $now; @file_put_contents($rl, json_encode(array_values($hits)));

$full = trim("$name $last");
$text = "🎓 Новая заявка — MY STUDY IN GREECE\n"
      . "Источник: $source\n"
      . "Имя: $full\nEmail: $email\n"
      . ($phone !== '' ? "Телефон/мессенджер: $phone\n" : '')
      . ($message !== '' ? "\n$message\n" : '')
      . "\nСтраница: $page\nВремя: " . date('d.m.Y H:i');

$sent = false;

// Telegram
if (!empty($cfg['telegram_bot_token']) && !empty($cfg['telegram_chat_id'])) {
  $url = 'https://api.telegram.org/bot' . $cfg['telegram_bot_token'] . '/sendMessage';
  $ctx = stream_context_create(['http' => [
    'method' => 'POST', 'timeout' => 8,
    'header' => "Content-Type: application/json\r\n",
    'content' => json_encode(['chat_id' => $cfg['telegram_chat_id'], 'text' => $text, 'disable_web_page_preview' => true]),
  ]]);
  $r = @file_get_contents($url, false, $ctx);
  if ($r !== false && strpos($r, '"ok":true') !== false) $sent = true;
}

// Email
if (!empty($cfg['mail_to'])) {
  $subject = '=?UTF-8?B?' . base64_encode("Заявка с сайта: $full ($source)") . '?=';
  $headers = "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\n"
           . 'From: ' . ($cfg['mail_from'] ?? 'no-reply@mystudygr.com') . "\r\n"
           . "Reply-To: $email\r\n";
  if (@mail($cfg['mail_to'], $subject, $text, $headers)) $sent = true;
}

out($sent ? 200 : 502, ['ok' => $sent]);
