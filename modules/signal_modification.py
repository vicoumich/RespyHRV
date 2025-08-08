from config import read_data, save_data
import pandas as pd
import numpy as np
from physio_piezo.respiration import compute_respiration_cycle_features
from physio_piezo.ecg import compute_instantaneous_rate
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
            },
            "delete_repeak": {
                "time": null,
                "peaks": [
                    {
                        "index": 230,
                        "curve": 6,
                        "x": 205.44140625,
                        "y": 1.8701320392137721
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
    modif_delete_rpeak = data["delete_rpeak"]["peaks"]
    data = read_data()

    new_cycles = data['cycles_features'].copy()
    new_rpeaks = data['ecg_peaks'].copy()
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
        #print(current_cycle)
        # fin debug

        if resp_type == 'expi':
            first_inspi  = current_cycle['inspi_time']
            second_inspi = current_cycle['next_inspi_time']
            new_expi = new['x_new']

            # debug
            # print(f"first = {first_inspi}, second = {second_inspi}, new = {new_expi}")
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
            # debug
            # print(f"first = {first_expi}, second = {new_inspi}, new = {second_expi}")
            # fin debug
            if first_expi < new_inspi < second_expi:
                new_cycles.at[index_to_move, 'inspi_time'] = new_inspi
                # Modification du nextinspi précédent si on est pas au premier cycle
                if first_expi > 0:
                    new_cycles.at[index_to_move - 1, 'next_inspi_time'] = new_inspi
                # debug
                # print("\n\ncycles courrant: ", new_cycles.iloc[index_to_move], "\ncycle précédent: ", new_cycles.iloc[index_to_move - 1])
                # fin debug
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


    # Suppression de pics-R
    # Checking que chaque suppression n'y est qu'une fois
    indexes = [peak['index'] for peak in modif_delete_rpeak]
    for peak in modif_delete_rpeak:
        try:
            # L'index ne change pas en fonction meme si on supprime des lignes
            new_rpeaks = new_rpeaks.drop(peak['index'])
        except:
            error_log.append(f"Erreur lors de la suppression du pics-R {peak}")
    new_rpeaks = new_rpeaks.reset_index(drop=True)
    instant_bpm = compute_instantaneous_rate(
        new_rpeaks, data['time_bpm'], units='bpm', interpolation_kind='linear'
    )
    data['instant_bpm'] = instant_bpm

    print(1)
    for pair in modif_delete:
        inspi = pair['inspi']
        inspi_index = inspi['index']
        expi  = pair['expi']
        expi_index = expi['index']
        arent_same_cycle = abs(inspi_index - expi_index)
        current_cycle = new_cycles.iloc[expi_index]
        print(2)
        # Si ont plus d'un index de différence 
        if arent_same_cycle > 1:
            error_log.append(f"inspi: {inspi['x']} et expi:{expi['x']} pas dans le meme cycle")
            continue
        if not(arent_same_cycle):
            print(3)
            # ordre: inspi -> expi
            if inspi_index == 0:
                # si c'est le premier cycle on supprime juste
                new_cycles = new_cycles.drop(inspi_index)
            else:
                # sinon, on supprime et on met le next inspi à la place de celui du cycle précédent
                current_next_inspi = new_cycles.at[inspi_index, "next_inspi_time"]
                # debug
                # print("current next inspi: ",current_next_inspi)
                # fin debug
                # Récupération de la position relative et non index
                pos = new_cycles.index.get_loc(expi_index)
                prev_index = new_cycles.index[pos - 1]
                new_cycles.at[prev_index, "next_inspi_time"] = current_next_inspi
                new_cycles = new_cycles.drop(expi_index)
                # debug
                # print("n-1 cycle: ",new_cycles.iloc[expi_index - 1])
                # print("n+1 cycle: ",new_cycles.iloc[expi_index + 1])
                # fin debug
        
        if arent_same_cycle:
            # ordre: expi -> inspi 
            # l'inspi est celle du cycle après l'expi
            # On remplace next_inspi par inspi actuel
            current_inspi_time = new_cycles.at[expi_index, "inspi_time"]
            # debug
            # print(f"\ncurrent_inspi_time: {current_inspi_time}")
            # print(f"\navant \n1:{new_cycles.iloc[expi_index + 1]} \n2:{new_cycles.iloc[expi_index]}")
            # fin debug
            pos = new_cycles.index.get_loc(expi_index)
            next_index = new_cycles.index[pos + 1]
            new_cycles.at[next_index, 'inspi_time'] = current_inspi_time
            new_cycles = new_cycles.drop(expi_index)
            # debug
            # print(f"\naprès \n1:{new_cycles.iloc[expi_index + 1]} \n2:{new_cycles.iloc[expi_index]}")
            # fin debug

        
    # debug
    # index = 20# modif_delete[0]['inspi']['index']
    # alpha = 3
    # [print(new_cycles.iloc[i]) for i in range(index - alpha, index + alpha)]
    # fin debug

    # Passage de données temporel à index dans le signal
    data['cycles'] = new_cycles[["inspi_time", "expi_time", "next_inspi_time"]].to_numpy()
    data['cycles'] = (data['cycles'] * data['sf']).astype(int)
    # Sauvegarde des modifications valides
    data['ecg_peaks'] = new_rpeaks

    # debug
    # print(data['cycles_features'], "\n\n", type(data['cycles_features']))
    # fin debug

    
    # debug
    # check1 = data['cycles'][:,0] <= data['cycles'][:,1]
    # check2 = data['cycles'][:,1] <= data['cycles'][:,2]
    # print("inspi <= expi", check1)
    # print("\expi <= next_inspi", check2)
    
    try:
        data['cycles_features'] = compute_respiration_cycle_features(data['clean_resp'], data['sf'], data['cycles'], 0.0)
        save_data(data)
    except Exception as e:
        print( f"Erreur inattendue dans la modification et la sauvegarde des cycles {e}")
        raise "erreur lors de la modif"
    # fin debug
    
    
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