#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys import argv
from socket import gethostbyname
import asyncio
import random
import os

HOST = "10.0.1.1"
PORT_DEALER = "668"
PORT_PLAYER = "667"
tableName = str
delay = int
playerName = str
players = {playerName : tableName}
tables = {tableName : delay}

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
    tables[localTableName] = localDelay
    
    writer.close()


async def handle_player_request(reader,writer):

    data = await reader.read() #préciser le nb n de bytes à lire, sinon écrire readline à la place de read 

    if data == "NAME": # nom d'une table
        writer.write(f'entrer le nom :\n')
        tableName = await reader.read()
        writer.write(f'recu, vous entrer dans la table {tableName}\n') # ajouter le cas ou le nom de table n'est pas bon
        playerName = writer.get_extra_info('peername'[0])
        players[playerName] = tableName

    if data == "p": # demande de pioche
        writer.write(f'Votre nouvelle carte est :\n')

    if data == "p": # demande de voir
        writer.write(f'Vous avez fini de jouer, votre score final est de : ... , en attente des autres joueurs\n')

    writer.close()
    reader.close()

async def blackjack_server():
    # démarre le serveur
    server_dealer = await asyncio.start_server(handle_dealer_request, HOST,PORT_DEALER)
    server_player = await asyncio.start_server(handle_player_request, HOST,PORT_PLAYER)
    async with server_dealer:
        await server_dealer.serve_forever()
    async with server_player:
        await server_player.serve_forever() 


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

async def ask_joueurs(reader,writer): # ajouter en paramètre le reader/writer mais je sais pas trop comment gerer ca
    writer.write(f"Que voulez-vous faire ? \"MORE 0\" pour passer ou \"MORE 1\" pour piocher.".encode() + b"\r\n") 
    await writer.drain()

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

# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Fonction qui gère tout
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

async def partie_multi(joueurs):
# On initialise une liste de liste dans lesquels on viendra mettre les cartes. Le +1 correspond au croupier qui sera toujours la première main de la liste    
    n = len(joueurs) #nbr de joueur(s)
    mains = [[]] * (n+1) # liste qui garde les mains des joueurs
    joueurs_actifs = [True] * n # sert de "compteur de joueur(s) actif(s)"
    choix = [] * n # pour sauvegarder les choix de chacun
    scores = [[]] * (n+1) # pour sauvegarder les scores des joueurs

    deck = melanger_deck(creer_deck())

    # le serveur pioche une carte
    mains[0].append(deck[-1])
    deck.pop

    # on distribue deux cartes par joueur
    for i in range(1,len(mains)):
        for j in range(2):
            mains[i].append(deck[-1])
            deck.pop

    # il faudrais afficher les cartes de chaque joueur sur leur ecran, on devrait pouvoir faire ca avec une fonction qui envoie masse de writer et en string les trucs que j'utilisais
    #   dans la v1 du jeu OU SINON juste renvoyer genre "Vos cartes : 2 de ♥, R de ♣" etc (histoire de pas s'embeter avec les affichages vu qu'il y a 0 points dessus)
            
    while(ilyatildesjoueursactifsdanslavion(joueurs_actifs)): 
      
        
        for i in range(0,n):
            # on calcule le score du joueur pour savoir si il peut jouer ou pas
            if score(mains[i+1])<=21:
                
                choixJoueur = ask_joueurs() # ajouter en paramètre le reader/writer mais je sais pas trop comment faire pour les recup etc // # on demande aux joueurs quel est leur choix

                if choixJoueur == "1": # si c'est 1 on pioche
                    mains[i+1].append(deck[-1])
                    deck.pop           # du coup ici aussi il faudrait lui afficher la nouvelle "carte" et son score.
                else :
                    choix[i] = 0
            else :
                choix[i] = 0

    while(scores[0]<16) : # le croupier fini de jouer si besoin (- de 16)
        mains[i+1].append(deck[-1])
        deck.pop
    
    for i in range(0,n):
        scores[i] = score(mains[i+1]) # on calcule les scores de tout le monde ( on devrait pouvoir le faire plus tôt je pense mais c'est plus simple ici pour l'instant)

    # et la il faut faire en sorte de renvoyer les scores a chacun + le score du croupier
    

if __name__ == '__main__':
    asyncio.run(blackjack_server())
    #on renvoie les scores des joueurs
    #fin de la partie