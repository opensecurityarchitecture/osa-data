#!/usr/bin/env python3
"""Add xlink:href control links to OSA pattern SVG diagrams.

Finds control ID badges (e.g. AU-02, AC-03) in SVG files and wraps
their parent <g> elements with <a xlink:href="/controls/{id}"> links.
Skips badges that are already linked.

Usage:
    python add-control-links.py                          # all sp-*.svg
    python add-control-links.py sp-054-*.svg             # specific file
    python add-control-links.py --dry-run                # preview only
"""

import re
import sys
from pathlib import Path

NIST_FAMILIES = {
    'AC', 'AT', 'AU', 'CA', 'CM', 'CP', 'IA', 'IR', 'MA', 'MP',
    'PE', 'PL', 'PM', 'PS', 'PT', 'RA', 'SA', 'SC', 'SI', 'SR',
}

CTRL_IN_TSPAN = re.compile(r'<tspan[^>]*>([A-Z]{2}-\d{2})</tspan>')


def find_enclosing_g(text, pos):
    """Find the start position of the <g> element enclosing `pos`."""
    depth = 0
    i = pos
    while i >= 0:
        if text[i] == '>':
            # Check for </g>
            if i >= 3 and text[i-3:i+1] == '</g>':
                depth += 1
                i -= 4
                continue
            # Check for opening <g> or <g ...>
            j = i
            while j > 0 and text[j-1] != '<':
                j -= 1
            j -= 1  # include the '<'
            if j >= 0:
                tag = text[j:i+1]
                if re.match(r'<g[\s>]', tag) and '/>' not in tag:
                    if depth == 0:
                        return j
                    depth -= 1
        i -= 1
    return None


def find_closing_g(text, g_start):
    """Find the end position (inclusive) of </g> that closes <g> at g_start."""
    depth = 0
    i = g_start + 1
    while i < len(text):
        if text[i] == '<':
            # Check for opening <g
            if text[i:i+2] == '<g' and (i + 2 >= len(text) or text[i+2] in ' >\t\n\r'):
                depth += 1
            # Check for </g>
            elif text[i:i+4] == '</g>':
                if depth == 0:
                    return i + 3  # position of final '>'
                depth -= 1
        i += 1
    return None


def is_inside_a_tag(text, pos):
    """Check if position is already inside an <a ...>...</a> element."""
    # Search backwards — if we hit <a before </a>, we're inside one
    i = pos
    while i >= 0:
        if text[i] == '>':
            if i >= 3 and text[i-3:i+1] == '</a>':
                return False  # closed <a> before us — not inside
            j = i
            while j > 0 and text[j-1] != '<':
                j -= 1
            j -= 1
            if j >= 0:
                tag = text[j:i+1]
                if tag.startswith('<a ') or tag == '<a>':
                    return True  # open <a> before us — inside
        i -= 1
    return False


def add_links(svg_text, dry_run=False):
    """Add <a xlink:href> wrappers around control badge <g> elements."""
    # Collect all modifications: (g_start, g_end, ctrl_id)
    modifications = []
    seen_positions = set()

    for m in CTRL_IN_TSPAN.finditer(svg_text):
        ctrl_id = m.group(1)
        family = ctrl_id.split('-')[0]

        if family not in NIST_FAMILIES:
            continue

        tspan_pos = m.start()

        if is_inside_a_tag(svg_text, tspan_pos):
            continue

        # Find the enclosing <g> (this is the badge group)
        g_start = find_enclosing_g(svg_text, tspan_pos)
        if g_start is None:
            continue

        # Avoid wrapping the same <g> twice (e.g. if control ID appears twice)
        if g_start in seen_positions:
            continue
        seen_positions.add(g_start)

        g_end = find_closing_g(svg_text, g_start)
        if g_end is None:
            continue

        # Sanity check: the badge group should be reasonably small
        group_text = svg_text[g_start:g_end+1]
        if len(group_text) > 2000:
            continue  # too large — probably matched a container group

        # Get indentation
        line_start = svg_text.rfind('\n', 0, g_start) + 1
        indent = ''
        for ch in svg_text[line_start:g_start]:
            if ch in ' \t':
                indent += ch
            else:
                break

        modifications.append((g_start, g_end, ctrl_id, indent))

    if dry_run:
        return svg_text, modifications

    # Apply modifications from end to start (so positions stay valid)
    result = svg_text
    for g_start, g_end, ctrl_id, indent in reversed(modifications):
        href = f'/controls/{ctrl_id.lower()}'
        # Insert </a> after </g>
        result = result[:g_end+1] + f'\n{indent}</a>' + result[g_end+1:]
        # Insert <a> before <g>
        result = result[:g_start] + f'<a xlink:href="{href}">\n{indent}' + result[g_start:]

    return result, modifications


def ensure_xlink_ns(svg_text):
    """Ensure xmlns:xlink is declared on the <svg> root."""
    if 'xmlns:xlink' not in svg_text:
        svg_text = svg_text.replace(
            'xmlns="http://www.w3.org/2000/svg"',
            'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"',
            1,
        )
    return svg_text


def process_file(path, dry_run=False):
    """Process a single SVG file. Returns count of links added."""
    with open(path, 'r') as f:
        svg = f.read()

    svg = ensure_xlink_ns(svg)
    result, mods = add_links(svg, dry_run=dry_run)

    if not mods:
        print(f'  {path.name}: no unlinked controls found')
        return 0

    ctrl_ids = [ctrl_id for _, _, ctrl_id, _ in mods]
    print(f'  {path.name}: {"would add" if dry_run else "added"} {len(mods)} links — {", ".join(ctrl_ids)}')

    if not dry_run:
        with open(path, 'w') as f:
            f.write(result)

    return len(mods)


def main():
    dry_run = '--dry-run' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--dry-run']

    img_dir = Path(__file__).resolve().parent.parent / 'website' / 'public' / 'images'

    if args:
        files = []
        for a in args:
            p = Path(a)
            if p.exists():
                files.append(p)
            else:
                # Try relative to img_dir
                matches = sorted(img_dir.glob(a))
                files.extend(matches)
    else:
        files = sorted(img_dir.glob('sp-*.svg'))

    if not files:
        print('No SVG files found.')
        sys.exit(1)

    total = 0
    for f in files:
        total += process_file(f, dry_run=dry_run)

    action = 'Would add' if dry_run else 'Added'
    print(f'\n{action} {total} control links across {len(files)} files')


if __name__ == '__main__':
    main()
