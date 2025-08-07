window.dash_clientside = window.dash_clientside || {};

window.dash_clientside.filtering = {
  updateLegendStore: function(restyleData, figure) {
    // Si pas de restyleData, ne rien faire
    if (!restyleData) {
      return window.dash_clientside.no_update;
    }
    // figure.data contient toutes les traces
    var names = figure.data
      .filter(trace => trace.visible)
      .map(trace => trace.name);
    console.log('okkkkk');
    return names;
  }
};