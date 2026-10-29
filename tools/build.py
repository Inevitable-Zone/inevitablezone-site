#!/usr/bin/env python3
"""Generator strony inevitable.zone.

Z jednego szablonu src/index.html (wszystkie sekcje, oba języki) tworzy w docs/
osobne strony z własnymi adresami, w wersji polskiej i angielskiej, z tytułami,
opisami, znacznikami hreflang, danymi strukturalnymi (JSON-LD) oraz stronami
artykułów Psychology News z docs/news.json. Na końcu zapisuje docs/sitemap.xml.

Uruchomienie z katalogu repozytorium:  python3 tools/build.py
Tylko biblioteka standardowa Pythona 3.
"""
import datetime
import html as H
import json
import os
import re
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src', 'index.html')
DOCS = os.path.join(ROOT, 'docs')
SITE = 'https://inevitable.zone'
LANGS = ('pl', 'en')

# widok -> adres w danym języku
PATHS = {
    'home':        {'pl': '/',                  'en': '/en/'},
    'oferta':      {'pl': '/oferta/',           'en': '/en/services/'},
    'program':     {'pl': '/program/',          'en': '/en/programme/'},
    'kompetencje': {'pl': '/kompetencje/',      'en': '/en/competences/'},
    'news':        {'pl': '/psychology-news/',  'en': '/en/psychology-news/'},
    'story':       {'pl': '/tell-me-a-story/',  'en': '/en/tell-me-a-story/'},
    'o-nas':       {'pl': '/o-nas/',            'en': '/en/about-us/'},
    'kontakt':     {'pl': '/kontakt/',          'en': '/en/contact/'},
}
ORDER = ['home', 'oferta', 'program', 'kompetencje', 'news', 'story', 'o-nas', 'kontakt']

