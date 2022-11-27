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
players = {playerName: [playerReader, playerWriter, tableName]}
tables = {tableName: delay}
waitingTables = []


async def handle_dealer_request(reader, writer):
    writer.write(f"Bienvenue sur le serveur de blackjack.".encode() + b"\r\n")

    # Récupération du nom de la table
    data = await reader.readline()
    localTableName = data[5:].decode()
    for table in tables.keys():
        if table == localTableName :
            writer.write(f"Nom de la table déjà existant".encode() + b"\r\n")
            data = await reader.readline()
            writer.write(f"Au revoir".encode() + b"\r\n")
            writer.close()
            await writer.wait_closed()
    writer.write(f"Nom de la table reçu.".encode() + b"\r\n")

    # Récupération du uptime delay de la table
    data = await reader.readline()
    localDelay = data[5:].decode()
    writer.write(f"Délai reçu.".encode() + b"\r\n")

    # insertion de la table dans le dictionnaire. La clé est le nom de la table, et le délai associé : la valeur.
    tables[localTableName] = int(localDelay)
    waitingTables.append(
        localTableName)  # ajoute le nom de la table aux waitingTable. Le décompte se lancera quand le premier joueur rejoindra
    writer.close()
    await writer.wait_closed()


async def handle_player_request(reader, writer):
    writer.write(f"Bienvenue sur le serveur de blackjack".encode() + b"\r\n")
    await writer.drain()

    data = await reader.readline()
    tableName = data[5:].decode()

    for table in waitingTables:
        nb = count(tableName)
        if tableName == table and (
                nb < 1):  # on vérifie que la table existe et compte le nb de fois qu'un joueur a cette table d'associée
            playerName = writer.get_extra_info('peername')[0]
            players[playerName] = [reader, writer,
                                   tableName]  # ajoute le joueur ainsi que ses readers et writers dans le dictionnaire
            writer.write(
                f'reçu, vous entrez dans la table {tableName}'.encode() + b"\r\n")
            await waitDelay(tableName)
            return
        elif tableName == table and (
                nb >= 1):
            playerName = writer.get_extra_info('peername')[0]
            players[playerName] = [reader, writer,
                                   tableName]  # ajoute le joueur ainsi que ses readers et writers dans le dictionnaire
            writer.write(
                f'reçu, vous entrez dans la table {tableName}'.encode() + b"\r\n")
            return
    writer.write("END".encode())
    writer.close()
    return


async def blackjack_server():
    # démarre le serveur
    server_dealer = await asyncio.start_server(handle_dealer_request, HOST, PORT_DEALER)
    server_player = await asyncio.start_server(handle_player_request, HOST, PORT_PLAYER)
    async with server_dealer:
        await server_dealer.serve_forever()
    async with server_player:
        await server_player.serve_forever()


def count(tableName):
    count = 0
    for name in players.keys():  # parcours des différents éléments du dictionnaire
        if tableName == players[name][
            2]:  # on compare si le nom de la table est égale à la valeur de la 3ème place de la liste de chaque élément.
            count += 1
    return count


async def waitDelay(tableName):
    for name in players.keys():
        if players[name][2] == tableName:
            players[name][1].write(
                f'Attente de participant'.encode() + b"\r\n")
    await asyncio.sleep(int(tables[tableName]))
    for name in players.keys():
        if players[name][2] == tableName:
            players[name][1].write(
                f'Lancement de la partie'.encode() + b"\r\n")
    ind = -1
    for i in waitingTables:
        ind += 1
        if tableName == i:
            del waitingTables[ind]

    await partie_multi(players, tableName)


# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Initialisation du jeu de carte
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

def creer_deck():
    deck = []
    couleurs = ["♦", "♥", "♠", "♣"]

    for i in range(0, 4):
        for j in range(0, 13):
            if j == 10:
                deck.append(["V", couleurs[i]])
            elif j == 11:
                deck.append(["D", couleurs[i]])
            elif j == 12:
                deck.append(["R", couleurs[i]])
            else:
                deck.append([j + 1, couleurs[i]])
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
        valeur = str(main[i][0])
        if (valeur > "9") or (valeur == "V") or (valeur == "D") or (valeur == "R"):
            s += 10
        elif (valeur == "1"):
            if (s + 11 > 21):
                s += 1
            else:
                s += 11
        else:
            s += int(valeur)
    return s


# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Permet de gérer si les joueurs ont le droit de jouer
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
def isActivePlayers(joueurs):
    res = False
    for i in joueurs:
        res = res or i

    return res

# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Affiche la main et le score en paramètre
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

async def affiche_mains(main, writer,
                        score):
    writer.write((f"Vos cartes sont : {main}".encode() + b"\r\n"))
    writer.write((f"Votre score est de : {score}".encode() + b"\r\n"))

# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Fonction qui permet de vérifier qui gagne entre le joueur et le serveur, et coupe la connexion avec le joueur
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

