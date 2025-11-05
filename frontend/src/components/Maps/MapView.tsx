// src/components/MapView.tsx
import React, { useEffect, useLayoutEffect, useMemo, useRef } from "react";
import L from "leaflet";
import type {
  Map as LeafletMap,
  Marker as LeafletMarker,
  GeoJSON as LeafletGeoJSON,
  LatLngExpression,
  LatLngTuple,
  LatLngBoundsExpression,
} from "leaflet";
import "leaflet/dist/leaflet.css";

// If you use a UI reset that sets img { max-width: 100% }, Leaflet tiles break.
// Inject a tiny CSS fix once to prevent tile gaps.
const injectLeafletTileCssFix = (() => {
  let injected = false;
  return () => {
    if (injected) return;
    injected = true;
    const css = `
      .leaflet-container img, .leaflet-pane img { max-width: none !important; }
      .leaflet-container { background: #f3f4f6ce; } /* subtle bg while tiles load */
    `;
    const style = document.createElement("style");
    style.setAttribute("data-leaflet-fix", "true");
    style.appendChild(document.createTextNode(css));
    document.head.appendChild(style);
  };
})();

// Robust icon URLs for Vite/webpack builds
import iconUrl from "leaflet/dist/images/marker-icon.png";
import iconRetinaUrl from "leaflet/dist/images/marker-icon-2x.png";
import shadowUrl from "leaflet/dist/images/marker-shadow.png";
L.Icon.Default.mergeOptions({ iconUrl, iconRetinaUrl, shadowUrl });

// ————————————————————————————————————————————————————————————————————————————
// Types / Props
// ————————————————————————————————————————————————————————————————————————————
export interface MapViewProps {
  className?: string;
  style?: React.CSSProperties;

  center?: LatLngExpression;
  zoom?: number;
  minZoom?: number;
  maxZoom?: number;
  maxBounds?: LatLngBoundsExpression;

  /** Show a marker at `center` */
  showCenterMarker?: boolean;

  /** Load & outline Vienna boundary + mask outside of it */
  loadViennaBoundary?: boolean;

  /** Extra GeoJSON URL to overlay (optional) */
  overlayGeoJsonUrl?: string; // e.g. "/assets/leaflet/maps/landesgraenze.geojson"
}

// ————————————————————————————————————————————————————————————————————————————
// Defaults
// ————————————————————————————————————————————————————————————————————————————
const DEFAULT_CENTER: LatLngExpression = [48.2082, 16.3738]; // Vienna
const DEFAULT_BOUNDS: LatLngTuple[] = [
  [47.9, 16.0],
  [48.5, 16.7],
];
const OUTER_MASK: LatLngExpression[][] = [
  [
    [47.5, 15.5],
    [47.5, 17.0],
    [48.7, 17.0],
    [48.7, 15.5],
    [47.5, 15.5],
  ],
];