META = {
    'home': {
        'pl': ('Psychologia biznesu dla zarządów i liderów · Inevitable Zone Institute',
               'Psychologia biznesu dla zarządów, liderów i zespołów. Programy rozwojowe, mentoring i interwencje kryzysowe prowadzone przez doktorów psychologii, wykładowców i praktyków biznesu.'),
        'en': ('Business psychology for boards and leaders · Inevitable Zone Institute',
               'Business psychology for boards, leaders and teams. Development programmes, mentoring and crisis interventions led by doctors of psychology, lecturers and business practitioners.'),
    },
    'oferta': {
        'pl': ('Szkolenia dla zarządów, mentoring i interwencje kryzysowe · Inevitable Zone',
               'Szkolenia i warsztaty dla liderów i zespołów, indywidualny mentoring menedżerski oraz sesje eksperckie i interwencje kryzysowe. Każdą współpracę zaczynamy od rozmowy diagnostycznej.'),
        'en': ('Leadership training, mentoring and crisis intervention · Inevitable Zone',
               'Training and workshops for leaders and teams, individual management mentoring, expert sessions and crisis interventions. Every engagement starts with a diagnostic conversation.'),
    },
    'program': {
        'pl': ('Program High-Performance Culture of Autonomy & Accountability · Inevitable Zone',
               'Proces rozwojowy, w którym uczestnicy przechodzą od zrozumienia własnego umysłu do świadomego przywództwa. Moduły dobieramy pod diagnozę organizacji.'),
        'en': ('High-Performance Culture of Autonomy & Accountability programme · Inevitable Zone',
               'A development process that takes participants from understanding their own minds to conscious leadership. Modules are selected for the organisation’s diagnosis.'),
    },
    'kompetencje': {
        'pl': ('Trenerzy i eksperci: psycholodzy, wykładowcy, praktycy · Inevitable Zone',
               'Doktorzy psychologii, lekarze, wykładowcy akademiccy, była oficer służb specjalnych i prelegenci TEDx. Poznaj ekspertów, którzy prowadzą programy Inevitable Zone Institute.'),
        'en': ('Trainers and experts: psychologists, lecturers, practitioners · Inevitable Zone',
               'Doctors of psychology, physicians, university lecturers, a former special services officer and TEDx speakers. Meet the experts who run Inevitable Zone Institute programmes.'),
    },
    'news': {
        'pl': ('Psychology News: psychologia pracy i przywództwa · Inevitable Zone',
               'Co kilka dni jedno badanie z psychologii pracy, przywództwa lub dobrostanu i krótko o tym, co z niego wynika dla firm.'),
        'en': ('Psychology News: workplace and leadership psychology · Inevitable Zone',
               'Every few days one study in workplace, leadership or wellbeing psychology, and briefly what it means for organisations.'),
    },
    'story': {
        'pl': ('Opowiedz nam swoją historię · Inevitable Zone Institute',
               'Napisz swoimi słowami, z czym mierzy się Twój zespół. Pomożemy ułożyć z tego wiadomość, którą możesz poprawić i wysłać do nas.'),
        'en': ('Tell us your story · Inevitable Zone Institute',
               'Write in your own words what your team is facing. We help turn it into a message you can edit and send to us.'),
    },
    'o-nas': {
        'pl': ('O nas: psychologia spotyka biznes · Inevitable Zone Institute',
               'Pomagamy organizacjom rozwijać liderów, przeprowadzać transformacje i budować odporne zespoły w czasach niepewności. Poznaj założycieli i zespół Inevitable Zone.'),
        'en': ('About us: where psychology meets business · Inevitable Zone Institute',
               'We help organisations develop leaders, carry out transformations and build resilient teams in uncertain times. Meet the founders and the Inevitable Zone team.'),
    },
    'kontakt': {
        'pl': ('Kontakt i konsultacja wstępna · Inevitable Zone Institute',
               'Porozmawiajmy o Państwa zespole. Po niezobowiązującej konsultacji wstępnej przygotujemy indywidualną propozycję i wycenę. INEVITABLE ZONE sp. z o.o., Kraków.'),
        'en': ('Contact and introductory consultation · Inevitable Zone Institute',
               'Let’s talk about your team. After a no-obligation introductory consultation we prepare an individual proposal and quote. INEVITABLE ZONE sp. z o.o., Kraków.'),
    },
}
CRUMB = {'home': {'pl': 'Strona główna', 'en': 'Home'},
         'oferta': {'pl': 'Oferta', 'en': 'Services'}, 'program': {'pl': 'Program', 'en': 'Programme'},
         'kompetencje': {'pl': 'Kompetencje', 'en': 'Competences'}, 'news': {'pl': 'Psychology News', 'en': 'Psychology News'},
         'story': {'pl': 'Tell me a story', 'en': 'Tell me a story'}, 'o-nas': {'pl': 'O nas', 'en': 'About us'},
         'kontakt': {'pl': 'Kontakt', 'en': 'Contact'}}
LOCALE = {'pl': 'pl_PL', 'en': 'en_GB'}
MONTHS_PL = ['stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca', 'lipca', 'sierpnia',
             'września', 'października', 'listopada', 'grudnia']
MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
             'September', 'October', 'November', 'December']
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}


