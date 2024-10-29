import numpy as np
import time
import random
def calculer_penalites(tp):
    """
    Calcule les pénalités pour chaque ligne et colonne en fonction de la différence entre les deux plus petits coûts disponibles.
    Stocke ces pénalités avec l'indice de la case à coût minimal et la capacité de cette case.
    """
    penalites_lignes = []
    penalites_colonnes = []

    # Calcul des pénalités pour chaque ligne
    for i in range(tp.nb_provisions):
        # Filtrage des colonnes où une allocation supplémentaire est possible
        if np.sum(tp.quantites[i, :]) < tp.total_provisions[i]:
            couts_valides = [(j, c) for j, c in enumerate(tp.couts[i, :]) if tp.total_commandes[j] > np.sum(tp.quantites[:, j])]
            if len(couts_valides) > 1:
                sorted_couts = sorted(couts_valides, key=lambda x: x[1])
                index_min_cost = sorted_couts[0][0]
                capacite_case = min(tp.total_provisions[i] - np.sum(tp.quantites[i, :]), tp.total_commandes[index_min_cost] - np.sum(tp.quantites[:, index_min_cost]))
                penalite = sorted_couts[1][1] - sorted_couts[0][1]
                penalites_lignes.append((i, penalite, capacite_case, index_min_cost))

    # Calcul des pénalités pour chaque colonne
    for j in range(tp.nb_commandes):
        if np.sum(tp.quantites[:, j]) < tp.total_commandes[j]:
            couts_valides = [(i, c) for i, c in enumerate(tp.couts[:, j]) if tp.total_provisions[i] > np.sum(tp.quantites[i, :])]
            if len(couts_valides) > 1:
                sorted_couts = sorted(couts_valides, key=lambda x: x[1])
                index_min_cost = sorted_couts[0][0]
                capacite_case = min(tp.total_commandes[j] - np.sum(tp.quantites[:, j]), tp.total_provisions[index_min_cost] - np.sum(tp.quantites[index_min_cost, :]))
                penalite = sorted_couts[1][1] - sorted_couts[0][1]
                penalites_colonnes.append((j, penalite, capacite_case, index_min_cost))

    return penalites_lignes, penalites_colonnes

def init_balas_hammer(tp):
    """
    Exécute l'algorithme de Balas-Hammer, sélectionnant les cases pour l'allocation basée sur les pénalités les plus élevées,
    jusqu'à ce que tous les totaux requis soient atteints ou qu'il n'y ait plus de pénalités disponibles.
    """

    cpt = 0 # Compteur d'itération

    while not (np.all(tp.quantites.sum(axis=1) == tp.total_provisions) and np.all(tp.quantites.sum(axis=0) == tp.total_commandes)):

        penalites_lignes, penalites_colonnes = calculer_penalites(tp)

        cpt+=1

        # Vérification si des options de pénalité sont disponibles
        if not penalites_lignes and not penalites_colonnes:
            # Ajustement final si aucune pénalité n'est calculable
            # print("Aucune option de pénalité disponible, ajustement des dernières cases pour respecter les totaux.")
            ajuster_dernieres_cases(tp)
            break

        # Sélection du meilleur candidat pour l'allocation basée sur la pénalité la plus élevée
        meilleur_candidat, est_ligne = selectionner_meilleur_candidat(penalites_lignes, penalites_colonnes)

        print(f"\nItération {cpt}")

        if(est_ligne):
            print(f"\tLa ligne {meilleur_candidat[0]+1} est celle de penalite maximale avec {meilleur_candidat[1]} ")
        else:
            print(f"\tLa colonne {meilleur_candidat[0]+1} est celle de penalite maximale avec {meilleur_candidat[1]} ")

        if meilleur_candidat:
            # Calcul de l'allocation optimale pour le meilleur candidat
            ligne, colonne, quantite = calculer_allocation(tp, meilleur_candidat, est_ligne)
            # print(f"Décision d'allocation basée sur la pénalité maximale de {'ligne' if est_ligne else 'colonne'} {ligne if est_ligne else colonne} avec une pénalité de {meilleur_candidat[1]} et une capacité de {meilleur_candidat[2]}")
            # Allocation de la quantité calculée à la case spécifiée
            allouer_case(tp, ligne, colonne, quantite)
        else:
            print("Aucune allocation possible selon les critères actuels.")

