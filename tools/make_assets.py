#!/usr/bin/env python3
"""Build the static assets: web fonts (subsets), photo, social card and icons.

Needs Pillow, fontTools and brotli (pip install pillow fonttools brotli). Run it again after
changing the photo or any heading text: the Chinese serif font is subset to the characters the
headings actually use.

    python tools/make_assets.py --photo /path/to/photo.jpg --texlive-fonts /path/to/texmf-dist/fonts/opentype/adobe
"""
import argparse
import html
import json
import pathlib
import re
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / 'assets' / 'fonts'
IMG = ROOT / 'assets' / 'img'
ACCENT = (45, 90, 150)
LATIN = ('U+0020-007E,U+00A0-00FF,U+0131,U+0152-0153,U+02C6,U+02DA,U+02DC,U+2010-2027,U+2030-203A,'
         'U+2044,U+20AC,U+2122,U+2190-2199,U+2212,U+2248,U+2260,U+2264-2265,U+FEFF,U+FFFD')
CJK_SERIF = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'


def subset(src, out, unicodes=None, text=None, font_number=None):
    cmd = [sys.executable, '-m', 'fontTools.subset', str(src), f'--output-file={out}', '--flavor=woff2',
           '--layout-features=kern,liga,calt,locl,ccmp,mark,mkmk', '--no-hinting', '--desubroutinize']
    if unicodes:
        cmd.append(f'--unicodes={unicodes}')
    if text:
        cmd.append(f'--text={text}')
    if font_number is not None:
        cmd.append(f'--font-number={font_number}')
    subprocess.run(cmd, check=True)
    print(f'{out.name}: {out.stat().st_size / 1024:.1f} KB')


def heading_chars():
    """CJK characters that are set in the serif face: headings, school names and the name."""
    chars = set()
    for page in ROOT.glob('**/*.html'):
        src = page.read_text(encoding='utf-8')
        src = re.sub(r'<svg.*?</svg>', '', src, flags=re.S)
        blocks = re.findall(r'<(?:h1|h2|h3)\b.*?</(?:h1|h2|h3)>', src, flags=re.S)
        blocks += re.findall(r'class="(?:school|alt-name|brand)".*?</span>', src, flags=re.S)
        for b in blocks:
            for ch in html.unescape(re.sub(r'<[^>]+>', '', b)):
                if ord(ch) >= 0x2e80:
                    chars.add(ch)
    return ''.join(sorted(chars)) + '（）：、，。·—“”'


def sc_font_number(path):
    from fontTools.ttLib import TTCollection
    for i, font in enumerate(TTCollection(path).fonts):
        if 'Noto Serif CJK SC' in str(font['name'].getDebugName(1)):
            return i
    raise SystemExit('Noto Serif CJK SC not found in ' + path)


def rename(path, family, style):
    """Give a subset its own name: the OFL forbids modified versions from using the Reserved Font Name 'Source'."""
    from fontTools.ttLib import TTFont
    font = TTFont(path)
    ps = family.replace(' ', '') + '-' + style
    for rec in font['name'].names:
        if rec.nameID in (1, 16, 21):
            rec.string = family
        elif rec.nameID in (2, 17, 22):
            rec.string = style
        elif rec.nameID == 4:
            rec.string = f'{family} {style}'
        elif rec.nameID == 6:
            rec.string = ps
        elif rec.nameID == 3:
            rec.string = f'{ps};subset'
    if 'CFF ' in font:
        cff = font['CFF '].cff
        cff.fontNames = [ps]
        top = cff.topDictIndex[0]
        top.FullName, top.FamilyName = f'{family} {style}', family
    font.flavor = 'woff2'
    font.save(path)


def build_fonts(texlive):
    FONTS.mkdir(parents=True, exist_ok=True)
    t = pathlib.Path(texlive)
    for src, family, style, out in [
        (t / 'sourceserif' / 'SourceSerif4-Semibold.otf', 'YZ Serif', 'Semibold', 'YZSerif-Semibold.woff2'),
        (t / 'sourceserif' / 'SourceSerif4-Regular.otf', 'YZ Serif', 'Regular', 'YZSerif-Regular.woff2'),
        (t / 'sourcesans' / 'SourceSans3-Regular.otf', 'YZ Sans', 'Regular', 'YZSans-Regular.woff2'),
        (t / 'sourcesans' / 'SourceSans3-Semibold.otf', 'YZ Sans', 'Semibold', 'YZSans-Semibold.woff2'),
    ]:
        subset(src, FONTS / out, unicodes=LATIN)
        rename(FONTS / out, family, style)
    chars = heading_chars()
    print(f'serif CJK characters: {len(chars)}')
    subset(CJK_SERIF, FONTS / 'NotoSerifSC-Bold.subset.woff2', text=chars, font_number=sc_font_number(CJK_SERIF))
    write_font_widths()


