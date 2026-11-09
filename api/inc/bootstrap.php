<?php
/**
 * Shared code for the lead endpoint (api/lead.php) and the admin panel (admin/).
 * Settings come from api/config.php (never committed to Git).
 */
declare(strict_types=1);

function msgr_config(): array
{
    static $cfg = null;
    if ($cfg !== null) return $cfg;
    $file = dirname(__DIR__) . '/config.php';
    $cfg = is_file($file) ? (array) require $file : [];
    $cfg += [
        'telegram_bot_token' => '',
        'telegram_chat_id'   => '',
        'mail_to'            => 'mystudygr1@gmail.com',
        'mail_from'          => 'no-reply@mystudygr.com',
        'allowed_origins'    => ['https://mystudygr.com', 'https://www.mystudygr.com'],
        // Leads database + admin data. Default: a folder NEXT TO public_html (not reachable from the web).
        'data_dir'           => dirname(__DIR__, 3) . '/msgr-data',
        'admin_setup_key'    => '',
        'github_token'       => '',
        'github_repo'        => 'J-ntk/MSGR',
        'github_branch'      => 'main',
        'timezone'           => 'Europe/Athens',
    ];
    date_default_timezone_set($cfg['timezone']);
    return $cfg;
}

function msgr_configured(): bool
{
    return is_file(dirname(__DIR__) . '/config.php');
}

function msgr_data_dir(): string
{
    $dir = rtrim(msgr_config()['data_dir'], '/');
    if (!is_dir($dir) && !@mkdir($dir, 0750, true)) {
        // Fallback inside the site, protected by its own .htaccess
        $dir = dirname(__DIR__) . '/data';
        if (!is_dir($dir)) @mkdir($dir, 0750, true);
    }
    $ht = $dir . '/.htaccess';
    if (!is_file($ht)) @file_put_contents($ht, "Require all denied\n");
    return $dir;
}

function db(): PDO
{
    static $pdo = null;
    if ($pdo) return $pdo;
    $pdo = new PDO('sqlite:' . msgr_data_dir() . '/msgr.sqlite', null, null, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]);
    $pdo->exec('PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON; PRAGMA busy_timeout=5000;');
    $pdo->exec("
      CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        updated_at TEXT,
        name TEXT, lastname TEXT, email TEXT, phone TEXT, message TEXT,
        source TEXT, page TEXT, lang TEXT,
        status TEXT NOT NULL DEFAULT 'new',
        notes TEXT DEFAULT '',
        notified INTEGER DEFAULT 0,
        ip_hash TEXT
      );
      CREATE INDEX IF NOT EXISTS leads_status ON leads(status);
      CREATE INDEX IF NOT EXISTS leads_created ON leads(created_at);
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        display_name TEXT,
        pass_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'editor',
        created_at TEXT NOT NULL,
        last_login TEXT
      );
      CREATE TABLE IF NOT EXISTS login_attempts (ip_hash TEXT, ts INTEGER);
      CREATE TABLE IF NOT EXISTS audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL, username TEXT, action TEXT, detail TEXT
      );
    ");
    return $pdo;
}

function now_str(): string { return date('Y-m-d H:i:s'); }

function ip_hash(): string
{
    return substr(hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '0') . '|msgr'), 0, 24);
}

function clean_str($v, int $max = 500): string
{
    $v = is_string($v) ? trim($v) : (is_numeric($v) ? (string) $v : '');
    $v = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F]/u', '', $v) ?? '';
    return mb_substr($v, 0, $max);
}

const LEAD_STATUSES = [
    'new'      => 'Новая',
    'progress' => 'В работе',
    'client'   => 'Стал клиентом',
    'done'     => 'Закрыта',
    'spam'     => 'Спам',
];
const LANG_NAMES = ['ru' => 'русский', 'uk' => 'украинский', 'kk' => 'казахский'];

function lead_text(array $l): string
{
    $full = trim(($l['name'] ?? '') . ' ' . ($l['lastname'] ?? ''));
    return "🎓 Новая заявка — MY STUDY IN GREECE\n"
        . 'Источник: ' . ($l['source'] ?? '') . "\n"
        . 'Язык сайта: ' . (LANG_NAMES[$l['lang'] ?? 'ru'] ?? 'русский') . "\n"
        . "Имя: $full\nEmail: " . ($l['email'] ?? '') . "\n"
        . (($l['phone'] ?? '') !== '' ? 'Телефон/мессенджер: ' . $l['phone'] . "\n" : '')
        . (($l['message'] ?? '') !== '' ? "\n" . $l['message'] . "\n" : '')
        . "\nСтраница: " . ($l['page'] ?? '') . "\nВремя: " . date('d.m.Y H:i')
        . (isset($l['id']) ? "\nЗаявка №" . $l['id'] . ' в админ-панели' : '');
}

/** Send a lead to Telegram and/or email. Returns true if at least one channel worked. */
function notify_lead(array $l): bool
{
    $cfg = msgr_config();
    $text = lead_text($l);
    $sent = false;
    if ($cfg['telegram_bot_token'] && $cfg['telegram_chat_id']) {
        $r = http_json('POST', 'https://api.telegram.org/bot' . $cfg['telegram_bot_token'] . '/sendMessage',
            ['chat_id' => $cfg['telegram_chat_id'], 'text' => $text, 'disable_web_page_preview' => true]);
        if (($r['body']['ok'] ?? false) === true) $sent = true;
    }
    if ($cfg['mail_to']) {
        $full = trim(($l['name'] ?? '') . ' ' . ($l['lastname'] ?? ''));
        $subject = '=?UTF-8?B?' . base64_encode("Заявка с сайта: $full (" . ($l['source'] ?? '') . ')') . '?=';
        $headers = "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\n"
            . 'From: ' . $cfg['mail_from'] . "\r\n";
        if (filter_var($l['email'] ?? '', FILTER_VALIDATE_EMAIL)) $headers .= 'Reply-To: ' . $l['email'] . "\r\n";
        if (@mail($cfg['mail_to'], $subject, $text, $headers)) $sent = true;
    }
    return $sent;
}

/** Minimal JSON HTTP client (curl if available, else streams). */
function http_json(string $method, string $url, ?array $body = null, array $headers = []): array
{
    $headers = array_merge(['Content-Type: application/json', 'Accept: application/json', 'User-Agent: MSGR-admin'], $headers);
    $payload = $body === null ? null : json_encode($body, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    if (function_exists('curl_init')) {
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_CUSTOMREQUEST => $method, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 20,
            CURLOPT_HTTPHEADER => $headers,
        ]);
        if ($payload !== null) curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
        $res = curl_exec($ch);
        $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $err = curl_error($ch);
        curl_close($ch);
        return ['status' => $code, 'body' => is_string($res) ? json_decode($res, true) : null, 'error' => $err];
    }
    $ctx = stream_context_create(['http' => [
        'method' => $method, 'timeout' => 20, 'ignore_errors' => true,
        'header' => implode("\r\n", $headers) . "\r\n", 'content' => $payload ?? '',
    ]]);
    $res = @file_get_contents($url, false, $ctx);
    $code = 0;
    foreach ($http_response_header ?? [] as $h) if (preg_match('#^HTTP/\S+ (\d+)#', $h, $m)) $code = (int) $m[1];
    return ['status' => $code, 'body' => is_string($res) ? json_decode($res, true) : null, 'error' => $res === false ? 'request failed' : ''];
}