# ---------------------------------------------------------------- HTML helpers
class _Locator(HTMLParser):
    """Finds the (start, end) offsets of outermost elements matching pred(tag, attrs)."""

    def __init__(self, text, pred):
        super().__init__(convert_charrefs=False)
        self.text, self.pred = text, pred
        self.lines = [0]
        for m in re.finditer('\n', text):
            self.lines.append(m.end())
        self.stack, self.spans = [], []

    def _off(self):
        ln, col = self.getpos()
        return self.lines[ln - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self._off()
        end = start + len(self.get_starttag_text())
        hit = not any(m for _, _, m in self.stack) and self.pred(tag, dict(attrs))
        if tag in VOID:
            if hit:
                self.spans.append((start, end))
            return
        self.stack.append((tag, start, hit))

    def handle_startendtag(self, tag, attrs):
        start = self._off()
        if not any(m for _, _, m in self.stack) and self.pred(tag, dict(attrs)):
            self.spans.append((start, start + len(self.get_starttag_text())))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        start = self._off()
        end = self.text.index('>', start) + 1
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                t, s, hit = self.stack[i]
                del self.stack[i:]
                if hit:
                    self.spans.append((s, end))
                return


def find_spans(text, pred):
    p = _Locator(text, pred)
    p.feed(text)
    p.close()
    return sorted(p.spans)


def remove_spans(text, spans):
    for s, e in sorted(spans, reverse=True):
        text = text[:s] + text[e:]
    return text


def classes(attrs):
    return (attrs.get('class') or '').split()


def strip_tags(s):
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


def fmt_date(d, lang):
    try:
        y, m, dd = [int(x) for x in d.split('-')]
    except Exception:
        return d
    return f'{dd} {(MONTHS_PL if lang == "pl" else MONTHS_EN)[m - 1]} {y}'


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace('</', '<\\/') + '</script>'


# ---------------------------------------------------------------- page building
def load():
    with open(SRC, encoding='utf-8') as f:
        tpl = f.read()
    try:
        with open(os.path.join(DOCS, 'news.json'), encoding='utf-8') as f:
            news = json.load(f)
    except FileNotFoundError:
        news = []
    news = [a for a in news if a.get('slug')]
    news.sort(key=lambda a: (str(a.get('date', '')), a['slug']), reverse=True)
    return tpl, news


def view_of_page(view):
    return 'o-nas' if view == 'zespol' else view


def localise(tpl, lang):
    """Keep only one language and make links/assets absolute."""
    other = 'en' if lang == 'pl' else 'pl'
    body_start = tpl.index('<body')
    head, body = tpl[:body_start], tpl[body_start:]
    body = remove_spans(body, find_spans(body, lambda t, a: other in classes(a)))
    out = head + body

    def link(m):
        name = m.group(1)
        if name in ('home', 'top'):
            return f'href="{PATHS["home"][lang]}"'
        if name == 'zespol':
            return f'href="{PATHS["o-nas"][lang]}#zespol"'
        if name in PATHS:
            return f'href="{PATHS[name][lang]}"'
        return m.group(0)
    out = re.sub(r'href="#([a-z\-]+)"', link, out)
    out = re.sub(r'(src|href)="(?!https?:|/|#|mailto:|tel:|data:|\')([^"]+)"', r'\1="/\2"', out)
    return out


def keep_views(page, keep):
    body_start = page.index('<body')
    head, body = page[:body_start], page[body_start:]
    body = remove_spans(body, find_spans(body, lambda t, a: 'data-view' in a and a['data-view'] not in keep))
    # unhide kept sections
    body = re.sub(r'(<[^>]*data-view="[^"]+"[^>]*?) hidden>', r'\1>', body)
    return head + body


def promote_h1(page, view):
    if view == 'home':
        return page
    m = re.search(r'<[a-z]+ [^>]*data-view="' + re.escape(view) + '"', page)
    if not m:
        return page
    start = m.start()
    h2 = page.find('<h2', start)
    nxt = page.find('data-view=', m.end())
    lab = page.find('<p class="label">', start)
    if h2 != -1 and (nxt == -1 or h2 < nxt):
        end = page.index('</h2>', h2)
        return page[:h2] + '<h1' + page[h2 + 3:end] + '</h1>' + page[end + 5:]
    if lab != -1:
        end = page.index('</p>', lab)
        return page[:lab] + '<h1 class="label">' + page[lab + len('<p class="label">'):end] + '</h1>' + page[end + 4:]
    return page


def set_head(page, lang, view, url, alt, title, desc, ld, extra_js, og_type='website', noindex=False):
    def sub(pattern, repl):
        nonlocal page
        new, n = re.subn(pattern, lambda m: repl, page, count=1)
        assert n == 1, pattern
        page = new
    e = H.escape
    sub(r'<html[^>]*>', f'<html lang="{lang}" data-lang="{lang}" data-v="{view}">')
    sub(r'<title>.*?</title>', f'<title>{e(title)}</title>')
    sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(desc)}">')
    sub(r'<meta property="og:type" content="[^"]*">', f'<meta property="og:type" content="{og_type}">')
    sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{SITE}{url}">')
    sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{e(title)}">')
    sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{e(desc)}">')
    links = [f'<link rel="canonical" href="{SITE}{url}">']
    if alt:
        links += [f'<link rel="alternate" hreflang="{l}" href="{SITE}{alt[l]}">' for l in LANGS]
        links.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}{alt["pl"]}">')
    links.append(f'<meta property="og:locale" content="{LOCALE[lang]}">')
    if alt:
        o = 'en' if lang == 'pl' else 'pl'
        links.append(f'<meta property="og:locale:alternate" content="{LOCALE[o]}">')
    if noindex:
        links.append('<meta name="robots" content="noindex">')
    links.append(jsonld(ld))
    links.append('<script>' + extra_js + '</script>')
    sub(r'<link rel="canonical" href="[^"]*">', '\n'.join(links))
    return page


