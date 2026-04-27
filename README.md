# PCF Bilanzierung

**Product Carbon Footprint** Bilanzierungstool nach **GHG Protocol Product Standard** und **ISO 14067** – Proof of Concept für graphische Druckerzeugnisse (gestrichenes Papier, Offsetdruck).

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/sathustra/pcf-bilanzierung)

---

## Features

- **5 GWP-Indikatoren** (fossil, biogenic emissions, biogenic uptake, LULUC, total)
- **4 Bilanzierungskategorien**: Materialien · Energie · Transport · Abfall
- **Life Cycle Stages**: Rohstoffbereitstellung · Herstellung · Transport & Lagerung
- **14 Sub-Kategorien** inkl. Strom, Wärme, Direktemissionen, Abfall
- **Datenqualitätsbewertung** (DQR = Ø TeR+GeR+TiR, emissionsgewichtet) mit Ampel-Logik
- **Primärdatenanteil** (PDS) als Prozentsatz
- **Excel-Export** der vollständigen Bilanz
- **Demo-Datensatz**: Katalog A4 glossy (80 g/m² gestrichenes Papier) mit realen ecoinvent-Faktoren

## Live Demo (Render – 1-Click Deploy)

1. Auf den **Deploy to Render**-Button klicken
2. GitHub-Account verbinden (falls noch nicht geschehen)
3. Render erstellt automatisch: Web Service (Python) + PostgreSQL
4. Nach ~2 min ist die App live – die Demo-Daten werden beim ersten Start automatisch geladen

> **Hinweis**: Render Free Tier schläft nach 15 min Inaktivität. Erster Request nach Schlaf dauert ~30 s.

## Lokale Entwicklung (Docker)

```bash
git clone https://github.com/sathustra/pcf-bilanzierung.git
cd pcf-bilanzierung
docker compose up -d
```

App läuft auf **http://localhost:8000** · API-Docs auf **http://localhost:8000/docs**

```bash
docker compose logs -f backend   # Logs
docker compose down              # Stoppen
```

## Tech Stack

| Schicht | Technologie |
|---|---|
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2 |
| Datenbank | PostgreSQL 16 |
| Frontend | HTML · Tailwind CSS · Chart.js |
| Deployment | Docker · Render |

## Projektstruktur

```
.
├── backend/
│   ├── main.py            # FastAPI App + Static File Serving
│   ├── models.py          # SQLAlchemy Datenmodelle
│   ├── schemas.py         # Pydantic Schemas
│   ├── calculations.py    # GWP-Berechnungslogik
│   ├── seed_data.py       # Demo-Daten
│   └── routers/           # API-Endpunkte
├── frontend/
│   ├── index.html         # Dashboard
│   ├── products.html      # Stammdaten
│   ├── emission_factors.html  # EF-Datenbank
│   ├── inventory.html     # Bilanzierungsdaten
│   └── js/api.js          # API-Client
├── docker-compose.yml
└── render.yaml            # Render Deployment Config
```

## Berechnungslogik

```
Batch-Emissionen [kgCO₂eq] = Aktivitätsdaten × Emissionsfaktor
PCF [kgCO₂eq / Bezugseinheit] = Batch-Emissionen / Jahresproduktion

GWP-fossil          = Σ fossile Emissionen
GWP-biogenic        = Σ biogene Emissionen
GWP-biogenic uptake = biogener C-Gehalt × 3,664 × (−1)
GWP-LULUC           = Σ LUC-Emissionen
GWP-total           = GWP-fossil + GWP-biogenic + GWP-LULUC

DQR = Σ (|Emission_i| × (TeR_i + GeR_i + TiR_i) / 3) / Σ |Emission_i|
```
