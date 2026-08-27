#!/usr/bin/env python3
"""소스 하나에서 두 벌을 만든다.

  index.html            GitHub Pages / 로컬 파일용. tokens.css 와 폰트를 파일로 연결.
  dist/artifact.html    claude.ai 아티팩트용. 바깥 파일을 못 쓰므로 전부 한 파일에 담는다.

  python3 src/build.py
"""
import base64
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')

TITLE = 'Menu Asset Fitter'
DESC = '메뉴 이미지를 120x120 규격에 맞춰 잘라내고 가운데 정렬해 내보내는 도구.'

read = lambda p: io.open(p, encoding='utf-8').read()

body = read(os.path.join(SRC, 'body.html'))
page_css = read(os.path.join(SRC, 'page.css'))
tokens = read(os.path.join(ROOT, 'tokens.css'))


def strip_dark(css):
    """라이트 전용 페이지다. 아티팩트 뷰어가 data-theme=dark 를 찍으면
    XDS 다크 토큰이 절반만 먹어 화면이 깨지므로 그 블록을 들어낸다."""
    start = css.find('.dark, [data-theme="dark"] {')
    if start == -1:
        return css
    depth, i = 0, css.index('{', start)
    while i < len(css):
        if css[i] == '{':
            depth += 1
        elif css[i] == '}':
            depth -= 1
            if depth == 0:
                return css[:start] + css[i + 1:]
        i += 1
    return css


def inline_font(css):
    """@font-face 의 woff2 를 data URI 로 바꿔 한 파일에 담는다."""
    path = os.path.join(ROOT, 'assets', 'PretendardVariable.woff2')
    b64 = base64.b64encode(io.open(path, 'rb').read()).decode('ascii')
    return css.replace(
        "url('assets/PretendardVariable.woff2') format('woff2')",
        "url(data:font/woff2;base64,%s) format('woff2')" % b64,
    )


# ---------- 1. index.html ----------

index = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="tokens.css">
<style>
{page}</style>
</head>
<body>
{body}</body>
</html>
""".format(title=TITLE, desc=DESC, page=page_css, body=body)

io.open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(index)


# ---------- 2. dist/artifact.html ----------

os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)

artifact = '<title>{title}</title>\n<style>\n{tokens}</style>\n<style>\n{page}</style>\n{body}'.format(
    title=TITLE,
    tokens=inline_font(strip_dark(tokens)),
    page=page_css,
    body=body,
)
io.open(os.path.join(ROOT, 'dist', 'artifact.html'), 'w', encoding='utf-8').write(artifact)


# ---------- 확인 ----------

for name, text in (('index.html', index), ('dist/artifact.html', artifact)):
    print('%-22s %7.2f KB' % (name, len(text.encode('utf-8')) / 1024))

assert '<script>' in index and index.count('<script>') == 1
assert 'data-theme="dark"' not in artifact, '아티팩트에 다크 블록이 남았다'
assert re.search(r'<title>.*?</title>', index)
print('ok')
