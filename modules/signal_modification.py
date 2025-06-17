from config import read_data
import pandas as pd

def main_modif(data: dict) -> str:
    """
        Fonction de modification des signaux en fonction des
        actions effectués par user sur l'interface web.
        Retourne une str indiquant la validité des modifs,
        sauvegarde les modifs si tout est valide.

        data(dict) : dictionnaire de la forme
        {
            "move_data": {
                "phase": "start",
                "current_cycle": null,
                "pairs": [
                    {
                        "old": {
                            "x_old": 734.42578125,
                            "y_old": -1.4576521233678585,
                            "trace": 2,
                            "index": 183
                        },
                        "new": {
                            "x_new": 758.5625,
                            "y_new": -1.1868788107295198
                        }
                    }
                ]
            },
            "delete_data": {
                "phase": "start",
                "start": null,
                "pairs": [
                    {
                        "start": {
                            "x_start": 857.63671875,
                            "y_start": -1.1312505192944085
                        },
                        "end": {
                            "x_end": 927.8671875,
                            "y_end": -1.0740062385410378
                        }
                    }
                ]
            },
            "add_data": {
                "type": "inspi",
                "point": null,
                "pairs": [
                    {
                        "type": "inspi",
                        "x": 894.78125,
                        "y": -1.1874713211594843
                    }
                ]
            }
        }

    """
    # Log des erreurs
    error_log = []
    # Chargement des données
    modif_move = data["move_data"]["pairs"]
    modif_delete = data["delete_data"]["pairs"]
    modif_add = data["add_data"]["pairs"]
    data = read_data()

    new_cycles = data['cycles_features'].copy()

    # Correspondance id traces et expi/inspi
    trace_label = {2: 'inspi', 3: 'expi'}
    
    #####################################################################
    ## Potentiellement faire toutes les vérifs après toutes les modifs ##
    #####################################################################


    
    # Déplacement des points à déplacer
    for pair in modif_move:
        old = pair['old']
        new = pair['new']
        resp_type = trace_label[pair['old']['trace']]
        index_to_move = old['index']
        current_cycle = new_cycles.iloc[index_to_move]

        # debug
        print(current_cycle)
        # fin debug

        if resp_type == 'expi':
            first_inspi  = current_cycle['inspi_time']
            second_inspi = current_cycle['next_inspi_time']
            new_expi = new['x_new']

            # debug
            print(f"first = {first_inspi}, second = {second_inspi}, new = {new_expi}")
            # fin debug
            # Vérification que l'expi reste entre ses deux inspi
            if first_inspi < new_expi < second_inspi:
                new_cycles.at[index_to_move, "expi_time"] = new_expi
            else: 
                if first_inspi >= new_expi :
                    error = build_error('move', resp_type, first_inspi, new_expi)
                elif new_expi >= second_inspi:
                    error = build_error('move', resp_type, second_inspi, new_expi)
                error_log.append(error)
                
        if resp_type == 'inspi':
            new_inspi = new['x_new']
            # Expi avant inspi = soit l'expi d'avant soit 0
            first_expi = new_cycles.iloc[index_to_move - 1]['expi_time'] if index_to_move > 0 else 0
            second_expi = current_cycle['expi_time']
            if first_expi < new_inspi < second_expi:
                new_cycles.at[index_to_move, 'inspi_time'] = new_inspi
                # Modification du nextinspi précédent si on est pas au premier cycle
                if first_expi > 0:
                    new_cycles.at[index_to_move, 'next_inspi_time'] = new_inspi
            else:
                if first_expi >= new_inspi:
                    error = build_error('move', resp_type, first_expi, new_inspi)
                elif second_expi <= new_inspi:
                    error = build_error('move', resp_type, second_expi, new_inspi)
                error_log.append(error)
    
    if error_log == []:
        result = "No issues in the modification process"
    else:
        result = "\n".join(error_log)
    return result

            ##### A continuer, ne pas oublier les cas extremes dans inspi et expi

        # new_cycles.at[index_to_move, f'{type}_time'] = new['x_new']


def build_error(
    modif_type: str,
    current: str,
    fix: int, move: int
) -> str:
    """
        modif_type: str = 'move' | 'delete' | 'add'
        current: str = 'inspi' | 'expi' | None
        time1: int
        time2: int
    """
    if modif_type == 'move':
        opposit_type = 'expi' if current == 'inspi' else 'inspi'
        position  = 'anterior' if fix >= move else 'next'
        position2 = 'after' if position == 'next' else 'before'
        return f"{current} moved {position2} the {position} {opposit_type} ({opposit_type}: {fix:2f}, new {current}: {move:2f})"

