<?php
/** Admin panel core: sessions, login, CSRF, roles, flash messages, helpers. */
declare(strict_types=1);
require dirname(__DIR__, 2) . '/api/inc/bootstrap.php';

header('X-Robots-Tag: noindex, nofollow');
header('X-Frame-Options: DENY');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: same-origin');
header("Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; frame-ancestors 'none'; form-action 'self'");

$secure = (($_SERVER['HTTPS'] ?? '') === 'on') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https');
session_name('msgr_admin');
session_set_cookie_params(['lifetime' => 0, 'path' => '/admin/', 'secure' => $secure, 'httponly' => true, 'samesite' => 'Strict']);
session_start();

// Idle timeout: 8 hours
if (isset($_SESSION['uid'], $_SESSION['seen']) && time() - $_SESSION['seen'] > 8 * 3600) {
    $_SESSION = [];
    session_regenerate_id(true);
}
$_SESSION['seen'] = time();

function e($v): string { return htmlspecialchars((string) $v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }

function csrf_token(): string
{
    if (empty($_SESSION['csrf'])) $_SESSION['csrf'] = bin2hex(random_bytes(32));
    return $_SESSION['csrf'];
}
function csrf_field(): string { return '<input type="hidden" name="csrf" value="' . e(csrf_token()) . '">'; }
function csrf_check(): void
{
    if (!hash_equals($_SESSION['csrf'] ?? '', (string) ($_POST['csrf'] ?? ''))) {
        http_response_code(400);
        exit('Сессия устарела. Обновите страницу и попробуйте ещё раз.');
    }
}

function flash(?string $msg = null, string $type = 'ok')
{
    if ($msg !== null) { $_SESSION['flash'][] = [$type, $msg]; return null; }
    $f = $_SESSION['flash'] ?? [];
    unset($_SESSION['flash']);
    return $f;
}

function redirect(string $to): void { header('Location: ' . $to); exit; }

function current_user(): ?array
{
    static $u = false;
    if ($u !== false) return $u;
    $u = null;
    if (!empty($_SESSION['uid'])) {
        $st = db()->prepare('SELECT id, username, display_name, role FROM users WHERE id = ?');
        $st->execute([$_SESSION['uid']]);
        $u = $st->fetch() ?: null;
    }
    return $u;
}

function require_login(?string $role = null): array
{
    $u = current_user();
    if (!$u) redirect('/admin/?p=login');
    if ($role === 'admin' && $u['role'] !== 'admin') { http_response_code(403); exit('Нет доступа.'); }
    return $u;
}

function users_count(): int { return (int) db()->query('SELECT COUNT(*) FROM users')->fetchColumn(); }

function audit(string $action, string $detail = ''): void
{
    $u = current_user();
    db()->prepare('INSERT INTO audit (ts, username, action, detail) VALUES (?,?,?,?)')
        ->execute([now_str(), $u['username'] ?? '—', $action, mb_substr($detail, 0, 500)]);
}

/** Brute-force protection: max 8 failed logins per 15 minutes per visitor. */
function login_blocked(): bool
{
    db()->prepare('DELETE FROM login_attempts WHERE ts < ?')->execute([time() - 900]);
    $st = db()->prepare('SELECT COUNT(*) FROM login_attempts WHERE ip_hash = ?');
    $st->execute([ip_hash()]);
    return (int) $st->fetchColumn() >= 8;
}

function try_login(string $username, string $password): bool
{
    $st = db()->prepare('SELECT * FROM users WHERE username = ?');
    $st->execute([mb_strtolower(trim($username))]);
    $u = $st->fetch();
    if (!$u || !password_verify($password, $u['pass_hash'])) {
        db()->prepare('INSERT INTO login_attempts (ip_hash, ts) VALUES (?, ?)')->execute([ip_hash(), time()]);
        return false;
    }
    if (password_needs_rehash($u['pass_hash'], PASSWORD_DEFAULT)) {
        db()->prepare('UPDATE users SET pass_hash = ? WHERE id = ?')->execute([password_hash($password, PASSWORD_DEFAULT), $u['id']]);
    }
    session_regenerate_id(true);
    $_SESSION['uid'] = (int) $u['id'];
    db()->prepare('UPDATE users SET last_login = ? WHERE id = ?')->execute([now_str(), $u['id']]);
    db()->prepare('DELETE FROM login_attempts WHERE ip_hash = ?')->execute([ip_hash()]);
    return true;
}

function create_user(string $username, string $name, string $password, string $role): ?string
{
    $username = mb_strtolower(trim($username));
    if (!preg_match('/^[a-z0-9._-]{3,32}$/', $username)) return 'Логин: 3–32 символа, латиница, цифры, точка, дефис.';
    if (mb_strlen($password) < 10) return 'Пароль — минимум 10 символов.';
    if (!in_array($role, ['admin', 'editor'], true)) $role = 'editor';
    try {
        db()->prepare('INSERT INTO users (username, display_name, pass_hash, role, created_at) VALUES (?,?,?,?,?)')
            ->execute([$username, trim($name) ?: $username, password_hash($password, PASSWORD_DEFAULT), $role, now_str()]);
    } catch (PDOException $e) {
        return 'Такой логин уже есть.';
    }
    return null;
}

function fmt_dt(?string $s): string
{
    if (!$s) return '—';
    $t = strtotime($s);
    return $t ? date('d.m.Y H:i', $t) : e($s);
}
