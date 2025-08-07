from dash import Dash, Output, Input, State, dcc, no_update
from modules.bdf_reader import process_resp, extract_signals, get_cycles_features
import physio_piezo
from config import save_data

def register_callbacks(app):
    @app.callback(
        Output('main-div-filtering', 'children'),
        Input('submit-filtering', 'n_clicks'),
        State("legend-store", "data"), 
        prevent_initial_call=True
    )
    def handle_submit_frequency(n_clicks: int, data: list[str]):
        if n_clicks == None:
            return no_update

        freq = float(data[1].split(' ')[0])
        # Application du nouveau apram à la resp brut
        # Et modification des cycles en fonction du 
        # nouveau signal
        loaded = extract_signals()
        resp = loaded['resp']
        sf = loaded['sf']
        new_resp = process_resp(resp, sf, freq)
        loaded['clean_resp'] = new_resp
        loaded['cycles'] = physio_piezo.respiration.detect_cycles_by_extrema(new_resp, sf, 2.5)
        loaded['cycles_features'] = get_cycles_features(new_resp, sf, loaded['cycles'])
        save_data(loaded)
        return dcc.Location(pathname='/analyse', id='redirect-after-select')
    
    
    app.clientside_callback(
        """
        function(restyleData, figure) {
            return window.dash_clientside.filtering.updateLegendStore(
                restyleData, figure
            );
        }
        """,
        Output('legend-store', 'data'),
        Input('signal-slider-graph', 'restyleData'), 
        State('signal-slider-graph', 'figure')
    )