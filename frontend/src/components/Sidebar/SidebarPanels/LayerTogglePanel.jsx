import React from 'react';

function LayerTogglePanel({ cityBorderMarkerRef, setcityBorderMarkerRef }) {
  return (
    <section aria-labelledby="layer-toggle-title">
      <h2 id="layer-toggle-title">Map Layers</h2>
      <label>
        <input
          type="checkbox"
          checked={cityBorderMarkerRef}
          onChange={(e) => setcityBorderMarkerRef(e.target.checked)}
        />
        Focus city border
      </label>
      {/* Future layers can be added here */}
    </section>
  );
}

export default LayerTogglePanel;
