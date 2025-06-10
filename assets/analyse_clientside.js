window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.clientside = {

  // Fonction appelée par le clientside_callback Dash
  // Inputs : cleaning_mode (string), existing figure (JS object)
  // Returns : nouvelle figure modifiée
toggle_traces: function(mode, fig) {
    if (!fig || !fig.data) { return fig; }
    // deep clone
    const newFig = JSON.parse(JSON.stringify(fig));
    newFig.data.forEach(trace => {
      if (mode === 'move') {
        // la ligne principale ne répond pas au hover
        if (trace.mode && trace.mode.includes('lines')) {
          trace.hoverinfo = 'skip';
        }
        // les points cycles répondent
        if (trace.mode && trace.mode.includes('markers')) {
          trace.hoverinfo = 'x+y';
          trace.hoveron   = 'points';
        }
      } else {
        // mode normal : tout hover
        trace.hoverinfo = 'all';
        delete trace.hoveron;
      }
    });
    return newFig;
  }

};
