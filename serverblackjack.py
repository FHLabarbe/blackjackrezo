#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys import argv
from socket import gethostbyname
import asyncio
import random
from operator import countOf
import os

HOST = "10.0.0.1"
PORT_DEALER = "668"
PORT_PLAYER = "667"
tableName = str
delay = int
playerName = str
playerWriter = asyncio.StreamWriter
playerReader = asyncio.StreamReader
#players = {playerName : tableName}
players = { playerName : [playerReader,playerWriter,tableName]} # le joueur est un nom, un reader, un writer et une table
tables = {tableName : delay}
waitingTables = []

async def handle_dealer_request(reader, writer):

    writer.write(f"Bienvenue sur le serveur de blackjack.".encode() + b"\r\n") 
    #await writer.drain()

    #Récupération du nom de la table
    data = await reader.readline()
    localTableName = data[5:].decode()
    writer.write(f"Nom de la table reçu.".encode() + b"\r\n")
    #await writer.drain()
    
    #Récupération du uptime delay de la table
    data = await reader.readline()
    localDelay = data[5:].decode()
    writer.write(f"Délai reçu.".encode() + b"\r\n")
    #await writer.drain()

    #insertion de la table dans le dictionnaire. La clé est le nom de la table, et le délai associé : la valeur.
    tables[localTableName] = int(localDelay) # ajoute la table et son délai aux tableS
    waitingTables.append(localTableName) # ajoute le nom de la table aux waitingTable. Le décompte se lancera quand le premier joueur rejoindra
    writer.close()


async def handle_player_request(reader,writer):

    writer.write(f"Bienvenue sur le serveur de blackjack".encode() + b"\r\n") 
    await writer.drain()

    data = await reader.readline()
    tableName = data[5:].decode()
    for table in waitingTables:
        nb = count(tableName)
        print(nb)
        if tableName == table and (nb < 1): # on vérifie que la table existe et compte le nb de fois qu'un joueur a cette table d'associée
            print("rire")
            playerName = writer.get_extra_info('peername'[0])
            players[playerName] = [reader,writer,tableName] # ajoute le joueur ainsi que ses readers et writers dans le dictionnaire
            writer.write(f'recu, vous entrez dans la table {tableName}'.encode() + b"\r\n") # ajouter le cas ou le nom de table n'est pas bon
            await waitDelay(tableName)
            return
        elif tableName == table and (nb >= 1): # gérer l'asynchronicité pour que le joueur ne rejoigne pas si la table est fermée
            print("rire mais avec qq'1")
            playerName = writer.get_extra_info('peername'[0])
            players[playerName] = [reader,writer,tableName] # ajoute le joueur ainsi que ses readers et writers dans le dictionnaire
            print("bonjour")
            writer.write(f'recu, vous entrez dans la table {tableName}'.encode() + b"\r\n") # ajouter le cas ou le nom de table n'est pas bon
            return
    writer.write("END".encode())
    writer.close()
    return

async def blackjack_server():
    # démarre le serveur
    server_dealer = await asyncio.start_server(handle_dealer_request, HOST,PORT_DEALER)
    server_player = await asyncio.start_server(handle_player_request, HOST,PORT_PLAYER)
    async with server_dealer:
        await server_dealer.serve_forever()
    async with server_player:
        await server_player.serve_forever() 


def count(tableName):
    count = 0
    for name in players.keys(): # parcours des différents éléments du dictionnaire
        if tableName == players[name][2]: #on compare si le nom de la table est égale à la valeur de la 3ème place de la liste de chaque élément.
            count+=1
    return count

async def waitDelay(tableName):
    for i in players.keys():
        if players[i][2] == tableName:
            players[i][1].write(f'debut du temps d attente'.encode() + b"\r\n") # ajouter le cas ou le nom de table n'est pas bon
    await asyncio.sleep(int(tables[tableName]))
    for i in players.keys():
        if players[i][2] == tableName:
            players[i][1].write(f'fin du temps d attente'.encode() + b"\r\n") # ajouter le cas ou le nom de table n'est pas bon
    ind = -1
    for i in waitingTables:
        ind +=1
        if tableName == i:
            del waitingTables[ind]
    
    await partie_multi(players,tableName)



# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Initialisation du jeu de carte
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

def creer_deck():
    deck = []
    couleurs = ["♦","♥","♠","♣"]

    for i in range(0,4):
        for j in range(0,13):
            num = j%14
            deck.append([j+1,couleurs[i]])
    return deck
    
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Mélanger le deck
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

def melanger_deck(deck):
    random.shuffle(deck)
    return deck

# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Calcul du score
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

def score(main):
    s = 0
    for i in range(len(main)):
        print(main[i][0])
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
# Fonction qui demande au joueurs leurs choix
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