// ————————————————————————————————————————————————————————————————————————————
// Component
// ————————————————————————————————————————————————————————————————————————————
export default function MapView({
  className = "",
  style,
  center = DEFAULT_CENTER,
  zoom = 13,
  minZoom = 11,
  maxZoom = 18,
  maxBounds = DEFAULT_BOUNDS,
  showCenterMarker = true,
  loadViennaBoundary = true,
  overlayGeoJsonUrl = "/assets/leaflet/maps/landesgraenze.geojson",
}: MapViewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<LeafletMap | null>(null);
  const markerRef = useRef<LeafletMarker | null>(null);
  const geoJsonLayersRef = useRef<LeafletGeoJSON[]>([]);
  const abortRef = useRef<AbortController | null>(null);

  // One-time CSS fix for tiles
  useLayoutEffect(() => {
    injectLeafletTileCssFix();
  }, []);

  // Initialize map once (on mount)
  useLayoutEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center,
      zoom,
      minZoom,
      maxZoom,
      maxBounds,
      maxBoundsViscosity: 1.0,
      zoomSnap: 0.5,
      wheelPxPerZoomLevel: 96,
      preferCanvas: true,
      attributionControl: true,
      zoomControl: true,
    });

    // Base layer (OSM)
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      updateWhenIdle: true,
      keepBuffer: 2,
      subdomains: "abc",
      crossOrigin: true,
      maxZoom,
    }).addTo(map);

    // A scale bar is handy
    L.control.scale({ metric: true, imperial: false }).addTo(map);

    mapRef.current = map;

    // Invalidate size right after mount and on the next tick (for CSS/layout)
    map.invalidateSize();
    setTimeout(() => map.invalidateSize(), 0);

    return () => {
      // Cleanup on unmount
      try {
        map.remove();
      } catch {
        /* noop */
      }
      mapRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Watch container size changes and invalidate map size
  useEffect(() => {
    if (!containerRef.current || !mapRef.current) return;
    const ro = new ResizeObserver(() => mapRef.current?.invalidateSize());
    ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);

  // Keep center/zoom in sync if the props change
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    map.setView(center, zoom, { animate: false });
  }, [center, zoom]);

  // Center marker
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    if (!showCenterMarker) {
      if (markerRef.current) {
        markerRef.current.remove();
        markerRef.current = null;
      }
      return;
    }

    if (markerRef.current) {
      markerRef.current.setLatLng(center);
    } else {
      markerRef.current = L.marker(center, { title: "City Center" }).addTo(map);
    }
  }, [center, showCenterMarker]);

  // Helper: clear any GeoJSON layers we added
  const clearGeoJson = useMemo(
    () => () => {
      geoJsonLayersRef.current.forEach((layer) => layer.remove());
      geoJsonLayersRef.current = [];
    },
    []
  );

  // Load Vienna boundary (WFS) with optional outside mask
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !loadViennaBoundary) return;

    // Reset previous overlays
    clearGeoJson();

    abortRef.current?.abort();
    const aborter = new AbortController();
    abortRef.current = aborter;

    const wfsUrl =
      "https://data.wien.gv.at/daten/geo?service=WFS&request=GetFeature&version=1.1.0&typeName=ogdwien:LANDESGRENZEOGD&srsName=EPSG:4326&outputFormat=json";

    fetch(wfsUrl, { signal: aborter.signal })
      .then((r) => {
        if (!r.ok) throw new Error(`WFS error ${r.status}`);
        return r.json();
      })
      .then((viennaGeoJson) => {
        if (!mapRef.current) return;

        const boundary = L.geoJSON(viennaGeoJson, {
          style: { color: "#111", weight: 1, fill: false },
        }).addTo(mapRef.current);
        geoJsonLayersRef.current.push(boundary);

        // Create a mask outside of the city polygon
        const layers = boundary.getLayers();
        const poly = layers[0] as any;
        const latLngs = (poly?.getLatLngs?.() || []) as LatLngExpression[][];
        if (latLngs?.[0]) {
          const mask = L.polygon([...OUTER_MASK, latLngs[0]], {
            fillColor: "#9ca3af",
            fillOpacity: 0.5,
            color: "#000",
            weight: 0,
            interactive: false,
          }).addTo(mapRef.current);
          // store mask as a GeoJSON wrapper for consistent cleanup
          // @ts-expect-error polygon is not GeoJSON, but we treat it the same for remove()
          geoJsonLayersRef.current.push(mask);
        }
      })
      .catch((e) => {
        if (e?.name !== "AbortError") {
          // eslint-disable-next-line no-console
          console.error("Error loading Vienna boundary:", e);
        }
      });

    return () => {
      aborter.abort();
    };
  }, [clearGeoJson, loadViennaBoundary]);

  // Optional overlay GeoJSON (local file)
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !overlayGeoJsonUrl) return;

    const controller = new AbortController();

    fetch(overlayGeoJsonUrl, { signal: controller.signal })
      .then((r) => {
        if (!r.ok) throw new Error(`Overlay fetch failed ${r.status}`);
        return r.json();
      })
      .then((data) => {
        if (!mapRef.current) return;
        const layer = L.geoJSON(data, {
          style: { color: "#ff6600", weight: 2, fillOpacity: 0.25 },
        }).addTo(mapRef.current);
        geoJsonLayersRef.current.push(layer);
      })
      .catch((e) => {
        if (e?.name !== "AbortError") {
          // eslint-disable-next-line no-console
          console.warn("Overlay GeoJSON load skipped:", e?.message || e);
        }
      });

    return () => controller.abort();
  }, [overlayGeoJsonUrl]);

  // Container style: give it a real size by default; allow override via props
  const mergedStyle = useMemo<React.CSSProperties>(
    () => ({
      width: "100%",
      height: "calc(100vh - 0px)", // adjust if you have a different header height
      ...style,
    }),
    [style]
  );

  return (
    <div
      ref={containerRef}
      className={`map-view leaflet-container ${className ?? ""}`}
      style={mergedStyle}
      role="region"
      aria-label="Interactive map"
    />
  );
}
