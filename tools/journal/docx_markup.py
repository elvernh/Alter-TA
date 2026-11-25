"""Rewrite DOCX paragraphs from a small markup while keeping the journal's run format.

Markup:
  [[ ... ]]   text changed in this revision (yellow highlight in the marked copy)
  *...*       explicit italic (\\* is a literal asterisk)
  _{...}      subscript
  ^{...}      superscript
English terms from ITALIC_TERMS are italicised automatically (journal rule: English
terms inside Indonesian text are italic), except in paragraphs built with auto=False.
"""
from __future__ import annotations

import copy
import re

from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}


def q(tag: str) -> str:
    return f'{{{W}}}{tag}'


ITALIC_TERMS = sorted({
    'failover time', 'Failover time', 'health check', 'Health check', 'error rate', 'Error rate',
    'failure detector', 'failure detectors', 'load balancer', 'load balancing', 'load tester', 'load test', 'Load test',
    'virtual user', 'virtual machine', 'timeout check', 'timeout connect', 'clock skew',
    'web server', 'round robin', 'least connection', 'ingress controller', 'on-premise', 'cloud computing',
    'high availability cluster', 'high availability', 'graceful failover', 'pilot study', 'Pilot study',
    'false positive', 'Service Level Objective', 'Requests per Second', 'warm-up', 'constant-vus',
    'constant-arrival-rate', 'open-loop', 'closed-loop', 'bare-metal', 'mistake recurrence time',
    'mistake duration', 'query accuracy probability', 'detection time', 'hash', 'timeout',
    'fall', 'rise', 'inter', 'instance', 'Instance', 'DOWN', 'UP', 'throughput', 'Throughput', 'container',
    'crash', 'Crash', 'hang', 'Hang', 'p-value', 'flapping', 'bootstrap', 'core', 'microservice',
    'baseline', 'failover', 'Failover', 'host', 'endpoint', 'error', 'image', 'timestamp',
    'Timestamp', 'clock', 'seed', 'daemon', 'pipeline', 'Pipeline', 'overhead', 'Overhead', 'roundrobin',
    'server', 'web', 'orchestrator', 'executor', 'stack', 'native', 'cpuset', 'subnet', 'bridge', 'port',
    'e-commerce', 'heartbeat', 'stateful', 'repository',
}, key=len, reverse=True)
_TERM_RE = re.compile(r'(?<![\w-])(' + '|'.join(re.escape(t) for t in ITALIC_TERMS) + r')(?![\w-])')

_TOKEN_RE = re.compile(r'(\\\*|\[\[|\]\]|\*|_\{[^}]*\}|\^\{[^}]*\})')


def parse(markup: str):
    """Yield (text, italic, hl, valign) segments."""
    hl = italic = False
    for tok in _TOKEN_RE.split(markup):
        if not tok:
            continue
        if tok == '\\*':
            yield '*', italic, hl, None
        elif tok == '[[':
            hl = True
        elif tok == ']]':
            hl = False
        elif tok == '*':
            italic = not italic
        elif tok.startswith('_{'):
            yield tok[2:-1], italic, hl, 'subscript'
        elif tok.startswith('^{'):
            yield tok[2:-1], italic, hl, 'superscript'
        else:
            yield tok, italic, hl, None


def auto_italic(segments, enabled=True):
    for text, italic, hl, valign in segments:
        if italic or not enabled or valign:
            yield text, italic, hl, valign
            continue
        pos = 0
        for m in _TERM_RE.finditer(text):
            if m.start() > pos:
                yield text[pos:m.start()], False, hl, valign
            yield m.group(0), True, hl, valign
            pos = m.end()
        if pos < len(text):
            yield text[pos:], False, hl, valign


def base_rpr(p):
    """Run properties of the paragraph's first plain run, without italic/highlight/valign."""
    for r in p.findall('w:r', NS):
        rpr = r.find('w:rPr', NS)
        if rpr is not None and rpr.find('w:i', NS) is None and rpr.find('w:vertAlign', NS) is None and ''.join(r.itertext()).strip():
            break
    else:
        r = p.find('w:r', NS)
        rpr = r.find('w:rPr', NS) if r is not None else None
    rpr = copy.deepcopy(rpr) if rpr is not None else etree.Element(q('rPr'))
    for tag in ('i', 'iCs', 'highlight', 'vertAlign', 'b', 'bCs'):
        for el in rpr.findall(f'w:{tag}', NS):
            rpr.remove(el)
    return rpr


