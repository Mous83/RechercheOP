import numpy as np
def init_nord_ouest(tp):
    # On parcourt le tableau de quantité
    for i in range(tp.nb_provisions):
        for j in range(tp.nb_commandes):
            # On vérifie que la case est bien à 0 et que la somme de la ligne et celle de la colonne sont strictement inférieur respectivement au total de la ligne et à celui de la colonne
            if tp.quantites[i, j] == 0 and np.sum(tp.quantites[i]) < tp.total_provisions[i] and \
                    np.sum(tp.quantites, axis=0)[j] < tp.total_commandes[j]:
                # On donne à la case actuelle la valeur maximale qu'elle peut avoir suivant les valeurs déjà présentes dans le tableau et les totaux
                if tp.total_provisions[i] - np.sum(tp.quantites[i]) <= tp.total_commandes[j] - \
                        np.sum(tp.quantites, axis=0)[j]:
                    tp.quantites[i, j] = tp.total_provisions[i] - np.sum(tp.quantites[i])
                else:
                    tp.quantites[i, j] = tp.total_commandes[j] - np.sum(tp.quantites, axis=0)[j]