#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys import argv
from socket import gethostbyname
import asyncio
import random
from operator import countOf
import os

HOST = "10.0.1.1"
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
    await writer.drain()

    #Récupération du nom de la table
    data = await reader.readline()
    localTableName = data[5:].decode()
    writer.write(f"Nom de la table reçu.".encode() + b"\r\n")
    await writer.drain()
    
    #Récupération du uptime delay de la table
    data = await reader.readline()
    localDelay = data[5:].decode()
    writer.write(f"Délai reçu.".encode() + b"\r\n")
    await writer.drain()

    #insertion de la table dans le dictionnaire. La clé est le nom de la table, et le délai associé : la valeur.
    tables[localTableName] = int(localDelay) # ajoute la table et son délai aux tableS
    waitingTables.append(localTableName) # ajoute le nom de la table aux waitingTable. Le décompte se lancera quand le premier joueur rejoindra
    writer.close()


async def handle_player_request(reader,writer):

    writer.write(f"Bienvenue sur le serveur de blackjack.".encode() + b"\r\n") 
    await writer.drain()

    tableName = await reader.readline() ## Il faut 2 cas, celui où le joueur est le premier arrivé, et celui il y a déjà du monde
    for table in waitingTables:
        if tableName == table and (countOf(players.values(), tableName) < 1): # on vérifie que la table existe et compte le nb de fois qu'un joueur a cette table d'associée
            playerName = writer.get_extra_info('peername'[0])
            players[playerName] = [reader,writer,tableName] # ajoute le joueur ainsi que ses readers et writers dans le dictionnaire
            waitDelay(tableName)
        elif tableName == table and (countOf(players.values(), tableName) > 1): # gérer l'asynchronicité pour que le joueur ne rejoigne pas si la table est fermée
            playerName = writer.get_extra_info('peername'[0])
            players[playerName] = [reader,writer,tableName] # ajoute le joueur ainsi que ses readers et writers dans le dictionnaire
        else :
            writer.write("END".encode())
            writer.close()
            return
    writer.write(f'recu, vous entrez dans la table {tableName}\n') # ajouter le cas ou le nom de table n'est pas bon

async def blackjack_server():
    # démarre le serveur
    server_dealer = await asyncio.start_server(handle_dealer_request, HOST,PORT_DEALER)
    server_player = await asyncio.start_server(handle_player_request, HOST,PORT_PLAYER)
    async with server_dealer:
        await server_dealer.serve_forever()
    async with server_player:
        await server_player.serve_forever() 


async def waitDelay(tableName):
    asyncio.sleep(tables[tableName])
    del waitingTables[tableName]
    # lancer la partie. appeller la fonction partie

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
    writer.write(f'.') # je crois que c'est ce qu'il faut envoyer pour activer la sequence de choix de carte (joueur.py ligne 33)
    #Récupération du choix
    data = await reader.readline()
    localChoix = data[6].decode() # on prend le 6e caractère ("MORE 1" on prend le "1")
    writer.write(f"Choix enregistré.".encode() + b"\r\n")
    await writer.drain()
    
    writer.close()

    return localChoix

def ilyatildesjoueursactifsdanslavion(joueurs):
    res = False
    for i in joueurs:
        res = res or i
    
    return res

def affiche_mains(main,writer,score): # cette fonction affiche les cartes et le score de la main donnée en paramètre au joueur dont le writer est en paramètre
    writer.write((f"Vos cartes sont :".encode() + b"\r\n"))
    for i in main:
        writer.write((f"{i}".encode() + b"\r\n"))
    writer.write((f"Votre score est de : {score}".encode() + b"\r\n"))
    writer.close()

def quiGagne(scoreServeur,scoreJoueur,writer): #fonction qui compare les scores et qui annonce les résultat d'une partie + met fin a la communication (rajouter le fait de pas contacter ceux qui ont deja perdu)
    if scoreServeur == scoreJoueur:
        writer.write((f"égalité".encode() + b"\r\n"))
    elif scoreServeur < scoreJoueur:
        writer.write((f"vous gagner".encode() + b"\r\n"))
    else:
        writer.write((f"vous perdez".encode() + b"\r\n"))
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
    choix = [] * n # pour sauvegarder les choix de chacun
    scores = [0] * (n+1) # pour sauvegarder les scores des joueurs

    deck = melanger_deck(creer_deck()) # on creer le deck et on le melange

    # le serveur pioche une carte
    mains[0].append(deck[-1])
    deck.pop
    scores[0] = score(mains[0])

    # on distribue deux cartes par joueur
    for i in range(1,len(mains)):
        for j in range(2):
            mains[i].append(deck[-1])
            deck.pop

    # on calcule les scores
    for i in range(1,n): 
        scores[i] = score(mains[i])
    
    # on va envoyer a chaque joueur la carte du croupier + on affiche la main du joueur en question
    for i in range(0,n):
        writerPartie[i].write((f"La carte du serveur est : {mains[0][0]}".encode() + b"\r\n"))
        affiche_mains(mains[i+1],writerPartie[i],score[i+1])

            
    while(ilyatildesjoueursactifsdanslavion(joueurs_actifs)):
      
        for i in range(0,n):
            # on calcule le score du joueur pour savoir si il peut jouer ou pas
            affiche_mains(mains[i+1])
            if joueurs_actifs[i]:

                choixJoueur = ask_joueurs(readerPartie[i],writerPartie[i])

                if choixJoueur == "1": # si c'est 1 on pioche
                    mains[i+1].append(deck[-1])
                    deck.pop
                    scores[i+1]+=score(mains[i+1])
                    writerPartie.write(f'Vous piochez une carte.'.encode() + b"\r\n")

                    if score[i+1]>21: #on regarde tout de suite apres avoir pioché si le score est > 21 comme ca on peux deja virer le joueur
                        joueurs_actifs[i] = False
                        writerPartie.write(f'Vous avez dépasser 21, vous avez perdu.'.encode() + b"\r\n")
                        affiche_mains(mains[i+1],writerPartie[i],score[i+1])
                        writerPartie.write(f"END".encode())
                        joueurs_actifs[i] = False
                else:
                    joueurs_actifs[i] = False

    scores[0] = scores(mains[0])

    while(scores[0]<17) : # le croupier fini de jouer si besoin (- de 17)
        mains[i+1].append(deck[-1])
        deck.pop
        score
        scores[0] = scores(mains[0])

    for i in range(0,n):
        quiGagne(scores[0],scores[i+1],writerPartie[i])
    

if __name__ == '__main__':
    asyncio.run(blackjack_server())