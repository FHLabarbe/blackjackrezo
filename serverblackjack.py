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
players = {playerName,tableName}
tables = {tableName, delay}

async def handle_dealer_request(reader, writer):
    #Le croupier est en attente du HELLO et ne reçoit pas le message pour le moment
    haveName = False
    haveDelay = False

    writer.write(f'Bienvenue sur le serveur de blackjack.')
    await writer.drain()
    while(not haveName):
        data = await reader.readline()
        writer.write(f'Veuillez rentrer le nom de la table que vous voulez créer sous la forme NAME [nom]\n')   
        if data[0,4] == "NAME":
            localTableName = data[5:]
            haveName = True
    
    while(not haveDelay):
        if data[0,4] == "TIME":
            localDelay = data[5:]
            haveDelay = True

    tables[localTableName].append(localDelay)

    writer.close()


async def handle_player_request(reader,writer):

    data = await reader.read() #préciser le nb n de bytes à lire, sinon écrire readline à la place de read 

    if data == "NAME": # nom d'une table
        writer.write(f'entrer le nom :\n')
        tableName = await reader.read()
        writer.write(f'recu, vous entrer dans la table {tableName}\n') # ajouter le cas ou le nom de table n'est pas bon
        playerName = writer.get_extra_info('peername'[0])
        players.append[playerName] = tableName

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
# Fonction qui gère tout
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

def partie_multi(n):
# On initialise une liste de liste dans lesquels on viendra mettre les cartes. Le +1 correspond au croupier qui sera toujours la première main de la liste    
    mains = [[]] * (n+1)
    choix = [] * n
    score_joueurs = [[]] * n

    deck = melanger_deck(creer_deck())

    for i in range(0,len(mains)) :
        for j in range(2):
            mains[i].append(deck[-1])
            deck.pop

    compteur_voir = 0

    while(compteur_voir == 0):
        # on attend les choix
        # on rempli la liste des choix en fonction des reponses des joueurs

        for i in range(0,n):
            if choix[i] == "v" :
                compteur_voir +=1
            elif choix[i] == "p" :
                mains[i+1].append(deck[-1])
                deck.pop

        if compteur_voir<n:
            compteur_voir = 0
    
    score_serveur = score(mains[0])

    while(score_serveur<16) :
        mains[i+1].append(deck[-1])
        deck.pop

        score_serveur = mains[0]
    
    for i in range(0,n):
        score_joueurs[i] = score(mains[i+1])
    

if __name__ == '__main__':
    asyncio.run(blackjack_server())
    #on renvoie les scores des joueurs
    #fin de la partie