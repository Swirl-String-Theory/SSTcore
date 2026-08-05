#!/usr/bin/env python3
"""
ideal_resolver.py -- verified resolution of the Gilbert ideal-geometry databases.

Covers all eight files published by Brian Gilbert on the Knot Atlas:

    knots  3-10 crossings          Ideal.txt
    links  2-9  crossings          IdealLinks.txt
    links 10    alternating        IdealLinks_10a.txt
    links 10    non-alternating    IdealLinks_10n.txt
    links 11a   L11a1..L11a300     IdealLinks_11a1.txt
    links 11a   L11a301..L11a548   IdealLinks_11a2.txt
    links 11n   L11n1..L11n230     IdealLinks_11n1.txt
    links 11n   L11n231..L11n459   IdealLinks_11n2.txt

Every resolved file is verified before it is returned.  Four entries are
hash-pinned (verified 3 Aug 2026); the four 11-crossing entries are not yet
pinned and are verified structurally (record count, ID pattern, tag, author)
with a warning.  Use pin_snippet() to promote them once you have a copy.

Design rules:
  * source files are never edited, renamed, or converted
  * integrity is checked on CRLF-normalized content, so LF and CRLF copies of
    the same database both verify
  * a candidate that exists but fails verification is skipped, never used
  * remote download is verified against the same criteria
"""

from pathlib import Path
import hashlib
import re
import shutil
import warnings

KATLAS = 'https://katlas.org'

BIBLIOGRAPHY = """\
Brian Gilbert, ideal knot and link databases, Knot Atlas (2016).
  Contact: brian.gilbert@xtra.co.nz
  [1] Ideal Knots, vol. 19 of Series on Knots and Everything,
      eds. A. Stasiak, V. Katritch, L. H. Kauffman, World Scientific (1998).
  [2] P. Pieranski, tables up to 9 crossings,
      http://fizyka.phys.put.poznan.pl/~pieransk/TablesUpTo9.html
"""


def _e(sha, records, tag, title, author, date, url, id_re=None, note=''):
    return dict(sha256=sha, records=records, tag=tag, title=title,
                author=author, date=date, url=url, id_re=id_re, note=note)


G = 'Brian Gilbert'

MANIFEST = {
    # ---- hash-pinned: verified 3 Aug 2026 against the author's own copies ----
    'ideal.txt': _e(
        'a16c0f6e9175fdd54ee8c50b3b32e23caa3b256e7da21145be00a5a58e08cc51',
        263, 'AB', 'Database of Ideal Knots 3-10 crossings',
        G, '6/11/2016 2:12:11 p.m.',
        KATLAS + '/images/d/d2/Ideal.txt.gz',
        note='includes 10 multi-component AB records and K11a* strays'),
    'idealLinks.txt': _e(
        '542aad3915b9b2aa3aa554720a5457b362550bc66f6f950c9bb31b253b7c575a',
        130, 'TL', 'Database of Ideal Links 2-9 crossings',
        G, '6/11/2016 2:13:50 p.m.',
        KATLAS + '/images/5/5a/IdealLinks.txt.gz',
        note='page states 845kb gz / 5.45Mb plain'),
    'idealLinks_10a.txt': _e(
        'b2be5888d5f2e085a034b016ada7d6d537dad71a53928a6a0bbb4d32e44bf9ef',
        174, 'TL', 'Database of Ideal Links L10a',
        G, '7/11/2016 9:37:16 p.m.',
        KATLAS + '/images/e/ec/IdealLinks_10a.txt.gz',
        note='page states 1.20Mb gz / 7.23Mb plain'),
    'idealLinks_10n.txt': _e(
        '81b9aaa6aaef48107f6c4cc90c1423046ed4dd4cf83b6fe478dd8fd90f4df92c',
        113, 'TL', 'Database of Ideal Links L10n',
        G, '7/11/2016 9:36:36 p.m.',
        KATLAS + '/images/d/de/IdealLinks_10n.txt.gz',
        note='page states 0.81Mb gz / 5.13Mb plain'),

    # ---- not yet hash-pinned: structural verification only -------------------
    # Record counts derive from the published ID ranges. Title and date are
    # unknown until a copy is inspected, so those checks are skipped.
    'idealLinks_11a1.txt': _e(
        None, 300, 'TL', None, G, None,
        KATLAS + '/images/f/f3/IdealLinks_11a1.txt.gz',
        id_re=r'^L11a\d+$',
        note='L11a1..L11a300; page states 1.79Mb gz / 10.02Mb plain'),
    'idealLinks_11a2.txt': _e(
        None, 248, 'TL', None, G, None,
        KATLAS + '/images/9/99/IdealLinks_11a2.txt.gz',
        id_re=r'^L11a\d+$',
        note='L11a301..L11a548; page states 1.91Mb gz / 11.48Mb plain'),
    'idealLinks_11n1.txt': _e(
        None, 230, 'TL', None, G, None,
        KATLAS + '/images/2/26/IdealLinks_11n1.txt.gz',
        id_re=r'^L11n\d+$',
        note='L11n1..L11n230; page states 1.34Mb gz / 7.70Mb plain'),
    'idealLinks_11n2.txt': _e(
        None, 229, 'TL', None, G, None,
        KATLAS + '/images/b/bb/IdealLinks_11n2.txt.gz',
        id_re=r'^L11n\d+$',
        note='L11n231..L11n459; page states 1.73Mb gz / 10.78Mb plain'),
}

