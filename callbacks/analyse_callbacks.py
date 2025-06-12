from dash import Input, Output, State, clientside_callback, no_update, html, dcc
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
        prevent_initial_call=True
    )
    def on_choosing_mode(mode):

        if mode == 'move':
            # si on entre en mode move
            # Remise à zéro des opération différentes en cours
            return "Phase 1: Click on a expi/inspi point"
        
        if mode == 'delete':
            # si on rentre en mode delete
            return "Click on the limits of the interval to delete, starting from min"
        
        if mode == 'add':
            # si mode add
            # Permet le choix d'ajouter une inspi ou une expi
            return [
                "Choose what you want to add and click where you want to add it",
                dcc.RadioItems(
                    id='to-add',
                    options=[
                        {'label': 'Inspi', 'value': 'inspi'}, 
                        {'label': 'Expi', 'value': 'expi'}
                    ],
                    value='inspi',
                    inline=True
                )
            ]
        return mode
        
    

    # Gestion des clicks sur le graph
    @app.callback(
        Output('move-store', 'data'),
        Output('delete-store', 'data'),
        Output('add-store', 'data', allow_duplicate=True),
        Output('log',   'children'),
        Input('analysis-graph', 'clickData'),
        State('cleaning-mode', 'value'),
        State('move-store',    'data'),
        State('delete-store',  'data'), 
        State('add-store', 'data'),
        prevent_initial_call=True
    )
    def handle_plot_click(clickData, mode, move_data, delete_data, add_data):
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
            add_data= build_add_response(add_data, pt)
        children = show_modifs(move_data['pairs'], delete_data['pairs'], add_data['pairs'])
        # debug
        print('\n')
        print("move data : ", move_data)
        print("delete data : ", delete_data)
        print("add data : ", add_data)
        print('\n')
        # fin debug
        return move_data, delete_data, add_data, children

    # Gestion du choix du type de point à ajouter
    @app.callback(
        Output('add-store', 'data'),
        Input('to-add', 'value'),
        State('add-store', 'data')
    )
    def choose_to_add(to_add, add_store):
        add_store["first"] = to_add
        add_store["phase"] = "start"
        add_store["point"] = None
        return add_store

    app.clientside_callback(
        """
        function(mode, moveData, deleteData, addData, fig) {
            return window.dash_clientside.clientside.toggle_traces(mode, moveData, deleteData, addData, fig);
        }
        """,
        Output('analysis-graph', 'figure'),
        Input('cleaning-mode', 'value'),
        Input('move-store', 'data'),
        Input('delete-store', 'data'),
        Input('add-store', 'data'),
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
        # log = html.Div("Phase 2 - Cliquez sur le nouveau point sur 'Respiration traitée'")
        return delete_data #, log
    
    if delete_data['phase'] == 'end':
        start = delete_data['start']
        end = {'x_end': x_clicked, 'y_end': y_clicked}
        # Vérification si start est bienavant end
        # switching des valeurs entre end et start si oui
        if start['x_start'] > end['x_end']:
            start['x_start'], end['x_end'] = end['x_end'], start['x_start']
            start['y_start'], end['y_end'] = end['y_end'], start['y_start']
        delete_data['pairs'].append({'start': start, 'end': end})

        delete_data['start'] = None
        delete_data['phase'] = 'start'

        return delete_data

def build_add_response(add_data, pt):
    """
        Gère le controle d'un joue d'expi si ajout d'inspi et inversement
        (on ne peut pas ajouter une expi sans ajouter l'inspi)
    """
    curve_idx   = pt['curveNumber']
    point_index = pt['pointIndex']
    x_clicked   = pt['x']
    y_clicked   = pt['y']
    trace_name  = pt['curveNumber']
    
    # if add_data['first'] is None:
    #     return add_data

    if add_data['phase'] == 'start':
        # premier point ajouté
        # add_data['first'] = 'expi' | 'inspi'
        add_data['point'] = {f'x_{add_data["first"]}': x_clicked,
                             f'y_{add_data["first"]}': y_clicked}
        add_data['phase'] = 'end'
        return add_data
    
    if add_data['phase'] == 'end':
        second = 'expi' if add_data['first'] == 'inspi' else 'inspi'
        second_point = {f'x_{second}': x_clicked, 
                        f'y_{second}': y_clicked}
        add_data['pairs'].append({add_data['first']: add_data['point'],
                                  second: second_point})
        # Réinitialise le storage pour repartir de zéro
        add_data['phase'] = 'start'

        return add_data


def show_modifs(move_pairs=[], delete_pairs=[], add_pairs=[]):
    children = []
    move_title = html.Div("Moves: ")
    delete_title = html.Div("Suppressions: ")
    add_title = html.Div("Additions: ")

    children.append(move_title)
    for pair in move_pairs:
        children.append(html.Div(f"{pair['old']['x_old']:.2f}s → {pair['new']['x_new']:.2f}s"))

    children.append(delete_title)
    for pair in delete_pairs:
        children.append(html.Div(f"{pair['start']['x_start']:.2f}s - {pair['end']['x_end']:.2f}s"))

    children.append(add_title)
    for pair in add_pairs:
        children.append(html.Div(f"+ inspi: {pair['inspi']['x_inspi']:.2f}s & expi: {pair['expi']['x_expi']:.2f}s"))

    return children    