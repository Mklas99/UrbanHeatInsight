import React from 'react';

function LayerTogglePanel({ cityCenterMarkerRef, setcityCenterMarkerRef }) {
  return (
    <section aria-labelledby="layer-toggle-title">
      <h2 id="layer-toggle-title">Map Layers</h2>
      <label>
        <input
          type="checkbox"
          checked={cityCenterMarkerRef}
          onChange={(e) => setcityCenterMarkerRef(e.target.checked)}
        />
        Show Heatmap
      </label>
      {/* Future layers can be added here */}
    </section>
  );
}

export default LayerTogglePanel;
