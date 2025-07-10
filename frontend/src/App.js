import React, { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet.heat";

export default function App() {
  const mapRef = useRef(null);

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map("map").setView([48.2082, 16.3738], 13);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution:
          '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(mapRef.current);

      // Add sample heatmap layer
      const points = [
        [48.2082, 16.3738, 0.5],
        [48.209, 16.37, 0.8],
        [48.207, 16.375, 0.3],
        [48.21, 16.38, 0.7],
      ];
      const heat = L.heatLayer(points, { radius: 25 }).addTo(mapRef.current);
    }
  }, []);

  return <div id="map" style={{ height: "100vh" }}></div>;
}