ORG_ID = SITE + '/#organization'
SITE_ID = SITE + '/#website'


def org(lang):
    return {
        '@type': 'ProfessionalService', '@id': ORG_ID,
        'name': 'Inevitable Zone Institute', 'legalName': 'INEVITABLE ZONE sp. z o.o.',
        'alternateName': 'Inevitable Zone', 'url': SITE + '/', 'logo': SITE + '/logo.png',
        'image': SITE + '/og-image.png', 'slogan': 'Human Reflection of Business',
        'description': META['home'][lang][1],
        'address': {'@type': 'PostalAddress', 'streetAddress': 'Kącik 4', 'postalCode': '30-549',
                    'addressLocality': 'Kraków', 'addressCountry': 'PL'},
        'taxID': '6793304174', 'email': 'adam.bugaj@inevitable.zone',
        'founder': [{'@type': 'Person', 'name': 'Karina Tomczyk'}, {'@type': 'Person', 'name': 'Adam Bugaj'}],
        'knowsAbout': (['psychologia biznesu', 'przywództwo', 'mentoring menedżerski', 'odporność psychiczna',
                        'interwencja kryzysowa', 'komunikacja', 'dobrostan w pracy', 'człowiek i sztuczna inteligencja']
                       if lang == 'pl' else
                       ['business psychology', 'leadership', 'management mentoring', 'psychological resilience',
                        'crisis intervention', 'communication', 'workplace wellbeing', 'people and artificial intelligence']),
    }


def graph(lang, url, title, desc, crumbs, extra=None):
    nodes = [org(lang),
             {'@type': 'WebSite', '@id': SITE_ID, 'url': SITE + '/', 'name': 'Inevitable Zone Institute',
              'inLanguage': ['pl', 'en'], 'publisher': {'@id': ORG_ID}},
             {'@type': 'WebPage', '@id': SITE + url, 'url': SITE + url, 'name': title, 'description': desc,
              'inLanguage': lang, 'isPartOf': {'@id': SITE_ID}, 'about': {'@id': ORG_ID}}]
    if len(crumbs) > 1:
        nodes.append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + u} for i, (n, u) in enumerate(crumbs)]})
    nodes += extra or []
    return {'@context': 'https://schema.org', '@graph': nodes}


def services_ld(page, lang):
    names = [strip_tags(m) for m in re.findall(r'<div class="tile-label">(.*?)</div>', page, re.S)]
    lines = [strip_tags(m) for m in re.findall(r'<p class="tile-line">(.*?)</p>', page, re.S)]
    out = []
    for i, n in enumerate(names):
        out.append({'@type': 'Service', 'name': n, 'description': lines[i] if i < len(lines) else n,
                    'provider': {'@id': ORG_ID}, 'areaServed': 'PL', 'availableLanguage': ['pl', 'en']})
    return out


