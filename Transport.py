import networkx as nx
import numpy as np
from prettytable import PrettyTable
from matplotlib import pyplot as plt
class ProblemeTransport:
    def __init__(self):
        self.quantites = None  # Matrice des quantites
        self.couts = None  # Matrice des couts
        self.nb_commandes = 0  # Nombre de commandes (colonnes)
        self.nb_provisions = 0  # Nombre de provisions (lignes)
        self.total_provisions = None
        self.total_commandes = None
        self.couts_potentiels = None
        self.couts_marginaux = None
        self.potentiels = []
        self.graphe = nx.DiGraph()


    def lire_fichier(self, nom_fichier):
        with open(nom_fichier, 'r') as fichier:
            premiere_ligne = fichier.readline().strip().split()
            self.nb_provisions = int(premiere_ligne[0])
            self.nb_commandes = int(premiere_ligne[1])

            # Initialisation des matrices
            self.couts = np.zeros((self.nb_provisions, self.nb_commandes), dtype=int)
            self.quantites = np.zeros((self.nb_provisions, self.nb_commandes), dtype=int)
            self.couts_marginaux = np.zeros((self.nb_provisions, self.nb_commandes))
            self.couts_potentiels = np.zeros((self.nb_provisions, self.nb_commandes))
            self.total_provisions = np.zeros(self.nb_provisions, dtype=int)
            self.total_commandes = np.zeros(self.nb_commandes, dtype=int)

            # Lire les donnees de couts et les totaux des provisions
            for i in range(self.nb_provisions):
                ligne = fichier.readline().strip().split()
                self.couts[i, :] = np.array(ligne[:self.nb_commandes], dtype=int)
                self.total_provisions[i] = int(ligne[self.nb_commandes])

            # Lire la derniere ligne pour les totaux des commandes
            self.total_commandes = np.array(fichier.readline().strip().split(), dtype=int)

    def afficher_tableau_complet(self):
        table = PrettyTable()
        noms_colonnes = ['Provision \\ Commande'] + [f'C{j + 1}' for j in range(self.nb_commandes)] + ['Total Provisions']
        table.field_names = noms_colonnes

        for i in range(self.nb_provisions):
            ligne = [f'P{i + 1}']
            for j in range(self.nb_commandes):
                ligne.append(f"{self.quantites[i, j]} ({self.couts[i, j]})")
            ligne.append(self.total_provisions[i])
            table.add_row(ligne)

        table.add_row(['-' * len(str(colonne)) for colonne in noms_colonnes])
        ligne_totaux = ['Total Commandes'] + list(self.total_commandes) + ['']
        table.add_row(ligne_totaux)
        print(table)

    def calculer_cout_total(self):
        total = 0
        for i in range(self.nb_provisions):
            for j in range(self.nb_commandes):
                total += self.quantites[i, j] * self.couts[i, j]
        return total

    def calcul_graphe(self):
        """Cree le graphe à partir des quantites actuelles."""
        self.graphe = nx.DiGraph()
        for i in range(self.nb_provisions):
            for j in range(self.nb_commandes):
                if self.quantites[i][j] != 0:
                    self.graphe.add_edge(f'P{i + 1}', f'C{j + 1}', weight=self.quantites[i][j])


    def maximiser_transport(self, cycle):
        """Maximise le transport le long du cycle detecte."""
        if not cycle:
            print("Pas de cycle detecte.")
            return

        # self.afficher_graphe()

        flux_min = 0

        est_forward = True

        for u, v, x in cycle:
            if x == 'forward':
                if flux_min == 0:
                    flux_min = self.graphe[u][v]['weight']
                elif self.graphe[u][v]['weight'] < flux_min:
                    flux_min = self.graphe[u][v]['weight']

        if(flux_min<=0):
            est_forward = False
            for u, v, x in cycle:
                if x != 'forward':
                    if flux_min == 0:
                        flux_min = self.graphe[u][v]['weight']
                    elif self.graphe[u][v]['weight'] < flux_min:
                        flux_min = self.graphe[u][v]['weight']



        # Ajuster les poids le long du cycle
        for u, v, x in cycle:
            if est_forward:
                if x == 'forward':
                    # print('plus')
                    self.graphe[u][v]['weight'] -= flux_min
                else:
                    # print('moins')
                    self.graphe[u][v]['weight'] += flux_min
            else:
                if x != 'forward':
                    # print('plus')
                    self.graphe[u][v]['weight'] -= flux_min
                else:
                    # print('moins')
                    self.graphe[u][v]['weight'] += flux_min

        # self.afficher_graphe()

        # Supprimer les aretes de poids nul
        for u, v, x in cycle:
            if (u, v) in self.graphe.edges and self.graphe[u][v]['weight'] == 0:
                self.graphe.remove_edge(u, v)


        # self.afficher_graphe()

        print("Transport maximise le long du cycle detecte.")

    def est_connexe(self):
        """Verifie si le graphe est connexe."""
        if not self.graphe.nodes:
            return False

        visites = {node: False for node in self.graphe.nodes}
        file = [next(iter(self.graphe.nodes))]
        visites[file[0]] = True

        while file:
            courant = file.pop(0)
            for voisin in nx.all_neighbors(self.graphe, courant):
                if not visites[voisin]:
                    visites[voisin] = True
                    file.append(voisin)
        return all(visites.values())

    def ajouter_arc_le_moins_cher(self):
        """Trouve et ajoute l'arc non connecté au plus faible coût."""
        meilleur_arc = None
        meilleur_cout = float('inf')
        meilleur_quantite = 0

        for i in range(self.nb_provisions):
            provision = f'P{i + 1}'
            for j in range(self.nb_commandes):
                commande = f'C{j + 1}'
                cout = self.couts[i][j]
                quantite = self.quantites[i][j]

                # Vérifier que l'arc n'est pas déjà dans le graphe et que la quantité est 0
                if (provision, commande) not in self.graphe.edges and quantite == 0:
                    self.graphe.add_edge(provision, commande, weight=quantite)


                    try:
                        nx.find_cycle(self.graphe, orientation='ignore')
                    except nx.NetworkXNoCycle:
                        # self.graphe.remove_edge(provision, commande)
                        if cout < meilleur_cout:
                            meilleur_arc = (provision, commande)
                            meilleur_cout = cout
                            meilleur_quantite = quantite

                    self.graphe.remove_edge(provision, commande)

        # Ajouter l'arc avec le coût le plus bas
        if meilleur_arc:
            provision, commande = meilleur_arc
            self.graphe.add_edge(provision, commande, weight=meilleur_quantite)
            print(f"Ajout d'un arc entre {provision} et {commande} avec un coût de {meilleur_cout}.")

        else:
            print("Aucun arc disponible pour l'ajout.")

    def connecter_graphe(self):
        """Vérifie et connecte le graphe s'il n'est pas connexe."""
        # Identifier les sous-graphes connectés
        sous_graphes = list(nx.weakly_connected_components(self.graphe))

        if len(sous_graphes) <= 1:
            print("Le graphe est déjà connexe.")
            return

        # Ajouter le meilleur arc
        self.ajouter_arc_le_moins_cher()

        print("Modification du graphe terminée.")


    def afficher_tableaux_couts(self):
        """Affiche les tableaux des coûts potentiels et marginaux."""
        # Créer un tableau pour les coûts potentiels
        tableau_potentiels = PrettyTable()
        tableau_potentiels.field_names = ['Provision \\ Commande'] + [f'C{j + 1}' for j in range(self.nb_commandes)]
        for i in range(self.nb_provisions):
            ligne = [f'P{i + 1}']
            for j in range(self.nb_commandes):
                ligne.append(f"{self.couts_potentiels[i, j]}")
            tableau_potentiels.add_row(ligne)
        print("\nTableau des coûts potentiels :")
        print(tableau_potentiels)

        # Créer un tableau pour les coûts marginaux
        tableau_marginaux = PrettyTable()
        tableau_marginaux.field_names = ['Provision \\ Commande'] + [f'C{j + 1}' for j in range(self.nb_commandes)]
        for i in range(self.nb_provisions):
            ligne = [f'P{i + 1}']
            for j in range(self.nb_commandes):
                ligne.append(f"{self.couts_marginaux[i, j]}")
            tableau_marginaux.add_row(ligne)
        print("\nTableau des coûts marginaux :")
        print(tableau_marginaux)

    def trouver_ajouter_optimiser_meilleure_arete(self):
        """Trouve la meilleure arête améliorante en utilisant les potentiels."""
        meilleure_arete = False

        for i in range(self.nb_provisions):
            for j in range(self.nb_commandes):
                if(self.couts_marginaux[i][j]<0):
                    if not meilleure_arete:
                        meilleur_pos = (i,j)
                        meilleure_arete = True
                    elif(self.couts_marginaux[i][j] < self.couts_marginaux[meilleur_pos[0], meilleur_pos[1]]):
                        meilleur_pos = (i,j)


        if meilleure_arete:
            print("On a trouvé une meilleure arête, qui est la suivante : "+f'P{meilleur_pos[0] + 1} '+f'C{meilleur_pos[1] + 1}')

            self.graphe.add_edge(f'P{meilleur_pos[0]+1}', f'C{meilleur_pos[1]+1}', weight=0)
            try:
                cycle = nx.find_cycle(self.graphe, orientation='ignore')
                print("Cycle detecte, maximisation du transport...", cycle)
                self.maximiser_transport(cycle)
            except nx.NetworkXNoCycle:
                print("Pas de cycle détecté dans le graphe.")
            return True
        return False

    def creer_matrice_potentiels(self):
        matrice_transport = np.copy(self.quantites)
        # Initialisation avec None pour indiquer les valeurs inconnues
        matrice_potentiels = np.full((self.nb_provisions + 1, self.nb_commandes + 1),
                                     None)
        # On ajoute une ligne et une colonne pour les potentiels

        # Remplir la matrice de potentiels là où le transport est non nul
        for i in range(self.nb_provisions):
            for j in range(self.nb_commandes):
                if (f"P{i+1}", f"C{j+1}") in list(self.graphe.edges()):
                    matrice_potentiels[i + 1, j + 1] = int(self.couts[i, j])

        # Définir le potentiel E(1) = 0 arbitrairement
        matrice_potentiels[1, 0] = 0  # E(1) = 0
        matrice_potentiels[0, 0] = ' / '


        # Correct way to apply conditions over specific rows or columns in a numpy array
        while check_none(matrice_potentiels):
            matrice_potentiels_last = np.copy(matrice_potentiels)
            for i in range(1, self.nb_commandes + 1):
                for j in range(1, self.nb_provisions + 1):
                    if matrice_potentiels[j, 0] is not None and matrice_potentiels[j, i] is not None:
                        matrice_potentiels[0, i] = matrice_potentiels[j, 0] - matrice_potentiels[j, i]

            for j in range(1, self.nb_provisions + 1):
                for i in range(1, self.nb_commandes + 1):
                    if matrice_potentiels[0, i] is not None and matrice_potentiels[j, i] is not None:
                        matrice_potentiels[j, 0] = matrice_potentiels[0, i] + matrice_potentiels[j, i]
            if np.array_equal(matrice_potentiels_last,matrice_potentiels):
                print("Erreur :")
                for i in range (self.nb_commandes+self.nb_provisions):
                    self.potentiels.append(None)
                return

        for i in range(1, self.nb_provisions + 1):
            for j in range(1, self.nb_commandes + 1):
                if matrice_potentiels[i, j] is None:
                    matrice_potentiels[i, j] = matrice_potentiels[i, 0] - matrice_potentiels[0, j]

        self.potentiels = np.concatenate((matrice_potentiels[1:, :1].flatten(),matrice_potentiels[:1, 1:].flatten()))
        self.couts_potentiels = matrice_potentiels[1:, 1:]
        self.couts_marginaux = self.couts - self.couts_potentiels

    def update_tableau_quantite(self):
        self.quantites = np.zeros((self.nb_provisions, self.nb_commandes), dtype=int)

        for (u,v,x) in self.graphe.edges(data='weight'):
            self.quantites[int(u[1:])-1, int(v[1:])-1] = int(x)

    def afficher_graphe(self):
        """Affiche le graphe avec les fournisseurs (P) en haut et les clients (C) en bas."""
        if not self.graphe.nodes or not self.graphe.edges:
            print("Le graphe est vide ou n'a pas encore été créé.")
            return

        # Positions manuelles des nœuds
        pos = {}
        # Séparation horizontale entre les nœuds
        x_offset = 1.0
        x_start = 0

        # Positionner les fournisseurs (P) sur une ligne en haut
        for i in range(self.nb_provisions):
            pos[f'P{i + 1}'] = (x_start + i * x_offset, 1)  # (x, y) où y = 1 pour la ligne du haut

        # Positionner les clients (C) sur une ligne en bas
        for j in range(self.nb_commandes):
            pos[f'C{j + 1}'] = (x_start + j * x_offset, 0)  # (x, y) où y = 0 pour la ligne du bas

        # Dessiner le graphe
        plt.figure(figsize=(10, 4))
        nx.draw(self.graphe, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=12,
                font_weight='bold', edge_color='gray')

        # Ajouter les labels des poids des arêtes
        labels = nx.get_edge_attributes(self.graphe, 'weight')
        nx.draw_networkx_edge_labels(self.graphe, pos, edge_labels=labels)

        plt.title("Graphe du Problème de Transport")
        plt.axis('off')  # Désactiver les axes pour une visualisation plus propre
        plt.show()

def check_none(matrice):
    nb_lignes, nb_colonnes = matrice.shape
    for i in range(1, nb_colonnes):
        for j in range(1, nb_lignes):
            if matrice[0, i] is None or matrice[j, 0] is None:
                return True
    return False

