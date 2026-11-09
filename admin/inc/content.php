<?php
/**
 * Website content editing: the JSON files in content/ live in the GitHub repository.
 * Saving = a commit through the GitHub API → GitHub Actions rebuilds the site and uploads it to the hosting.
 */
declare(strict_types=1);

/** What can be edited, and how each file looks. Field types: L (text in RU/UA/KZ), LT (long text), LH (formatted text),
 *  text, number, date, bool, select, list (of items), obj (fixed group of fields). */
function content_collections(): array
{
    $L = ['type' => 'L'];
    $money = ['type' => 'number', 'label' => 'Сумма, €', 'min' => 0];
    return [
        'packages' => [
            'file' => 'content/packages.json', 'title' => 'Цены и пакеты', 'icon' => '€',
            'hint' => 'Цены, этапы оплаты и состав пакетов. Изменения появятся на страницах «Услуги», «Главная», в сравнении и в тесте.',
            'schema' => ['type' => 'obj', 'fields' => [
                'packages' => ['type' => 'list', 'label' => 'Пакеты', 'fixed' => true, 'itemTitle' => 'name', 'item' => ['type' => 'obj', 'fields' => [
                    'name'     => ['type' => 'L', 'label' => 'Название'],
                    'price'    => ['type' => 'number', 'label' => 'Цена, €', 'min' => 0],
                    'badge'    => ['type' => 'L', 'label' => 'Метка (необязательно)', 'optional' => true],
                    'summary'  => ['type' => 'LT', 'label' => 'Короткое описание'],
                    'stages'   => ['type' => 'list', 'label' => 'Этапы оплаты', 'itemTitle' => 'label', 'item' => ['type' => 'obj', 'fields' => [
                        'label' => ['type' => 'L', 'label' => 'Этап'], 'amount' => $money]]],
                    'features' => ['type' => 'list', 'label' => 'Что входит', 'item' => $L],
                    'consultant' => ['type' => 'obj', 'label' => 'Лимиты консультанта', 'optional' => true, 'fields' => [
                        'writtenPerMonth' => ['type' => 'number', 'label' => 'Письменных обращений в месяц', 'min' => 0],
                        'hoursTotal'      => ['type' => 'number', 'label' => 'Часов связи', 'min' => 0]]],
                    'quizText' => ['type' => 'LT', 'label' => 'Текст рекомендации в тесте «Проверить шансы»', 'optional' => true],
                ]]],
                'compare' => ['type' => 'list', 'label' => 'Таблица сравнения (значения по порядку пакетов: ✓ — входит, — — не входит, или свой текст)', 'itemTitle' => 'label', 'item' => ['type' => 'obj', 'fields' => [
                    'label'  => ['type' => 'L', 'label' => 'Строка'],
                    'values' => ['type' => 'list', 'label' => 'Значения', 'fixed' => true, 'item' => $L]]]],
            ]],
        ],
        'faq' => [
            'file' => 'content/faq.json', 'title' => 'Вопросы и ответы', 'icon' => '?',
            'hint' => 'Страница «Вопросы». Ответы также попадают в Google как расширенный сниппет FAQ.',
            'schema' => ['type' => 'list', 'label' => 'Разделы', 'itemTitle' => 'group', 'item' => ['type' => 'obj', 'fields' => [
                'group' => ['type' => 'L', 'label' => 'Название раздела'],
                'items' => ['type' => 'list', 'label' => 'Вопросы', 'itemTitle' => 'q', 'item' => ['type' => 'obj', 'fields' => [
                    'q' => ['type' => 'L', 'label' => 'Вопрос'],
                    'a' => ['type' => 'LT', 'label' => 'Ответ']]]],
            ]]],
        ],
        'calendar' => [
            'file' => 'content/calendar.json', 'title' => 'Календарь поступления', 'icon' => '◷',
            'hint' => 'Этапы и даты на странице «Календарь». Обновляйте даты, когда Министерство объявит новый цикл.',
            'schema' => ['type' => 'list', 'label' => 'Этапы', 'itemTitle' => 'title', 'item' => ['type' => 'obj', 'fields' => [
                'when'   => ['type' => 'L', 'label' => 'Когда (например «2 — 9 июля 2027»)'],
                'title'  => ['type' => 'L', 'label' => 'Заголовок'],
                'text'   => ['type' => 'LT', 'label' => 'Описание'],
                'kind'   => ['type' => 'select', 'label' => 'Тип', 'options' => ['prep' => 'Подготовка', 'key' => 'Ключевая дата', 'after' => 'После зачисления']],
                'portal' => ['type' => 'bool', 'label' => 'Показать ссылку на портал подачи заявок'],
            ]]],
        ],
        'universities' => [
            'file' => 'content/universities.json', 'title' => 'Университеты', 'icon' => '⌂',
            'hint' => 'Карточки на странице «Университеты».',
            'schema' => ['type' => 'list', 'label' => 'Университеты', 'itemTitle' => 'name', 'item' => ['type' => 'obj', 'fields' => [
                'name'    => ['type' => 'L', 'label' => 'Название'],
                'greek'   => ['type' => 'text', 'label' => 'Название по-гречески / сокращение'],
                'city'    => ['type' => 'L', 'label' => 'Город'],
                'group'   => ['type' => 'select', 'label' => 'Фильтр', 'options' => ['athens' => 'Афины и Пирей', 'thess' => 'Салоники', 'other' => 'Другие города']],
                'founded' => ['type' => 'text', 'label' => 'Год основания'],
                'profile' => ['type' => 'LT', 'label' => 'Направления'],
            ]]],
        ],
        'articles' => [
            'file' => 'content/articles.json', 'title' => 'Статьи (блог)', 'icon' => '✎',
            'hint' => 'Новые статьи помогают сайту расти в Google. Адрес статьи (slug) — латиницей, после публикации его лучше не менять.',
            'schema' => ['type' => 'list', 'label' => 'Статьи', 'itemTitle' => 'title', 'newFirst' => true, 'item' => ['type' => 'obj', 'fields' => [
                'title'   => ['type' => 'L', 'label' => 'Заголовок'],
                'slug'    => ['type' => 'text', 'label' => 'Адрес: mystudygr.com/blog/…/', 'pattern' => '^[a-z0-9]+(-[a-z0-9]+)*$', 'slugFrom' => 'title'],
                'date'    => ['type' => 'date', 'label' => 'Дата публикации'],
                'minutes' => ['type' => 'number', 'label' => 'Минут на чтение', 'min' => 1],
                'art'     => ['type' => 'select', 'label' => 'Иллюстрация в шапке', 'options' => ['learn' => 'Библиотека', 'cont' => 'Театр', 'univ' => 'Академия', 'cal' => 'Башня', 'faq' => 'Сова', 'blog' => 'Свиток', 'about' => 'Кариатиды', 'serv' => 'Стоя', 'home' => 'Храм']],
                'desc'    => ['type' => 'LT', 'label' => 'Краткое описание (видно в Google, до 160 символов)', 'max' => 200],
                'body'    => ['type' => 'LH', 'label' => 'Текст статьи'],
            ]]],
        ],
    ];
}

