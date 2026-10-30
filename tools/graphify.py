#!/usr/bin/env python3
"""/graphify: a one-page visual map of the Quran apps project (owner, 2026-10-30): key numbers, the room each top-level folder
takes under the 1 GB GitHub Pages limit, the tree of apps (from apps.json) and the other folders, every tool and script with
its first docstring line, the skills, the file types, the largest files, and what looks missing or out of place.
Usage: python3 tools/graphify.py [OUT.html]      (default: graphify.html in the current folder; self-contained, RTL, light/dark)"""
import os, re, sys, json, glob, html as H, datetime, subprocess, hashlib
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
LIMIT = 1024 * 2**20           # GitHub Pages: a published site may be at most 1 GB
BIG_FILE = 25 * 2**20           # GitHub warns at 50 MB and refuses 100 MB; flag files well before that
SCRIPT_EXT = ('.py', '.js', '.mjs', '.sh')
STATUS = {'draft': 'قيد البناء', 'ready': 'جاهز'}
FOLDER_NAMES = {'apps': 'التطبيقات', 'assets': 'التصميم والسكربتات المشتركة', 'data': 'نص المصحف الموثّق', 'tools': 'أدوات البناء والفحص',
                'templates': 'قالب التطبيق الجديد', '.claude': 'مهارات Claude', '.github': 'إعدادات GitHub'}
TAMYIZ = {'ملف': 'ملفًا', 'مجلد': 'مجلدًا', 'تطبيق': 'تطبيقًا', 'مجلد فرعي': 'مجلدًا فرعيًا'}


def count(n, one, many):
    """Arabic counted noun: plural for 3–10, accusative singular for 11–99, singular otherwise."""
    m = n % 100
    return '%d %s' % (n, many if 3 <= m <= 10 else TAMYIZ.get(one, one) if m >= 11 else one)


def tracked(root):
    """The files Pages publishes: those git tracks plus new ones not ignored (all files, without .git, when git is missing)."""
    try:
        r = subprocess.run(['git', '-C', root, 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], capture_output=True, check=True)
        return sorted({f for f in r.stdout.decode('utf8').split('\0') if f and os.path.isfile(root + f) and not os.path.islink(root + f)})
    except Exception:
        out = []
        for d, sub, fs in os.walk(root):
            if '.git' in sub: sub.remove('.git')
            out += [os.path.relpath(os.path.join(d, f), root) for f in fs if not os.path.islink(os.path.join(d, f))]
        return out


def walk(root):
    """Size and file count of every folder (recursively), the size of every file, and per-extension totals."""
    size, files, all_files, ext = {'': 0}, {'': 0}, [], {}
    for rel in tracked(root):
        s = os.path.getsize(root + rel)
        all_files.append((s, rel))
        e = os.path.splitext(rel)[1].lower() if '.' in os.path.basename(rel).lstrip('.') else '(بلا امتداد)'
        c = ext.setdefault(e, [0, 0]); c[0] += 1; c[1] += s
        parts = rel.split('/')[:-1]
        for i in range(len(parts) + 1):
            k = '/'.join(parts[:i]) + ('/' if i else '')
            size[k] = size.get(k, 0) + s; files[k] = files.get(k, 0) + 1
    return size, files, len(size) - 1, all_files, ext


def first_doc(p):
    t = open(p, encoding='utf8', errors='ignore').read(6000)
    t = re.sub(r'^#!.*\n', '', t)
    m = (re.match(r'\s*(?:[rRuU]?)("""|\'\'\')(.*?)(?:\1|$)', t, re.S) or re.match(r'\s*()/\*\*?(.*?)\*/', t, re.S)
         or re.match(r'\s*()((?:(?://|#)[^\n]*\n?)+)', t))
    if not m: return ''
    s = re.sub(r'^\s*(?://|#|\*)\s?', '', m.group(2).strip(), flags=re.M).strip()
    s = ' '.join(s.split('\n\n')[0].split())            # the first paragraph, its wrapped lines joined
    s = re.split(r'(?<=[^\d\s][.!?؟])\s', s)[0]          # … up to the end of its first sentence
    return s if len(s) <= 240 else s[:239] + '…'


def human(b):
    """A size for the page, isolated left-to-right so «4.9 MB» does not flip to «MB 4.9»."""
    s = ('%.2f GB' % (b / 2**30) if b >= 2**30 else ('%.1f MB' % (b / 2**20)) if b >= 2**20 else '%d KB' % max(1, round(b / 1024)))
    return '<bdi dir="ltr">%s</bdi>' % s