def calculer_allocation(tp, candidat, est_ligne):
    ligne, colonne = candidat[0], candidat[3]
    if est_ligne:
        quantite_possible = min(tp.total_provisions[ligne] - np.sum(tp.quantites[ligne, :]), tp.total_commandes[colonne] - np.sum(tp.quantites[:, colonne]))
    else:
        ligne, colonne = colonne, ligne  # Inverser pour la logique de colonne
        quantite_possible = min(tp.total_commandes[colonne] - np.sum(tp.quantites[:, colonne]), tp.total_provisions[ligne] - np.sum(tp.quantites[ligne, :]))
    return ligne, colonne, quantite_possible

def selectionner_meilleur_candidat(penalites_lignes, penalites_colonnes):
    max_penalite_ligne = max((x[1] for x in penalites_lignes), default=-1)
    max_penalite_colonne = max((x[1] for x in penalites_colonnes), default=-1)
    if max_penalite_ligne == max_penalite_colonne:
        # print("Égalité des pénalités maximales entre les lignes et les colonnes.")
        pass
    if max_penalite_ligne >= max_penalite_colonne:
        # print(f"Choix d'une ligne sur base de la pénalité la plus élevée de {max_penalite_ligne}.")
        return max((x for x in penalites_lignes if x[1] == max_penalite_ligne), key=lambda x: x[2], default=None), True
    else:
        # print(f"Choix d'une colonne sur base de la pénalité la plus élevée de {max_penalite_colonne}.")
        return max((x for x in penalites_colonnes if x[1] == max_penalite_colonne), key=lambda x: x[2], default=None), False

def allouer_case(tp, ligne, colonne, quantite):
    tp.quantites[ligne, colonne] += quantite
    #print(f"Alloué {quantite} unités à la position ({ligne}, {colonne}).")

def ajuster_dernieres_cases(tp):
    """
    Ajuste les dernières cases non attribuées pour s'assurer que les totaux des lignes et des colonnes correspondent aux totaux requis.
    Cela est nécessaire lorsque les pénalités ne peuvent plus guider l'allocation.
    """
    for i in range(tp.nb_provisions):
        total_actuel_ligne = np.sum(tp.quantites[i, :])
        if total_actuel_ligne < tp.total_provisions[i]:
            difference = tp.total_provisions[i] - total_actuel_ligne
            for j in range(tp.nb_commandes):
                possible_addition = min(difference, tp.total_commandes[j] - np.sum(tp.quantites[:, j]))
                if possible_addition > 0:
                    tp.quantites[i, j] += possible_addition
                    difference -= possible_addition
                if difference <= 0:
                    break

    for j in range(tp.nb_commandes):
        total_actuel_colonne = np.sum(tp.quantites[:, j])
        if total_actuel_colonne < tp.total_commandes[j]:
            difference = tp.total_orders[j] - total_actuel_colonne
            for i in range(tp.num_provisions):
                possible_addition = min(difference, tp.total_provisions[i] - np.sum(tp.quantities[i, :]))
                if possible_addition > 0:
                    tp.quantities[i, j] += possible_addition
                    difference -= possible_addition
                if difference <= 0:
                    break

def verifier_equilibre(tp):
    """
    Vérifie si le problème de transport est équilibré.
    """
    total_provisions = np.sum(tp.total_provisions)
    total_commandes = np.sum(tp.total_commandes)
    if total_provisions == total_commandes:
        print("\nLe problème est équilibré.")
        return True
    else:
        print("\nLe problème n'est pas équilibré. Total des provisions:", total_provisions, "vs Total des commandes:",
              total_commandes)
        return False