/* ------------------------------ GitHub API ------------------------------ */

/** Local mode (for testing on a computer): 'content_local_dir' => '/path/to/repo' in config.php. */
function local_dir(): string { return rtrim((string) (msgr_config()['content_local_dir'] ?? ''), '/'); }

function gh_ready(): bool { $c = msgr_config(); return local_dir() !== '' || ($c['github_token'] !== '' && $c['github_repo'] !== ''); }

function gh(string $method, string $path, ?array $body = null): array
{
    $c = msgr_config();
    return http_json($method, 'https://api.github.com/repos/' . $c['github_repo'] . $path, $body, [
        'Authorization: Bearer ' . $c['github_token'], 'X-GitHub-Api-Version: 2022-11-28', 'Accept: application/vnd.github+json',
    ]);
}

/** Returns [data(array), sha] or throws. */
function gh_read_json(string $file, ?string $ref = null): array
{
    if (local_dir() !== '') {
        $raw = (string) @file_get_contents(local_dir() . '/' . $file);
        $data = json_decode($raw, true);
        if (!is_array($data)) throw new RuntimeException('Не найден файл ' . $file);
        return [$data, md5($raw)];
    }
    $ref = $ref ?? msgr_config()['github_branch'];
    $r = gh('GET', '/contents/' . str_replace('%2F', '/', rawurlencode($file)) . '?ref=' . rawurlencode($ref));
    if ($r['status'] !== 200 || empty($r['body']['content'])) {
        throw new RuntimeException('GitHub: не удалось прочитать ' . $file . ' (код ' . $r['status'] . ')');
    }
    $data = json_decode(base64_decode($r['body']['content']), true);
    if (!is_array($data)) throw new RuntimeException('Файл ' . $file . ' повреждён.');
    return [$data, $r['body']['sha']];
}

