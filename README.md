# IoT Grasmaaier Sensor

Documentatie en bronbestanden voor het IoT Grasmaaier Sensor project in een samenwerking tussen Groenvoorziening A.J. van der Werf en Hanze Hogeschool Groningen (2026).


## Branches

| Branch | Beschrijving |
|--------|-------------|
| `main` | Overige bestanden voor documentatie, code zelf is voornamelijk gewerkt in branches. |
| `webapp-uitbreidingen` | Meest recente versie (branch) met GPS-functionaliteit |


## Uitgebreide documentatie (gelinkt aan Confluence)

| Bestand | Inhoud |
|---------|--------|
| `Bestanden Delen.md` | Bestandsdeling in de Cloud op een plek |
| `Overzicht.md` | Projectoverzicht |
| `Requirementanalyse.md` | Functionele en niet-functionele requirements, dit was aan het begin |
| `Retrospectives.md` | Retrospectives per periode |
| `Spike Stories.md` | Spike stories en onderzoekstaken die tijd hebben gekost |
| `Stand-Up Log.md` | Stand-up schema en logboek, zowel voor periode 1 als periode 2 |
| `Verdeling Taken.md` | Taakverdeling binnen het team |


## Scrumboard & Issues

- **Scrumboard** — dit is een belangrijk onderdeel en is voor het beste overzicht te vinden onder *Projects -> Scrumboard*
- **Requirements** — ook direct in te zien via *Issues*
- **Insights** — Hier vind je wat statistieken en verdere *Inzichten* in de uitwerking van het project.


## Namen

- **Namen** — Drie van ons (Mats, Koen & Damian) hebben eigen *Naam* in onze gebruikersnaam zitten, Wouter is de overige dus (MemeWeft).

Overzicht
Flask-webapplicatie voor het registreren en visualiseren van graslengtemetingen (vermoedelijk via een Raspberry Pi Pico-sensor), met een klantenportaal waarin klanten (zoals "Gemeente Groningen") alleen hun eigen data zien, en beheerders (admin) alles zien en gebruikers kunnen beheren.

Architectuur
app/
├── run.py                  → entrypoint, start de Flask dev-server
├── backend/
│   ├── __init__.py         → exporteert create_app
│   ├── app.py               → Flask app-factory, config, blueprint-registratie
│   ├── auth.py              → login/logout, login_required & admin_required decorators
│   ├── database.py          → measurements.db: schema + connectiebeheer
│   ├── users_db.py          → users.db: schema + connectiebeheer + seed-data
│   ├── model.py              → MeasurementRepository & ReportRepository (queries)
│   ├── users.py              → UserRepository (CRUD gebruikers)
│   └── routes.py            → alle pagina- en API-routes
├── templates/                → Jinja2 HTML-templates
└── data/
    ├── measurements.db        → SQLite db met metingen + rapportages
    └── users.db                → SQLite db met gebruikers
test.py                          → testscript dat nepmetingen naar de API stuurt
run.py
Entrypoint. Maakt de app via create_app() en start app.run() op port 5000 met debug aan.

backend/app.py — App-factory
create_app(): maakt de data/-map aan indien nodig, configureert Flask (template/static folders, database-paden, SECRET_KEY), initialiseert beide databases (init_app, init_users_app) en registreert de blueprints auth_bp en main_bp.
backend/database.py — Metingen-database
get_db(): opent/hergebruikt een SQLite-connectie via Flask's g (request-context).
close_db(): sluit de connectie aan het einde van de request (teardown).
init_app(app): maakt tabellen aan als ze niet bestaan:
measurements: id, height_mm, location, measured_at, latitude, longitude, client_name
reports: id, title, week_nr, year, avg_height, compliance, notes, created_at, expires_at
Bevat een migratie: voegt client_name toe aan bestaande tabellen (ALTER TABLE in try/except, want de kolom kan al bestaan) en koppelt bekende Groningse locaties automatisch aan klant "Gemeente Groningen".
backend/users_db.py — Gebruikers-database
Vergelijkbaar patroon (get_users_db, close_users_db, init_users_app).
Tabel users: id, username, password_hash, is_admin, client_name, created_at.
Seed: maakt automatisch een hardcoded admin-account (admin / 69420) en een voorbeeldklant gemeente_groningen / groningen2026 met client_name = "Gemeente Groningen".
backend/model.py — Data-repositories
MeasurementRepository (alle methodes ondersteunen optioneel filteren op client_name, zodat klanten alleen hun eigen data zien):