# order of rPr children required by the schema (subset used here)
_RPR_ORDER = ['rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike', 'color',
              'spacing', 'w', 'kern', 'position', 'sz', 'szCs', 'highlight', 'u', 'effect', 'shd',
              'vertAlign', 'lang']


def _sorted_rpr(rpr):
    kids = list(rpr)
    for k in kids:
        rpr.remove(k)
    kids.sort(key=lambda e: _RPR_ORDER.index(etree.QName(e).localname)
              if etree.QName(e).localname in _RPR_ORDER else 99)
    for k in kids:
        rpr.append(k)
    return rpr


def make_run(text, rpr, italic, hl, valign, marked, force_italic=False, bold=False):
    r = etree.Element(q('r'))
    rp = copy.deepcopy(rpr)
    if bold:
        rp.append(etree.Element(q('b')))
        rp.append(etree.Element(q('bCs')))
    if italic or force_italic:
        rp.append(etree.Element(q('i')))
        rp.append(etree.Element(q('iCs')))
    if hl and marked:
        h = etree.Element(q('highlight'))
        h.set(q('val'), 'yellow')
        rp.append(h)
    if valign:
        v = etree.Element(q('vertAlign'))
        v.set(q('val'), valign)
        rp.append(v)
    r.append(_sorted_rpr(rp))
    t = etree.SubElement(r, q('t'))
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return r


def set_paragraph(p, markup, marked, auto=True, keep_runs=0, all_italic=False):
    """Replace the paragraph's runs (after the first `keep_runs`) with the markup."""
    rpr = base_rpr(p) if not all_italic else _first_text_rpr(p, keep_runs)
    text_runs = [r for r in p.findall('w:r', NS) if ''.join(r.itertext()).strip()]
    bold = bool(text_runs) and keep_runs == 0 and all(
        r.find('w:rPr/w:b', NS) is not None for r in text_runs)
    runs = [c for c in p if etree.QName(c).localname in ('r', 'hyperlink', 'bookmarkStart', 'bookmarkEnd',
                                                          'commentRangeStart', 'commentRangeEnd', 'proofErr')]
    kept = 0
    for c in runs:
        if etree.QName(c).localname == 'r' and kept < keep_runs:
            kept += 1
            continue
        p.remove(c)
    for text, italic, hl, valign in auto_italic(parse(markup), enabled=auto and not all_italic):
        p.append(make_run(text, rpr, italic, hl, valign, marked, force_italic=all_italic, bold=bold))


def _first_text_rpr(p, skip):
    runs = p.findall('w:r', NS)
    r = runs[skip] if len(runs) > skip else runs[-1]
    rpr = copy.deepcopy(r.find('w:rPr', NS))
    for tag in ('i', 'iCs', 'highlight', 'vertAlign', 'b', 'bCs'):
        for el in rpr.findall(f'w:{tag}', NS):
            rpr.remove(el)
    return rpr


def para_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def italic_mask(p):
    out = []
    for r in p.iter(q('r')):
        rpr = r.find('w:rPr', NS)
        it = rpr is not None and rpr.find('w:i', NS) is not None
        for t in r.findall('w:t', NS):
            out.extend([it] * len(t.text or ''))
    return out


def markup_text(p):
    """Paragraph text with subscripts/superscripts written as _{...}/^{...} (italics dropped:
    they are re-derived by auto_italic when the paragraph is rebuilt)."""
    out = []
    for r in p.iter(q('r')):
        rpr = r.find('w:rPr', NS)
        va = rpr.find('w:vertAlign', NS) if rpr is not None else None
        t = ''.join(x.text or '' for x in r.findall('w:t', NS))
        if va is not None and va.get(q('val')) == 'subscript':
            out.append('_{' + t + '}')
        elif va is not None and va.get(q('val')) == 'superscript':
            out.append('^{' + t + '}')
        else:
            out.append(t)
    return ''.join(out)
