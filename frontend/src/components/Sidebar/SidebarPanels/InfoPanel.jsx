import React from 'react';

function InfoPanel() {
  return (
    <section aria-labelledby="info-title" style={{ marginTop: '1rem' }}>
      <h2 id="info-title">About this Map</h2>
      <p>
        This is the base layer of Vienna. 
        Use the controls above to toggle layers and adjust settings.
      </p>
    </section>
  );
}

export default InfoPanel;
