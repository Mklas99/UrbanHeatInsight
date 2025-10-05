# ADR: Integration of Heterogeneous Open Data Sources for Urban Heatmap

## Context
Das Projekt *Urban-Heat-Insight* zielt darauf ab, urbane Hitzeinseln in Wien (Pilotstadt) zu erkennen, zu prognostizieren und zu visualisieren. Hierfür müssen verschiedene offene Datenquellen (z. B. Satellitendaten, Baumkataster, Luftmessnetz, Bevölkerungsdaten, Höhenmodelle) genutzt werden.  
Die Herausforderung besteht darin, dass diese Daten in unterschiedlichen Formaten (GeoTIFF, WFS, CSV, Shapefile, JSON, etc.), zeitlicher Auflösung und Genauigkeit vorliegen. Ohne standardisierte Integration sind konsistente Analysen und Visualisierungen nicht möglich.

---

## Decision
Wir setzen auf eine **modulare Datenintegrationsarchitektur** mit folgenden Prinzipien:

- Einheitliche Georeferenzierung aller Daten auf ein Standard-Coordinate Reference System (WGS 84).
- Nutzung von **ETL-Pipelines** (Extract, Transform, Load) zur automatisierten Standardisierung, Harmonisierung und Aktualisierung.
- Ablage in einem **datenbankgestützten Data Lakehouse** (z. B. PostgreSQL/PostGIS + S3/MinIO), das sowohl Raster- als auch Vektorformate unterstützt.
- **API-first Ansatz**: Bereitstellung über REST-APIs und Webservices, damit Modelle (XGBoost, Clustering, Zeitreihen-Forecasts) und das Frontend (Leaflet/WebGIS) modular auf dieselbe Datenbasis zugreifen.
- **Versionierung & Reproduzierbarkeit**: Einsatz von Git+DVC für Datenstände und Metadaten-Tracking.

---

## Consequences

### Vorteile:
- Standardisierte, reproduzierbare Basis für alle Analysen und Visualisierungen.
- Einfaches Hinzufügen neuer Datenquellen durch die modulare Architektur.
- Verbesserte Datenqualität (Fehlerreduktion, Lückenfüllung, einheitliches Format).
- Grundlage für spätere Skalierung auf weitere Städte (Salzburg, Graz, etc.).

### Nachteile / Risiken:
- Initialer Integrationsaufwand hoch (ETL-Pipeline-Bau, Datenmapping).
- Potenzielle Performance-Probleme bei sehr großen Rasterdaten (Satellitenbilder).
- Abhängigkeit von externen Open-Data-Schnittstellen (z. B. Ausfälle oder Formatänderungen).
- Höhere Anforderungen an Monitoring & Maintenance (Datenversionen, API-Health).

---

## Status
**open** (in Entwicklung – wird im Prototypen bis Ende 2025 umgesetzt)
