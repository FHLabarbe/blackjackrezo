#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys import argv
from socket import gethostbyname
import asyncio

HOST = "10.0.1.1"
PORT_DEALER = "668"
PORT_PLAYER = "667"

tables = []

async def handle_dealer_request(dealer_reader, dealer_writer):
    pass

async def handle_player_request(player_reader, player_writer):
    pass

async def blackjack_server():
    # démarre le serveur
    server_dealer = await asyncio.start_server(handle_dealer_request, HOST,PORT_DEALER)
    server_player = await asyncio.start_server(handle_player_request, HOST,PORT_PLAYER)
    async with server_dealer:
        await server_dealer.serve_forever()
    async with server_player:
        await server_player.serve_forever() 

if __name__ == '__main__':
    asyncio.run(blackjack_server())