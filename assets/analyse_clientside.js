window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.clientside = {

  // Fonction appelée par le clientside_callback Dash
  // Inputs : cleaning_mode (string), existing figure (JS object)
  // Returns : nouvelle figure modifiée
toggle_traces: function(mode, moveData, fig) {
    // phase start si pas de phase
    var phase = moveData.phase || 'start';
    console.log("mode = ", mode);
    console.log("phase = ", phase);
    if (!fig || !fig.data) { return fig; }
    // deep clone
    const newFig = JSON.parse(JSON.stringify(fig));
    newFig.data.forEach(trace => {
      if (mode === 'move' && phase == 'start') {
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

    // Suppression des anciens points modifiés pour éviter duplication sur le plot
    newFig.data = newFig.data.filter(t => {
      return !(t.name && (t.name.startsWith('Move_old') || t.name.startsWith('Move_new')));
    });

    // Pour chaque pair old new on les places sur le plot
    (moveData.pairs||[]).forEach((pair,i) => {
      // récup couleur de la trace du point déplacé
      const orig = newFig.data[pair.old.trace];
      const color = orig && orig.line && orig.line.color
                    || (orig.marker && orig.marker.color)
                    || 'black';

      // Trace des anciens points (semi-transparents)
      newFig.data.push({
        x: [pair.old.x_old],
        y: [pair.old.y_old],
        mode: 'markers',
        name: `Move_old_${i+1}`,
        marker: { color: color, size: 10, opacity: 0.3 },
        hoverinfo: 'skip',
        showlegend: false
      });

      // Trace des nouveaux points (opaques)
      newFig.data.push({
        x: [pair.new.x_new],
        y: [pair.new.y_new],
        mode: 'markers',
        name: `Move_new_${i+1}`,
        marker: { color: color, size: 10, opacity: 1.0 },
        hoverinfo: 'x+y',
        showlegend: false
      });
    });

    return newFig;
  }

};
