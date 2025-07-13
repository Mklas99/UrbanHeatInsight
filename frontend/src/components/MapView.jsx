import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import './MapView.css';

function MapView({ heatRadius }) {
  const mapRef = useRef(null);
  const cityCenterMarkerRef = useRef(null);

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map('map', {
        center: [48.2082, 16.3738], // Vienna center
        zoom: 13,
        minZoom: 11,
        maxZoom: 18,
        maxBounds: [
          [47.9, 16.0],  // SW boundary
          [48.5, 16.7]   // NE boundary
        ],
        maxBoundsViscosity: 1.0
      });

      // Add a basemap layer (OpenStreetMap)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(mapRef.current);

      // Load Vienna's city boundary GeoJSON
      fetch("https://data.wien.gv.at/daten/geo?service=WFS&request=GetFeature&version=1.1.0&typeName=ogdwien:LANDESGRENZEOGD&srsName=EPSG:4326&outputFormat=json")
        .then(res => res.json())
        .then(viennaGeoJson => {
          // Display Vienna's boundary
          const viennaBoundary = L.geoJSON(viennaGeoJson, {
            style: {
              color: '#000',
              weight: 1,
              fill: false
            }
          }).addTo(mapRef.current);

          // Define a smaller bounding box around Vienna
          const outer = [
            [
              [47.5, 15.5], // SW corner
              [47.5, 17.0], // SE corner
              [48.7, 17.0], // NE corner
              [48.7, 15.5], // NW corner
              [47.5, 15.5]  // Close the polygon
            ]
          ];

          // Extract the boundary polygon (1st feature assumed to be Vienna)
          const viennaPolygon = viennaBoundary.getLayers()[0].getLatLngs();

          // Apply a "hole" over Vienna, to highlight it
          L.polygon([...outer, viennaPolygon[0]], {
            fillColor: '#888',
            fillOpacity: 0.6,
            color: '#000',
            weight: 0,
            interactive: false
          }).addTo(mapRef.current);
        });
    }
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;

    // Remove existing city center marker if any
    if (cityCenterMarkerRef.current) {
      cityCenterMarkerRef.current.remove();
      cityCenterMarkerRef.current = null;
    }

    // Add a marker for the city center
    const cityCenter = [48.2082, 16.3738]; // Vienna center coordinates
    cityCenterMarkerRef.current = L.marker(cityCenter, {
      title: 'Vienna City Center'
    }).addTo(mapRef.current);
  }, []);

  return <div id="map" className="map-view" aria-label="Map with City Center Pin" />;
}

export default MapView;
