# Inevitable Zone – uruchomienie strony na inevitable.zone

## Zawartość paczki

| Element | Co to jest |
|---|---|
| `public/` | Cała strona: `index.html`, zdjęcia, logo, `news.json`, polityka prywatności |
| `netlify/functions/story.mjs` | Asystent „Tell me a story” (wywołuje Claude przez API Anthropic) |
| `netlify.toml` | Konfiguracja hostingu Netlify |

## Krok 1. Konto i wdrożenie (Netlify, ok. 15 minut)

1. Załóż konto na netlify.com (plan darmowy wystarczy na start).
2. Zainstaluj Node.js (nodejs.org) – jednorazowo.
3. W Terminalu przejdź do folderu `inevitable-zone-web` i uruchom:
   ```
   npx netlify-cli login
   npx netlify-cli deploy --prod
   ```
   Przy pierwszym wdrożeniu wybierz „Create & configure a new project”, nazwa np. `inevitable-zone`.
4. Strona działa pod adresem `inevitable-zone.netlify.app`.

Wariant bez Terminala: przeciągnij folder `public` na app.netlify.com/drop. Strona, formularze i Psychology News działają, ale asystent „Tell me a story” wtedy nie działa (pokazuje prosty szkic do poprawienia), bo funkcja wymaga wdrożenia przez Terminal lub GitHub.

## Krok 2. Asystent „Tell me a story”

1. Załóż konto na console.anthropic.com, doładuj saldo i utwórz klucz API.
2. Ustaw limit wydatków miesięcznych (np. 20 USD), żeby zabezpieczyć się przed nadużyciem.
3. W Netlify: Project configuration → Environment variables → dodaj `ANTHROPIC_API_KEY` z kluczem.
4. Opcjonalnie `ANTHROPIC_MODEL` (domyślnie `claude-sonnet-4-6`; sprawdź aktualne nazwy modeli w dokumentacji Anthropic).
5. Wdróż ponownie: `npx netlify-cli deploy --prod`.

## Krok 3. Formularze i powiadomienia

Formularze „contact” i „story” są wykrywane automatycznie przez Netlify Forms.
W Netlify: Forms → włącz wykrywanie formularzy (Enable form detection) przed pierwszym wdrożeniem, potem Forms → Form notifications → Email notification na adres zespołu.

## Krok 4. Domena inevitable.zone

1. W Netlify: Domain management → Add a domain → `inevitable.zone`.
2. U rejestratora domeny ustaw rekordy DNS dokładnie tak, jak pokaże Netlify (zwykle rekord A dla `inevitable.zone` i CNAME dla `www` wskazujący na `inevitable-zone.netlify.app`). Alternatywnie przenieś obsługę DNS do Netlify.
3. Certyfikat HTTPS Netlify wystawi automatycznie po propagacji DNS (od kilku minut do 48 godzin).
4. Uwaga: jeśli poczta @inevitable.zone działa na tej domenie, nie zmieniaj rekordów MX.

## Psychology News – publikacja artykułów

1. Co 3 dni zaplanowane zadanie w Claude przygotowuje szkic artykułu.
2. Zatwierdzasz go w wersji strony w Claude (sekcja „Do zatwierdzenia”).
3. Poproś Claude: „wyeksportuj zatwierdzone artykuły do news.json”. Plik trafi do `public/news.json`.
4. Wdróż ponownie (`npx netlify-cli deploy --prod` albo przeciągnij `public`).

## Przed publikacją

- [ ] Polityka prywatności – weryfikacja prawnika, data, okres przechowywania danych
- [ ] Sąd rejestrowy w danych spółki (wymagany obok numeru KRS)
- [ ] Zgody trenerów na publikację zdjęć i biogramów
- [ ] Adres e-mail do powiadomień z formularzy
- [ ] Opcjonalnie: kroje pisma z własnego serwera zamiast Google Fonts (ostrożniejsze podejście do RODO)
