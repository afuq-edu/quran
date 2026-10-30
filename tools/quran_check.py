#!/usr/bin/env python3
"""Check every ayah written in the apps against the verified mushaf text in data/quran.json (owner, 2026-10-30).
1. data/quran.json itself: unchanged (its SHA-256), 114 surahs, 6236 ayat.
2. Every data-ayah="S:A" in HTML/JS and every JSON object with surah/ayah/text: the reference exists and the text is exact.
3. Any other run of Uthmani text (three words or more, with Quranic marks): it must appear in the mushaf, letter for letter
   once the diacritics are set aside; otherwise it is reported as a likely typo or a verse from another script.
Usage: python3 tools/quran_check.py [PATH ...]     (default: apps/ templates/ index.html; exit code 1 when something is wrong)"""
import os, re, sys, json, glob, hashlib, unicodedata
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
DATA = R + 'data/quran.json'
SHA256 = 'ae088d42ef33ca360f3e19775a73604212910de650bd24170a307a364d20d344'   # set by tools/quran_check.py --seal
EXTS = ('.html', '.htm', '.js', '.mjs', '.json')

MARKS = re.compile('[ؐ-ًؚ-ٰٟۖ-ۭـ]')       # harakat, Quranic marks, tatweel
UTHMANI = re.compile('[ٱۖ-ۭ]')                                    # alef wasla and the small high marks
RUN = re.compile('[؀-ۿݐ-ݿࢠ-ࣿ][؀-ۿݐ-ݿࢠ-ࣿ  ]*')


def nfc(s): return ' '.join(unicodedata.normalize('NFC', s).split())      # same marks typed in another order


def norm(s):
    s = MARKS.sub('', s)
    s = re.sub('[ٱآأإ]', 'ا', s).replace('ى', 'ي')
    s = re.sub('[۝۞۩٠-٩۰-۹0-9()]', ' ', s)          # ayah-end signs and numbers
    return ' '.join(s.split())


def main():
    args = sys.argv[1:]
    raw = open(DATA, 'rb').read()
    if args == ['--seal']:                       # after a deliberate, reviewed replacement of data/quran.json only
        t = open(__file__, encoding='utf8').read()
        open(__file__, 'w', encoding='utf8').write(re.sub(r"SHA256 = '[0-9a-f]*'", "SHA256 = '%s'" % hashlib.sha256(raw).hexdigest(), t, count=1))
        print('sealed'); return
    q = json.loads(raw)
    errors, warns, ok = [], [], 0
    if hashlib.sha256(raw).hexdigest() != SHA256: errors.append('data/quran.json تغيّر عن النسخة الموثقة (SHA-256 مختلف).')
    if len(q) != 114 or sum(len(s['ayat']) for s in q) != 6236:
        errors.append('data/quran.json: %d سورة و%d آية بدل 114 و6236.' % (len(q), sum(len(s['ayat']) for s in q)))
    ayah = lambda s, a: q[s - 1]['ayat'][a - 1] if 1 <= s <= 114 and 1 <= a <= len(q[s - 1]['ayat']) else None
    corpus = ' | '.join(norm(t) for s in q for t in s['ayat'])

    def ref_check(where, s, a, text):
        nonlocal ok
        want = ayah(s, a)
        if want is None: errors.append('%s: المرجع %d:%d غير موجود في المصحف.' % (where, s, a)); return
        if text is None: ok += 1; return
        got = ' '.join(re.sub('<[^>]+>', '', text).split())
        if nfc(got) == nfc(want): ok += 1
        elif norm(got) == norm(want): warns.append('%s: الآية %d:%d حروفها صحيحة لكن تشكيلها يختلف عن المصحف.' % (where, s, a))
        else: errors.append('%s: نص الآية %d:%d لا يطابق المصحف: «%s»' % (where, s, a, got[:80]))

    paths = args or ['apps', 'templates', 'index.html']
    files = []
    for p in paths:
        p = os.path.join(R, p)
        if os.path.isdir(p): files += [f for f in glob.glob(p + '/**/*', recursive=True) if f.endswith(EXTS)]
        elif os.path.exists(p): files.append(p)
    checked_refs = set()
    for f in sorted(files):
        rel = os.path.relpath(f, R)
        t = open(f, encoding='utf8', errors='ignore').read()
        for m in re.finditer(r'data-ayah="(\d+):(\d+)"[^>]*>([^<]*)<', t):
            if '{' in m.group(3) or "'" in m.group(3): continue     # filled at run time from Quran.load()
            ref_check(rel, int(m.group(1)), int(m.group(2)), m.group(3) or None); checked_refs.add(m.group(3))
        if f.endswith('.json'):
            def walk(o):
                if isinstance(o, dict):
                    s = o.get('surah', o.get('sura')); a = o.get('ayah', o.get('aya'))
                    if isinstance(s, int) and isinstance(a, int):
                        ref_check(rel, s, a, o.get('text')); checked_refs.add(o.get('text'))
                    for v in o.values(): walk(v)
                elif isinstance(o, list):
                    for v in o: walk(v)
            try: walk(json.loads(t))
            except ValueError: warns.append('%s: ليس JSON صالحًا.' % rel)
        for m in RUN.finditer(t):
            run = m.group(0).strip()
            if len(run.split()) < 3 or not UTHMANI.search(run) or run in checked_refs: continue
            n = norm(run)
            if n and n in corpus: ok += 1
            else: errors.append('%s: نص بالرسم العثماني لم يُعثر عليه في المصحف: «%s»' % (rel, run[:80]))

    print('آيات ومقاطع مطابقة: %d · أخطاء: %d · تنبيهات: %d' % (ok, len(errors), len(warns)))
    for e in errors: print('✗', e)
    for w in warns: print('!', w)
    sys.exit(1 if errors else 0)


if __name__ == '__main__': main()