get_map_data() — locaties + coördinaten + hoogte voor de kaartweergave.
get_all(limit, client_name) — laatste N metingen.
insert(height_mm, location, lat, lon, client_name) — nieuwe meting toevoegen (gebruikt door de Pico/sensor-API).
get_stats() — totaal, gemiddelde, max, min hoogte.
get_location_summary() — gemiddelde/max per locatie + kwaliteitsklasse (A ≤50mm, B ≤80mm, C >80mm).
get_quality_summary() — aantal metingen per kwaliteitsklasse.
get_compliance_pct() — percentage metingen ≤80mm (norm-naleving).
get_chart_data() — dagelijks gemiddelde per locatie, laatste 28 dagen (voor grafieken).
get_unique_location_count() — aantal unieke locaties/velden.
ReportRepository:

get_all() — actieve (niet-verlopen) rapporten incl. resterende dagen.
delete(report_id) — rapport verwijderen.
generate_weekly() — genereert (idempotent, één keer per week) een weekrapport op basis van de laatste 7 dagen data, met een vervaldatum van 30 dagen.
purge_expired() — verwijdert verlopen rapporten.
backend/users.py — UserRepository
get_all() — alle gebruikers (admins eerst).
get_by_username / get_by_id — opzoeken.
verify(username, password) — login-check met wachtwoord-hash.
create(username, password, is_admin, client_name) — nieuwe gebruiker (faalt stil als username al bestaat).
update_password — wachtwoord wijzigen.
delete(user_id) — verwijderen, met bescherming: de account admin kan nooit verwijderd worden.
backend/auth.py — Authenticatie
login_required: decorator, stuurt naar /login als er geen sessie is.
admin_required: idem, plus check op session["is_admin"] (anders terug naar dashboard).
Routes: GET/POST /login (toont formulier / verwerkt login, zet sessie incl. client_name), GET /logout (wist sessie).
backend/routes.py — Pagina's & API
Helper _client(): geeft client_name van ingelogde gebruiker terug (None = admin/intern, ziet alles).

Pagina's (allen login_required, tenzij anders vermeld):

/ → redirect naar /dashboard
/dashboard → statistieken, locatie-overzicht, compliance%, aantal locaties
/kaart → kaartweergave met meetpunten (gefilterd per klant)
/measurement → tabel met losse metingen
/reports → rapportages (ruimt eerst verlopen rapporten op)
/users (admin_required) → gebruikersbeheer
API-endpoints:

POST /api/measurement — open, geen login (bedoeld voor de Pico-sensor) — voegt meting toe.
GET /api/measurements, /api/chart-data, /api/quality-summary, /api/location-summary — JSON-data voor dashboards, gefilterd per ingelogde klant.
POST /api/users / POST /api/users/<id>/password / DELETE /api/users/<id> (admin_required) — gebruikersbeheer; eigen account en admin-account kunnen niet verwijderd worden.
POST /api/reports/generate / DELETE /api/reports/<id> — rapportagebeheer.
Templates (templates/*.html)
base.html — layout/navigatie, wordt door andere templates ge-extend.
login.html — inlogformulier.
dashboard.html — KPI's, grafieken, locatie-overzicht.
kaart.html — interactieve kaart met meetpunten, veldpolygonen, kleurzones per kwaliteit/marge, maairoute-logica, pop-ups met kwaliteitseisen.
measurement.html — tabel met individuele metingen.
reports.html — lijst van rapportages met genereer/verwijder-acties.
users.html — admin-paneel: gebruikers aanmaken, wachtwoord wijzigen, verwijderen, klant koppelen.
test.py — Test/seed-script
Geen geautomatiseerde test, maar een script dat via urllib neppe meetdata naar POST /api/measurement stuurt om de database te vullen:

stuur(...) — verstuurt één meting. 
veld(...) — genereert een rooster van nx×ny meetpunten binnen een rechthoekig gebied met een hoogtefunctie hfn(dy, dx), plus ruis. 
Onderaan: 3 velden gekoppeld aan "Gemeente Groningen" en 3 interne (klant-loze) velden. 