def people_ld(page):
    items = []
    for m in re.finditer(r'<article class="tr"[^>]*>(.*?)</article>', page, re.S):
        a = m.group(1)
        name = re.search(r'<h3>(.*?)</h3>', a, re.S)
        spec = re.search(r'<p class="spec">(.*?)</p>', a, re.S)
        img = re.search(r'<img [^>]*src="([^"]+)"', a)
        if not name:
            continue
        p = {'@type': 'Person', 'name': strip_tags(name.group(1)), 'worksFor': {'@id': ORG_ID}}
        if spec:
            p['knowsAbout'] = strip_tags(spec.group(1))
        if img:
            p['image'] = SITE + img.group(1)
        items.append({'@type': 'ListItem', 'position': len(items) + 1, 'item': p})
    return [{'@type': 'ItemList', 'name': 'Trenerzy i eksperci Inevitable Zone', 'itemListElement': items}] if items else []


def news_static(news, lang):
    if not news:
        return None
    rows = []
    for a in news:
        url = PATHS['news'][lang] + a['slug'] + '/'
        tag = a.get('tag_' + lang) or a.get('tag_pl') or a.get('tag') or ''
        rows.append('<article class="art"><time datetime="%s">%s</time><div>%s<h3><a href="%s">%s</a></h3><p class="lead">%s</p></div></article>' % (
            H.escape(a.get('date', '')), H.escape(fmt_date(a.get('date', ''), lang)),
            ('<span class="tag">%s</span>' % H.escape(tag)) if tag else '', url,
            H.escape(a.get('title_' + lang) or a.get('title_pl', '')), H.escape(a.get('lead_' + lang) or a.get('lead_pl', ''))))
    return ''.join(rows)


def article_section(a, lang):
    L = lang
    title = a.get('title_' + L) or a.get('title_pl', '')
    lead = a.get('lead_' + L) or a.get('lead_pl', '')
    body = a.get('body_' + L) or a.get('body_pl', '')
    tag = a.get('tag_' + L) or a.get('tag_pl') or a.get('tag') or ''
    paras = ''.join('<p>%s</p>' % H.escape(p.strip()) for p in re.split(r'\n\s*\n', body) if p.strip())
    src = a.get('source_url') or ''
    src_html = ''
    if src.startswith('https://'):
        src_html = '<p class="src hint">%s<a href="%s" target="_blank" rel="noopener">%s</a></p>' % (
            'Źródło: ' if L == 'pl' else 'Source: ', H.escape(src), H.escape(a.get('source_name') or src))
    back = PATHS['news'][L]
    return ('<section class="in sec view" id="news" data-view="news">\n'
            '    <a class="back" href="%s"><span aria-hidden="true">←</span> Psychology News</a>\n'
            '    <article class="art art-full"><time datetime="%s">%s</time><div>%s<h1>%s</h1><p class="lead">%s</p>'
            '<div class="body">%s</div>%s<p class="art-cta"><a class="lux-link" href="%s">%s →</a></p></div></article>\n'
            '  </section>') % (back, H.escape(a.get('date', '')), H.escape(fmt_date(a.get('date', ''), L)),
                               ('<span class="tag">%s</span>' % H.escape(tag)) if tag else '',
                               H.escape(title), H.escape(lead), paras, src_html, PATHS['kontakt'][L],
                               'Porozmawiajmy o tym, co to oznacza dla Państwa zespołu' if L == 'pl' else 'Let’s talk about what this means for your team')


def routes_js(lang, alt):
    routes = {l: {v: PATHS[v][l] for v in PATHS} for l in LANGS}
    for l in LANGS:
        routes[l]['zespol'] = PATHS['o-nas'][l]
    return 'window.IZ_ALT=%s;window.IZ_ROUTES=%s;' % (json.dumps(alt), json.dumps(routes))


def write(path, text):
    full = os.path.join(DOCS, path.strip('/'), 'index.html') if path != '/' else os.path.join(DOCS, 'index.html')
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(text)
    return full


