#!/usr/bin/env bash
set -e

echo "=== PCF Bilanzierung PoC ==="
echo ""

# Check Docker
if ! command -v docker &>/dev/null; then
  echo "❌ Docker nicht gefunden. Bitte Docker Desktop installieren."
  exit 1
fi

echo "▶ Starte PostgreSQL und Backend..."
docker compose up -d --build

echo ""
echo "⏳ Warte auf Startup..."
sleep 5

echo ""
echo "✅ Applikation läuft:"
echo "   → Frontend:  http://localhost:8000"
echo "   → API Docs:  http://localhost:8000/docs"
echo ""
echo "Logs anzeigen: docker compose logs -f backend"
echo "Stoppen:       docker compose down"
