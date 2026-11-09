<?php
/**
 * Copy this file to config.php (same folder) and fill in the values.
 * config.php is blocked from the web by api/.htaccess and ignored by Git — never commit real tokens.
 *
 * Telegram: create a bot with @BotFather → copy the token.
 *   Add the bot to your group/chat, send it a message, then open
 *   https://api.telegram.org/bot<TOKEN>/getUpdates and find "chat":{"id": ...}.
 *
 * GitHub (for "Опубликовать" in the admin panel): github.com → Settings → Developer settings →
 *   Fine-grained tokens → Generate. Repository access: only J-ntk/MSGR.
 *   Permissions: Contents = Read and write, Actions = Read-only.
 */
return [
    // --- Leads: where new requests are sent ---
    'telegram_bot_token' => '',                       // e.g. '123456789:AA...'
    'telegram_chat_id'   => '',                       // e.g. '-1001234567890' (group) or your user id
    'mail_to'            => 'mystudygr1@gmail.com',
    'mail_from'          => 'no-reply@mystudygr.com', // a mailbox on your domain gives the best delivery
    'allowed_origins'    => ['https://mystudygr.com', 'https://www.mystudygr.com'],

    // --- Admin panel ---
    // One-time key to create the first admin account at /admin/ (any long random text). Clear it afterwards.
    'admin_setup_key'    => '',
    // Database folder. Default = "msgr-data" next to public_html (not reachable from the web).
    // 'data_dir'        => '/home/d/djdordje/mystudygr.com/msgr-data',

    // --- Publishing through GitHub ---
    'github_token'       => '',                       // fine-grained token (see above)
    'github_repo'        => 'J-ntk/MSGR',
    'github_branch'      => 'main',
];
