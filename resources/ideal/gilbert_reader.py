#!/usr/bin/env python3
"""
gilbert_reader.py -- one reader for every Gilbert ideal-geometry database.

Handles all three encodings found in the corpus without editing the source
files:

    <AB Id=...>  <Coeff .../>                       single-component knots
    <AB Id=... n="k">  <Component>  <Coeff .../>    multi-component, AB style
    <TL Id=...>  <STRING L=...>  <Coeff .../>       links, TL style

Returns a uniform structure so downstream code never branches on format:

    {
      'id'      : original database Id, unchanged   (e.g. 'K11a367', 'L4a1')
      'conway'  : Conway notation string
      'D'       : declared thickness (usually 1.0)
      'L'       : declared total length, or nan if the record omits it
      'ncomp'   : number of components
      'series'  : [ (harmonic_index[], A[n,3], B[n,3], L_component), ... ]
      'source'  : filename it came from
    }

Keep the source files pristine.  If you need friendlier names, alias them
here -- never in the data.
"""

import re
import numpy as np

# Optional aliases.  Left-hand side is YOUR name, right-hand side is the
# database Id.  Nothing is renamed in the files themselves.
ALIASES = {
    '3_1':  '3:1:1',
    '4_1':  '4:1:1',
    '5_1':  '5:1:1',
    '5_2':  '5:1:2',
    '11_1': 'K11a367',        # Conway "11", the (2,11) torus knot
    # NOTE: K11a247 has Conway "9 2"; it is NOT 11_2 in any standard
    # numbering.  Do not alias it to one.
}

_ATTR = re.compile(r'(\w+)\s*=\s*"([^"]*)"')
_COEFF = re.compile(r'<Coeff\s+([^/]*?)/>')


def _num(d, k, default=float('nan')):
    try:
        return float(d[k])
    except (KeyError, ValueError):
        return default


def _coeffs(block):
    idx, A, B = [], [], []
    for m in _COEFF.finditer(block):
        a = dict(_ATTR.findall(m.group(1)))
        if 'A' in a and 'B' in a:
            idx.append(int(a.get('I', '1')))
            A.append([float(x) for x in a['A'].split(',')])
            B.append([float(x) for x in a['B'].split(',')])
    if not A:
        return None
    return np.array(idx), np.array(A), np.array(B)


def read(path):
    """Parse any Gilbert database.  Line endings (CRLF or LF) are irrelevant."""
    txt = open(path, errors='ignore').read().replace('\r', '')
    header = re.search(r'<DATA[^>]*>', txt)
    header = header.group(0) if header else ''
    out = []

    for tag in ('AB', 'TL'):
        for m in re.finditer(r'<%s\s+([^>]*)>(.*?)</%s>' % (tag, tag), txt, re.S):
            at = dict(_ATTR.findall(m.group(1)))
            body = m.group(2)
            series = []

            # TL style: one <STRING> per component, each with its own L
            for sm in re.finditer(r'<STRING\s+([^>]*)>(.*?)</STRING>', body, re.S):
                sa = dict(_ATTR.findall(sm.group(1)))
                c = _coeffs(sm.group(2))
                if c:
                    series.append((*c, _num(sa, 'L')))

            # AB style with explicit <Component> blocks
            if not series:
                for cm in re.finditer(r'<Component[^>]*>(.*?)</Component>', body, re.S):
                    c = _coeffs(cm.group(1))
                    if c:
                        series.append((*c, float('nan')))

            # plain AB style, single component
            if not series:
                c = _coeffs(body)
                if c:
                    series.append((*c, _num(at, 'L')))

            if series:
                out.append(dict(id=at.get('Id'), conway=at.get('Conway', ''),
                                D=_num(at, 'D', 1.0), L=_num(at, 'L'),
                                ncomp=len(series), series=series,
                                source=path.split('/')[-1], header=header))
    return out


def read_all(paths):
    recs = []
    for p in paths:
        recs.extend(read(p))
    return recs


def index(recs):
    """Lookup by database Id, with ALIASES resolved."""
    by_id = {r['id']: r for r in recs}
    for alias, real in ALIASES.items():
        if real in by_id:
            by_id[alias] = by_id[real]
    return by_id


if __name__ == '__main__':
    import sys, glob
    paths = sys.argv[1:] or sorted(glob.glob('/mnt/user-data/uploads/ideal*.txt'))
    recs = read_all(paths)
    print("%-24s %6s %6s %8s %s" % ("file", "recs", "1-comp", "multi", "header title"))
    print("-" * 96)
    for p in paths:
        r = [x for x in recs if x['source'] == p.split('/')[-1]]
        t = re.search(r'Title="([^"]*)"', r[0]['header']) if r else None
        print("%-24s %6d %6d %8d %s"
              % (p.split('/')[-1], len(r),
                 sum(1 for x in r if x['ncomp'] == 1),
                 sum(1 for x in r if x['ncomp'] > 1),
                 t.group(1) if t else ''))
    print("-" * 96)
    print("total %d records, %d components" % (len(recs), sum(r['ncomp'] for r in recs)))

    by = index(recs)
    print()
    for k in ['3:1:1', '3_1', 'K11a367', '11_1', 'L4a1', 'L6n1']:
        r = by.get(k)
        print("  %-10s -> %-10s Conway=%-8s ncomp=%d harmonics=%s"
              % (k, r['id'] if r else 'MISSING', r['conway'] if r else '-',
                 r['ncomp'] if r else 0,
                 [len(s[0]) for s in r['series']] if r else '-'))
