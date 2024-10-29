import os
from Transport import *
from Balas_Hammer import *
from Nord_Ouest import *
from fonctions import *
import networkx as nx
import time

premier_test = True
continuer = True

ascii_art()

while continuer:
    # Question pour l'utilisateur
    if premier_test:
        question = "\nVoulez-vous tester un probleme de transport ? (oui/non): "
    else:
        question = "\nVoulez-vous tester un autre probleme de transport ? (oui/non): "

    # Décider si l'utilisateur souhaite tester un problème
    while True:
        reponse = input(question).lower()
        if reponse in ['oui', 'non']:
            break
        print("Entree invalide. Veuillez entrer 'oui' ou 'non'.")

    if reponse == 'non':
        break

    # Obtenir le numéro du problème
    while True:
        num_saisi = input("\nQuel probleme de transport souhaitez-vous tester ? (saisir un numero) : ")
        if num_saisi.isdigit():
            num_probleme = int(num_saisi)
            break
        print("Entree invalide. Veuillez saisir un numero.")

    nom_fichier = f"Proposition_{num_probleme}.txt"

    # Chemin du répertoire contenant le fichier
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fichiers_test_dir = os.path.join(script_dir, 'fichiers_test')
    chemin_fichier = os.path.join(fichiers_test_dir, nom_fichier)

    # Vérifier si le fichier existe
    if os.path.exists(chemin_fichier):

        print(f"\nChargement de {nom_fichier}...\n")

        # Lecture du fichier et stockage en mémoire
        ma_proposition = ProblemeTransport()
        ma_proposition.lire_fichier(chemin_fichier)
        ma_proposition.afficher_tableau_complet()

        # Choix de l'algorithme d'initialisation
        print("\nQuel algorithme souhaitez-vous utiliser pour la proposition initiale ? :\n\t1. Nord-Ouest\n\t2. Balas-Hammer\n")
        algo_choice = input("\tChoix : ")

        # Fixer la proposition initiale
        if verifier_equilibre(ma_proposition):
            if algo_choice == '1':
                print("\nInitialisation avec Nord-Ouest...")
                init_nord_ouest(ma_proposition)
            elif algo_choice == '2':
                print("\nInitialisation avec Balas-Hammer...")
                init_balas_hammer(ma_proposition)

            print("\nProposition de transport apres initialisation : ")
            ma_proposition.afficher_tableau_complet()

            # Déroulement de la méthode du marche-pied
            optimisation_complete = False
            while not optimisation_complete:
                # Calculer et afficher le coût total
                print(f"Coût total actuel : {ma_proposition.calculer_cout_total()}")

                ma_proposition.calcul_graphe()

                # Détecter un cycle
                try:
                    cycle = nx.find_cycle(ma_proposition.graphe, orientation='ignore')
                    print("Cycle detecte, maximisation du transport...", cycle)
                    ma_proposition.maximiser_transport(cycle)

                except nx.NetworkXNoCycle:
                    print("Pas de cycle détecté dans le graphe.")

                # Vérifier la connectivité et modifier le graphe si nécessaire
                if not ma_proposition.est_connexe():
                    print("\nGraphe non connexe, modification nécessaire.")
                    ma_proposition.connecter_graphe()

                # Calculer et afficher les potentiels
                ma_proposition.creer_matrice_potentiels()

                # Afficher les tables des coûts potentiels et marginaux
                ma_proposition.afficher_tableaux_couts()

                # Ajout de la meilleure arête et maximisation si coûts marginaux négatifs, sinon fin
                if not ma_proposition.trouver_ajouter_optimiser_meilleure_arete():
                    print("\nPas de coûts marginaux négatifs donc proposition optimale atteinte.")

                    ma_proposition.afficher_tableau_complet()

                    print(f"Coût total : {ma_proposition.calculer_cout_total()}")

                    # ma_proposition.afficher_graphe()

                    optimisation_complete = True
                else:
                    ma_proposition.update_tableau_quantite()

        else:
            print("\nProblème d'équilibre détecté, ne peut pas continuer.")

    else:
        print("\nLe fichier n'existe pas !")

    premier_test = False
