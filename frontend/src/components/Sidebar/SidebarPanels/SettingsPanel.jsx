import React from 'react';

function SettingsPanel({ heatRadius, setHeatRadius }) {
  return (
    <section aria-labelledby="settings-title" style={{ marginTop: '1rem' }}>
      <h2 id="settings-title">Settings</h2>
      <label htmlFor="heat-radius">
        Heatmap Radius: {heatRadius}
        <input
          id="heat-radius"
          type="range"
          min="10"
          max="50"
          value={heatRadius}
          onChange={(e) => setHeatRadius(Number(e.target.value))}
        />
      </label>
    </section>
  );
}

export default SettingsPanel;