async def ask_joueurs(reader, writer):
    message = ".\n"
    writer.write(message.encode()) # je crois que c'est ce qu'il faut envoyer pour activer la sequence de choix de carte (joueur.py ligne 33)
    #Récupération du choix
    data = await reader.readline()
    dec_data = data.decode()
    localChoix = dec_data[5] # on prend le 6e caractère ("MORE 1" on prend le "1")
    writer.write(f"Choix enregistré".encode() + b"\r\n")
    #await writer.drain()

    return localChoix

def isActivePlayers(joueurs):
    res = False
    for i in joueurs:
        res = res or i
    
    return res

def affiche_mains(main,writer,score): # cette fonction affiche les cartes et le score de la main donnée en paramètre au joueur dont le writer est en paramètre
    writer.write((f"Vos cartes sont : {main}".encode() + b"\r\n"))
    writer.write((f"Votre score est de : {score}".encode() + b"\r\n"))

def quiGagne(scoreServeur,scoreJoueur,writer): #fonction qui compare les scores et qui annonce les résultat d'une partie + met fin a la communication (rajouter le fait de pas contacter ceux qui ont deja perdu)
    if (scoreServeur > 21 and scoreJoueur > 21) or ((scoreServeur > scoreJoueur or scoreJoueur>21) and scoreServeur<22):
        writer.write((f"vous perdez".encode() + b"\r\n"))

    elif scoreServeur == scoreJoueur :
        writer.write((f"égalité".encode() + b"\r\n"))

    elif (scoreServeur < scoreJoueur or scoreServeur>21) and scoreJoueur<22:
        writer.write((f"vous gagner".encode() + b"\r\n"))

    writer.write((f"END".encode() + b"\r\n"))


# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Fonction qui gère tout
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

async def partie_multi(joueurs,nomTable):

    n = 0 
    readerPartie = []
    writerPartie = []

    for i in joueurs.keys():
        if joueurs[i][2] == nomTable:
            readerPartie.append(joueurs[i][0]) #on stocke les reader
            writerPartie.append(joueurs[i][1]) #et les writer (pour que ce soit plus facile a utiliser plus tard)
            n+=1 #on compte aussi le nombre de joueurs

    mains = [[]] * (n+1) # liste qui garde les mains des joueurs
    joueurs_actifs = [True] * n # sert de "compteur de joueur(s) actif(s)"
    #choix = [] * n # pour sauvegarder les choix de chacun
    scores = [0] * (n+1) # pour sauvegarder les scores des joueurs

    deck = melanger_deck(creer_deck()) # on creer le deck et on le melange

    # le serveur pioche une carte
    mains[0] = [deck[-1]]
    deck.pop()

    # on distribue deux cartes par joueur
    for i in range(1,len(mains)):
        for j in range(2):
            mains[i].append(deck[-1])
            deck.pop()

    # on calcule les scores
    for i in range(0,n+1):
        scores[i] = score(mains[i])

    print(scores)
    
    # on va envoyer a chaque joueur la carte du croupier + on affiche la main du joueur en question
    for i in range(0,n):
        writerPartie[i].write((f"La carte du serveur est : {mains[0][0]}".encode() + b"\r\n"))
        await writerPartie[i].drain()

            
    while(isActivePlayers(joueurs_actifs)):
      
        for i in range(0,n):
            # on calcule le score du joueur pour savoir si il peut jouer ou pas
            affiche_mains(mains[i+1],writerPartie[i],scores[i+1])# ne pas oublier les autres parametres d'appel
            if joueurs_actifs[i]:

                choixJoueur = await ask_joueurs(readerPartie[i],writerPartie[i])
                print(str(choixJoueur) + " ouga bouga la saga des singe oui la")

                if choixJoueur == "1": # si c'est 1 on pioche
                    mains[i+1].append(deck[-1])
                    deck.pop()
                    scores[i+1]=score(mains[i+1])
                    nouv_carte = mains[i+1][-1]
                    writerPartie[i].write(f'Vous piochez la carte : {nouv_carte}'.encode() + b"\r\n")

                    if scores[i+1]>21: #on regarde tout de suite apres avoir pioché si le score est > 21 comme ca on peux deja virer le joueur
                        writerPartie[i].write(f'Vous avez dépasser 21, vous avez perdu'.encode() + b"\r\n")
                        affiche_mains(mains[i+1],writerPartie[i],scores[i+1])
                        joueurs_actifs[i] = False
                else:
                    joueurs_actifs[i] = False

    while(scores[0]<17) : # le croupier fini de jouer si besoin (- de 17)
        mains[0].append(deck[-1])
        deck.pop()
        scores[0] = score(mains[0])

    writerPartie[i].write((f"La main du serveur est : {mains[0]}".encode() + b"\r\n"))
    writerPartie[i].write((f"Le score du serveur est : {scores[0]}".encode() + b"\r\n"))
    for i in range(0,n):
        affiche_mains(mains[i+1],writerPartie[i],scores[i+1])
        quiGagne(scores[0],scores[i+1],writerPartie[i])
    
    tables.pop(nomTable)

    

if __name__ == '__main__':
    asyncio.run(blackjack_server())