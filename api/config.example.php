<?php
/**
 * Copy this file to config.php (same folder) and fill in the values.
 * config.php is blocked from the web by api/.htaccess — never commit real tokens to Git.
 *
 * Telegram: create a bot with @BotFather → copy the token.
 *   Then add the bot to your group/chat, send it a message and open
 *   https://api.telegram.org/bot<TOKEN>/getUpdates to find "chat":{"id": ...}.
 */
return [
  'telegram_bot_token' => '',            // e.g. '123456789:AA...'
  'telegram_chat_id'   => '',            // e.g. '-1001234567890' (group) or your user id
  'mail_to'            => 'mystudygr1@gmail.com',
  'mail_from'          => 'no-reply@mystudygr.com',  // must be a mailbox on your domain for good delivery
  'allowed_origins'    => ['https://mystudygr.com', 'https://www.mystudygr.com'],
];