def path(p): return '<code dir="ltr">%s</code>' % H.escape(p)


def bar(b, label, note='', base=LIMIT):
    pct = 100 * b / base if base else 0
    tone = 'ok' if pct < 70 else ('warn' if pct <= 90 else 'bad')
    return ('<div class="row"><div class="rh"><b>%s</b><span>%s · <bdi>%s%%</bdi></span></div><div class="bar"><i class="%s" style="width:%.1f%%"></i>'
            '</div>%s</div>') % (label, human(b), ('%.0f' % pct) if pct >= 1 else '%.1f' % pct, tone, min(100, pct),
                                 ('<small>%s</small>' % note) if note else '')


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else 'graphify.html'
    size, files, ndirs, all_files, ext = walk(R)
    total = size.get('', 0)
    reg = json.load(open(R + 'apps.json', encoding='utf8')) if os.path.exists(R + 'apps.json') else {'apps': []}
    apps = reg.get('apps', [])
    quran = json.load(open(R + 'data/quran.json', encoding='utf8')) if os.path.exists(R + 'data/quran.json') else []
    tools = sorted(f for f in glob.glob(R + 'tools/**/*', recursive=True) + glob.glob(R + 'assets/**/*', recursive=True)
                   if f.endswith(SCRIPT_EXT))
    skills = sorted(glob.glob(R + '.claude/skills/*/SKILL.md'))
    ready = sum(1 for a in apps if a.get('status') == 'ready')
    stats = [('الملفات', '{:,}'.format(len(all_files))), ('المجلدات', '{:,}'.format(ndirs)), ('الحجم الكلي', human(total)),
             ('التطبيقات', len(apps)), ('جاهزة', ready), ('قيد البناء', len(apps) - ready),
             ('سور المصحف', len(quran)), ('آيات المصحف', '{:,}'.format(sum(len(s['ayat']) for s in quran))),
             ('الأدوات والسكربتات', len(tools)), ('مهارات Claude', len(skills))]

    # ---- what looks missing or out of place ---------------------------------------------------------------------------
    notes = []
    if total > 0.7 * LIMIT:
        notes.append('حجم المشروع %s، أي %d%% من حد GitHub Pages ‏1 GB.' % (human(total), round(100 * total / LIMIT)))
    if not os.path.exists(R + 'apps.json'): notes.append('لا يوجد فهرس التطبيقات %s.' % path('apps.json'))
    on_disk = {os.path.basename(d.rstrip('/')) for d in glob.glob(R + 'apps/*/')}
    listed = {a['slug'] for a in apps}
    for s in sorted(on_disk - listed): notes.append('المجلد %s ليس في %s (لن يظهر في الصفحة الرئيسية).' % (path('apps/%s/' % s), path('apps.json')))
    for s in sorted(listed - on_disk): notes.append('التطبيق %s مسجّل في %s ومجلده غير موجود.' % (path(s), path('apps.json')))
    for a in apps:
        d = R + 'apps/%s/' % a['slug']
        if not os.path.exists(d + 'index.html'): continue
        t = open(d + 'index.html', encoding='utf8').read()
        lack = []
        if not re.search(r'<html[^>]*\blang="ar"[^>]*\bdir="rtl"|<html[^>]*\bdir="rtl"[^>]*\blang="ar"', t): lack.append('lang="ar" dir="rtl"')
        if 'assets/design.css' not in t: lack.append('assets/design.css')
        if not os.path.exists(d + 'sw.js') or 'manifest.webmanifest' not in t: lack.append('العمل بلا إنترنت (tools/pwa.py)')
        if not a.get('desc'): lack.append('وصف في apps.json')
        if lack: notes.append('%s %s ينقصه: %s.' % (H.escape(a['title']), path('apps/%s/' % a['slug']), '، '.join(lack)))
    try:
        sys.path.insert(0, R + 'tools'); sys.dont_write_bytecode = True
        import quran_check
        if quran and hashlib.sha256(open(R + 'data/quran.json', 'rb').read()).hexdigest() != quran_check.SHA256:
            notes.append('نص المصحف %s تغيّر عن النسخة الموثّقة. شغّل %s.' % (path('data/quran.json'), path('tools/quran_check.py')))
    except Exception: pass
    if quran and (len(quran) != 114 or sum(len(s['ayat']) for s in quran) != 6236):
        notes.append('نص المصحف ناقص: %d سورة و%d آية بدل 114 و6236.' % (len(quran), sum(len(s['ayat']) for s in quran)))
    big = sorted([x for x in all_files if x[0] >= BIG_FILE], reverse=True)
    if big: notes.append('%s أكبر من %d MB (أكبرها %s ‏%s).' % (count(len(big), 'ملف', 'ملفات'), BIG_FILE // 2**20, path(big[0][1]), human(big[0][0])))
    nodoc = [os.path.relpath(f, R) for f in tools if not first_doc(f)]
    if nodoc: notes.append('أدوات بلا شرح في أولها: %s.' % ' '.join(path(f) for f in nodoc))
    junk = [f for s, f in all_files if f.endswith(('.pyc', '.DS_Store', 'Thumbs.db', '~')) or '__pycache__/' in f]
    if junk: notes.append('ملفات مؤقتة لا داعي لها: %s.' % ' '.join(path(f) for f in junk[:10]))
    note_html = ''.join('<li>%s</li>' % n for n in notes) or '<li>لا شيء لافت: كل التطبيقات مسجّلة ومكتملة الأساسيات.</li>'

    # ---- room: each top-level folder against 1 GB ----------------------------------------------------------------------
    folders = bar(total, 'المشروع كله', 'ما ينشره GitHub Pages (الملفات المتتبَّعة في git)')
    for k in sorted((k for k in size if k and k.count('/') == 1), key=lambda k: -size[k]):
        lab = FOLDER_NAMES.get(k[:-1], '')
        folders += bar(size[k], path(k) + (' <span class="lab">%s</span>' % lab if lab else ''), count(files[k], 'ملف', 'ملفات'))

    # ---- tree: apps from apps.json, then the other folders ------------------------------------------------------------
    def dir_node(k, depth, label=''):
        kids = sorted((x for x in size if x.startswith(k) and x != k and x[len(k):].count('/') == 1), key=lambda x: -size[x])
        loose = sorted(f for s, f in all_files if f.startswith(k) and '/' not in f[len(k):])
        inner = ''.join(dir_node(x, depth + 1) for x in kids[:40]) if depth < 3 else (
            '<p class="legend">%s</p>' % count(len(kids), 'مجلد فرعي', 'مجلدات فرعية') if kids else '')
        if len(kids) > 40 and depth < 3: inner += '<p class="legend">… و%s</p>' % count(len(kids) - 40, 'مجلد', 'مجلدات')
        if loose:
            sz = dict((f, s) for s, f in all_files)
            inner += '<ul>%s</ul>' % ''.join('<li>%s <em>%s</em></li>' % (path(f[len(k):]), human(sz[f])) for f in loose[:30])
            if len(loose) > 30: inner += '<p class="legend">… و%s</p>' % count(len(loose) - 30, 'ملف', 'ملفات')
        return '<details class="node"><summary>%s%s<em>%s · %s · %s</em></summary>%s</details>' % (
            label, path(k), count(len(kids), 'مجلد', 'مجلدات'), count(files.get(k, 0), 'ملف', 'ملفات'), human(size.get(k, 0)), inner)

    tree = ''
    app_nodes = ''
    for a in apps:
        k = 'apps/%s/' % a['slug']
        chips = ''.join('<span class="chip%s">%s</span> ' % (' st' if i == 0 else '', H.escape(t)) for i, t in
                        enumerate([STATUS.get(a.get('status'), a.get('status', '—'))] + a.get('tags', [])))
        if k in size:
            app_nodes += dir_node(k, 2, '<b>%s</b> %s' % (H.escape(a['title']), chips))
        else:
            app_nodes += '<details class="node"><summary><b>%s</b> %s%s<em>المجلد غير موجود</em></summary></details>' % (
                H.escape(a['title']), chips, path(k))
    tree += '<details class="node" open><summary><b>التطبيقات</b> %s<em>%s · %s · %s</em></summary>%s</details>' % (
        path('apps/'), count(len(apps), 'تطبيق', 'تطبيقات'), count(files.get('apps/', 0), 'ملف', 'ملفات'), human(size.get('apps/', 0)),
        app_nodes or '<p class="legend">لا تطبيقات بعد.</p>')
    for k in sorted((k for k in size if k and k.count('/') == 1 and k != 'apps/'), key=lambda k: -size[k]):
        lab = FOLDER_NAMES.get(k[:-1], '')
        tree += dir_node(k, 1, ('<b>%s</b> ' % lab) if lab else '')
    rootf = sorted(f for s, f in all_files if '/' not in f)
    tree += '<details class="node"><summary><b>ملفات الجذر</b><em>%s</em></summary><p>%s</p></details>' % (
        count(len(rootf), 'ملف', 'ملفات'), ' '.join(path(f) for f in rootf))

    # ---- tables -------------------------------------------------------------------------------------------------------
    tool_rows = ''.join('<tr><td>%s</td><td dir="auto">%s</td></tr>' % (path(os.path.relpath(f, R)), H.escape(first_doc(f)) or '<span class="muted">—</span>')
                        for f in tools)
    skill_rows = ''
    for s in skills:
        t = open(s, encoding='utf8').read()
        n = re.search(r'^name:\s*(.+)$', t, re.M); d = re.search(r'^description:\s*(.+)$', t, re.M)
        skill_rows += '<tr><td>%s</td><td dir="auto">%s</td></tr>' % (path('/' + (n.group(1).strip() if n else os.path.basename(os.path.dirname(s)))),
                                                                     H.escape(d.group(1).strip() if d else ''))
    ext_rows = ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td class="mini"><div class="bar"><i class="ok" style="width:%.1f%%"></i></div></td></tr>'
                       % (path(e), '{:,}'.format(c[0]), human(c[1]), 100 * c[1] / total if total else 0)
                       for e, c in sorted(ext.items(), key=lambda x: -x[1][1]))
    big_rows = ''.join('<tr><td>%s</td><td>%s</td></tr>' % (path(f), human(s)) for s, f in sorted(all_files, reverse=True)[:15])

    cards = ''.join('<div class="st"><b>%s</b><span>%s</span></div>' % (n, H.escape(t)) for t, n in stats)
    try: head = subprocess.run(['git', '-C', R, 'log', '-1', '--format=%h · %cd', '--date=format:%Y-%m-%d %H:%M'],
                               capture_output=True, text=True).stdout.strip()
    except Exception: head = ''
    when = datetime.datetime.now().strftime('%Y-%m-%d %H:%M') + ((' — آخر تعديل <bdi dir="ltr">%s</bdi>' % H.escape(head)) if head else '')
    page = TEMPLATE
    for a, b in (('when', when), ('cards', cards), ('notes', note_html), ('folders', folders), ('tree', tree),
                 ('tools', tool_rows), ('skills', skill_rows), ('ext', ext_rows), ('big', big_rows)):
        page = page.replace('{{%s}}' % a, b)
    open(out, 'w', encoding='utf8').write(page)
    print('map written:', out, '|', re.sub('<[^>]+>', '', ' · '.join('%s %s' % (t, n) for t, n in stats)), '| notes:', len(notes))


TEMPLATE = '''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>خريطة تطبيقات القرآن</title><style>
:root{--bg:#F6F3EC;--card:#fff;--ink:#1E2421;--muted:#5F6B64;--line:#E1D9C7;--brand:#0F6B4F;--ok:#1F8A4C;--warn:#C27A0E;--bad:#C63E3E;--chip:#EFE9DC;--gold:#F6EBCF;--note:#FFF6E5}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0E1512;--card:#16201C;--ink:#E9EFEB;--muted:#9DB0A6;--line:#2A3A33;--brand:#4CC39A;--chip:#1D2A25;--gold:#2D2715;--ok:#4CC38A;--warn:#F0A63A;--bad:#F06A6A;--note:#2A2616}}
:root[data-theme="dark"]{--bg:#0E1512;--card:#16201C;--ink:#E9EFEB;--muted:#9DB0A6;--line:#2A3A33;--brand:#4CC39A;--chip:#1D2A25;--gold:#2D2715;--ok:#4CC38A;--warn:#F0A63A;--bad:#F06A6A;--note:#2A2616}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}body{margin:0;background:var(--bg);color:var(--ink);font-family:Tahoma,"Segoe UI",system-ui,sans-serif;line-height:1.7}
main{max-width:1000px;margin:0 auto;padding:20px 16px 60px}h1{margin:0;font-size:clamp(22px,5vw,30px)}h2{font-size:19px;margin:30px 0 10px}
.top{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}#theme{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:99px;min-width:44px;min-height:44px;font:inherit;cursor:pointer}
.sub{color:var(--muted);margin:2px 0 16px;font-size:14px}.muted{color:var(--muted)}
code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px;unicode-bidi:isolate;overflow-wrap:anywhere}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(135px,1fr));gap:10px}.st{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px}
.st b{display:block;font-size:24px;color:var(--brand)}.st span{color:var(--muted);font-size:13.5px}
.notes{background:var(--note);border:1px solid var(--line);border-radius:14px;padding:10px 14px}.notes ul{margin:0;padding-inline-start:20px}.notes li{margin:4px 0}
.box{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:6px 14px}
.row{padding:10px 0;border-top:1px solid var(--line)}.row:first-child{border-top:0}.rh{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:baseline}
.rh span{color:var(--muted);font-size:14px}.lab{color:var(--muted);font-weight:normal;font-size:13px}.row small{color:var(--muted)}
.bar{height:10px;border-radius:99px;background:var(--chip);margin:6px 0 2px;overflow:hidden}.bar i{display:block;height:100%;border-radius:99px}
.ok{background:var(--ok)}.warn{background:var(--warn)}.bad{background:var(--bad)}
.legend{color:var(--muted);font-size:13px;margin:6px 0}
details.node{border-top:1px dashed var(--line);padding:4px 0}details details{margin-inline-start:14px}
.box>details:first-child{border-top:0}summary{cursor:pointer;padding:3px 0;overflow-wrap:anywhere}
summary em,li em{display:inline-block;white-space:nowrap;font-style:normal;color:var(--muted);font-size:12.5px;margin-inline-start:8px}
summary code{margin-inline-start:6px;color:var(--muted)}ul{margin:4px 0 8px;padding-inline-start:18px}li{margin:3px 0}
.chip{font-size:12.5px;padding:1px 10px;border-radius:99px;background:var(--chip);border:1px solid var(--line);white-space:nowrap}.chip.st{background:var(--gold)}
.wrap{overflow-x:auto;border-radius:14px;border:1px solid var(--line)}table{width:100%;border-collapse:collapse;background:var(--card);font-size:14px}
td[dir=auto]{text-align:start}th{text-align:start;font-size:13px;color:var(--muted);padding:8px 10px;background:var(--chip)}td{padding:7px 10px;border-top:1px solid var(--line);vertical-align:top}
td:first-child{white-space:nowrap}td.mini{width:30%;min-width:80px}td.mini .bar{margin:8px 0}
@media (max-width:600px){td:first-child{white-space:normal}.stack tr{display:block;border-top:1px solid var(--line)}.stack tr:first-child{display:none}
.stack td{display:block;border:0;padding:3px 12px}.stack td:first-child{padding-top:10px;font-weight:bold}.stack td:last-child{padding-bottom:10px}}
</style></head><body><main>
<div class="top"><div><h1>🗺️ خريطة تطبيقات القرآن</h1><p class="sub">أُنشئت {{when}}</p></div><button id="theme" type="button" aria-label="الوضع الفاتح أو الداكن">🌓</button></div>
<div class="stats">{{cards}}</div>
<h2>ما يحتاج انتباهًا</h2><div class="notes"><ul>{{notes}}</ul></div>
<h2>حجم كل مجلد رئيسي (من حد GitHub Pages ‏1 GB)</h2><p class="legend">الأخضر تحت 70%، والبرتقالي حتى 90%، والأحمر فوقه.</p><div class="box">{{folders}}</div>
<h2>بنية المشروع</h2><p class="legend">التطبيقات من فهرس <code dir="ltr">apps.json</code>، ثم بقية المجلدات. اضغط على أي فرع لفتحه.</p><div class="box">{{tree}}</div>
<h2>الأدوات والسكربتات</h2><div class="wrap stack"><table><tr><th>الملف</th><th>ما يفعله (أول جملة من شرحه)</th></tr>{{tools}}</table></div>
<h2>مهارات Claude</h2><div class="wrap stack"><table><tr><th>الأمر</th><th>الوصف</th></tr>{{skills}}</table></div>
<h2>أنواع الملفات</h2><div class="wrap"><table><tr><th>النوع</th><th>العدد</th><th>الحجم</th><th>من الكل</th></tr>{{ext}}</table></div>
<h2>أكبر الملفات</h2><div class="wrap"><table><tr><th>الملف</th><th>الحجم</th></tr>{{big}}</table></div>
</main><script>
(function(){var b=document.getElementById('theme'),r=document.documentElement;
function cur(){return r.dataset.theme||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light')}
b.onclick=function(){r.dataset.theme=cur()=='dark'?'light':'dark'};})();
</script></body></html>'''

if __name__ == '__main__': main()