function gh_write_json(string $file, array $data, string $sha, string $message): array
{
    $json = json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT) . "\n";
    $u = current_user();
    if (local_dir() !== '') {
        $path = local_dir() . '/' . $file;
        if (md5((string) @file_get_contents($path)) !== $sha) throw new RuntimeException('Файл успели изменить в другом окне. Обновите страницу.');
        file_put_contents($path, $json);
        return ['local' => true];
    }
    $r = gh('PUT', '/contents/' . str_replace('%2F', '/', rawurlencode($file)), [
        'message' => $message, 'content' => base64_encode($json), 'sha' => $sha, 'branch' => msgr_config()['github_branch'],
        'committer' => ['name' => 'MSGR admin (' . ($u['username'] ?? '?') . ')', 'email' => 'admin@mystudygr.com'],
    ]);
    if ($r['status'] === 409 || $r['status'] === 422) throw new RuntimeException('Файл успели изменить в другом окне. Обновите страницу — ваши правки нужно будет повторить.');
    if ($r['status'] !== 200 && $r['status'] !== 201) throw new RuntimeException('GitHub отклонил сохранение (код ' . $r['status'] . '). Проверьте токен в config.php.');
    return $r['body'];
}

function gh_history(string $file, int $n = 15): array
{
    if (local_dir() !== '') return [];
    $r = gh('GET', '/commits?path=' . rawurlencode($file) . '&sha=' . rawurlencode(msgr_config()['github_branch']) . '&per_page=' . $n);
    return $r['status'] === 200 && is_array($r['body']) ? $r['body'] : [];
}

function gh_last_runs(int $n = 5): array
{
    if (local_dir() !== '') return [];
    $r = gh('GET', '/actions/runs?per_page=' . $n . '&branch=' . rawurlencode(msgr_config()['github_branch']));
    return $r['status'] === 200 ? ($r['body']['workflow_runs'] ?? []) : [];
}

/* ------------------------------ validation ------------------------------ */

/** Keep only safe formatting in article text. */
function sanitize_rich(string $html): string
{
    $html = trim($html);
    if ($html === '') return '';
    $allowed = ['p' => ['class'], 'h2' => [], 'h3' => [], 'ul' => [], 'ol' => [], 'li' => [], 'strong' => [], 'b' => [],
                'em' => [], 'i' => [], 'a' => ['href'], 'br' => [], 'div' => ['class'], 'blockquote' => []];
    $doc = new DOMDocument();
    libxml_use_internal_errors(true);
    $doc->loadHTML('<?xml encoding="utf-8"?><div id="root">' . $html . '</div>', LIBXML_HTML_NOIMPLIED | LIBXML_HTML_NODEFDTD);
    libxml_clear_errors();
    $root = $doc->getElementById('root');
    if (!$root) return '';
    $walk = function (DOMNode $node) use (&$walk, $allowed, $doc) {
        foreach (iterator_to_array($node->childNodes) as $child) {
            if ($child instanceof DOMElement) {
                $tag = strtolower($child->tagName);
                if ($tag === 'span' || $tag === 'font') { // unwrap
                    $walk($child);
                    while ($child->firstChild) $node->insertBefore($child->firstChild, $child);
                    $node->removeChild($child);
                    continue;
                }
                if (!isset($allowed[$tag]) || in_array($tag, ['script', 'style', 'iframe'], true)) { $node->removeChild($child); continue; }
                foreach (iterator_to_array($child->attributes) as $attr) {
                    $n = strtolower($attr->name);
                    if (!in_array($n, $allowed[$tag], true)) { $child->removeAttribute($attr->name); continue; }
                    if ($n === 'href' && !preg_match('#^(https?://|mailto:|tel:|/|\#)#i', trim($attr->value))) $child->removeAttribute('href');
                    if ($n === 'class') {
                        $ok = array_intersect(preg_split('/\s+/', $attr->value), ['lead', 'note', 'note--warn']);
                        if ($ok) $child->setAttribute('class', implode(' ', $ok)); else $child->removeAttribute('class');
                    }
                }
                $walk($child);
            } elseif ($child instanceof DOMComment) {
                $node->removeChild($child);
            }
        }
    };
    $walk($root);
    $out = '';
    foreach ($root->childNodes as $c) $out .= $doc->saveHTML($c);
    $out = preg_replace('#<p>(\s|&nbsp;|<br>)*</p>#u', '', $out);
    return trim(str_replace('&nbsp;', ' ', $out));
}