PINNED = [k for k, v in MANIFEST.items() if v['sha256']]
UNPINNED = [k for k, v in MANIFEST.items() if not v['sha256']]


class IdealDataError(RuntimeError):
    """Raised when a resolved database fails verification."""


class UnpinnedDataWarning(UserWarning):
    """Passed structural checks but no pinned hash is available."""


# --------------------------------------------------------------------------
def normalized_bytes(path) -> bytes:
    raw = Path(path).read_bytes()
    return raw.replace(b'\r\n', b'\n').replace(b'\r', b'\n')


def inspect(path) -> dict:
    """Structural summary of a candidate file."""
    norm = normalized_bytes(path)
    txt = norm.decode('utf-8', 'ignore')
    m = re.search(r'<DATA[^>]*>', txt)
    hdr = m.group(0) if m else ''
    t = re.search(r'Title="([^"]*)"', hdr)
    d = re.search(r'Date="([^"]*)"', hdr)
    return dict(sha256=hashlib.sha256(norm).hexdigest(), nbytes=len(norm),
                header=hdr, title=t.group(1) if t else None,
                date=d.group(1) if d else None,
                ids=re.findall(r'<(?:AB|TL)\s[^>]*Id="([^"]*)"', txt),
                n_ab=len(re.findall(r'<AB\s', txt)),
                n_tl=len(re.findall(r'<TL\s', txt)))


def verify(path, key, strict=True) -> dict:
    spec = MANIFEST[key]
    info = inspect(path)
    n = info['n_ab'] if spec['tag'] == 'AB' else info['n_tl']

    checks = {}
    if spec['sha256']:
        checks['sha'] = info['sha256'] == spec['sha256']
    checks['records'] = n == spec['records']
    if spec['author']:
        checks['author'] = spec['author'] in info['header']
    if spec['date']:
        checks['date'] = spec['date'] in info['header']
    if spec['title']:
        checks['title'] = spec['title'] in info['header']
    if spec['id_re']:
        rx = re.compile(spec['id_re'])
        checks['ids'] = bool(info['ids']) and all(rx.match(i) for i in info['ids'])

    rep = dict(path=str(path), key=key, records=n, checks=checks,
               sha256=info['sha256'], header=info['header'],
               nbytes=info['nbytes'], pinned=bool(spec['sha256']),
               ok=all(checks.values()))

    if rep['ok'] and not rep['pinned']:
        warnings.warn(
            "%s passed structural checks (%d <%s> records, ID pattern ok) but "
            "is not hash-pinned. Promote it with pin_snippet(path, key)."
            % (key, n, spec['tag']), UnpinnedDataWarning, stacklevel=2)

    if strict and not rep['ok']:
        bad = [k for k, v in checks.items() if not v]
        raise IdealDataError(
            "%s failed verification as '%s' (failed: %s).\n"
            "  expected %d <%s> records%s\n"
            "  got      %d records, sha256 %s, %d bytes\n"
            "  header:  %s\n"
            "  Do not substitute a converted or renamed copy: format conversion\n"
            "  has previously dropped link components silently."
            % (path, key, ', '.join(bad), spec['records'], spec['tag'],
               (", sha256 " + spec['sha256']) if spec['sha256'] else "",
               n, info['sha256'], info['nbytes'], info['header'] or '(none)'))
    return rep


def pin_snippet(path, key) -> str:
    """Paste-ready MANIFEST entry for a file you have obtained and checked."""
    spec = MANIFEST[key]
    info = inspect(path)
    n = info['n_ab'] if spec['tag'] == 'AB' else info['n_tl']
    return ("    %r: _e(\n        %r,\n        %d, %r, %r,\n"
            "        G, %r,\n        %r,\n        id_re=%r,\n        note=%r),"
            % (key, info['sha256'], n, spec['tag'], info['title'],
               info['date'], spec['url'], spec['id_re'], spec['note']))


