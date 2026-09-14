# Game Server Management Bot

This project seeks to better enable hosting a game server (Valheim specifically) by enabling automatic startup/stand down via Discord/afk timers. A Discord bot enables the users to stand the server back up whenever they go to play and it is down. The list of documented functions is not comprehensive, and there is room to add to it.

There are three components:

1. Discord
2. Hetzner (VPS/Cloud provider)
3. GameManager

The Discord piece is merely a bot capable of receiving and sending messages to users and commands to the Hetzner and GameManager components. The Hetzner piece is solely responsible for infrastructural updates, like creating/deleting server instances, assigning a fixed IP address, and attaching the Volume (persistent storage) as needed. The GameManager will be responsible for the status of the actual container running on the VPS, plus tracking player counts to stand it down whenever no players join for a period of more than 25 minutes.

## Discord API

Using the Discord API we are able to allow any user to request the server be stood up with either a message or slash command. In general, it is merely an interface which calls into other components to retrieve statuses and invoke functions.

- `discord.py` will manage the API components, including auth/login, and the parsing of messages. This will be a thin wrapper that just acts as an input/output stream and doesn't handle any core logic. 

### Command List

- `status` - get current state of the server. Uses the server's health endpoint for checking.
- `stop` - manually stop server. Should call the same shutdown as the AFK timer.
- `start` - If the server is stopped, start it. If it is started, send the `status` result.
- `restart` - If the server is running, stop, then start it. If it is not running, 
- `players` - TODO: see if this is possible - return list of players on the server at that time

## Hetzner API

- `hetzner.py` will manage the Cloud Services, aiming to standup and shutdown the server instance as necessary. 

### Command List

- `get_status` - get server healthcheck status
- `get_servers` - get all servers the user can access
- `get_ip` - get server IP address
- `delete_server` - shutdown the server gracefully - should be used whenever possible
- `force_stop_server` - shutdown the server aggressively
- `start_server` - If server is not up, start it
- `restart_game_server` - Command specifically to restart container running game

## Game Manager

- `gameManager.py` will manage the core logic of the game instance, aiming to own it's single instance of a Valheim server and either start it up when it is not active, or stand it down when it is AFK for a period of time. Messages will be passed from and to the Discord bot to either run commands, get current state, or notify on shutdown. Whenever the server is to be modified, it can call into the Hetzner API piece.
- TBD - will own the actual game server setup on new Hetzner instance creation? + gracefully shutting down, AFK checks, etc.

### Command List

- `main` - Loop checking server status
- `get_players` - Check player count
- `_afk_incrememnt` - if no players, increment a stateful tracking variable for time without logged on user

## App Loop

- `main.py` will aim to instantiate instances of all the three components necessary for running.

### Command List

- `main` - The app running loop