def build():
    tpl, news = load()
    today = datetime.date.today().isoformat()
    sitemap = []
    written = []
    for lang in LANGS:
        base = localise(tpl, lang)
        for view in ORDER:
            url = PATHS[view][lang]
            alt = {l: PATHS[view][l] for l in LANGS}
            page = keep_views(base, {view})
            page = promote_h1(page, view)
            title, desc = META[view][lang]
            crumbs = [(CRUMB['home'][lang], PATHS['home'][lang])] + ([(CRUMB[view][lang], url)] if view != 'home' else [])
            extra = []
            if view == 'oferta':
                extra = services_ld(page, lang)
            if view == 'kompetencje':
                extra = people_ld(page)
            if view == 'news':
                st = news_static(news, lang)
                if st:
                    page = re.sub(r'(<div id="n-list" class="news">).*?(</div>\n)', lambda m: m.group(1) + st + m.group(2), page, count=1, flags=re.S)
            page = set_head(page, lang, view, url, alt, title, desc, graph(lang, url, title, desc, crumbs, extra), routes_js(lang, alt))
            written.append(write(url, page))
            sitemap.append((alt, today))
        # article pages
        for a in news:
            url = PATHS['news'][lang] + a['slug'] + '/'
            alt = {l: PATHS['news'][l] + a['slug'] + '/' for l in LANGS}
            page = keep_views(base, {'news'})
            s, e = find_spans(page[page.index('<body'):], lambda t, at: at.get('data-view') == 'news')[0]
            off = page.index('<body')
            page = page[:off + s] + article_section(a, lang) + page[off + e:]
            title = (a.get('title_' + lang) or a.get('title_pl', '')) + ' · Psychology News'
            desc = a.get('lead_' + lang) or a.get('lead_pl', '')
            art = {'@type': 'Article', 'headline': a.get('title_' + lang) or a.get('title_pl', ''), 'description': desc,
                   'datePublished': a.get('date'), 'inLanguage': lang, 'author': {'@id': ORG_ID}, 'publisher': {'@id': ORG_ID},
                   'mainEntityOfPage': SITE + url, 'image': SITE + '/og-image.png'}
            if (a.get('source_url') or '').startswith('https://'):
                art['isBasedOn'] = a['source_url']
            crumbs = [(CRUMB['home'][lang], PATHS['home'][lang]), ('Psychology News', PATHS['news'][lang]), (art['headline'], url)]
            page = set_head(page, lang, 'news', url, alt, title, desc, graph(lang, url, title, desc, crumbs, [art]),
                            routes_js(lang, alt), og_type='article')
            written.append(write(url, page))
            if lang == 'pl':
                sitemap.append((alt, a.get('date') or today))
    # sitemap with language alternates
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    seen = set()
    for alt, mod in sitemap:
        for l in LANGS:
            if alt[l] in seen:
                continue
            seen.add(alt[l])
            out.append('  <url><loc>%s%s</loc><lastmod>%s</lastmod>' % (SITE, alt[l], mod))
            for l2 in LANGS:
                out.append('    <xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>' % (l2, SITE, alt[l2]))
            out.append('    <xhtml:link rel="alternate" hreflang="x-default" href="%s%s"/>' % (SITE, alt['pl']))
            out.append('  </url>')
    out.append('</urlset>')
    with open(os.path.join(DOCS, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    # 404: strona główna bez indeksowania (stare lub błędne adresy)
    with open(os.path.join(DOCS, 'index.html'), encoding='utf-8') as f:
        home = f.read()
    with open(os.path.join(DOCS, '404.html'), 'w', encoding='utf-8') as f:
        f.write(home.replace('<meta name="description"', '<meta name="robots" content="noindex">\n<meta name="description"', 1))
    print('Zapisano %d stron i sitemap.xml (%d adresów).' % (len(written), len(seen)))


if __name__ == '__main__':
    build()