# --------------------------------------------------------------------------
def _candidates(key, extra_dirs=()) -> list:
    stem, ext = key.rsplit('.', 1)
    names = {key, stem[0].upper() + stem[1:] + '.' + ext}
    dirs = []
    for modname in ('SSTcore', 'sstcore'):
        try:
            pkg = __import__(modname)
        except ImportError:
            continue
        for getter in ('get_ideal_txt_path', 'get_resources_dir'):
            fn = getattr(pkg, getter, None)
            if fn is None:
                continue
            try:
                p = Path(fn())
            except Exception:
                continue
            dirs.append(p.parent if p.is_file() else p)
        break
    here = Path(__file__).resolve().parent
    dirs += [here.parent.parent / 'resources', here / 'resources', here]
    dirs += [Path(x) for x in extra_dirs]

    out, seen = [], set()
    for d in dirs:
        for nm in names:
            q = Path(d) / nm
            try:
                if not q.exists():
                    continue
                real = q.resolve()
            except OSError:
                continue
            if real in seen:
                continue
            seen.add(real)
            out.append(q)
    return out


def resolve(key, dest_dir=None, extra_dirs=(), allow_remote=False,
            verbose=True) -> Path:
    if key not in MANIFEST:
        raise KeyError("no manifest entry for %r; known: %s"
                       % (key, sorted(MANIFEST)))
    failures = []
    for cand in _candidates(key, extra_dirs):
        rep = verify(cand, key, strict=False)
        if rep['ok']:
            if dest_dir is None:
                return cand
            dest = Path(dest_dir) / key
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(dest.suffix + '.partial')
            shutil.copy2(cand, tmp)
            verify(tmp, key, strict=True)
            tmp.replace(dest)
            if verbose:
                print("[ideal] %s <- %s (%s)"
                      % (key, cand, 'pinned' if rep['pinned'] else 'structural'))
            return dest
        failures.append(rep)

    if not allow_remote:
        raise IdealDataError(
            "no verified local copy of %s.\n"
            "  candidates checked: %s\n"
            "  Remote download is disabled by default. Pass allow_remote=True\n"
            "  to fetch %s; it will be verified against the same criteria."
            % (key, [f['path'] for f in failures] or 'none found',
               MANIFEST[key]['url']))

    import gzip, urllib.request
    url = MANIFEST[key]['url']
    dest = Path(dest_dir or '.') / key
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + '.partial')
    with urllib.request.urlopen(url) as r:
        blob = r.read()
    if url.endswith('.gz'):
        blob = gzip.decompress(blob)
    tmp.write_bytes(blob)
    try:
        verify(tmp, key, strict=True)
    except IdealDataError:
        tmp.unlink(missing_ok=True)
        raise
    tmp.replace(dest)
    if verbose:
        print("[ideal] %s <- %s (remote, verified)" % (key, url))
    return dest


def resolve_all(keys=None, dest_dir=None, **kw) -> dict:
    out = {}
    for k in (keys or MANIFEST):
        try:
            out[k] = resolve(k, dest_dir=dest_dir, **kw)
        except IdealDataError as e:
            out[k] = e
    return out


# --------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/mnt/user-data/uploads')
    print("verifying candidates in %s\n" % d)
    print("  %-22s %-6s %-8s %-11s %s" % ("file", "state", "verdict",
                                          "records", "notes"))
    print("  " + "-" * 92)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UnpinnedDataWarning)
        for key, spec in MANIFEST.items():
            p = d / key
            state = 'pinned' if spec['sha256'] else 'UNPIN'
            if not p.exists():
                print("  %-22s %-6s %-8s %-11s %s"
                      % (key, state, 'ABSENT', '-/%d' % spec['records'],
                         spec['note']))
                continue
            rep = verify(p, key, strict=False)
            bad = [k for k, v in rep['checks'].items() if not v]
            print("  %-22s %-6s %-8s %-11s %s"
                  % (key, state, 'OK' if rep['ok'] else 'FAIL',
                     '%d/%d' % (rep['records'], spec['records']),
                     '' if rep['ok'] else 'failed: ' + ','.join(bad)))
    print()
    print("  pinned: %d    structural only: %d    total records expected: %d"
          % (len(PINNED), len(UNPINNED), sum(v['records'] for v in MANIFEST.values())))
    print()
    print(BIBLIOGRAPHY)
