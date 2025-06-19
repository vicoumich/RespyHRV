from config import read_data
import pandas as pd
import numpy as np

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
                "phase": "start",
                "first": "inspi",
                "point": {
                    "x_inspi": 78.140625,
                    "y_inspi": -1.1043318631349957
                },
                "pairs": [
                    {
                        "inspi": {
                            "x_inspi": 78.140625,
                            "y_inspi": -1.1043318631349957
                        },
                        "expi": {
                            "x_expi": 78.86328125,
                            "y_expi": -1.307471442846559
                        }
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
    opposit_resp = {'inspi': 'expi', 'expi': 'inspi'}
    
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


    # Ajout des points à ajouter
    # Précondition: avoir couples inspi expi
    for pair in modif_add:
        inspi_time = pair['inspi']['x_inspi']
        expi_time  = pair['expi']['x_expi']
        # Premier à arriver dans le temps
        # first_time, first_label = (inspi_time, 'inspi') if inspi_time < expi_time else (expi_time, 'expi')
        if inspi_time < expi_time:
            first_time, first_label = inspi_time, 'inspi'
        else : first_time, first_label = expi_time, 'expi'
        # Identification du cycles où on insère les points
        index = np.searchsorted(new_cycles['inspi_time'].values, first_time, side='left') - 1
        cycle = new_cycles.iloc[index]
        # Soit avant soit après expi
        
        # Entre inspi_time et expi_time
        if first_time < cycle['expi_time']:
            # Si on a inspi-inspi au lieu de inspi-expi
            if first_label == 'inspi':
                error = build_error('add', first_label, 
                                    cycle['inspi_time'], inspi_time, expi_time)
                error_log.append(error)
            # Si cycle ajouté n'est pas compris dans le cycle existant

            elif inspi_time >= cycle['expi_time']:
                error = build_error('add', first_label, 
                                    expi_time, cycle['expi_time'], inspi_time)
                error_log.append(error)
            # on a bien inspi-expi-inspi-expi 
            else:
                old_expi  = cycle['expi_time']
                old_next_inspi = cycle['next_inspi_time']
                # Mise à jour du cycle courrant
                new_cycles.at[index, 'expi_time'] = expi_time
                new_cycles.at[index, 'next_inspi_time'] = inspi_time
                # Création de la nouvelle ligne
                new_row = pd.DataFrame([{col: np.nan for col in new_cycles.columns}])
                new_row.at[0, 'inspi_time'] = inspi_time
                new_row.at[0, 'expi_time'] = old_expi
                new_row.at[0, 'next_inspi_time'] = old_next_inspi
                # Insertion cohérente dans les cycles
                new_cycles = _insert_row(new_cycles, new_row, index)

        else:
            # on a expi-expi au lieu de expi-inspi
            if first_label == 'expi':
                error = build_error('add', first_label, 
                                    cycle['expi_time'], expi_time, inspi_time)
                error_log.append(error)
            # SI le newcycle n'est pas compris dans le courrant
            # pas besoin de vérifier pour l'inspi car elle
            # est logiquement avant

            elif expi_time >= cycle['next_inspi_time']:
                error = build_error('add', opposit_resp[first_label], 
                                    inspi_time, cycle['next_inspi_time'], expi_time)
                error_log.append(error)
            # on a expi-inspi-expi-next_inspi
            else:
                old_next_inspi = cycle['next_inspi_time']
                # Maj du cycle courant 
                new_cycles.at[index, 'next_inspi_time'] = inspi_time
                # Nouvelle ligne
                new_row = pd.DataFrame([{col: np.nan for col in new_cycles.columns}])
                new_row.at[0, 'inspi_time'] = inspi_time
                new_row.at[0, 'expi_time']  = expi_time
                new_row.at[0, 'next_inspi_time'] = old_next_inspi
                new_cycles = _insert_row(new_cycles, new_row, index)

        
    
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
    time1: int, time2: int, time3=None
) -> str:
    """
        modif_type: str = 'move' | 'delete' | 'add'
        current: str = 'inspi' | 'expi' | None
        time1: int
        time2: int
        time3: int (optionel)
    """
    opposit_type = 'expi' if current == 'inspi' else 'inspi'
    if modif_type == 'move':
        position  = 'anterior' if time1 >= time2 else 'next'
        position2 = 'after' if position == 'next' else 'before'
        return f"{current} moved {position2} the {position} {opposit_type} ({opposit_type}: {time1:2f}, new {current}: {time2:2f})"
    if modif_type == 'add':
        return f"{current} added right after {current} without {opposit_type} between ({current}: {time1:2f}s, {current}: {time2:2f}, {opposit_type}: {time3:2f}s)"


def _insert_row(df: pd.DataFrame, row: pd.DataFrame, index: int) -> None:
    index += 1
    df_top = df.iloc[:index]
    df_bottom = df.iloc[index:]
    df = pd.concat([df_top, row, df_bottom], ignore_index=True)
    return df