/** Clean + check incoming data against the schema. Errors are collected in $errs. */
function validate_value($v, array $s, string $path, array &$errs)
{
    $label = $s['label'] ?? $path;
    switch ($s['type']) {
        case 'L': case 'LT': case 'LH':
            if (!is_array($v)) $v = ['ru' => is_string($v) ? $v : ''];
            $max = $s['max'] ?? ($s['type'] === 'LH' ? 200000 : ($s['type'] === 'LT' ? 4000 : 400));
            $o = [];
            foreach (['ru', 'uk', 'kk'] as $c) {
                $t = is_string($v[$c] ?? null) ? $v[$c] : '';
                $t = $s['type'] === 'LH' ? sanitize_rich($t) : trim(preg_replace('/\s+/u', ' ', strip_tags($t)) ?? '');
                $o[$c] = mb_substr($t, 0, $max);
            }
            if ($o['ru'] === '' && empty($s['optional'])) $errs[] = "«{$label}»: заполните русский вариант.";
            if ($o['ru'] === '' && !empty($s['optional'])) return null;
            return $o;
        case 'text':
            $t = trim(strip_tags((string) (is_scalar($v) ? $v : '')));
            if (!empty($s['pattern']) && !preg_match('/' . $s['pattern'] . '/', $t)) $errs[] = "«{$label}»: только латиница, цифры и дефисы.";
            return mb_substr($t, 0, 300);
        case 'number':
            if (!is_numeric($v)) { $errs[] = "«{$label}»: нужно число."; return 0; }
            $n = $v + 0;
            if (isset($s['min']) && $n < $s['min']) $errs[] = "«{$label}»: не меньше {$s['min']}.";
            return is_float($n) && floor($n) != $n ? $n : (int) $n;
        case 'date':
            $t = (string) $v;
            if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $t)) { $errs[] = "«{$label}»: дата в формате ГГГГ-ММ-ДД."; $t = date('Y-m-d'); }
            return $t;
        case 'bool':
            return (bool) $v;
        case 'select':
            $t = (string) $v;
            if (!isset($s['options'][$t])) $t = array_key_first($s['options']);
            return $t;
        case 'obj':
            if ($v === null && !empty($s['optional'])) return null;
            $v = is_array($v) ? $v : [];
            $o = $v; // keep unknown keys (e.g. package id, extras) untouched
            foreach ($s['fields'] as $k => $fs) {
                $val = validate_value($v[$k] ?? null, $fs, "$path.$k", $errs);
                if ($val === null && !empty($fs['optional'])) { unset($o[$k]); continue; }
                $o[$k] = $val;
            }
            return $o;
        case 'list':
            $v = is_array($v) ? array_values($v) : [];
            $o = [];
            foreach ($v as $i => $item) $o[] = validate_value($item, $s['item'], "$path[$i]", $errs);
            return $o;
    }
    return $v;
}

function validate_collection(string $key, $data, $old, array &$errs)
{
    $col = content_collections()[$key];
    $clean = validate_value($data, $col['schema'], $key, $errs);
    if ($key === 'packages') {
        // the set of packages is fixed (their colours/buttons are designed per package)
        $oldIds = array_column($old['packages'] ?? [], 'id');
        $newIds = array_column($clean['packages'] ?? [], 'id');
        if ($oldIds !== $newIds) $errs[] = 'Набор пакетов менять нельзя — только их содержимое.';
        foreach ($clean['compare'] ?? [] as $row) {
            if (count($row['values'] ?? []) !== count($newIds)) { $errs[] = 'В каждой строке сравнения должно быть ' . count($newIds) . ' значений.'; break; }
        }
    }
    if ($key === 'articles') {
        $seen = [];
        foreach ($clean as $a) {
            if (isset($seen[$a['slug']])) $errs[] = 'Адрес статьи «' . $a['slug'] . '» повторяется.';
            $seen[$a['slug']] = true;
            if (($a['body']['ru'] ?? '') === '') $errs[] = 'Статья «' . ($a['title']['ru'] ?? '') . '»: нет текста.';
        }
    }
    return $clean;
}

/** Fields where UA/KZ translation is missing (shown as a warning; the site then shows Russian). */
function missing_translations($v, array $s, string $where = ''): array
{
    $out = [];
    if (in_array($s['type'], ['L', 'LT', 'LH'], true)) {
        if (is_array($v) && ($v['ru'] ?? '') !== '') {
            foreach (['uk' => 'UA', 'kk' => 'KZ'] as $c => $lab) if (($v[$c] ?? '') === '') $out[] = trim($where . ' → ' . ($s['label'] ?? '')) . " ($lab)";
        }
    } elseif ($s['type'] === 'obj' && is_array($v)) {
        foreach ($s['fields'] as $k => $fs) $out = array_merge($out, missing_translations($v[$k] ?? null, $fs, $where));
    } elseif ($s['type'] === 'list' && is_array($v)) {
        foreach ($v as $i => $item) {
            $t = $where;
            if (isset($s['itemTitle']) && is_array($item) && isset($item[$s['itemTitle']])) {
                $x = $item[$s['itemTitle']];
                $t = trim($where . ' / ' . mb_substr(is_array($x) ? ($x['ru'] ?? '') : (string) $x, 0, 40), ' /');
            }
            $out = array_merge($out, missing_translations($item, $s['item'], $t));
        }
    }
    return $out;
}
