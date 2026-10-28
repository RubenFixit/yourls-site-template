<?php
/**
 * Deployment health endpoint — template-owned (yourls-site-template).
 *
 * 200 {"ok": true}  when the server-local config loads and the database answers SELECT 1.
 * 503 {"ok": false} otherwise.
 * Deliberately discloses nothing else (no versions, no error messages).
 */

define('YM_CONFIG_OPTIONAL', true);

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, max-age=0');
header('X-Robots-Tag: noindex, nofollow');

/**
 * Build a PDO MySQL DSN from YOURLS_DB_HOST, which may be "host", "host:port"
 * or "host:/path/to/socket".
 */
function ym_health_dsn(string $host, string $dbname): string
{
    $parts = ["dbname={$dbname}", 'charset=utf8mb4'];
    $pos = strrpos($host, ':');
    if ($pos !== false && strpos($host, ']') === false) {
        $name = substr($host, 0, $pos);
        $extra = substr($host, $pos + 1);
        if ($extra !== '' && $extra[0] === '/') {
            $parts[] = "unix_socket={$extra}";
        } else {
            $parts[] = 'host=' . ($name === '' ? 'localhost' : $name);
            if (ctype_digit($extra)) {
                $parts[] = "port={$extra}";
            }
        }
    } else {
        $parts[] = "host={$host}";
    }
    return 'mysql:' . implode(';', $parts);
}

$ok = false;
try {
    $loaded = require __DIR__ . '/user/config.php';
    if ($loaded !== false
        && defined('YOURLS_DB_HOST') && defined('YOURLS_DB_NAME')
        && defined('YOURLS_DB_USER') && defined('YOURLS_DB_PASS')) {
        $pdo = new PDO(
            ym_health_dsn((string) YOURLS_DB_HOST, (string) YOURLS_DB_NAME),
            (string) YOURLS_DB_USER,
            (string) YOURLS_DB_PASS,
            [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_TIMEOUT => 3]
        );
        $ok = ((int) $pdo->query('SELECT 1')->fetchColumn()) === 1;
    }
} catch (Throwable $e) {
    $ok = false;
}

http_response_code($ok ? 200 : 503);
echo json_encode(['ok' => $ok]), "\n";
