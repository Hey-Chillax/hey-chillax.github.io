"""Turn a draw.io SVG export into an inline-ready, theme-aware SVG for the homepage, and write the colour CSS.

    python3 tools/drawio/webify.py IN.svg OUT.svg "aria label"     # one file
    python3 tools/drawio/webify.py --css                            # rewrite tools/drawio/diagram-colors.css

What it does to the export of `draw.io -x -f svg --crop -b 0`:
* drops the XML prolog, DOCTYPE, the PNG fallbacks draw.io puts next to every HTML label, and the "Text is not SVG"
  warning link; keeps the viewBox and adds role="img", an aria-label and class="dg";
* replaces every palette colour (fills and strokes, which draw.io writes both as attributes and as light-dark()
  styles, and text colours inside the HTML labels) with var(--dg-NAME), so the page's light and dark themes recolour
  the figure (CSS variables do not work in SVG presentation attributes, so they move into style);
* sets the font families to the web fonts: the hand-drawn face ('YZ Hand' = Comic Neue on the site) for words,
  Times New Roman for symbols.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from dlib import palette_vars  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
VARS = palette_vars()
LIGHT_TO_VAR = {}
for _name, (_light, _dark) in VARS.items():
    assert _light.lower() not in LIGHT_TO_VAR, ('two names share a light colour', _name, LIGHT_TO_VAR.get(_light.lower()))
    LIGHT_TO_VAR[_light.lower()] = _name
HAND_STACK = "'YZ Hand', 'Comic Neue', 'Comic Sans MS', 'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', sans-serif"
MATH_STACK = "'Times New Roman', Times, 'Liberation Serif', serif"
unknown = set()


def to_hex(c):
    c = c.strip()
    m = re.fullmatch(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*[\d.]+)?\s*\)', c)
    if m:
        return '#%02x%02x%02x' % tuple(int(v) for v in m.groups())
    if re.fullmatch(r'#[0-9a-fA-F]{3}', c):
        return '#' + ''.join(ch * 2 for ch in c[1:]).lower()
    return c.lower()


def light_of(value):
    """The light-theme colour of a CSS colour value, unwrapping light-dark(a, b)."""
    value = value.strip()
    m = re.fullmatch(r'light-dark\((.*)\)', value)
    if m:
        inner = m.group(1)
        depth, cut = 0, None
        for i, ch in enumerate(inner):
            depth += ch == '('
            depth -= ch == ')'
            if ch == ',' and depth == 0:
                cut = i
                break
        value = inner[:cut]
    return to_hex(value)


def var_for(value):
    h = light_of(value)
    if h in ('none', 'transparent'):
        return h
    name = LIGHT_TO_VAR.get(h)
    if name is None:
        unknown.add(h)
        return value
    return f'var({name})'


def fix_tag(tag):
    """Move fill/stroke attributes and light-dark styles of one SVG start tag onto CSS variables."""
    attrs = dict(re.findall(r'\s([\w:-]+)="([^"]*)"', tag))
    name = re.match(r'<([\w:]+)', tag).group(1)
    style = attrs.get('style', '')
    decl = [d.strip() for d in style.split(';') if d.strip()]
    props = {}
    for d in decl:
        if ':' in d:
            k, v = d.split(':', 1)
            props[k.strip()] = v.strip()
    for key in ('fill', 'stroke'):
        if key in props:
            props[key] = var_for(props[key])
        elif key in attrs:
            v = var_for(attrs[key])
            if v.startswith('var('):
                props[key] = v
    for key in ('fill', 'stroke'):
        if key in attrs and key in props and props[key].startswith('var('):
            del attrs[key]
    for k in ('pointer-events', 'data-cell-id'):
        attrs.pop(k, None)
    if props:
        attrs['style'] = '; '.join(f'{k}: {v}' for k, v in props.items())
    else:
        attrs.pop('style', None)
    end = '/>' if tag.rstrip().endswith('/>') else '>'
    return f'<{name}' + ''.join(f' {k}="{v}"' for k, v in attrs.items()) + end


def fix_html_colors(s):
    """Text and background colours inside the HTML labels (foreignObject)."""
    def repl(m):
        return f'{m.group(1)}: {var_for(m.group(2))}'
    s = re.sub(r'(?<![\w-])(color|background-color)\s*:\s*(light-dark\((?:[^()]|\([^()]*\))*\)|rgba?\([^)]*\)|#[0-9a-fA-F]{3,6})', repl, s)
    return s


def webify(svg, label):
    s = re.sub(r'<\?xml[^>]*\?>\s*', '', svg)
    s = re.sub(r'<!DOCTYPE[^>]*>\s*', '', s)
    s = re.sub(r'<switch><g requiredFeatures="[^"]*"/><a [^>]*><text[^>]*>Text is not SVG - cannot display</text></a></switch>', '', s)
    s = re.sub(r'<switch>(<foreignObject.*?</foreignObject>)(?:<image[^>]*/>|<text[^>]*>.*?</text>)</switch>', r'\1', s, flags=re.S)
    s = re.sub(r' requiredFeatures="[^"]*"', '', s)
    s = re.sub(r' data-drawio-colors="[^"]*"', '', s)
    s = s.replace('<defs/>', '')
    m = re.match(r'<svg([^>]*)>', s)
    head = m.group(1)
    vb = re.search(r'viewBox="([^"]+)"', head).group(1)
    _, _, w, h = (float(v) for v in vb.split())
    root = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" class="dg" '
            f'viewBox="{vb}" width="{w:g}" height="{h:g}" role="img" aria-label="{label}">')
    s = root + s[m.end():]
    # fills and strokes of the shapes
    s = re.sub(r'<(?:rect|path|ellipse|circle|polygon|polyline|line|g)\b[^>]*>', lambda t: fix_tag(t.group(0)), s)
    s = fix_html_colors(s)
    # fonts
    s = re.sub(r"font-family\s*:\s*(?:&quot;|'|\")?Comic Sans MS(?:&quot;|'|\")?", f'font-family: {HAND_STACK}', s)
    s = re.sub(r"font-family\s*:\s*(?:&quot;|'|\")?Times New Roman(?:&quot;|'|\")?", f'font-family: {MATH_STACK}', s)
    s = re.sub(r'font-family="Comic Sans MS"', f'font-family="{HAND_STACK}"', s)
    s = re.sub(r'font-family="Times New Roman"', f'font-family="{MATH_STACK}"', s)
    s = re.sub(r' pointer-events="[^"]*"', '', s)
    s = re.sub(r' data-cell-id="[^"]*"', '', s)
    s = re.sub(r'<g>\s*</g>', '', s)
    return s


def write_css(path=HERE / 'diagram-colors.css'):
    light = '\n'.join(f'  {k}: {v[0]};' for k, v in VARS.items())
    dark = '\n'.join(f'    {k}: {v[1]};' for k, v in VARS.items())
    path.write_text('/* Colours of the draw.io method diagrams (tools/drawio). Generated by webify.py --css; edit dlib.py. */\n'
                    f':root {{\n{light}\n}}\n@media (prefers-color-scheme: dark) {{\n  :root {{\n{dark}\n  }}\n}}\n')
    return path


if __name__ == '__main__':
    if sys.argv[1:] == ['--css']:
        print('wrote', write_css())
    else:
        src, dst, label = sys.argv[1], sys.argv[2], sys.argv[3]
        out = webify(pathlib.Path(src).read_text(encoding='utf-8'), label)
        pathlib.Path(dst).write_text(out, encoding='utf-8')
        if unknown:
            print('colours not in the palette:', ', '.join(sorted(unknown)))
        print('wrote', dst, len(out))