async def quiGagne(scoreServeur, scoreJoueur,
             writer):
    if (scoreServeur > 21 and scoreJoueur > 21) or (
            (scoreServeur > scoreJoueur or scoreJoueur > 21) and scoreServeur < 22):
        writer.write((f"vous perdez".encode() + b"\r\n"))

    elif scoreServeur == scoreJoueur:
        writer.write((f"égalité".encode() + b"\r\n"))

    elif (scoreServeur < scoreJoueur or scoreServeur > 21) and scoreJoueur < 22:
        writer.write((f"vous gagnez".encode() + b"\r\n"))

    writer.write((f"END".encode() + b"\r\n"))


# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Fonction qui récupère le choix du joueur
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

async def demander_choix_joueur(reader,writer):
    message = ".\n"
    writer.write(
        message.encode())
    data = await reader.readline()
    dec_data = data.decode()
    localChoix = dec_data[5]  # on prend le 6e caractère ("MORE 1" on prend le "1")
    writer.write(f"Choix enregistré".encode() + b"\r\n")

    return localChoix

# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Récupère le choix du joueur et devient une tâche dans la fonction principale pour l'appel asynchrone
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

async def traitement_joueur(reader,writer,joueurs_actifs,scores,mains,deck,main_serveur):
    if joueurs_actifs :
        await affiche_mains(mains, writer, scores)
        choixJoueur = await demander_choix_joueur(reader, writer)

        if choixJoueur == "1":
            mains.append(deck[-1])
            deck.pop()
            scores = score(mains)
            nouv_carte = mains[-1]
            writer.write(f'Vous piochez la carte : {nouv_carte}'.encode() + b"\r\n")

            if scores > 21:
                joueurs_actifs = False
                score_serveur = score(main_serveur)
                writer.write((f"La main du serveur est : {main_serveur}".encode() + b"\r\n"))
                writer.write((f"Le score du serveur est : {score_serveur}".encode() + b"\r\n"))
                writer.write((f"Vous avez dépassé 21, vous avez donc perdu, merci d'attendre la fin de la partie".encode() + b"\r\n"))

        else:
            joueurs_actifs = False

    return joueurs_actifs,scores,mains,deck

# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Fonction ayant le rôle de "main". Servira a executer l'intégralité de la partie. Elle est appelée une fois par table quand la partie est lancée
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#

async def partie_multi(joueurs, nomTable):
    n = 0
    readerPartie = []
    writerPartie = []

    for i in joueurs.keys():
        if joueurs[i][2] == nomTable:
            readerPartie.append(joueurs[i][0])  # on stocke les reader
            writerPartie.append(joueurs[i][1])  # et les writer
            n += 1  # on compte aussi le nombre de joueurs

    mains = [[] for i in range(n + 1)]  # liste qui garde les mains des joueurs
    joueurs_actifs = [[True] for i in range(n)]  # sert de "compteur de joueur(s) actif(s)"
    scores = [[0] for i in range(n + 1)]  # pour sauvegarder les scores des joueurs

    deck = melanger_deck(creer_deck())  # on cree le deck et on le melange

    # le serveur pioche une carte
    mains[0] = [deck[-1]]
    deck.pop()

    # on distribue deux cartes par joueur
    for i in range(1, len(mains)):
        for j in range(2):
            mains[i].append(deck[-1])
            deck.pop()

    # on calcule les scores
    for i in range(0, n + 1):
        scores[i] = score(mains[i])

    # on va envoyer à chaque joueur la carte du croupier et on affiche la main du joueur en question
    for i in range(0, n):
        writerPartie[i].write((f"La carte du serveur est : {mains[0][0]}".encode() + b"\r\n"))

    while isActivePlayers(joueurs_actifs):

        tasks = []

        for i in range(0, n):

            task = asyncio.create_task(traitement_joueur(readerPartie[i],writerPartie[i],joueurs_actifs[i],scores[i+1],mains[i+1],deck,mains[0]))
            tasks.append(task)

        for i in range(0, n):
            joueurs_actifs[i], scores[i+1], mains[i+1], deck = await tasks[i]

        while len(tasks) > 0:
            tasks.pop()

    while scores[0] < 17:  # le croupier finit de jouer si besoin (- de 17)
        mains[0].append(deck[-1])
        deck.pop()
        scores[0] = score(mains[0])


    for i in range(0, n):
        if joueurs_actifs[i] == False :
            writerPartie[i].write((f"La main du serveur est : {mains[0]}".encode() + b"\r\n"))
            writerPartie[i].write((f"Le score du serveur est : {scores[0]}".encode() + b"\r\n"))
            await affiche_mains(mains[i + 1], writerPartie[i], scores[i + 1])
            await quiGagne(scores[0], scores[i + 1], writerPartie[i])

    for i in range(len(writerPartie)):
        writerPartie[i].close()  # ferme tous les writers
    listPlayersToPop = []  # passe par un dictionnaire pour ne pas changer la taille de ce dernier pendant le parcours
    for name in players.keys():
        if nomTable == players[name][2]:
            listPlayersToPop.append(name)
    for i in range(len(listPlayersToPop)):
        players.pop(listPlayersToPop[i])  # on supprime les joueurs qui ont fini la partie
    tables.pop(nomTable)  # supprime la table


if __name__ == '__main__':
    asyncio.run(blackjack_server())