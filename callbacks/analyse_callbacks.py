from dash import Input, Output, State, clientside_callback, no_update, html
import plotly.graph_objects as go
from config import analysis_path, useful_channel_asr
import os

def register_callbacks(app):
    # Gestion du bouton de retour des changements des cycles
    @app.callback(
        Output('channels-asr', 'children'),
        Input('btn-submit', 'n_clicks'),
        prevent_initial_call=True
    )
    def on_validate_cycles(n_clicks):
        print("clicked")

    # Gestion des modes de modification des cycles
    # move, delete, add
    @app.callback(
        Output('mode-state', 'children'),
        Input('cleaning-mode', 'value'),
        State('move-store', 'data'),
        prevent_initial_call=True
    )
    def on_choosing_mode(mode, move_data):
        if mode != 'move':
            # reset si on sort du mode Move
            move_data['phase'] = 'start'
            move_data['current_cycle'] = None
            return mode
        # si on entre en mode move
        return "Phase 1: Click on a expi/inspi point"
    

    # Gestion des clicks sur le graph
    @app.callback(
        Output('move-store', 'data'),
        Output('move-log',   'children'),
        Input('analysis-graph', 'clickData'),
        State('cleaning-mode', 'value'),
        State('move-store',    'data'),
        prevent_initial_call=True
    )
    def handle_move_click(clickData, mode, move_data):
        # si on n’est pas en mode move, on ne fait rien
        if mode != 'move' or clickData is None:
            return move_data, no_update

        # récup l'index de la trace et du point
        pt = clickData['points'][0]
        curve_idx   = pt['curveNumber']
        point_index = pt['pointIndex']
        x_clicked   = pt['x']
        y_clicked   = pt['y']
        trace_name  = pt['curveNumber']

        # debug
        print("\n\n Point cliqué :\n")
        print(pt)
        # fin debug 

        # si phase 1 : on attend un cycle (markers)
        if move_data['phase'] == 'start':
            ##################################################################
            ## Condition à trouver pour s'assurer que le point est un cycle ##
            ##################################################################
            if 0:
            ##################################################################
                return move_data, html.Div("Erreur : sélectionnez d’abord un point cycle.")
            # on stocke le point cycle d’origine
            move_data['current_cycle'] = {
                'x_old': x_clicked,
                'y_old': y_clicked,
                'trace': trace_name,
                'index': point_index
            }
            move_data['phase'] = 'select_resp'
            # on demande ensuite la phase 2
            log = html.Div("Phase 2 – Cliquez sur le nouveau point sur ‘Respiration traitée’")

            # debug
            print("\n\nStorage local:\n")
            print(move_data)
            # fin debug 

            return move_data, log

        # si phase 2 : on attend un point sur la respiration traitée
        if move_data['phase'] == 'select_resp':
            #############################################################################
            ## Condition à trouver pour s'assurer que le point est sur le signal respi ##
            #############################################################################
            if 0:
            #############################################################################
            # if pt.get('curveNumber') is None or 'lines' not in pt['mode']:
                return move_data, html.Div("Erreur : sélectionnez un point sur la courbe Respiration traitée.")
            # on a sélectionné le nouveau point
            old = move_data['current_cycle']
            new = {'x_new': x_clicked, 'y_new': y_clicked}
            # ici tu peux ajouter ta vérif de validité avant d’accepter
            # par exemple : if abs(new['x_new']-old['x_old'])> seuil: rejet…

            # on ajoute à la liste des paires
            move_data['pairs'].append({'old': old, 'new': new})
            # reset de la phase
            move_data['phase'] = 'start'
            move_data['current_cycle'] = None

            # rebuild de la liste à afficher
            children = []
            for i, pair in enumerate(move_data['pairs'], start=1):
                children.append(html.Div(f"{i}. cycle @ {pair['old']['x_old']:.2f}s → {pair['new']['x_new']:.2f}s"))

            return move_data, children

        # Sinon on ne change rien
        return move_data, no_update


    app.clientside_callback(
        """
        function(mode, moveData, fig) {
            return window.dash_clientside.clientside.toggle_traces(mode, moveData, fig);
        }
        """,
        Output('analysis-graph', 'figure'),
        Input('cleaning-mode', 'value'),
        Input('move-store', 'data'),
        State('analysis-graph', 'figure'),
        prevent_initial_call=True
    )