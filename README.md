# Inevitable Zone – inevitable.zone

Strona Inevitable Zone Institute. Hosting: GitHub Pages z folderu `docs/`, domena inevitable.zone (plik `docs/CNAME`).

## Jak to działa

- `src/index.html` – jedyny szablon strony: wszystkie sekcje, wersja polska i angielska. **Zmiany treści i wyglądu robimy tutaj.**
- `tools/build.py` – generator (Python 3, bez dodatkowych bibliotek). Tworzy w `docs/` osobne strony z własnymi adresami:
  `/`, `/oferta/`, `/program/`, `/kompetencje/`, `/psychology-news/`, `/tell-me-a-story/`, `/o-nas/`, `/kontakt/`
  oraz wersję angielską pod `/en/...`, strony artykułów `/psychology-news/<slug>/`, `sitemap.xml` i `404.html`.
- `src/catalog.json` – katalog szkoleń: grupy, tytuły, zajawki, opisy, efekty i forma (PL i EN). Z niego powstają `/szkolenia/` i `/en/training/` oraz strony każdego szkolenia; moduły Programu linkują do szkoleń (MODULE_MAP w build.py).
- `docs/news.json` – zatwierdzone artykuły Psychology News (pole `slug` = adres artykułu).

Po każdej zmianie szablonu lub `news.json`:

```
python3 tools/build.py
```

Pliki `index.html` w `docs/` (i podfolderach) są generowane – nie edytujemy ich ręcznie.
