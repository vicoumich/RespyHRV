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
        State('delete-store', 'data'),
        prevent_initial_call=True
    )
    def on_choosing_mode(mode, move_data, delete_data):
        # debug
        print("move data : ", move_data)
        print("delete data : ", delete_data)
        # fin debug

        if mode == 'move':
            # si on entre en mode move
            # Remise à zéro des opération différentes en cours
            delete_data['phase'] = 'start'
            delete_data['start'] = None
            return "Phase 1: Click on a expi/inspi point"
        
        if mode == 'delete':
            # si on rentre en mode delete
            move_data['phase'] = 'start'
            move_data['current_cycle'] = None
            return "Click on the first point of the interval to delete"
        
        # reset si on sort du mode Move et Delete
        move_data['phase'] = 'start'
        move_data['current_cycle'] = None
        delete_data['phase'] = 'start'
        delete_data['start'] = None
        return mode
        
    

    # Gestion des clicks sur le graph
    @app.callback(
        Output('move-store', 'data'),
        Output('delete-store', 'data'),
        Output('log',   'children'),
        Input('analysis-graph', 'clickData'),
        State('cleaning-mode', 'value'),
        State('move-store',    'data'),
        State('delete-store',  'data'), 
        prevent_initial_call=True
    )
    def handle_move_click(clickData, mode, move_data, delete_data):
        # if mode != 'move' or clickData is None:
        #     return move_data, no_update

        # récup l'index de la trace et du point
        pt = clickData['points'][0]

        # Identification du mode de modif en cours
        if mode == 'move':
            move_data= build_move_response(move_data, pt)
        if mode == 'delete':
            delete_data= build_delete_response(delete_data, pt)
        if mode == 'add':
            pass
        children = show_modifs(move_data['pairs'], delete_data['pairs'])
        return move_data, delete_data, children

    app.clientside_callback(
        """
        function(mode, moveData, deleteData, fig) {
            return window.dash_clientside.clientside.toggle_traces(mode, moveData, deleteData, fig);
        }
        """,
        Output('analysis-graph', 'figure'),
        Input('cleaning-mode', 'value'),
        Input('move-store', 'data'),
        Input('delete-store', 'data'),
        State('analysis-graph', 'figure'),
        prevent_initial_call=True
    )


def build_move_response(move_data, pt):
    """
    Prend les données de move et du point cliqué et renvoie le nouvel
    état des données et l'affichage des log de modifs avec move
    """
    curve_idx   = pt['curveNumber']
    point_index = pt['pointIndex']
    x_clicked   = pt['x']
    y_clicked   = pt['y']
    trace_name  = pt['curveNumber']

    # si phase 1 : on attend un cycle (markers)
    if move_data['phase'] == 'start':
        ##################################################################
        ## Condition à trouver pour s'assurer que le point est un cycle ##
        ##################################################################
        if 0:
        ##################################################################
            return move_data #, html.Div("Erreur : sélectionnez d'abord un point cycle.")
        # on stocke le point cycle d'origine
        move_data['current_cycle'] = {
            'x_old': x_clicked,
            'y_old': y_clicked,
            'trace': trace_name,
            'index': point_index
        }
        move_data['phase'] = 'select_resp'
        return move_data # , log

    # si phase 2 : on attend un point sur la respiration traitée
    if move_data['phase'] == 'select_resp':
        #############################################################################
        ## Condition à trouver pour s'assurer que le point est sur le signal respi ##
        #############################################################################
        if 0:
        #############################################################################
        # if pt.get('curveNumber') is None or 'lines' not in pt['mode']:
            return move_data #, html.Div("Erreur : sélectionnez un point sur la courbe Respiration traitée.")
        # on a sélectionné le nouveau point
        old = move_data['current_cycle']
        new = {'x_new': x_clicked, 'y_new': y_clicked}

        move_data['pairs'].append({'old': old, 'new': new})
        # reset de la phase
        move_data['phase'] = 'start'
        move_data['current_cycle'] = None
        return move_data
    return move_data #, no_update

def build_delete_response(delete_data, pt):
    curve_idx   = pt['curveNumber']
    point_index = pt['pointIndex']
    x_clicked   = pt['x']
    y_clicked   = pt['y']
    trace_name  = pt['curveNumber']

    if delete_data['phase'] == 'start':
        start = {'x_start': x_clicked, 'y_start': y_clicked}
        delete_data['start'] = start

        delete_data['phase'] = 'end'
        log = html.Div("Phase 2 - Cliquez sur le nouveau point sur 'Respiration traitée'")
        return delete_data #, log
    
    if delete_data['phase'] == 'end':
        start = delete_data['start']
        end = {'x_end': x_clicked, 'y_end': y_clicked}
        delete_data['pairs'].append({'start': start, 'end': end})

        delete_data['start'] = None
        delete_data['phase'] = 'start'

        return delete_data

def show_modifs(move_pairs=[], delete_pairs=[], add_pairs=[]):
    children = []
    move_title = html.Div("Moves: ")
    delete_title = html.Div("Suppressions: ")
    add_title = html.Div("Additions: ")

    children.append(move_title)
    for pair in move_pairs:
        children.append(html.Div(f"Modif {pair['old']['x_old']:.2f}s → {pair['new']['x_new']:.2f}s"))

    children.append(delete_title)
    for pair in delete_pairs:
        children.append(html.Div(f"Delete {pair['start']['x_start']:.2f}s - {pair['end']['x_end']:.2f}s"))

    children.append(add_title)
    for pair in add_pairs:
        children.append()

    return children    