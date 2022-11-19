import random
import os

# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Initialisation du jeu de carte
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
def creer_deck():
    deck =[]
    couleurs = ["♦","♥","♠","♣"]

    for i in range(0,4):
        for j in range(0,13):
            num = j%14
            deck.append([j+1,couleurs[i]])
    return deck
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Mélangation du deck
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

def melanger_deck(deck):
    random.shuffle(deck)
    return deck

# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Affichage des cartes
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

def haut_carte():
    print("----------")
    print("|        |")
    print("|        |")

def bas_carte():
    print("|        |")
    print("|        |")
    print("----------")

def affiche_carte(carte):
    tetes = ["V","D","R"]
    haut_carte()
    if carte[0]==10:
        print("|  "+str(carte[0])+" "+str(carte[1])+"  |")
    elif carte[0]>10:
        print("|  "+str(tetes[carte[0]-11])+"  "+str(carte[1])+"  |")
    else :
        print("|  "+str(carte[0])+"  "+str(carte[1])+"  |")
    bas_carte()

def face_cache():
    print("----------")
    print("|/\/\/\/\|")
    print("|\/\/\/\/|")
    print("|/\/\/\/\|")
    print("|\/\/\/\/|")
    print("|/\/\/\/\|")
    print("----------")

# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Fonctions d'affichage
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

def affiche_main(main,aff):
    if(aff):
        print("Votre main :")
    for i in range(len(main)):
        affiche_carte(main[i])

def affiche_croupier(main_croupier):
    l = len(main_croupier)
    affiche_carte(main_croupier[0])
    face_cache()
    if(l>2):
        for i in range(2,l):
            affiche_carte(main_croupier[i])

# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Manipulation des cartes
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

def distribution(deck):
    main = []
    for i in range(2):
        main.append(deck[-1])
        deck.pop()
    return main

def pioche(deck,main):
    main.append(deck[-1])
    deck.pop()
    return main

# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Calcul du score
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

def score(main):
    s = 0
    for i in range(len(main)):
        if(main[i][0]>9):
            s+=10
        elif(main[i][0]==1):
            if(s+11>21):
                s+=1
            else:
                s+=11
        else:
            s += main[i][0]
    return s

# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Gestion du tour du croupier
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
def tour_croupier(main_croupier):
    if(score(main_croupier)<17):
        print("Le croupier pioche.\n")
        pioche(deck,main_croupier)
    else:
        print("Le croupier ne pioche pas.\n")

# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Fonction qui gère tout
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

def partie(deck,main,croupier):
    main = distribution(deck)
    croupier = distribution(deck)

    continu = True

    print("Votre main initiale :")
    affiche_main(main,False)

    if (score(main)==21):
        print("Vous gagnez avec un BlackJack !")
    else:

        print("Main initiale du croupier :")
        affiche_croupier(croupier)

        while((score(main)<22)and(continu)):
            
            choix = input("Quel est votre choix ?\ns pour voir votre main actuelle,\np pour piocher,\nm pour afficher la main du croupier,\nv pour voir\n")
            match choix:
                case "s":
                    affiche_main(main,True)
                    print("Votre score actuel est : "+str(score(main))+"\n")
                case "p":
                    main = pioche(deck,main)
                    affiche_main(main,True)
                    tour_croupier(croupier)
                    if(score(croupier)>21):
                        continu = False
                case "m":
                    print("main du croupier :")
                    affiche_croupier(croupier)
                case "v":
                    tour_croupier(croupier)
                    continu = False
                case _:
                    print("Choix incorrect.\n")
            

        sc = score(croupier)
        sj = score(main)

        print("Main du croupier :")
        affiche_main(croupier,False)
        print("Score final du croupier : "+str(sc)+"\n")
        print("Votre main finale :")
        affiche_main(main,False)
        print("Votre score final: "+str(sj)+"\n")

        if (sj>21):
            if(sc>21):
                print("Égalité.")
            else :
                print("Votre score dépasse 21, vous perdez.")
        else:
            if(sj>sc or sc>21):
                if(sj==21):
                    print("Vous gagnez avec un BlackJack !")
                else :
                    print("Vous gagnez !")
            elif(sj==sc):
                print("Égalité.")    
            else:
                print("Vous avez perdu.")