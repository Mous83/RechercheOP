import networkx as nx
from Transport import *
from Balas_Hammer import *

# Creation de l'objet
mon_tableau = ProblemeTransport()

# Lecture et stockage des infos du fichier texte dans la memoire
mon_tableau.lire_fichier('test2.txt')

init_balas_hammer(mon_tableau)

mon_tableau.calcul_graphe()

# Find and print the cycle in the graph
try:
    cycle = nx.find_cycle(mon_tableau.graphe, orientation='original')
    print("Cycle detected:", cycle)
except nx.NetworkXNoCycle:
    print("No cycle detected in the graph.")

# print("Matrice des couts unitaires")
# print(mon_tableau.costs)
#
# print("\nMatrice des quantites")
# print(mon_tableau.quantities)
#
# print("\nNombre de commandes")
# print(mon_tableau.num_orders)
#
#
# print("\nNombre de provision")
# print(mon_tableau.num_provisions)
#
# print("\nTotal des provisions (par ligne)")
# print(mon_tableau.total_provisions)
#
# print("\nTotal des commandes (par colonne)")
# print(mon_tableau.total_orders)