def write_font_widths():
    """Advance widths of the sans subsets, which tools/figlib.py uses to lay out chart text."""
    from fontTools.ttLib import TTFont
    widths = {}
    for weight, name in [('400', 'YZSans-Regular.woff2'), ('600', 'YZSans-Semibold.woff2')]:
        font = TTFont(FONTS / name)
        upm, hmtx = font['head'].unitsPerEm, font['hmtx']
        widths[weight] = {chr(cp): round(hmtx[g][0] / upm, 4) for cp, g in font.getBestCmap().items() if cp < 0x2e80}
    out = ROOT / 'tools' / 'data' / 'font_widths.json'
    if out.exists():   # keep tables this function does not write (e.g. the hand-drawn diagram face)
        old = json.loads(out.read_text(encoding='utf-8'))['widths']
        widths = {**old, **widths}
    note = ('Advance widths in em: 400/600 = YZ Sans (Source Sans 3) subsets, written by tools/make_assets.py; '
            'hand400/hand700 = Comic Neue, the hand-drawn diagram face. Read by tools/figlib.py.')
    out.write_text(json.dumps({'note': note, 'widths': widths}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'{out.name}: {len(widths["400"])} characters')


def rounded(im, radius):
    mask = Image.new('L', im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], radius, fill=255)
    out = Image.new('RGBA', im.size)
    out.paste(im, (0, 0), mask)
    return out


def crop_box(im, box):
    """box = (x0, y0, x1, y1) as fractions of the image size."""
    x0, y0, x1, y1 = box
    return im.crop((int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height)))


# Crop of "ID photo/Life photo.png" (3024 x 4032): head, waving hand and shoulders, without the neighbours.
PORTRAIT_BOX = (0.2074, 0.2278, 0.4889, 0.4917)   # 4:5
AVATAR_BOX = (0.2815, 0.2222, 0.4963, 0.3833)     # 1:1, face centred


def build_images(photo, texlive):
    IMG.mkdir(parents=True, exist_ok=True)
    src = ImageOps.exif_transpose(Image.open(photo)).convert('RGB')
    portrait = crop_box(src, PORTRAIT_BOX)
    pic = portrait.resize((400, 500), Image.LANCZOS)
    pic.save(IMG / 'photo.jpg', quality=86, optimize=True, progressive=True)
    avatar = crop_box(src, AVATAR_BOX).resize((460, 460), Image.LANCZOS)
    avatar.save(IMG / 'avatar.jpg', quality=88, optimize=True, progressive=True)
    print('photo.jpg', (IMG / 'photo.jpg').stat().st_size // 1024, 'KB; avatar.jpg', (IMG / 'avatar.jpg').stat().st_size // 1024, 'KB')

    t = pathlib.Path(texlive)
    serif = ImageFont.truetype(str(t / 'sourceserif' / 'SourceSerif4-Semibold.otf'), 84)
    sans = ImageFont.truetype(str(t / 'sourcesans' / 'SourceSans3-Regular.otf'), 32)
    sans_b = ImageFont.truetype(str(t / 'sourcesans' / 'SourceSans3-Semibold.otf'), 30)
    zh = ImageFont.truetype(CJK_SERIF, 52, index=sc_font_number(CJK_SERIF))

    card = Image.new('RGB', (1200, 630), (255, 255, 255))
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, 14, 630], fill=ACCENT)
    d.text((86, 150), 'Yi Zhang', font=serif, fill=(27, 31, 36))
    nx = 86 + d.textlength('Yi Zhang', font=serif) + 22
    d.text((nx, 176), '张益', font=zh, fill=(107, 115, 128))
    d.text((88, 278), 'LLM post-training · multimodal LLMs · agentic RL', font=sans, fill=(71, 80, 92))
    d.text((88, 326), 'M.S. student, Nanjing University', font=sans, fill=(71, 80, 92))
    d.text((88, 420), 'Looking for an LLM algorithm internship', font=sans_b, fill=ACCENT)
    d.text((88, 466), 'hey-chillax.github.io', font=sans, fill=(107, 115, 128))
    face = rounded(portrait.resize((328, 410), Image.LANCZOS), 24)
    card.paste(face, (808, 110), face)
    card.save(IMG / 'og.png', optimize=True)
    print('og.png', (IMG / 'og.png').stat().st_size // 1024, 'KB')

    icon = Image.new('RGB', (180, 180), ACCENT)
    di = ImageDraw.Draw(icon)
    f = ImageFont.truetype(str(t / 'sourcesans' / 'SourceSans3-Semibold.otf'), 84)
    tw = di.textlength('YZ', font=f)
    di.text(((180 - tw) / 2, 36), 'YZ', font=f, fill=(255, 255, 255))
    icon.save(IMG / 'apple-touch-icon.png', optimize=True)
    (IMG / 'favicon.svg').write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        '<rect width="32" height="32" rx="7" fill="#2d5a96"/>'
        '<text x="16" y="21.5" text-anchor="middle" font-family="Source Sans 3,Segoe UI,Helvetica,Arial,sans-serif" '
        'font-size="15" font-weight="700" fill="#fff">YZ</text></svg>\n', encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--photo', help='the original life photo; PORTRAIT_BOX and AVATAR_BOX choose the crops')
    ap.add_argument('--texlive-fonts', required=True, help='…/texmf-dist/fonts/opentype/adobe (Source Serif 4 / Source Sans 3)')
    ap.add_argument('--fonts-only', action='store_true')
    a = ap.parse_args()
    build_fonts(a.texlive_fonts)
    if not a.fonts_only:
        if not a.photo:
            raise SystemExit('--photo is required unless --fonts-only')
        build_images(a.photo, a.texlive_fonts)


if __name__ == '__main__':
    main()
