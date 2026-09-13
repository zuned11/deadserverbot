# Game Server Management Bot

This project seeks to better enable hosting a game server (Valheim specifically) by enabling automatic startup/stand down via Discord/afk timers. 

## Discord API

Using the Discord API we are able to allow any user to request the server be stood up with either a message or slash command. 

- `discord.py` will manage the API components, including auth/login, and the parsing of messages. This will be a thin wrapper that just acts as an input/output stream and doesn't handle any core logic.

## Hetzner API

- `hetzner.py` will manage the Cloud Services, aiming to standup and shutdown the server instance as necessary. 

## Game Manager

- `gameManager.py` will manage the core logic of the game instance, aiming to own it's single instance of a Valheim server and either start it up when it is not active, or stand it down when it is AFK for a period of time. Messages will be passed from and to the Discord bot to either run commands, get current state, or notify on shutdown. Whenever the server is to be modified, it can call into the Hetzner API piece.

## App Loop

- `main.py` will aim to instantiate instances of all the three components necessary for running.
